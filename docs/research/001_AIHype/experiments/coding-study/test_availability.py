"""Synthetic availability receipts only; no real CLI or provider calls."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, Mock

import availability


def transcript(item_type='agent_message', text='READY', usage=None):
    rows = [{'type': 'thread.started', 'thread_id': 'synthetic'}, {'type': 'turn.started'},
            {'type': 'item.completed', 'item': {'type': item_type, 'text': text}},
            {'type': 'turn.completed'}]
    if usage is not None:
        rows[-1]['usage'] = usage
    return b'\n'.join(json.dumps(row).encode() for row in rows)


class AvailabilityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.binary = self.root / 'synthetic-codex'
        self.binary.write_bytes(b'not an executable')
        self.profile = self.root / 'profile.json'
        self.profile.write_text(json.dumps({'model': 'test-model', 'model_provider': 'openai',
            'tool_version': 'test-version', 'executable_sha256': availability.file_hash(self.binary),
            'configuration_overrides': {'model': 'test-model', 'model_provider': 'openai',
                                        'features.plugins': False},
            'future_cli_options': ['--no-daemon', '--ask-for-approval', 'on-request']}))

    def test_plan_does_not_launch_and_uses_exec_only_flags(self):
        with patch.object(availability.subprocess, 'Popen') as process:
            result = availability.plan(self.root / 'out', self.binary, self.profile)
        process.assert_not_called()
        command = result['command']
        self.assertIn('--ignore-user-config', command)
        self.assertIn('--ephemeral', command)
        self.assertNotIn('--no-daemon', command)
        self.assertNotIn('--ask-for-approval', command)
        self.assertEqual(command[-1], availability.PROMPT)
        self.assertEqual(command[command.index('--sandbox') + 1], 'read-only')
        self.assertEqual(list((self.root / 'out' / 'empty-workspace').iterdir()), [])
        self.assertEqual((self.root / 'out' / 'plan.json').stat().st_mode & 0o777, 0o600)
        self.assertEqual(result['provider_processes_launched'], 0)

    def test_exclusive_output_and_binary_pin(self):
        availability.plan(self.root / 'out', self.binary, self.profile)
        with self.assertRaises(FileExistsError):
            availability.plan(self.root / 'out', self.binary, self.profile)
        self.binary.write_bytes(b'changed')
        with self.assertRaises(ValueError):
            availability.plan(self.root / 'changed', self.binary, self.profile)
        self.assertFalse((self.root / 'changed').exists())

    def test_gate_and_timeout_limit(self):
        with patch.object(availability.subprocess, 'Popen') as process:
            with self.assertRaises(ValueError):
                availability.run(self.root / 'out')
        process.assert_not_called()
        self.assertFalse((self.root / 'out').exists())
        for timeout in (0, -1, 121, True):
            with self.assertRaises(ValueError):
                availability.plan(self.root / 'invalid', self.binary, self.profile, timeout)

    def test_success_retains_unknown_usage_and_model_as_null(self):
        result = availability.parse_events(transcript(), b'READY\n', 0)
        self.assertTrue(result['available'])
        self.assertIsNone(result['usage'])
        self.assertIsNone(result['cost_usd'])
        self.assertIsNone(result['returned_model_id'])

    def test_observed_model_and_usage_preserved_without_inference(self):
        raw = transcript(usage={'input_tokens': 3, 'output_tokens': 1})
        raw += b'\n' + json.dumps({'type': 'thread.started', 'model': 'exposed-name'}).encode()
        result = availability.parse_events(raw, b'READY', 0)
        self.assertEqual(result['returned_model_id'], 'exposed-name')
        self.assertEqual(result['usage']['input_tokens'], 3)
        self.assertIsNone(result['cost_usd'])

    def test_nonstandard_numbers_invalid_usage_and_cost_fail_closed(self):
        for constant in (b'NaN', b'Infinity', b'-Infinity', b'1e999'):
            raw = transcript() + b'\n{"type":"turn.started","unrelated":' + constant + b'}'
            self.assertFalse(availability.parse_events(raw, b'READY', 0)['available'])
        for usage in ({'cost_usd': float('nan')}, {'cost_usd': float('inf')},
                {'cost_usd': -1}, {'cost_usd': True}, {'cost_usd': '0.01'},
                {'input_tokens': -1}, {'input_tokens': 1.5}, {'input_tokens': True},
                {'input_tokens': '3'}, {'input_tokens': {}}, {'cost_usd': {}},
                {'output_tokens': float('inf')},
                {'input_tokens_details': {'cached_tokens': -1}}):
            result = availability.parse_events(transcript(usage=usage), b'READY', 0)
            self.assertFalse(result['available'], usage)
            self.assertIsNone(result['usage'])
            self.assertIsNone(result['cost_usd'])
        raw = transcript().replace(b'{"type": "turn.completed"}',
            b'{"type":"turn.completed","usage":{"cost_usd":1e999}}')
        self.assertFalse(availability.parse_events(raw, b'READY', 0)['available'])
        self.assertTrue(availability.parse_events(
            transcript(usage={'input_tokens': 0, 'cost_usd': 0.0}), b'READY', 0)['available'])

    def test_exposed_different_model_requires_review_without_alias_guessing(self):
        for returned, expected_review in (('test-model', False), ('test-model-snapshot', True)):
            raw = transcript() + b'\n' + json.dumps({'type': 'thread.started', 'model': returned}).encode()
            result = availability.parse_events(raw, b'READY', 0, requested_model='test-model')
            self.assertEqual(result['requires_identity_review'], expected_review)
            self.assertEqual(result['available'], not expected_review)
            self.assertEqual(result['returned_model_id'], returned)
        absent = availability.parse_events(transcript(), b'READY', 0, requested_model='test-model')
        self.assertFalse(absent['requires_identity_review'])
        self.assertIsNone(absent['returned_model_id'])
        self.assertTrue(absent['available'])

    def test_wrong_reply_exit_error_and_timeout_fail(self):
        for raw, final, code, timeout in ((transcript(text='NO'), b'NO', 0, False),
                (transcript(), b' READY ', 0, False), (transcript(), b'READY', 2, False),
                (transcript(), b'READY', 0, True), (b'', b'READY', 0, False)):
            self.assertFalse(availability.parse_events(raw, final, code, timeout)['available'])

    def test_known_tools_and_unknown_events_fail_closed(self):
        for item in ('command_execution', 'function_call', 'mcp_tool_call', 'web_search',
                     'tool_request', 'future_tool'):
            self.assertFalse(availability.parse_events(transcript(item), b'READY', 0)['available'])
        for extra in (b'{bad', b'[]', b'{"type":"new.event"}', b'{"type":"error","message":"failed"}'):
            self.assertFalse(availability.parse_events(transcript() + b'\n' + extra, b'READY', 0)['available'])

    def test_runner_preserves_raw_artifacts_once_with_fake_process(self):
        process = Mock()
        process.returncode = 0
        process.communicate.return_value = (transcript(), b'synthetic stderr')
        def launch(*args, **kwargs):
            (self.root / 'out' / 'last-message.txt').write_bytes(b'READY\n')
            return process
        with patch.object(availability.subprocess, 'Popen', side_effect=launch) as mocked:
            result = availability.run(self.root / 'out', allow_online_probe=True,
                                      executable=self.binary, profile_path=self.profile)
        self.assertEqual(mocked.call_count, 1)
        self.assertTrue(result['available'])
        self.assertEqual(result['kind'], 'availability_not_experiment_result')
        for name, digest in result['raw_artifact_sha256'].items():
            self.assertEqual(digest, availability.file_hash(self.root / 'out' / name))
        self.assertEqual((self.root / 'out' / 'stderr.txt').read_bytes(), b'synthetic stderr')

    def test_timeout_retains_partial_output_without_retry(self):
        process = Mock(pid=1234, returncode=-9)
        process.communicate.side_effect = [availability.subprocess.TimeoutExpired('fake', 1),
                                          (b'partial-output', b'partial-stderr')]
        with patch.object(availability.subprocess, 'Popen', return_value=process) as mocked, \
                patch.object(availability.os, 'killpg') as kill:
            result = availability.run(self.root / 'out', allow_online_probe=True,
                executable=self.binary, profile_path=self.profile, timeout_seconds=1)
        self.assertEqual(mocked.call_count, 1)
        kill.assert_called_once()
        self.assertTrue(result['timed_out'])
        self.assertFalse(result['available'])
        self.assertEqual((self.root / 'out' / 'stdout.jsonl').read_bytes(), b'partial-output')


if __name__ == '__main__':
    unittest.main()
