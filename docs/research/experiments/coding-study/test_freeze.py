"""Synthetic artifacts only: no editor, provider, participant, or task is launched."""

from copy import deepcopy
import json
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch

import availability
import freeze
import prepare
import runtime


class FreezeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        (self.root / 'sessions').mkdir()
        self.configured = prepare.load(freeze.ROOT / 'session.configured.json')
        self.profile = prepare.load(freeze.ROOT / 'codex.study.json')
        self.binary = self.root / 'codex-test-binary'
        self.binary.write_bytes(b'never executed')
        self.profile['executable_sha256'] = prepare.sha(self.binary)
        self.profile_path = self.root / 'codex.study.json'
        self.write(self.profile_path, self.profile)
        self.runtime_directory = self.root / 'sessions/runtime'
        self.runtime_directory.mkdir()
        self.write(self.runtime_directory / 'report.json', {'synthetic': True})
        self.context = {'configured': self.configured, 'profile': self.profile,
                        'runtime': {'synthetic': True}, 'runtime_directory': str(self.runtime_directory),
                        'codex_metadata_directory': str(self.root / 'sessions/metadata'),
                        'executable': str(self.binary)}
        self.addCleanup(patch.stopall)
        patch.object(freeze, 'ROOT', self.root).start()
        patch.object(runtime, 'ROOT', self.root).start()
        patch.object(freeze, '_context', side_effect=self.current_context).start()

    def current_context(self, *_):
        context = deepcopy(self.context)
        context['component_sha256'] = {str(self.profile_path): prepare.sha(self.profile_path),
                                       str(self.binary): prepare.sha(self.binary)}
        return context

    @staticmethod
    def write(path, value):
        path.write_text(json.dumps(value, indent=2) + '\n')

    def output(self, name='freeze'):
        return self.root / 'sessions' / name

    def receipt(self, name='probe'):
        out = self.output(name)
        out.mkdir()
        (out / 'empty-workspace').mkdir()
        command = [str(self.binary), 'exec', '--ignore-user-config', '--ephemeral',
                   '--skip-git-repo-check', '--sandbox', 'read-only', '--json',
                   '--output-last-message', str(out / 'last-message.txt'), '-C', str(out / 'empty-workspace')]
        for key, value in self.profile['configuration_overrides'].items():
            command.extend(['-c', key + '=' + json.dumps(value)])
        command.append(availability.PROMPT)
        identity = {'requested_model': self.profile['model'], 'requested_provider': self.profile['model_provider'],
                    'profile_sha256': prepare.sha(self.profile_path), 'executable_sha256': prepare.sha(self.binary),
                    'outer_retries': 0, 'model_or_provider_fallback': False}
        self.write(out / 'plan.json', {'command': command, 'profile_path': str(self.profile_path), **identity})
        transcript = '\n'.join(json.dumps(row) for row in [
            {'type': 'thread.started'}, {'type': 'turn.started'},
            {'type': 'item.completed', 'item': {'type': 'agent_message', 'text': 'READY'}},
            {'type': 'turn.completed'}]) + '\n'
        (out / 'stdout.jsonl').write_text(transcript)
        (out / 'stderr.txt').write_text('')
        (out / 'last-message.txt').write_text('READY\n')
        parsed = availability.parse_events(transcript, b'READY\n', 0, False, requested_model=self.profile['model'])
        self.write(out / 'receipt.json', {'kind': 'availability_not_experiment_result', **identity, **parsed,
                   'exit_code': 0, 'timed_out': False, 'plan_sha256': prepare.sha(out / 'plan.json'),
                   'raw_artifact_sha256': {name: prepare.sha(out / name) for name in
                                          ('stdout.jsonl', 'stderr.txt', 'last-message.txt')}})
        return out

    def refresh_session_hash(self, directory):
        report = prepare.load(directory / 'freeze-report.json')
        report['session_sha256'] = prepare.sha(directory / 'session.frozen.json')
        self.write(directory / 'freeze-report.json', report)

    def test_unknown_and_missing_availability_remain_blocked_and_private(self):
        out = self.output()
        result = freeze.freeze_session(out, self.runtime_directory)
        self.assertFalse(result['execution_ready'])
        self.assertEqual(len(result['readiness_blockers']), 2)
        self.assertNotIn('condition_assignments', result)
        saved = freeze.verify_frozen(out)
        self.assertIsNone(saved['familiarity']['implemented_task_ids'])
        for name in ('schedule.json', 'session.frozen.json', 'freeze-report.json'):
            self.assertEqual(stat.S_IMODE((out / name).stat().st_mode), 0o600)

    def test_prior_implementation_cannot_be_marked_ready(self):
        report = freeze.freeze_session(self.output(), self.runtime_directory,
                    {'status': 'prior_implementation_tasks_reported', 'implemented_task_ids': ['P1A']}, self.receipt())
        self.assertFalse(report['execution_ready'])
        self.assertEqual(report['readiness_blockers'], ['prior_implementation_familiarity_unresolved'])
        self.assertFalse(report['assignments_disclosure_permitted'])

    def test_known_familiarity_still_requires_availability(self):
        report = freeze.freeze_session(self.output(), self.runtime_directory,
                                       {'status': 'no_prior_implementation_reported', 'implemented_task_ids': []})
        self.assertEqual(report['readiness_blockers'], ['later_authorized_online_availability_unverified'])

    def test_promotion_preserves_schedule_seed_and_original_bytes(self):
        original, promoted = self.output(), self.output('promoted')
        freeze.freeze_session(original, self.runtime_directory)
        saved_before = (original / 'session.frozen.json').read_bytes()
        with patch.object(freeze.schedule, 'generate', side_effect=AssertionError('must not redraw')):
            report = freeze.finalize_session(original, promoted,
                        {'status': 'no_prior_implementation_reported', 'implemented_task_ids': []}, self.receipt())
        self.assertTrue(report['execution_ready'])
        first, second = freeze.verify_frozen(original), freeze.verify_frozen(promoted)
        self.assertEqual(first['randomization_seed'], second['randomization_seed'])
        self.assertEqual(first['session_id'], second['session_id'])
        self.assertEqual((original / 'schedule.json').read_bytes(), (promoted / 'schedule.json').read_bytes())
        self.assertEqual((original / 'session.frozen.json').read_bytes(), saved_before)
        self.assertTrue(second['frozen_at_utc'].endswith('Z'))

    def test_never_overwrites(self):
        freeze.freeze_session(self.output(), self.runtime_directory)
        with patch.object(freeze.schedule, 'generate', side_effect=AssertionError('must not redraw')):
            with self.assertRaises(FileExistsError):
                freeze.freeze_session(self.output(), self.runtime_directory)

    def test_raw_tamper_and_forged_success_are_rejected(self):
        receipt_directory = self.receipt()
        (receipt_directory / 'last-message.txt').write_text('OTHER\n')
        with self.assertRaises(ValueError):
            freeze.freeze_session(self.output(), self.runtime_directory, availability_directory=receipt_directory)
        receipt = prepare.load(receipt_directory / 'receipt.json')
        receipt['raw_artifact_sha256']['last-message.txt'] = prepare.sha(receipt_directory / 'last-message.txt')
        self.write(receipt_directory / 'receipt.json', receipt)
        with self.assertRaisesRegex(ValueError, 'successful tool-free'):
            freeze.freeze_session(self.output(), self.runtime_directory, availability_directory=receipt_directory)

    def test_assignment_and_stage_tampering_rejected_even_with_updated_hashes(self):
        out = self.output()
        freeze.freeze_session(out, self.runtime_directory)
        saved = prepare.load(out / 'session.frozen.json')
        saved['condition_assignments']['P1A'] = 'invalid'
        self.write(out / 'session.frozen.json', saved)
        self.refresh_session_hash(out)
        with self.assertRaisesRegex(ValueError, 'assignment'):
            freeze.verify_frozen(out)
        data = prepare.load(out / 'schedule.json')
        data['slots'][0]['stage'] = 2
        self.write(out / 'schedule.json', data)
        saved['schedule_sha256'] = prepare.sha(out / 'schedule.json')
        self.write(out / 'session.frozen.json', saved)
        self.refresh_session_hash(out)
        with self.assertRaisesRegex(ValueError, 'stage'):
            freeze.verify_frozen(out)

    def test_component_drift_and_cap_tampering_rejected(self):
        out = self.output()
        freeze.freeze_session(out, self.runtime_directory)
        saved = prepare.load(out / 'session.frozen.json')
        saved['active_author_cap_seconds_per_task'] += 1
        self.write(out / 'session.frozen.json', saved)
        self.refresh_session_hash(out)
        with self.assertRaisesRegex(ValueError, 'timing'):
            freeze.verify_frozen(out)
        self.binary.write_bytes(b'drift')
        with self.assertRaisesRegex(ValueError, 'component'):
            freeze.verify_frozen(out)

    def test_disclosure_and_blocker_tampering_rejected(self):
        out = self.output()
        freeze.freeze_session(out, self.runtime_directory)
        report = prepare.load(out / 'freeze-report.json')
        report['assignments_disclosure_permitted'] = True
        self.write(out / 'freeze-report.json', report)
        with self.assertRaisesRegex(ValueError, 'Readiness'):
            freeze.verify_frozen(out)
        report['assignments_disclosure_permitted'] = False
        self.write(out / 'freeze-report.json', report)
        saved = prepare.load(out / 'session.frozen.json')
        saved['remaining_execution_inputs'] = []
        self.write(out / 'session.frozen.json', saved)
        self.refresh_session_hash(out)
        with self.assertRaisesRegex(ValueError, 'Readiness'):
            freeze.verify_frozen(out)

    def test_schedule_identity_must_match_actual_locks(self):
        out = self.output()
        freeze.freeze_session(out, self.runtime_directory)
        data = prepare.load(out / 'schedule.json')
        data['task_pool_sha256'] = '0' * 64
        self.write(out / 'schedule.json', data)
        saved = prepare.load(out / 'session.frozen.json')
        saved['task_pool_sha256'] = data['task_pool_sha256']
        saved['schedule_sha256'] = prepare.sha(out / 'schedule.json')
        self.write(out / 'session.frozen.json', saved)
        self.refresh_session_hash(out)
        with self.assertRaisesRegex(ValueError, 'current locked'):
            freeze.verify_frozen(out)


if __name__ == '__main__':
    unittest.main()
