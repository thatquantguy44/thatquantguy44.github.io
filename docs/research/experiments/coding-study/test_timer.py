"""Synthetic interval/deadline tests; no participant observations or model calls."""

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import timer


class FakeClock:
    def __init__(self):
        self.ns = 0
        self.utc = datetime(2026, 10, 29, 12, tzinfo=timezone.utc)

    def monotonic_ns(self):
        return self.ns

    def utc_now(self):
        return self.utc

    def advance(self, seconds, wall=None):
        self.ns += round(seconds * 1e9)
        self.utc += timedelta(seconds=seconds if wall is None else wall)


def ready_manifest():
    return {'kind': 'synthetic_frozen_manifest_fixture', 'execution_ready': True,
            'session_id': 'synthetic-session', 'participant_id': 'synthetic-participant',
            'repository_commit': 'a' * 40, 'task_pool_sha256': 'b' * 64, 'schedule_sha256': 'c' * 64,
            'execution_environment_frozen': True, 'frozen_at_utc': '2026-10-29T12:00:00Z',
            'timing_method': {'id': timer.METHOD, 'clock_anomaly_tolerance_seconds': 5},
            'active_author_cap_seconds_per_task': 3600, 'wall_cap_seconds_per_task': 5400,
            'ai_tool_and_model_binding': {'tool': 'synthetic-tool', 'model': 'synthetic-model'},
            'condition_assignments': {f'P{i}{letter}': 'ai_enabled' if letter == 'A' else 'no_ai'
                                      for i in range(1, 5) for letter in 'AB'}}


class TimerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.out = Path(self.temp.name) / 'timer'
        self.clock = FakeClock()

    def session(self, **options):
        return timer.TimerSession(self.out, {'kind': 'synthetic-clock-fixture'}, 'synthetic-task', 'synthetic',
                                  clock=self.clock, synthetic=True, **options)

    def records(self, name):
        return [json.loads(line) for line in (self.out / name).read_text().splitlines()]

    def test_disjoint_active_categories_and_passive_waits_reconcile(self):
        session = self.session()
        self.clock.advance(10)
        session.switch('author_verification')
        self.clock.advance(4)
        session.switch('model_wait')
        self.clock.advance(20)
        session.switch('correction_rework')
        self.clock.advance(3)
        session.switch('interruption')
        self.clock.advance(2)
        result = session.finish('accepted')
        self.assertEqual(result['total_nonoverlapping_active_seconds'], 17)
        self.assertEqual(result['model_wait_seconds'], 20)
        self.assertEqual(result['interruption_seconds'], 2)
        self.assertEqual(result['calendar_elapsed_seconds'], 39)
        self.assertEqual(sum(r['duration_seconds'] for r in self.records('intervals.jsonl')), 39)
        self.assertIsNone(result['automated_checks_passed'])
        self.assertIsNone(result['author_assessed_accepted'])
        self.assertIsNone(result['independent_review_passed'])

    def test_active_work_during_model_generation_counts_only_active(self):
        session = self.session(initial_category='model_wait')
        self.clock.advance(2)
        session.switch('implementation_debugging')
        session.note('Model still generating; I am reviewing another input')
        self.clock.advance(5)
        result = session.finish('rejected')
        self.assertEqual(result['model_wait_seconds'], 2)
        self.assertEqual(result['total_nonoverlapping_active_seconds'], 5)
        self.assertEqual(result['calendar_elapsed_seconds'], 7)

    def test_active_cap_counts_all_author_work_and_records_actual_overrun(self):
        session = self.session(active_cap_seconds=10, wall_cap_seconds=30)
        self.clock.advance(4)
        session.switch('author_verification')
        self.clock.advance(3)
        session.switch('correction_rework')
        self.clock.advance(3.25)
        self.assertTrue(session.check_deadlines())
        self.assertEqual(session.summary['terminal_status'], 'timeout')
        self.assertEqual(session.summary['active_cap_overrun_seconds'], .25)

    def test_wall_cap_includes_wait_and_interruptions(self):
        session = self.session(active_cap_seconds=10, wall_cap_seconds=20, initial_category='other_wait')
        self.clock.advance(19)
        self.assertFalse(session.check_deadlines())
        session.switch('interruption')
        self.clock.advance(1)
        self.assertTrue(session.check_deadlines())
        self.assertEqual(session.summary['total_nonoverlapping_active_seconds'], 0)
        self.assertEqual(session.summary['terminal_status'], 'timeout')

    def test_deadline_wins_over_finish_switch_and_status(self):
        for command in ('finish', 'switch', 'status'):
            with self.subTest(command=command):
                self.out = Path(self.temp.name) / command
                self.clock = FakeClock()
                session = self.session(active_cap_seconds=1, wall_cap_seconds=2)
                self.clock.advance(1)
                if command == 'finish':
                    session.finish('accepted')
                elif command == 'switch':
                    session.switch('other_wait')
                else:
                    session.status()
                self.assertEqual(session.summary['terminal_status'], 'timeout')

    def test_status_and_notes_do_not_double_count_or_close_intervals(self):
        session = self.session()
        self.clock.advance(2)
        self.assertEqual(session.status()['active_seconds'], 2)
        session.note('Checking a requirement')
        self.assertEqual(session.status()['active_seconds'], 2)
        self.clock.advance(3)
        result = session.finish('accepted')
        self.assertEqual(result['total_nonoverlapping_active_seconds'], 5)
        self.assertEqual(len(self.records('intervals.jsonl')), 1)

    def test_output_creation_and_closed_state_refuse_reuse(self):
        session = self.session()
        with self.assertRaises(FileExistsError):
            self.session()
        session.finish('abandoned')
        original = (self.out / 'summary.json').read_bytes()
        with self.assertRaises(ValueError):
            session.finish('accepted')
        self.assertEqual((self.out / 'summary.json').read_bytes(), original)

    def test_invalid_categories_caps_and_status_are_rejected(self):
        for options in ({'active_cap_seconds': True}, {'wall_cap_seconds': 0},
                        {'active_cap_seconds': 11, 'wall_cap_seconds': 10}, {'initial_category': 'double_work'}):
            with self.assertRaises(ValueError):
                self.session(**options)
            self.assertFalse(self.out.exists())
        session = self.session()
        with self.assertRaises(ValueError):
            session.switch('both_active_and_wait')
        with self.assertRaises(ValueError):
            session.finish('verified_success')
        self.assertFalse(session.closed)

    def test_direct_nonsynthetic_constructor_requires_ready_matching_bindings(self):
        manifest = ready_manifest()
        unready = dict(manifest, execution_ready=False)
        for candidate, options in ((unready, {}),
                                   (manifest, {'active_cap_seconds': 1}),
                                   (manifest, {'wall_cap_seconds': 6000}),
                                   (manifest, {'clock_anomaly_tolerance_seconds': 6})):
            with self.subTest(options=options):
                with self.assertRaises(ValueError):
                    timer.TimerSession(self.out, candidate, 'P1A', 'ai_enabled', **options)
                self.assertFalse(self.out.exists())

    def test_clock_jump_makes_open_interval_unknown_preserving_closed_lower_bound(self):
        session = self.session()
        self.clock.advance(3)
        session.switch('author_verification')
        self.clock.advance(1, wall=101)
        self.assertTrue(session.check_deadlines())
        result = session.summary
        self.assertEqual(result['terminal_status'], 'abandoned')
        self.assertFalse(result['timing_complete'])
        self.assertEqual(result['known_closed_active_seconds_lower_bound'], 3)
        self.assertIsNone(result['total_nonoverlapping_active_seconds'])
        self.assertIsNone(result['calendar_elapsed_seconds'])
        self.assertIsNone(self.records('intervals.jsonl')[-1]['duration_seconds'])
        self.assertEqual(result['clock_anomaly']['utc_delta_seconds'], 101)

    def test_backwards_monotonic_or_utc_invalidates_measurement(self):
        for clock_type in ('monotonic', 'utc'):
            self.out = Path(self.temp.name) / clock_type
            self.clock = FakeClock()
            session = self.session()
            self.clock.advance(2)
            session.status()
            self.clock.advance(-1 if clock_type == 'monotonic' else 1,
                               wall=1 if clock_type == 'monotonic' else -1)
            session.check_deadlines()
            self.assertFalse(session.summary['timing_complete'])
            self.assertIsNotNone(session.summary['clock_anomaly'])

    def test_small_clock_drifts_accumulate_into_an_anomaly(self):
        session = self.session()
        for _ in range(3):
            self.clock.advance(1, wall=3)
            session.check_deadlines()
        self.assertTrue(session.closed)
        self.assertEqual(session.summary['clock_anomaly']['cumulative_divergence_seconds'], 6)

    def test_invalid_clock_sample_abandons_immediately_without_recovery_duration(self):
        session = self.session()
        self.clock.ns = 'invalid'
        self.assertFalse(session.switch('other_wait'))
        self.assertTrue(session.closed)
        self.assertIsNone(session.summary['ended_at_utc'])
        self.assertIsNone(session.summary['total_nonoverlapping_active_seconds'])
        self.assertIsNone(self.records('intervals.jsonl')[-1]['duration_seconds'])

    def test_abort_retains_partial_measurement_without_resume_or_assumed_recovery(self):
        session = self.session()
        self.clock.advance(4)
        result = session.abort('Synthetic interruption')
        self.assertEqual(result['terminal_status'], 'abandoned')
        self.assertFalse(result['timing_complete'])
        self.assertEqual(result['known_closed_active_seconds_lower_bound'], 4)
        self.assertIsNone(result['total_nonoverlapping_active_seconds'])
        self.assertIsNone(result['independent_review_passed'])

    def test_event_sequences_are_append_only_and_interval_boundaries_touch(self):
        session = self.session()
        self.clock.advance(1)
        session.switch('other_wait')
        self.clock.advance(2)
        session.finish('rejected')
        events = self.records('events.jsonl')
        self.assertEqual([r['sequence'] for r in events], list(range(1, len(events) + 1)))
        intervals = self.records('intervals.jsonl')
        self.assertEqual(intervals[0]['end_monotonic_ns'], intervals[1]['start_monotonic_ns'])

    def test_smoke_is_real_clock_diagnostic_without_participant_or_verified_outcomes(self):
        result = timer.smoke(self.out)
        self.assertEqual(result['kind'], 'synthetic_timer_diagnostic_not_study_result')
        self.assertEqual(result['task_id'], 'synthetic-smoke')
        self.assertEqual(result['terminal_status'], 'timeout')
        self.assertIsNone(result['automated_checks_passed'])
        self.assertIsNone(json.loads((self.out / 'metadata.json').read_text())['participant_id'])

    @unittest.skipUnless(os.name == 'posix', 'Bound interactive environment is POSIX')
    def test_partial_stdin_line_does_not_block_deadline_and_stdin_mode_restores(self):
        read_fd, write_fd = os.pipe()
        manifest = ready_manifest()
        manifest['active_author_cap_seconds_per_task'] = .01
        manifest['wall_cap_seconds_per_task'] = .02
        try:
            os.write(write_fd, b'note partial line without newline')
            with os.fdopen(read_fd, 'r') as source, patch('sys.stdin', source), redirect_stdout(io.StringIO()):
                original = os.get_blocking(source.fileno())
                result = timer.interactive(manifest, 'P1A', 'ai_enabled', self.out)
                self.assertEqual(os.get_blocking(source.fileno()), original)
            self.assertEqual(result['terminal_status'], 'timeout')
        finally:
            os.close(write_fd)


class ReadinessTests(unittest.TestCase):
    def test_unready_missing_assignment_wrong_condition_are_rejected(self):
        manifest = ready_manifest()
        timer.validate_manifest(manifest, 'P1A', 'ai_enabled')
        variants = [dict(manifest, execution_ready=False), dict(manifest, condition_assignments=None),
                    dict(manifest, schedule_sha256=None), dict(manifest, frozen_at_utc=None),
                    dict(manifest, timing_method=None), dict(manifest, ai_tool_and_model_binding=None)]
        for candidate in variants:
            with self.assertRaises(ValueError):
                timer.validate_manifest(candidate, 'P1A', 'ai_enabled')
        with self.assertRaises(ValueError):
            timer.validate_manifest(manifest, 'P1A', 'no_ai')

    def test_ready_list_assignment_and_timing_id_string_are_supported(self):
        manifest = ready_manifest()
        manifest['timing_method'] = timer.METHOD
        manifest['condition_assignments'] = [{'task_id': task, 'condition': condition}
                                            for task, condition in manifest['condition_assignments'].items()]
        self.assertEqual(timer.validate_manifest(manifest, 'P2B', 'no_ai')['active_cap_seconds'], 3600)

    def test_duplicate_unbalanced_assignments_and_bool_caps_rejected(self):
        manifest = ready_manifest()
        duplicate = deepcopy(manifest)
        duplicate['condition_assignments'] = [{'task_id': 'P1A', 'condition': 'ai_enabled'}] * 2
        unbalanced = deepcopy(manifest)
        unbalanced['condition_assignments']['P1B'] = 'ai_enabled'
        for candidate in (duplicate, unbalanced, dict(manifest, active_author_cap_seconds_per_task=True)):
            with self.assertRaises(ValueError):
                timer.validate_manifest(candidate, 'P1A', 'ai_enabled')


if __name__ == '__main__':
    unittest.main()
