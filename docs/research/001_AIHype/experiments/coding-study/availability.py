#!/usr/bin/env python3
"""Prepare a generic Codex availability probe; online execution is opt-in only.

This is not a coding task, experiment result, or proof of runtime isolation.
No model, authentication, or metadata command is invoked by ``plan``.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
PROMPT = 'Do not use tools or read files. Reply with exactly READY.'
MAX_TIMEOUT_SECONDS = 120


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_private(path, value):
    payload = value if isinstance(value, bytes) else (json.dumps(value, indent=2) + '\n').encode()
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'wb') as handle:
        handle.write(payload)


def plan(directory, executable=None, profile_path=None, timeout_seconds=120):
    """Write an exclusive, private invocation plan without launching anything."""
    if isinstance(timeout_seconds, bool) or not 0 < timeout_seconds <= MAX_TIMEOUT_SECONDS:
        raise ValueError('Timeout must be greater than zero and at most 120 seconds')
    profile_path = Path(profile_path or ROOT / 'codex.study.json').resolve()
    profile = json.loads(profile_path.read_text())
    found = executable or shutil.which('codex')
    if not found:
        raise ValueError('Pass --codex with the pinned installed executable')
    executable = Path(found).resolve(strict=True)
    observed_hash = file_hash(executable)
    if observed_hash != profile['executable_sha256']:
        raise ValueError('CLI hash differs from the pinned profile; rebind first')
    overrides = profile['configuration_overrides']
    if overrides.get('model') != profile['model'] or overrides.get('model_provider') != profile['model_provider']:
        raise ValueError('Requested model/provider must match explicit profile overrides')
    out = Path(directory).resolve()
    out.mkdir(parents=True, mode=0o700, exist_ok=False)
    workspace = out / 'empty-workspace'
    workspace.mkdir(mode=0o700)
    command = [str(executable), 'exec', '--ignore-user-config', '--ephemeral',
               '--skip-git-repo-check', '--sandbox', 'read-only', '--json',
               '--output-last-message', str(out / 'last-message.txt'), '-C', str(workspace)]
    # Deliberately do not copy interactive-only future_cli_options.
    for key, value in overrides.items():
        command.extend(['-c', key + '=' + json.dumps(value)])
    command.append(PROMPT)
    result = {'kind': 'availability_probe_plan_not_launched', 'command': command,
              'profile_path': str(profile_path), 'profile_sha256': file_hash(profile_path),
              'executable_sha256': observed_hash, 'requested_model': profile['model'],
              'requested_provider': profile['model_provider'], 'tool_version': profile['tool_version'],
              'timeout_seconds': timeout_seconds, 'outer_retries': 0,
              'transport_retries': None, 'model_or_provider_fallback': False,
              'provider_processes_launched': 0,
              'scope': 'One generic prompt in an empty directory; no SDK or task input',
              'authorization': 'Execution requires explicit permission to lift offline-only preparation and --allow-online-probe'}
    write_private(out / 'plan.json', result)
    return result


def reject_json_constant(value):
    raise ValueError('Nonstandard JSON number: ' + value)


def finite_json_float(value):
    number = float(value)
    if not math.isfinite(number):
        raise ValueError('JSON number exceeds finite float range')
    return number


def valid_usage(value, key=''):
    """Usage consists of nonnegative finite counts/costs and optional details."""
    if key.endswith('_tokens'):
        return isinstance(value, int) and not isinstance(value, bool) and value >= 0
    if key == 'cost_usd' and isinstance(value, (dict, list)):
        return False
    if isinstance(value, dict):
        return all(isinstance(name, str) and valid_usage(child, name)
                   for name, child in value.items())
    if value is None and key.endswith('_details'):
        return True
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    if (isinstance(value, float) and not math.isfinite(value)) or value < 0:
        return False
    return True


def parse_events(stdout, final_message, returncode, timed_out=False, requested_model=None):
    """Validate a synthetic or recorded JSONL transcript, failing closed."""
    problems = []
    events = []
    models = set()
    usage = None
    cost = None
    messages = []
    completed_turns = 0
    allowed_events = {'thread.started', 'turn.started', 'turn.completed', 'item.started',
                      'item.updated', 'item.completed'}
    for number, line in enumerate(stdout.splitlines(), 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line, parse_constant=reject_json_constant,
                               parse_float=finite_json_float)
        except (ValueError, UnicodeDecodeError):
            problems.append(f'Invalid JSONL at line {number}')
            continue
        if not isinstance(event, dict):
            problems.append(f'Non-object event at line {number}')
            continue
        events.append(event)
        kind = event.get('type')
        if kind not in allowed_events:
            problems.append(f'Unrecognized or failed event type at line {number}: {kind!r}')
        for key in ('model', 'model_id'):
            if isinstance(event.get(key), str):
                models.add(event[key])
        if kind in {'item.started', 'item.updated', 'item.completed'}:
            item = event.get('item')
            if not isinstance(item, dict):
                problems.append(f'Missing item at line {number}')
                continue
            item_kind = item.get('type')
            # Everything except plain reasoning and assistant text is rejected,
            # including command_execution, function_call, mcp_tool_call,
            # web_search, tool_request, and new/unknown potential tool types.
            if item_kind not in {'agent_message', 'reasoning'}:
                problems.append(f'Tool or unknown item at line {number}: {item_kind!r}')
            if kind == 'item.completed' and item_kind == 'agent_message':
                messages.append(item.get('text'))
        if kind == 'turn.completed':
            completed_turns += 1
            if 'usage' in event and event['usage'] is not None:
                candidate = event['usage']
                if not isinstance(candidate, dict) or not valid_usage(candidate):
                    problems.append(f'Invalid usage or cost at line {number}')
                else:
                    usage = candidate
                    cost = usage.get('cost_usd')
    if returncode != 0:
        problems.append(f'CLI exit code: {returncode!r}')
    if timed_out:
        problems.append('Probe timed out')
    if completed_turns != 1:
        problems.append('Expected exactly one completed turn')
    if not messages or messages[-1] != 'READY':
        problems.append('Final recorded assistant message is not exactly READY')
    try:
        decoded = final_message.decode('utf-8') if isinstance(final_message, bytes) else final_message
    except UnicodeDecodeError:
        decoded = None
    if not isinstance(decoded, str) or decoded.rstrip('\r\n') != 'READY':
        problems.append('Last-message artifact is not exactly READY')
    identity_review = bool(requested_model is not None and any(model != requested_model for model in models))
    if identity_review:
        problems.append('Returned model identity differs from requested model; explicit identity review required')
    return {'available': not problems, 'problems': problems, 'event_count': len(events),
            'returned_model_ids': sorted(models),
            'returned_model_id': next(iter(models)) if len(models) == 1 else None,
            'requires_identity_review': identity_review,
            'usage': usage, 'cost_usd': cost,
            'tool_free_transcript_verified': bool(events) and not any('Tool or unknown' in p or 'Unrecognized' in p or 'Invalid JSONL' in p or 'Non-object' in p or 'Missing item' in p for p in problems)}


def run(directory, *, allow_online_probe=False, executable=None, profile_path=None, timeout_seconds=120):
    """Run once only after explicit online authorization; never retry or fall back."""
    if not allow_online_probe:
        raise ValueError('Online probe requires --allow-online-probe and explicit user authorization')
    prepared = plan(directory, executable, profile_path, timeout_seconds)
    out = Path(directory).resolve()
    started = datetime.now(timezone.utc).isoformat()
    start_ns = time.monotonic_ns()
    stdout, stderr = b'', b''
    timed_out = False
    returncode = None
    launch_error = None
    # Private mode applies also to the CLI-created last-message artifact.
    previous_umask = os.umask(0o077)
    try:
        try:
            process = subprocess.Popen(prepared['command'], cwd=out / 'empty-workspace',
                                       stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, start_new_session=True)
            try:
                stdout, stderr = process.communicate(timeout=timeout_seconds)
            except subprocess.TimeoutExpired:
                timed_out = True
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass  # The process may exit between the deadline and kill.
                stdout, stderr = process.communicate()
            returncode = process.returncode
        except OSError as exc:
            launch_error = type(exc).__name__
    finally:
        os.umask(previous_umask)
    elapsed = (time.monotonic_ns() - start_ns) / 1_000_000_000
    write_private(out / 'stdout.jsonl', stdout)
    write_private(out / 'stderr.txt', stderr)
    last_path = out / 'last-message.txt'
    if not last_path.exists():
        write_private(last_path, b'')
    last_message = last_path.read_bytes()
    parsed = parse_events(stdout, last_message, returncode, timed_out,
                          requested_model=prepared['requested_model'])
    if launch_error:
        parsed['available'] = False
        parsed['problems'].append('CLI launch failed: ' + launch_error)
    receipt = {'kind': 'availability_not_experiment_result', **parsed,
               'started_at_utc': started, 'ended_at_utc': datetime.now(timezone.utc).isoformat(),
               'elapsed_seconds': elapsed, 'exit_code': returncode, 'timed_out': timed_out,
               'requested_model': prepared['requested_model'], 'requested_provider': prepared['requested_provider'],
               'profile_sha256': prepared['profile_sha256'],
               'executable_sha256': prepared['executable_sha256'],
               'plan_sha256': file_hash(out / 'plan.json'),
               'raw_artifact_sha256': {name: file_hash(out / name) for name in
                                       ('stdout.jsonl', 'stderr.txt', 'last-message.txt')},
               'outer_retries': 0, 'transport_retries': None, 'model_or_provider_fallback': False,
               'limitations': ['Availability only; no coding quality, reliability, or isolation result.',
                               'Requested model name is not an immutable model snapshot.',
                               'Unexposed token usage and cost remain null; internal transport retries are unknown.']}
    write_private(out / 'receipt.json', receipt)
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['plan', 'run'], nargs='?', default='plan')
    parser.add_argument('--out', required=True)
    parser.add_argument('--codex')
    parser.add_argument('--allow-online-probe', action='store_true')
    parser.add_argument('--timeout-seconds', type=float, default=120)
    args = parser.parse_args(argv)
    if args.action == 'plan':
        result = plan(args.out, args.codex, timeout_seconds=args.timeout_seconds)
    else:
        result = run(args.out, allow_online_probe=args.allow_online_probe,
                     executable=args.codex, timeout_seconds=args.timeout_seconds)
    print(json.dumps(result, indent=2))
    return 0 if result.get('available', True) else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({'error': str(exc)}), file=sys.stderr)
        sys.exit(2)
