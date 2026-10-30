#!/usr/bin/env python3
"""Offline manual task timer. It records intervals; it never runs an AI or verifies code."""

import argparse
import codecs
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import selectors
import sys
import time


METHOD = 'interactive_monotonic_intervals_v1'
ACTIVE = ('implementation_debugging', 'author_verification', 'correction_rework')
PASSIVE = ('model_wait', 'other_wait', 'interruption')
CATEGORIES = ACTIVE + PASSIVE
CONDITIONS = ('ai_enabled', 'no_ai')
ALIASES = {'impl': ACTIVE[0], 'verify': ACTIVE[1], 'rework': ACTIVE[2],
           'model_wait': PASSIVE[0], 'other_wait': PASSIVE[1], 'break': PASSIVE[2]}


def number(value):
    try:
        return type(value) in (int, float) and math.isfinite(value)
    except OverflowError:
        return False


def positive(value, name):
    if not number(value) or value <= 0:
        raise ValueError(f'{name} must be finite and positive')
    return float(value)


def load(path):
    def unique(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                raise ValueError(f'Duplicate JSON key: {key}')
            obj[key] = value
        return obj
    return json.loads(Path(path).read_text(), object_pairs_hook=unique,
                      parse_float=lambda value: float(value) if math.isfinite(float(value)) else (_ for _ in ()).throw(ValueError('Non-finite JSON')),
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('Non-finite JSON')))


def write(path, data):
    with Path(path).open('x') as handle:
        json.dump(data, handle, indent=2, allow_nan=False)
        handle.write('\n')


def digest(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def utc_text(value):
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise ValueError('Clock UTC value must be a timezone-aware datetime')
    return value.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')


def valid_utc(value):
    if not isinstance(value, str) or not value.endswith('Z'):
        return False
    try:
        datetime.fromisoformat(value[:-1] + '+00:00')
        return True
    except ValueError:
        return False


def validate_manifest(manifest, task_id, condition):
    """Require explicit frozen bindings; this is not authentication or authorization."""
    if not isinstance(manifest, dict) or manifest.get('execution_ready') is not True:
        raise ValueError('Session is not execution-ready')
    if condition not in CONDITIONS or not re.fullmatch(r'P[1-4][AB]', task_id):
        raise ValueError('Invalid task or condition')
    for key in ('session_id', 'participant_id'):
        if not isinstance(manifest.get(key), str) or not manifest[key].strip():
            raise ValueError(f'Missing {key}')
    for key, length in (('repository_commit', 40), ('task_pool_sha256', 64), ('schedule_sha256', 64)):
        if not isinstance(manifest.get(key), str) or not re.fullmatch(rf'[0-9a-f]{{{length}}}', manifest[key]):
            raise ValueError(f'Missing/invalid {key}')
    if manifest.get('execution_environment_frozen') is not True or not valid_utc(manifest.get('frozen_at_utc')):
        raise ValueError('Environment and session must be frozen')
    method = manifest.get('timing_method')
    method_id = method.get('id') if isinstance(method, dict) else method
    if method_id != METHOD:
        raise ValueError('Timing method is not bound to this logger')
    active = positive(manifest.get('active_author_cap_seconds_per_task'), 'Active cap')
    wall = positive(manifest.get('wall_cap_seconds_per_task'), 'Wall cap')
    if wall < active:
        raise ValueError('Wall cap must be at least the active cap')
    tolerance = positive(method.get('clock_anomaly_tolerance_seconds', 5) if isinstance(method, dict) else 5,
                         'Clock anomaly tolerance')
    binding = manifest.get('ai_tool_and_model_binding')
    if not isinstance(binding, dict) or not binding:
        raise ValueError('AI tool/model binding is missing')
    tool = binding.get('tool') or binding.get('tool_name')
    model = binding.get('model') or binding.get('model_id')
    if not isinstance(tool, str) or not tool.strip() or not isinstance(model, str) or not model.strip():
        raise ValueError('Exact AI tool/model identity must be bound')
    assignments = manifest.get('condition_assignments')
    if isinstance(assignments, list):
        mapping = {}
        for item in assignments:
            if not isinstance(item, dict) or item.get('task_id') in mapping:
                raise ValueError('Invalid/duplicate assignment')
            mapping[item.get('task_id')] = item.get('condition')
    elif isinstance(assignments, dict):
        mapping = assignments
    else:
        raise ValueError('Explicit condition assignments are missing')
    expected = {f'P{pair}{letter}' for pair in range(1, 5) for letter in 'AB'}
    if set(mapping) != expected or any(c not in CONDITIONS for c in mapping.values()):
        raise ValueError('All eight task conditions must be assigned')
    if any({mapping[f'P{pair}A'], mapping[f'P{pair}B']} != set(CONDITIONS) for pair in range(1, 5)):
        raise ValueError('Each pair requires one task in each condition')
    if mapping[task_id] != condition:
        raise ValueError('Requested condition does not match the frozen assignment')
    return {'active_cap_seconds': active, 'wall_cap_seconds': wall,
            'clock_anomaly_tolerance_seconds': tolerance}


class SystemClock:
    @staticmethod
    def monotonic_ns():
        return time.monotonic_ns()

    @staticmethod
    def utc_now():
        return datetime.now(timezone.utc)


class TimerSession:
    """Single-process interval state machine. Injected clocks are for synthetic tests only."""

    def __init__(self, directory, manifest, task_id, condition, *, clock=None,
                 active_cap_seconds=3600, wall_cap_seconds=5400,
                 clock_anomaly_tolerance_seconds=5, initial_category=ACTIVE[0], synthetic=False):
        bound = validate_manifest(manifest, task_id, condition) if not synthetic else None
        self.active_cap = positive(active_cap_seconds, 'Active cap')
        self.wall_cap = positive(wall_cap_seconds, 'Wall cap')
        self.tolerance = positive(clock_anomaly_tolerance_seconds, 'Clock anomaly tolerance')
        if self.wall_cap < self.active_cap or initial_category not in CATEGORIES:
            raise ValueError('Invalid caps/category')
        if bound is not None and (self.active_cap != bound['active_cap_seconds'] or
                                  self.wall_cap != bound['wall_cap_seconds'] or
                                  self.tolerance != bound['clock_anomaly_tolerance_seconds']):
            raise ValueError('Timer caps/tolerance differ from the frozen session binding')
        self.clock = clock or SystemClock()
        initial_ns, initial_utc = self.clock.monotonic_ns(), self.clock.utc_now()
        if type(initial_ns) is not int or initial_ns < 0:
            raise ValueError('Invalid initial monotonic clock')
        utc_text(initial_utc)
        self.out = Path(directory)
        self.out.mkdir(parents=True, exist_ok=False)
        self.manifest = deepcopy(manifest)
        self.task_id, self.condition, self.synthetic = task_id, condition, synthetic
        self.start_ns = self.last_ns = self.interval_ns = initial_ns
        self.start_utc = self.last_utc = self.interval_utc = initial_utc
        self.category = initial_category
        self.totals_ns = {category: 0 for category in CATEGORIES}
        self.sequence = 0
        self.closed = False
        self.summary = None
        write(self.out / 'session.json', self.manifest)
        write(self.out / 'metadata.json', {
            'kind': 'synthetic_timer_diagnostic' if synthetic else 'manual_task_timer',
            'timing_method': METHOD, 'task_id': task_id, 'condition': condition,
            'participant_id': None if synthetic else manifest.get('participant_id'),
            'session_id': None if synthetic else manifest.get('session_id'),
            'session_manifest_sha256': digest(self.manifest),
            'started_at_utc': utc_text(initial_utc), 'active_cap_seconds': self.active_cap,
            'wall_cap_seconds': self.wall_cap, 'clock_anomaly_tolerance_seconds': self.tolerance,
            'external_tool_termination_verified': None,
            'note': 'Manual classification; logger signals stop and does not stop IDE/model tools.'})
        self._event('started', initial_ns, initial_utc, category=initial_category)

    def _append(self, name, record):
        with (self.out / name).open('a') as handle:
            handle.write(json.dumps(record, allow_nan=False) + '\n')
            handle.flush()

    def _event(self, kind, now_ns, now_utc, **fields):
        self.sequence += 1
        self._append('events.jsonl', {'sequence': self.sequence, 'kind': kind,
                     'at_utc': utc_text(now_utc), 'monotonic_elapsed_ns': now_ns - self.start_ns, **fields})

    def _sample(self):
        if self.closed:
            raise ValueError('Timer is closed; recovery/resume is not permitted')
        now_ns = now_utc = None
        try:
            now_ns, now_utc = self.clock.monotonic_ns(), self.clock.utc_now()
            utc_text(now_utc)
            if type(now_ns) is not int or now_ns < 0:
                raise ValueError('Invalid monotonic clock sample')
        except (ValueError, TypeError, OverflowError) as exc:
            anomaly = {'type': 'invalid_clock_sample', 'raw_monotonic_sample': repr(now_ns),
                       'raw_utc_sample': repr(now_utc), 'message': str(exc)}
            self._append('intervals.jsonl', {'category': self.category,
                         'started_at_utc': utc_text(self.interval_utc), 'ended_at_utc': None,
                         'start_monotonic_ns': self.interval_ns, 'end_monotonic_ns': None,
                         'duration_seconds': None, 'measurement_status': 'unknown_clock_anomaly'})
            self._event('clock_anomaly', self.last_ns, self.last_utc, timestamp_is_last_valid_sample=True, **anomaly)
            self._finalize('abandoned', 'Invalid clock sample; no recovery duration inferred', self.last_ns, self.last_utc,
                           complete=False, clock_anomaly=anomaly)
            return None
        mono_delta = (now_ns - self.last_ns) / 1e9
        utc_delta = (now_utc - self.last_utc).total_seconds()
        total_divergence = (now_utc - self.start_utc).total_seconds() - (now_ns - self.start_ns) / 1e9
        if mono_delta < 0 or utc_delta < 0 or abs(utc_delta - mono_delta) > self.tolerance or abs(total_divergence) > self.tolerance:
            anomaly = {'monotonic_delta_seconds': mono_delta, 'utc_delta_seconds': utc_delta,
                       'delta_divergence_seconds': utc_delta - mono_delta,
                       'cumulative_divergence_seconds': total_divergence}
            self._append('intervals.jsonl', {'category': self.category,
                         'started_at_utc': utc_text(self.interval_utc), 'ended_at_utc': utc_text(now_utc),
                         'start_monotonic_ns': self.interval_ns, 'end_monotonic_ns': now_ns,
                         'duration_seconds': None, 'measurement_status': 'unknown_clock_anomaly'})
            self._event('clock_anomaly', now_ns, now_utc, **anomaly)
            self._finalize('abandoned', 'Clock discontinuity; open interval is unknown', now_ns, now_utc,
                           complete=False, clock_anomaly=anomaly)
            return None
        self.last_ns, self.last_utc = now_ns, now_utc
        return now_ns, now_utc

    def _active(self, now_ns):
        return (sum(self.totals_ns[c] for c in ACTIVE) +
                (now_ns - self.interval_ns if self.category in ACTIVE else 0)) / 1e9

    def _close_interval(self, now_ns, now_utc):
        duration = now_ns - self.interval_ns
        self.totals_ns[self.category] += duration
        self._append('intervals.jsonl', {'category': self.category,
                     'started_at_utc': utc_text(self.interval_utc), 'ended_at_utc': utc_text(now_utc),
                     'start_monotonic_ns': self.interval_ns, 'end_monotonic_ns': now_ns,
                     'duration_seconds': duration / 1e9, 'measurement_status': 'observed'})

    def _finalize(self, status, reason, now_ns, now_utc, *, complete=True,
                  reported_status=None, clock_anomaly=None):
        self.closed = True
        known_active = sum(self.totals_ns[c] for c in ACTIVE) / 1e9
        observed_wall = (now_ns - self.start_ns) / 1e9
        self.summary = {
            'kind': 'synthetic_timer_diagnostic_not_study_result' if self.synthetic else 'participant_reported_timing_record',
            'task_id': self.task_id, 'condition': self.condition,
            'session_manifest_sha256': digest(self.manifest), 'timing_method': METHOD,
            'terminal_status': status, 'participant_reported_terminal_status': reported_status,
            'stop_reason': reason, 'started_at_utc': utc_text(self.start_utc),
            'ended_at_utc': None if clock_anomaly and clock_anomaly.get('type') == 'invalid_clock_sample' else utc_text(now_utc),
            'last_valid_clock_sample_at_utc': utc_text(self.last_utc),
            'timing_complete': complete, 'clock_anomaly': clock_anomaly,
            'author_effort_seconds': {c: self.totals_ns[c] / 1e9 if complete else None for c in ACTIVE},
            'total_nonoverlapping_active_seconds': known_active if complete else None,
            'known_closed_active_seconds_lower_bound': known_active,
            'model_wait_seconds': self.totals_ns['model_wait'] / 1e9 if complete else None,
            'other_wait_seconds': self.totals_ns['other_wait'] / 1e9 if complete else None,
            'interruption_seconds': self.totals_ns['interruption'] / 1e9 if complete else None,
            'calendar_elapsed_seconds': observed_wall if complete else None,
            'observed_monotonic_elapsed_seconds_diagnostic': observed_wall,
            'active_cap_seconds': self.active_cap, 'wall_cap_seconds': self.wall_cap,
            'active_cap_overrun_seconds': max(0, known_active - self.active_cap) if complete else None,
            'wall_cap_overrun_seconds': max(0, observed_wall - self.wall_cap) if complete else None,
            'automated_checks_passed': None, 'author_assessed_accepted': None,
            'independent_review_passed': None, 'external_tool_termination_verified': None,
            'ai_usage_and_cost': None,
            'note': 'Timer status is participant-reported or a stop signal; acceptance/quality requires separate evidence.'}
        self._event('finished', now_ns, now_utc, terminal_status=status, timing_complete=complete, reason=reason)
        write(self.out / 'summary.json', self.summary)
        return self.summary

    def _deadline(self, now_ns, now_utc):
        active, wall = self._active(now_ns), (now_ns - self.start_ns) / 1e9
        if active >= self.active_cap or wall >= self.wall_cap:
            self._close_interval(now_ns, now_utc)
            reason = 'Active author cap reached' if active >= self.active_cap else 'Wall cap reached'
            self._finalize('timeout', reason, now_ns, now_utc)
            return True
        return False

    def check_deadlines(self):
        sample = self._sample()
        return self.closed if sample is None else self._deadline(*sample)

    def switch(self, category):
        if category not in CATEGORIES:
            raise ValueError('Unknown timing category')
        sample = self._sample()
        if sample is None or self._deadline(*sample):
            return False
        now_ns, now_utc = sample
        self._close_interval(now_ns, now_utc)
        previous = self.category
        self.category, self.interval_ns, self.interval_utc = category, now_ns, now_utc
        self._event('category_changed', now_ns, now_utc, previous_category=previous, category=category)
        return True

    def note(self, text):
        if not isinstance(text, str) or not text.strip():
            raise ValueError('Note must contain text')
        sample = self._sample()
        if sample is None or self._deadline(*sample):
            return False
        self._event('note', *sample, text=text)
        return True

    def status(self):
        if self.closed:
            return deepcopy(self.summary)
        sample = self._sample()
        if sample is None or self._deadline(*sample):
            return deepcopy(self.summary)
        now_ns, _ = sample
        return {'terminal_status': None, 'category': self.category,
                'active_seconds': self._active(now_ns), 'wall_seconds': (now_ns - self.start_ns) / 1e9,
                'active_remaining_seconds': max(0, self.active_cap - self._active(now_ns)),
                'wall_remaining_seconds': max(0, self.wall_cap - (now_ns - self.start_ns) / 1e9)}

    def finish(self, status, reason='Participant ended the task'):
        if status not in ('accepted', 'rejected', 'abandoned'):
            raise ValueError('Participant status must be accepted, rejected, or abandoned')
        sample = self._sample()
        if sample is None or self._deadline(*sample):
            return deepcopy(self.summary)
        self._close_interval(*sample)
        return self._finalize(status, reason, *sample, reported_status=status)

    def abort(self, reason):
        """Close only the observed partial interval; never extrapolate recovery time."""
        if self.closed:
            return deepcopy(self.summary)
        try:
            sample = self._sample()
        except (ValueError, TypeError, OverflowError) as exc:
            # Last valid raw sample is retained; no duration is inferred for the open interval.
            self._event('measurement_error', self.last_ns, self.last_utc, message=str(exc))
            return self._finalize('abandoned', reason, self.last_ns, self.last_utc, complete=False)
        if sample is None:
            return deepcopy(self.summary)
        if self._deadline(*sample):
            return deepcopy(self.summary)
        self._close_interval(*sample)
        return self._finalize('abandoned', reason, *sample, complete=False)


def smoke(directory):
    session = TimerSession(directory, {'kind': 'synthetic_diagnostic'}, 'synthetic-smoke', 'synthetic',
                           active_cap_seconds=.02, wall_cap_seconds=.04,
                           initial_category='model_wait', synthetic=True)
    while not session.closed:
        time.sleep(.005)
        session.check_deadlines()
    return session.summary


def interactive(manifest, task_id, condition, directory):
    settings = validate_manifest(manifest, task_id, condition)
    # A selectable, nonblocking descriptor keeps deadline checks running even
    # when a pipe supplies a partial line. No blocked daemon input thread remains
    # at interpreter shutdown. The bound participant environment is POSIX.
    if os.name != 'posix':
        raise ValueError('Interactive timing requires selectable POSIX stdin; smoke is portable')
    descriptor = sys.stdin.fileno()
    selector = selectors.SelectSelector()
    selector.register(descriptor, selectors.EVENT_READ)
    original_blocking = os.get_blocking(descriptor)
    os.set_blocking(descriptor, False)
    try:
        session = TimerSession(directory, manifest, task_id, condition, **settings)
    except BaseException:
        selector.close()
        os.set_blocking(descriptor, original_blocking)
        raise
    decoder = codecs.getincrementaldecoder('utf-8')(errors='replace')
    pending = ''
    print('Timer started. Commands: impl, verify, rework, model_wait, other_wait, break, status, note TEXT, finish accepted|rejected|abandoned', flush=True)
    print('At a cap, STOP working. This logger cannot stop your editor or AI tool.', flush=True)

    def command(text):
        text = text.strip()
        try:
            if text in ALIASES:
                session.switch(ALIASES[text])
            elif text.startswith('switch '):
                session.switch(text.partition(' ')[2])
            elif text == 'status':
                print(json.dumps(session.status(), allow_nan=False), flush=True)
            elif text.startswith('note '):
                session.note(text.partition(' ')[2])
            elif text.startswith('finish '):
                session.finish(text.partition(' ')[2])
            elif text in ('quit', 'q'):
                session.finish('abandoned')
            elif text:
                print('Unknown command; use impl/verify/rework/model_wait/other_wait/break/status/note/finish.', flush=True)
        except ValueError as exc:
            print(f'Command rejected: {exc}', flush=True)

    try:
        while not session.closed:
            session.check_deadlines()
            if session.closed:
                break
            if not selector.select(timeout=.25):
                continue
            chunk = os.read(descriptor, 4096)
            if not chunk:
                pending += decoder.decode(b'', final=True)
                if pending:
                    command(pending)
                if not session.closed:
                    session.abort('Input ended unexpectedly; no cross-process resume')
                break
            pending += decoder.decode(chunk)
            while '\n' in pending and not session.closed:
                line, pending = pending.split('\n', 1)
                command(line)
    except KeyboardInterrupt:
        session.abort('Keyboard interrupt; partial measurement retained')
    except Exception:
        session.abort('Timer failure; partial measurement retained')
        raise
    finally:
        selector.close()
        try:
            os.set_blocking(descriptor, original_blocking)
        except OSError:
            pass
    print('STOP: ' + session.summary['terminal_status'] + '. External tool termination is unverified.', flush=True)
    return session.summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    run = sub.add_parser('run')
    run.add_argument('--session', required=True)
    run.add_argument('--task', required=True)
    run.add_argument('--condition', choices=CONDITIONS, required=True)
    run.add_argument('--out', required=True)
    diagnostic = sub.add_parser('smoke')
    diagnostic.add_argument('--out', required=True)
    args = parser.parse_args()
    result = smoke(args.out) if args.command == 'smoke' else interactive(load(args.session), args.task, args.condition, args.out)
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({'error': str(exc)}), file=sys.stderr)
        sys.exit(2)
