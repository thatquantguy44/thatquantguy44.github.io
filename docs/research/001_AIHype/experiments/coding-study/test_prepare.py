"""Preparation integrity checks only; no SDK implementation or study attempts."""

import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch

import prepare


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def archive(self, name='file.txt', kind=None):
        path = self.root / 'source.tar'
        with tarfile.open(path, 'w') as handle:
            member = tarfile.TarInfo(name)
            if kind is not None:
                member.type = kind
                member.linkname = '/tmp/outside'
                handle.addfile(member)
            else:
                member.size = 4
                handle.addfile(member, io.BytesIO(b'data'))
        return path

    def test_source_extraction_preserves_content_and_refuses_overwrite(self):
        archive = self.archive('src/item.txt')
        dest = self.root / 'workspace'
        prepare.extract(archive, dest)
        self.assertEqual((dest / 'src/item.txt').read_text(), 'data')
        with self.assertRaises(FileExistsError):
            prepare.extract(archive, dest)

    def test_archive_escape_and_links_rejected_before_file_write(self):
        for index, (name, kind) in enumerate((('../outside', None), ('/tmp/outside', None), ('link', tarfile.SYMTYPE), ('hard', tarfile.LNKTYPE))):
            archive = self.archive(name, kind)
            dest = self.root / str(index)
            with self.assertRaises(ValueError):
                prepare.extract(archive, dest)
            self.assertEqual(list(dest.rglob('*')), [])

    def test_bad_snapshot_digest_is_rejected(self):
        self.archive()
        with patch.object(prepare, 'bank', return_value={'source': {'archive_sha256': '0' * 64}}):
            with self.assertRaises(ValueError):
                prepare.check_snapshot(self.root)

    def test_hash_lock_rejects_changed_task_definitions(self):
        bank = {'tasks': [{'task_id': f'P{i}{a}'} for i in range(1, 5) for a in 'AB']}
        with patch.object(prepare, 'bank', return_value=bank), \
                patch.object(prepare, 'load', return_value={'sha256': {'file': 'old'}}), \
                patch.object(prepare, 'current_hashes', return_value={'file': 'changed'}):
            with self.assertRaises(ValueError):
                prepare.verify()

    def test_audit_detects_packet_changes_and_unexpected_source_edits(self):
        workspace = self.root / 'workspace'
        workspace.mkdir()
        (workspace / 'target.py').write_text('original')
        (workspace / 'other.py').write_text('original')
        (self.root / 'TASK.md').write_text('original')
        prepare.write(self.root / 'packet.json', {'task_id': 'P1A', 'allowed_changed_paths': ['target.py'],
                      'workspace_sha256': prepare.source_hashes(workspace),
                      'packet_sha256': {'TASK.md': prepare.sha(self.root / 'TASK.md')}})
        (workspace / 'target.py').write_text('permitted change')
        self.assertTrue(prepare.audit(self.root)['local_integrity_pass'])
        (workspace / 'other.py').write_text('unexpected change')
        (self.root / 'TASK.md').write_text('changed requirements')
        report = prepare.audit(self.root)
        self.assertFalse(report['local_integrity_pass'])
        self.assertEqual(report['unexpected_changed_paths'], ['other.py'])
        self.assertEqual(report['altered_packet_artifacts'], ['TASK.md'])

    def test_export_is_fresh_unassigned_and_exposes_only_current_task(self):
        package = self.root / 'research/experiments/coding-study'
        (package / 'tasks').mkdir(parents=True)
        (package / 'acceptance').mkdir()
        (package.parents[1] / 'coding-experiment-protocol.md').write_text('Protocol [context](elsewhere.md)\n')
        (package / 'tasks/P1A.md').write_text('Task [protocol](../../../coding-experiment-protocol.md)\n')
        (package / 'tasks/P1B.md').write_text('Other task must not be exported\n')
        (package / 'acceptance/test_p1a.py').write_text('# current task requirements\n')
        archive = self.archive('src/module.py')
        data = {'source': {'commit': 'pinned'}, 'tasks': [{'task_id': 'P1A', 'target': 'src/module.py',
                'brief': 'tasks/P1A.md', 'acceptance': 'acceptance/test_p1a.py'}]}
        with patch.object(prepare, 'ROOT', package), patch.object(prepare, 'bank', return_value=data), \
                patch.object(prepare, 'verify', return_value={'bank_lock_sha256': 'f' * 64}), \
                patch.object(prepare, 'check_snapshot', return_value=archive):
            out = self.root / 'packet'
            result = prepare.export(self.root, 'P1A', out)
            self.assertIsNone(result['condition'])
            self.assertEqual((out / 'TASK.md').read_text(), 'Task [protocol](PROTOCOL.md)\n')
            self.assertEqual((out / 'PROTOCOL.md').read_text(), 'Protocol context\n')
            self.assertEqual(list((out / 'acceptance').iterdir()), [out / 'acceptance/test_acceptance.py'])
            self.assertNotIn('Other task', ''.join(p.read_text() for p in out.glob('*.md')))
            self.assertTrue(prepare.audit(out)['local_integrity_pass'])
            with self.assertRaises(FileExistsError):
                prepare.export(self.root, 'P1A', out)

    def test_junit_classifies_requirements_vs_collection_errors(self):
        path = self.root / 'junit.xml'
        path.write_text('<testsuites><testsuite tests="3" failures="1" errors="1" skipped="0"/></testsuites>')
        self.assertEqual(prepare.test_counts(path), {'tests': 3, 'failures': 1, 'errors': 1, 'skipped': 0})

    def test_json_duplicates_and_file_overwrite_rejected(self):
        path = self.root / 'data.json'
        path.write_text('{"a": 1, "a": 2}')
        with self.assertRaises(ValueError):
            prepare.load(path)
        with self.assertRaises(FileExistsError):
            prepare.write(path, {})


if __name__ == '__main__':
    unittest.main()
