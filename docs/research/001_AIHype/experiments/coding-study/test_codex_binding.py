"""Local binding checks with fake CLI metadata; no real provider/model calls."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import codex_binding


class BindingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.binary = self.root / 'codex'
        self.binary.write_bytes(b'synthetic binary fixture')
        self.profile = {'tool': 'Codex CLI', 'tool_version': 'synthetic-version',
                        'executable_sha256': codex_binding.file_hash(self.binary),
                        'model': 'synthetic-model', 'reasoning_effort': 'high',
                        'configuration_overrides': {'model': 'synthetic-model', 'features.multi_agent': False, 'features.plugins': False},
                        'future_cli_options': ['--no-daemon']}
        (self.root / 'codex.study.json').write_text(json.dumps(self.profile))
        self.commands = []

    def metadata(self, executable, args):
        self.commands.append(args)
        if args == ['--version']:
            return 'codex-cli synthetic-version\n'
        if args[-2:] == ['features', 'list']:
            return 'multi_agent stable false\nplugins stable false\n'
        if args[-3:] == ['mcp', 'list', '--json']:
            return json.dumps([{'name': 'fixture_server', 'enabled': not bool(args[:-3]),
                                'transport': {'headers': {'secret': 'MUST-NOT-BE-RETAINED'}}}])
        raise AssertionError('Only metadata commands are allowed')

    def check(self):
        with patch.object(codex_binding, 'ROOT', self.root), \
                patch.object(codex_binding, 'metadata', side_effect=self.metadata):
            return codex_binding.check(self.root / 'out', self.binary)

    def test_only_metadata_commands_and_no_secret_retention(self):
        result = self.check()
        self.assertTrue(result['all_mcp_servers_disabled_observed'])
        self.assertEqual(result['provider_prompt_calls'], 0)
        self.assertIsNone(result['live_model_available'])
        combined = ''.join(p.read_text() for p in (self.root / 'out').iterdir())
        self.assertNotIn('MUST-NOT-BE-RETAINED', combined)
        self.assertIn('mcp_servers.fixture_server.enabled=false', combined)
        self.assertEqual(len(self.commands), 4)
        self.assertIn('features.plugins=false', self.commands[1])
        self.assertFalse(any('exec' in args or 'review' in args for args in self.commands))

    def test_changed_binary_rejected_before_metadata_commands(self):
        self.binary.write_bytes(b'changed')
        with self.assertRaises(ValueError):
            self.check()
        self.assertEqual(self.commands, [])
        self.assertFalse((self.root / 'out').exists())

    def test_wrong_version_and_active_server_rejected(self):
        original = self.metadata
        def wrong_version(executable, args):
            return 'codex-cli changed\n' if args == ['--version'] else original(executable, args)
        with patch.object(codex_binding, 'ROOT', self.root), \
                patch.object(codex_binding, 'metadata', side_effect=wrong_version):
            with self.assertRaises(ValueError):
                codex_binding.check(self.root / 'out', self.binary)
        def active_server(executable, args):
            if args[-3:] == ['mcp', 'list', '--json']:
                return '[{"name":"fixture_server","enabled":true}]'
            return original(executable, args)
        with patch.object(codex_binding, 'ROOT', self.root), \
                patch.object(codex_binding, 'metadata', side_effect=active_server):
            with self.assertRaises(ValueError):
                codex_binding.check(self.root / 'out', self.binary)
        self.assertFalse((self.root / 'out').exists())

    def test_ambiguous_or_duplicate_server_names_rejected(self):
        for payload in ('{}', '[{"name":"has.dot"}]', '[{"name":"same"},{"name":"same"}]'):
            with self.assertRaises(ValueError):
                codex_binding.servers(payload)

    def test_disabled_feature_required_and_output_refuses_overwrite(self):
        original = self.metadata
        def enabled(executable, args):
            return 'multi_agent stable true\n' if args[-2:] == ['features', 'list'] else original(executable, args)
        with patch.object(codex_binding, 'ROOT', self.root), \
                patch.object(codex_binding, 'metadata', side_effect=enabled):
            with self.assertRaises(ValueError):
                codex_binding.check(self.root / 'out', self.binary)
        self.check()
        with self.assertRaises(FileExistsError):
            self.check()


if __name__ == '__main__':
    unittest.main()
