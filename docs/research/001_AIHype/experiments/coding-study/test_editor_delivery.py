"""Synthetic short-profile checks; no GUI or provider calls."""

import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

import pytest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import editor_delivery


@pytest.fixture
def setup(tmp_path, monkeypatch):
    root = tmp_path / 'study'
    source = root / 'sessions/runtime'
    (source / 'user-data/User').mkdir(parents=True)
    settings = source / 'user-data/User/settings.json'
    settings.write_bytes(b'{\n "chat.disableAIFeatures": true\n}\n')
    (source / 'report.json').write_text('{"frozen": true}\n')
    workspace = root / 'sessions/workspace'
    workspace.mkdir()
    native = root / 'Code'
    native.write_bytes(b'native executable fixture')
    frozen = {'profile': {'settings_sha256': editor_delivery.runtime.prepare.sha(settings)},
              'editor': {'version': '1.143.1', 'files': {'executable': {
                  'path': str(native), 'sha256': editor_delivery.runtime.prepare.sha(native)}}},
              'locks': {'task_definitions_lock_sha256': 'a' * 64,
                        'session_controls_lock_sha256': 'b' * 64}}
    verified = []

    def verify(directory):
        verified.append(directory)
        assert directory == source
        return frozen

    cache = Path(tempfile.mkdtemp(prefix='edt-', dir='/private/tmp'))
    requests = []

    def new_cache(**kwargs):
        requests.append(kwargs)
        return str(cache)

    monkeypatch.setattr(editor_delivery.runtime, 'ROOT', root)
    monkeypatch.setattr(editor_delivery.runtime, 'verify_runtime', verify)
    monkeypatch.setattr(editor_delivery.tempfile, 'mkdtemp', new_cache)
    monkeypatch.setattr(editor_delivery.runtime.subprocess, 'run', lambda *a, **k: pytest.fail('No launch allowed'))
    yield root, source, workspace, cache, frozen, verified, requests
    shutil.rmtree(cache)


def test_short_delivery_preserves_exact_settings_and_identity(setup):
    root, source, workspace, cache, frozen, verified, requests = setup
    before = (source / 'user-data/User/settings.json').read_bytes()
    out = root / 'sessions/delivery'
    report = editor_delivery.prepare_delivery(source, workspace, out)
    assert verified == [source]
    assert requests == [{'prefix': 'aih-', 'dir': '/private/tmp'}]
    assert (cache / 'user-data/User/settings.json').read_bytes() == before
    assert (source / 'user-data/User/settings.json').read_bytes() == before
    assert not list((cache / 'extensions').iterdir())
    assert report['command'][0] == frozen['editor']['files']['executable']['path']
    assert '--new-window' in report['command'] and '--disable-extensions' in report['command']
    assert report['command'][-1] == str(workspace)
    assert report['runtime_report_sha256'] == editor_delivery.runtime.prepare.sha(source / 'report.json')
    assert report['runtime_helper_sha256'] == editor_delivery.runtime.prepare.sha(Path(editor_delivery.runtime.__file__))
    assert report['delivery_helper_sha256'] == editor_delivery.runtime.prepare.sha(Path(editor_delivery.__file__))
    assert report['source_session_runtime_bindings'] == frozen['locks']
    assert report['conservative_main_socket_path_bytes'] <= 90
    assert report['gui_launched'] is False and report['provider_calls'] == 0
    assert report['execution_ready'] is False and report['operator_verification_pending'] is True
    assert out.stat().st_mode & 0o777 == 0o700
    assert (out / 'report.json').stat().st_mode & 0o777 == 0o600
    assert (cache / 'user-data/User/settings.json').stat().st_mode & 0o777 == 0o600


def test_existing_delivery_refused_before_creating_cache(setup):
    root, source, workspace, _, _, _, requests = setup
    out = root / 'sessions/delivery'
    out.mkdir()
    (out / 'keep.txt').write_text('untouched')
    with pytest.raises(FileExistsError):
        editor_delivery.prepare_delivery(source, workspace, out)
    assert requests == []
    assert (out / 'keep.txt').read_text() == 'untouched'


def test_output_path_guard(setup):
    root, source, workspace, _, _, _, requests = setup
    with pytest.raises(ValueError, match='ignored'):
        editor_delivery.prepare_delivery(source, workspace, root / 'public')
    assert requests == [] and not (root / 'public').exists()


def test_workspace_must_be_existing_directory(setup):
    root, source, _, _, _, _, requests = setup
    workspace = root / 'file.txt'
    workspace.write_text('not a workspace')
    with pytest.raises(ValueError, match='directory'):
        editor_delivery.prepare_delivery(source, workspace, root / 'sessions/delivery')
    assert requests == []


def test_settings_drift_fails_before_output(setup):
    root, source, workspace, _, frozen, _, requests = setup
    frozen['profile']['settings_sha256'] = '0' * 64
    with pytest.raises(ValueError, match='settings hash'):
        editor_delivery.prepare_delivery(source, workspace, root / 'sessions/delivery')
    assert requests == [] and not (root / 'sessions/delivery').exists()


def test_overlong_or_multibyte_socket_path_refused():
    with pytest.raises(ValueError, match='90-byte'):
        editor_delivery._socket_length(Path('/private/tmp/' + 'x' * 90), '1.143.1')
    with pytest.raises(ValueError, match='90-byte'):
        editor_delivery._socket_length(Path('/private/tmp/' + 'é' * 40), '1.143.1')


def test_child_environment_sanitized_without_mutating_or_recording(setup, monkeypatch):
    root, source, workspace, _, _, _, _ = setup
    original = {'HOME': '/unchanged', 'PATH': '/same', 'OTHER_SECRET': 'never-save-me',
                'VSCODE_PID': '1', 'VSCODE_IPC_HOOK_CLI': 'socket', 'ELECTRON_RUN_AS_NODE': '1',
                'ELECTRON_OTHER': 'keep', 'PREFIX_VSCODE_TEST': 'keep'}
    result = editor_delivery.launch_environment(original)
    assert result == {key: value for key, value in original.items()
                      if key not in {'VSCODE_PID', 'VSCODE_IPC_HOOK_CLI', 'ELECTRON_RUN_AS_NODE'}}
    assert original['VSCODE_PID'] == '1' and result['HOME'] == '/unchanged'
    monkeypatch.setenv('VSCODE_FIXTURE', 'remove')
    assert 'VSCODE_FIXTURE' not in editor_delivery.launch_environment()
    assert os.environ['VSCODE_FIXTURE'] == 'remove'
    editor_delivery.prepare_delivery(source, workspace, root / 'sessions/delivery')
    assert 'never-save-me' not in (root / 'sessions/delivery/report.json').read_text()
