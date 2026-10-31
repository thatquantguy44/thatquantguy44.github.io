"""Synthetic schedule checks; no participant tasks or provider calls."""

from contextlib import redirect_stdout
from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch

import schedule


class ScheduleTests(unittest.TestCase):
    def setUp(self):
        self.data = schedule.generate(42, task_pool_sha256='a' * 64,
                                      session_controls_sha256='b' * 64)

    def test_independent_constraints_across_many_seeds(self):
        expected_ids = {f'P{number}{letter}' for number in range(1, 5) for letter in 'AB'}
        seen_orders = set()
        seen_ai_tasks = set()
        for seed in range(100):
            data = schedule.generate(seed)
            slots = data['slots']
            self.assertEqual(len(slots), 8)
            self.assertEqual({slot['task_id'] for slot in slots}, expected_ids)
            self.assertEqual([slot['position'] for slot in slots], list(range(1, 9)))
            self.assertEqual([slot['stage'] for slot in slots], [1] * 4 + [2] * 4)
            for start, expected_pairs in ((0, {'P1', 'P2'}), (4, {'P3', 'P4'})):
                stage = slots[start:start + 4]
                self.assertEqual({slot['pair_id'] for slot in stage}, expected_pairs)
                self.assertEqual({stage[0]['condition'], stage[2]['condition']}, {'ai_enabled', 'no_ai'})
                for pair_start in (0, 2):
                    pair = stage[pair_start:pair_start + 2]
                    pair_id = pair[0]['pair_id']
                    self.assertEqual({slot['task_id'] for slot in pair}, {pair_id + 'A', pair_id + 'B'})
                    self.assertTrue(all(slot['pair_id'] == pair_id for slot in pair))
                    self.assertEqual({slot['condition'] for slot in pair}, {'ai_enabled', 'no_ai'})
            seen_orders.add(tuple(slot['pair_id'] for slot in slots[::2]))
            seen_ai_tasks.add(tuple(sorted(task for task, condition in data['condition_assignments'].items()
                                           if condition == 'ai_enabled')))
        self.assertGreater(len(seen_orders), 1)
        self.assertGreater(len(seen_ai_tasks), 1)

    def test_explicit_seed_replays_without_global_random_state(self):
        with patch('random.shuffle', side_effect=AssertionError('global RNG forbidden')):
            self.assertEqual(self.data, schedule.generate(42, task_pool_sha256='a' * 64,
                                                         session_controls_sha256='b' * 64))
        self.assertEqual(self.data['seed'], 42)
        self.assertEqual(self.data['seed_source'], 'caller_supplied')

    def test_fresh_seed_is_retained_and_replayable(self):
        with patch.object(schedule.secrets, 'randbits', return_value=123456) as draw:
            data = schedule.generate()
        draw.assert_called_once_with(128)
        self.assertEqual(data['seed'], 123456)
        self.assertEqual(data['seed_source'], 'secrets.randbits(128)')
        self.assertEqual(data['slots'], schedule.generate(123456)['slots'])

    def test_metadata_binds_locks_without_claiming_observations(self):
        self.assertEqual(self.data['kind'], 'schedule_not_results')
        self.assertEqual(self.data['task_pool_sha256'], 'a' * 64)
        self.assertEqual(self.data['session_controls_sha256'], 'b' * 64)
        self.assertEqual(self.data['empirical_observations'], 0)
        self.assertEqual(self.data['planned_task_count'], 8)
        self.assertIn('No task counts as an observation', self.data['interpretation'])
        self.assertEqual(self.data['algorithm'], 'restricted_staged_pairs_v1')

    def test_invalid_seed_and_lock_digests_rejected(self):
        for bad_seed in (-1, True, '42', 1.5):
            with self.subTest(seed=bad_seed), self.assertRaises(ValueError):
                schedule.generate(bad_seed)
        for field in ('task_pool_sha256', 'session_controls_sha256'):
            for bad_hash in (None, '', 'a' * 63, 'z' * 64, 'A' * 64):
                with self.subTest(field=field, digest=bad_hash), self.assertRaises(ValueError):
                    schedule.generate(42, **{field: bad_hash})
                invalid = deepcopy(self.data)
                invalid[field] = bad_hash
                with self.assertRaises(ValueError):
                    schedule.validate_schedule(invalid)

    def test_missing_duplicate_and_invalid_tasks_rejected(self):
        for change in ('missing', 'duplicate', 'invalid'):
            data = deepcopy(self.data)
            if change == 'missing':
                data['slots'].pop()
            else:
                data['slots'][1]['task_id'] = data['slots'][0]['task_id'] if change == 'duplicate' else 'P5A'
            with self.subTest(change=change), self.assertRaises(ValueError):
                schedule.validate_schedule(data)

    def test_stage_and_position_violations_rejected(self):
        for field, bad_value in (('stage', 2), ('stage', True), ('position', 2), ('position', True)):
            data = deepcopy(self.data)
            data['slots'][0][field] = bad_value
            with self.subTest(field=field, value=bad_value), self.assertRaises(ValueError):
                schedule.validate_schedule(data)
        data = deepcopy(self.data)
        data['slots'] = data['slots'][4:] + data['slots'][:4]
        for position, slot in enumerate(data['slots'], 1):
            slot['position'] = position
        with self.assertRaisesRegex(ValueError, 'stage 1'):
            schedule.validate_schedule(data)

    def test_cross_pair_identity_and_interleaving_rejected(self):
        data = deepcopy(self.data)
        data['slots'][0]['pair_id'] = data['slots'][2]['pair_id']
        with self.assertRaisesRegex(ValueError, 'identity'):
            schedule.validate_schedule(data)
        data = deepcopy(self.data)
        data['slots'][1], data['slots'][2] = data['slots'][2], data['slots'][1]
        for position, slot in enumerate(data['slots'], 1):
            slot['position'] = position
        with self.assertRaisesRegex(ValueError, 'contiguous'):
            schedule.validate_schedule(data)

    def test_unbalanced_conditions_and_unknown_conditions_rejected(self):
        data = deepcopy(self.data)
        data['slots'][1]['condition'] = data['slots'][0]['condition']
        with self.assertRaisesRegex(ValueError, 'one task per condition'):
            schedule.validate_schedule(data)
        data = deepcopy(self.data)
        for index in (2, 3):
            current = data['slots'][index]['condition']
            data['slots'][index]['condition'] = 'no_ai' if current == 'ai_enabled' else 'ai_enabled'
        with self.assertRaisesRegex(ValueError, 'balance'):
            schedule.validate_schedule(data)
        data = deepcopy(self.data)
        data['slots'][0]['condition'] = 'review_agent'
        with self.assertRaisesRegex(ValueError, 'unknown condition'):
            schedule.validate_schedule(data)

    def test_assignment_mapping_seed_and_algorithm_tampering_rejected(self):
        data = deepcopy(self.data)
        data['condition_assignments'].pop(next(iter(data['condition_assignments'])))
        with self.assertRaisesRegex(ValueError, 'condition_assignments'):
            schedule.validate_schedule(data)
        data = deepcopy(self.data)
        data['seed'] = 999
        with self.assertRaisesRegex(ValueError, 'recorded seed'):
            schedule.validate_schedule(data)
        for key, value in (('algorithm', 'unrestricted'), ('constraints', {}),
                           ('empirical_observations', 8), ('empirical_observations', False)):
            data = deepcopy(self.data)
            data[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                schedule.validate_schedule(data)

    def test_private_canonical_write_returns_digest_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'private.json'
            digest = schedule.write_schedule(path, self.data)
            original = path.read_bytes()
            self.assertEqual(digest, hashlib.sha256(original).hexdigest())
            self.assertEqual(json.loads(original), self.data)
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            with self.assertRaises(FileExistsError):
                schedule.write_schedule(path, schedule.generate(43))
            self.assertEqual(path.read_bytes(), original)

    def test_invalid_schedule_is_never_written(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'invalid.json'
            data = deepcopy(self.data)
            data['slots'].pop()
            with self.assertRaises(ValueError):
                schedule.write_schedule(path, data)
            self.assertFalse(path.exists())

    def test_cli_reports_only_path_and_digest(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'private.json'
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(schedule.main(['--seed', '42', '--out', str(path)]), 0)
            message = output.getvalue()
            self.assertIn(hashlib.sha256(path.read_bytes()).hexdigest(), message)
            self.assertNotIn('ai_enabled', message)
            self.assertNotIn('no_ai', message)
            self.assertNotIn('P1A', message)


if __name__ == '__main__':
    unittest.main()
