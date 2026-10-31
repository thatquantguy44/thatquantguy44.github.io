import json
from pathlib import Path
import plistlib
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import runtime


@pytest.fixture
def prepared(tmp_path, monkeypatch):
    root = tmp_path / 'study'
    root.mkdir()
    monkeypatch.setattr(runtime, 'ROOT', root)
    monkeypatch.setattr(runtime.platform, 'platform', lambda: 'macOS-test-arm64')
    monkeypatch.setattr(runtime.platform, 'machine', lambda: 'arm64')
    locks = {'task_definitions_lock_sha256': 'a' * 64,
             'session_controls_lock_sha256': 'b' * 64,
             'source_commit': 'c' * 40,
             'common_source_and_documentation_archive_sha256': 'd' * 64}
    monkeypatch.setattr(runtime, 'verify_locks', lambda: locks.copy())
    app = tmp_path / 'Code.app/Contents/Resources/app'
    editor = app / 'bin/code'
    workbench = app / 'out/vs/workbench/workbench.desktop.main.js'
    files = [editor, app.parent.parent / 'MacOS/Code', app / 'product.json', app / 'package.json', workbench]
    for path in files:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('\n'.join(runtime.SETTINGS) if path == workbench else '{}')
    (app.parent.parent / 'Info.plist').write_bytes(plistlib.dumps({'CFBundleExecutable': 'Code'}))
    calls = []

    def run(args, **kwargs):
        calls.append(args)
        assert kwargs == {'capture_output': True, 'text': True, 'timeout': 30, 'check': True}
        if args == [str(editor), '--version']:
            output = '1.143.1\n' + 'e' * 40 + '\narm64\n'
        elif args == ['/bin/zsh', '--version']:
            output = 'zsh test shell\n'
        elif '--list-extensions' in args:
            assert '--user-data-dir' in args and '--extensions-dir' in args
            assert '--disable-extensions' in args
            output = ''
        else:
            raise AssertionError('Unexpected command, potentially a GUI launch: ' + repr(args))
        return subprocess.CompletedProcess(args, 0, output, '')

    monkeypatch.setattr(runtime.subprocess, 'run', run)
    return root, editor, calls, locks


def test_private_profile_metadata_only_and_no_secrets(prepared, monkeypatch):
    root, editor, calls, locks = prepared
    monkeypatch.setenv('UNRELATED_API_SECRET', 'not-for-the-report')
    out = root / 'sessions/runtime'
    report = runtime.prepare_runtime(out, editor)
    assert report['execution_ready'] is False
    assert report['gui_launched'] is False
    assert report['locks'] == locks
    assert report['editor']['version'] == '1.143.1'
    assert report['editor']['setting_name_check_proves_effective_gui_configuration'] is False
    assert report['extension_inventory']['installed_extensions'] == []
    assert not list((out / 'extensions').iterdir())
    assert runtime.prepare.load(out / 'user-data/User/settings.json') == runtime.SETTINGS
    assert out.stat().st_mode & 0o777 == 0o700
    assert (out / 'report.json').stat().st_mode & 0o777 == 0o600
    assert (out / 'user-data/User/settings.json').stat().st_mode & 0o777 == 0o600
    assert 'not-for-the-report' not in (out / 'report.json').read_text()
    assert len(calls) == 3
    assert not any('--new-window' in command for command in calls)
    assert runtime.verify_runtime(out) == report


def test_existing_output_is_never_replaced(prepared):
    root, editor, _, _ = prepared
    out = root / 'sessions/runtime'
    runtime.prepare_runtime(out, editor)
    before = (out / 'report.json').read_bytes()
    with pytest.raises(FileExistsError):
        runtime.prepare_runtime(out, editor)
    assert (out / 'report.json').read_bytes() == before


def test_output_must_be_ignored_private_location(prepared):
    root, editor, _, _ = prepared
    with pytest.raises(ValueError, match='ignored'):
        runtime.prepare_runtime(root / 'public', editor)
    assert not (root / 'public').exists()


@pytest.mark.parametrize('change, message', [('settings', 'settings'), ('editor', 'installation'),
                                            ('extensions', 'extension'), ('locks', 'binding')])
def test_freeze_drift_fails(prepared, monkeypatch, change, message):
    root, editor, _, locks = prepared
    out = root / 'sessions/runtime'
    runtime.prepare_runtime(out, editor)
    if change == 'settings':
        (out / 'user-data/User/settings.json').write_text('{}')
    elif change == 'editor':
        editor.write_text('changed')
    elif change == 'extensions':
        (out / 'extensions/new-extension').mkdir()
    else:
        monkeypatch.setattr(runtime, 'verify_locks', lambda: {**locks, 'source_commit': '0' * 40})
    with pytest.raises(ValueError, match=message):
        runtime.verify_runtime(out)


def test_extension_inventory_rejects_any_extensions(prepared, monkeypatch):
    root, editor, calls, _ = prepared
    original = runtime._run
    monkeypatch.setattr(runtime, '_run', lambda args: 'publisher.extension@1.0' if '--list-extensions' in args else original(args))
    out = root / 'sessions/runtime'
    with pytest.raises(ValueError, match='inventory'):
        runtime.prepare_runtime(out, editor)
    assert not (out / 'report.json').exists()


def test_cli_generated_empty_inventory_is_removed(prepared, monkeypatch):
    root, editor, _, _ = prepared
    original = runtime._run

    def inventory(args):
        result = original(args)
        if '--list-extensions' in args:
            extensions = Path(args[args.index('--extensions-dir') + 1])
            (extensions / 'extensions.json').write_text('[]')
        return result

    monkeypatch.setattr(runtime, '_run', inventory)
    out = root / 'sessions/runtime'
    runtime.prepare_runtime(out, editor)
    assert not list((out / 'extensions').iterdir())


def test_missing_setting_name_fails_before_output(prepared):
    root, editor, _, _ = prepared
    (editor.parent.parent / 'out/vs/workbench/workbench.desktop.main.js').write_text('')
    out = root / 'sessions/runtime'
    with pytest.raises(ValueError, match='settings'):
        runtime.prepare_runtime(out, editor)
    assert not out.exists()


def test_task_recipe_creates_new_profile_without_launch(prepared, monkeypatch):
    root, editor, calls, locks = prepared
    out = root / 'sessions/runtime'
    runtime.prepare_runtime(out, editor)
    packet = root / 'sessions/packets/P1A'
    (packet / 'workspace').mkdir(parents=True)
    (packet / 'packet.json').write_text(json.dumps({'task_id': 'P1A', 'condition': None,
                                                  'bank_lock_sha256': locks['task_definitions_lock_sha256']}))
    monkeypatch.setattr(runtime.prepare, 'bank', lambda: {'tasks': [{'task_id': 'P1A'}]})
    count = len(calls)
    recipe = runtime.prepare_task_editor(out, packet)
    assert len(calls) == count
    assert recipe['gui_launched'] is False
    assert recipe['operator_verification_pending'] is True
    assert '--new-window' in recipe['command'] and '--disable-extensions' in recipe['command']
    assert recipe['command'][-1] == str(packet / 'workspace')
    profile = out / 'task-editors/P1A'
    assert runtime.prepare.load(profile / 'user-data/User/settings.json') == runtime.SETTINGS
    assert not list((profile / 'extensions').iterdir())
    with pytest.raises(FileExistsError):
        runtime.prepare_task_editor(out, packet)


def test_lock_verification_detects_changed_control(tmp_path, monkeypatch):
    root = tmp_path / 'research/experiments/coding-study'
    root.mkdir(parents=True)
    (root / 'control.py').write_text('original')
    bank_digest = 'a' * 64
    (root / 'session-controls.lock.json').write_text(json.dumps({
        'task_definitions_lock_sha256': bank_digest,
        'sha256': {'control.py': runtime.prepare.sha(root / 'control.py')}}))
    monkeypatch.setattr(runtime, 'ROOT', root)
    monkeypatch.setattr(runtime.prepare, 'verify', lambda: {'bank_lock_sha256': bank_digest})
    monkeypatch.setattr(runtime.prepare, 'bank', lambda: {'source': {'commit': 'b' * 40, 'archive_sha256': 'c' * 64}})
    assert runtime.verify_locks()['source_commit'] == 'b' * 40
    (root / 'control.py').write_text('changed')
    with pytest.raises(ValueError, match='control changed'):
        runtime.verify_locks()
