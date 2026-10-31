#!/usr/bin/env python3
"""Prepare private, offline editor metadata. Never launch a GUI or study task."""

import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import plistlib
import subprocess
import sys

import prepare

ROOT = Path(__file__).resolve().parent
DEFAULT_EDITOR = '/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code'
SETTINGS = {
    'chat.disableAIFeatures': True,
    'editor.inlineSuggest.enabled': False,
    'extensions.autoUpdate': False,
    'extensions.autoCheckUpdates': False,
    'update.mode': 'none',
    'telemetry.telemetryLevel': 'off',
    'workbench.enableExperiments': False,
    'files.autoSave': 'off',
}


def _write(path, value):
    """Create private JSON without replacing any previous artifact."""
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'w') as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write('\n')


def _new_private_directory(path):
    path = Path(path).resolve()
    allowed = [ROOT / 'sessions', ROOT / 'runs']
    if not any(path.is_relative_to(root.resolve()) and path != root.resolve() for root in allowed):
        raise ValueError('Runtime output must be a new directory beneath ignored sessions/ or runs/')
    path.mkdir(mode=0o700, parents=True, exist_ok=False)
    return path


def verify_locks():
    bank = prepare.verify()
    path = ROOT / 'session-controls.lock.json'
    lock = prepare.load(path)
    if lock['task_definitions_lock_sha256'] != bank['bank_lock_sha256']:
        raise ValueError('Session controls refer to a different task bank')
    for name, digest in lock['sha256'].items():
        source = (ROOT / name).resolve()
        if not source.is_relative_to(ROOT.parents[1].resolve()) or prepare.sha(source) != digest:
            raise ValueError(f'Session control changed: {name}')
    return {'task_definitions_lock_sha256': bank['bank_lock_sha256'],
            'session_controls_lock_sha256': prepare.sha(path),
            'source_commit': prepare.bank()['source']['commit'],
            'common_source_and_documentation_archive_sha256': prepare.bank()['source']['archive_sha256']}


def _run(arguments):
    result = subprocess.run(arguments, capture_output=True, text=True, timeout=30, check=True)
    return result.stdout.strip()


def editor_metadata(editor_path):
    editor = Path(editor_path).resolve(strict=True)
    app = editor.parent.parent
    bundle_info = app.parent.parent / 'Info.plist'
    with bundle_info.open('rb') as handle:
        executable_name = plistlib.load(handle)['CFBundleExecutable']
    if not isinstance(executable_name, str) or Path(executable_name).name != executable_name:
        raise ValueError('Invalid editor bundle executable name')
    files = {'cli': editor, 'executable': app.parent.parent / 'MacOS' / executable_name,
             'bundle_info': bundle_info,
             'product': app / 'product.json', 'package': app / 'package.json',
             'workbench': app / 'out/vs/workbench/workbench.desktop.main.js'}
    if not all(path.is_file() for path in files.values()):
        raise ValueError('Expected installed VS Code CLI, executable, product metadata, and workbench')
    lines = _run([str(editor), '--version']).splitlines()
    if len(lines) != 3 or not lines[0] or len(lines[1]) != 40 or not lines[2]:
        raise ValueError('Unexpected VS Code version response')
    settings_source = files['workbench'].read_text()
    recognized = {key: key in settings_source for key in SETTINGS}
    if not all(recognized.values()):
        raise ValueError('One or more requested editor settings are absent from the local workbench')
    return {'path': str(editor), 'version': lines[0], 'commit': lines[1], 'architecture': lines[2],
            'files': {name: {'path': str(path), 'sha256': prepare.sha(path)} for name, path in files.items()},
            'setting_names_present_in_local_workbench': recognized,
            'setting_name_check_proves_effective_gui_configuration': False}


def _profile(directory):
    user_data = directory / 'user-data'
    user = user_data / 'User'
    user.mkdir(mode=0o700, parents=True)
    user_data.chmod(0o700)
    extensions = directory / 'extensions'
    extensions.mkdir(mode=0o700)
    _write(user / 'settings.json', SETTINGS)
    return user_data, extensions


def _inventory(editor, user_data, extensions):
    args = [editor, '--list-extensions', '--show-versions', '--disable-extensions',
            '--user-data-dir', str(user_data), '--extensions-dir', str(extensions), '--sync', 'off']
    output = _run(args)
    # The inventory command writes an empty extensions.json even when no
    # extensions exist. Remove only that verified empty, generated inventory
    # so the launch template still has a literally empty extensions directory.
    generated_inventory = extensions / 'extensions.json'
    removed_inventory = False
    if generated_inventory.is_file() and not generated_inventory.is_symlink():
        if prepare.load(generated_inventory) != []:
            raise ValueError('Isolated editor extension inventory must be empty')
        generated_inventory.unlink()
        removed_inventory = True
    if output or any(extensions.iterdir()):
        raise ValueError('Isolated editor extension inventory must be empty')
    return {'command': args, 'installed_extensions': [], 'extensions_directory_empty': True,
            'empty_generated_inventory_removed': removed_inventory,
            'built_in_editor_features_inventoried': False}


def prepare_runtime(directory, editor_path=DEFAULT_EDITOR):
    """Freeze local metadata and a settings template, without starting the editor."""
    locks = verify_locks()
    editor = editor_metadata(editor_path)
    shell = Path('/bin/zsh')
    environment = {'python': sys.version, 'python_executable': str(Path(sys.executable).resolve()),
                   'platform': platform.platform(), 'architecture': platform.machine(),
                   'dependencies': {name: importlib.metadata.version(name) for name in ('pytest', 'numpy')},
                   'shell': {'path': str(shell), 'version': _run([str(shell), '--version']),
                             'sha256': prepare.sha(shell)}}
    out = _new_private_directory(directory)
    user_data, extensions = _profile(out)
    inventory = _inventory(editor['path'], user_data, extensions)
    settings_path = user_data / 'User/settings.json'
    if prepare.load(settings_path) != SETTINGS:
        raise ValueError('CLI inventory changed the prepared editor settings')
    report = {'kind': 'offline_editor_preparation_not_execution_readiness',
              'created_utc': datetime.now(timezone.utc).isoformat(), 'execution_ready': False,
              'gui_launched': False, 'model_calls': 0, 'study_tasks_started': 0,
              'locks': locks, 'editor': editor, 'environment': environment,
              'profile': {'user_data': str(user_data), 'extensions': str(extensions),
                          'settings': str(settings_path), 'settings_sha256': prepare.sha(settings_path)},
              'extension_inventory': inventory,
              'future_task_launch': {'helper': 'prepare_task_editor', 'fresh_profile_per_task': True,
                                     'extensions_disabled_in_both_conditions': True,
                                     'codex_allowed_only_in_ai_enabled_condition': True},
              'limitations': ['No operating-system sandbox or network isolation is established.',
                              'Settings names exist locally; effective GUI behavior is not yet verified.',
                              'Other applications and AI tools require operator checks before each attempt.',
                              'The common source/documentation archive is pinned by the task bank; this helper does not audit task packets.']}
    _write(out / 'report.json', report)
    return report


def verify_runtime(directory):
    """Detect drift in the frozen editor, environment, locks, and template."""
    out = Path(directory).resolve()
    report = prepare.load(out / 'report.json')
    if report['kind'] != 'offline_editor_preparation_not_execution_readiness':
        raise ValueError('Unexpected runtime report')
    if report['locks'] != verify_locks():
        raise ValueError('Source or session-control binding changed')
    for record in report['editor']['files'].values():
        if prepare.sha(record['path']) != record['sha256']:
            raise ValueError('Editor installation changed')
    settings = out / 'user-data/User/settings.json'
    if prepare.sha(settings) != report['profile']['settings_sha256'] or prepare.load(settings) != SETTINGS:
        raise ValueError('Editor settings changed')
    if any((out / 'extensions').iterdir()):
        raise ValueError('Editor extension directory is no longer empty')
    environment = report['environment']
    if environment['platform'] != platform.platform() or environment['architecture'] != platform.machine():
        raise ValueError('Operating-system runtime changed')
    if environment['python'] != sys.version or environment['python_executable'] != str(Path(sys.executable).resolve()):
        raise ValueError('Python runtime changed')
    if any(importlib.metadata.version(name) != version for name, version in environment['dependencies'].items()):
        raise ValueError('Python dependency changed')
    if prepare.sha(environment['shell']['path']) != environment['shell']['sha256']:
        raise ValueError('Shell executable changed')
    return report


def prepare_task_editor(runtime_directory, packet_directory):
    """Create a new task profile and return its GUI command; do not execute it."""
    report = verify_runtime(runtime_directory)
    packet_path = Path(packet_directory).resolve(strict=True)
    packet = prepare.load(packet_path / 'packet.json')
    task_id = packet['task_id']
    if task_id not in {task['task_id'] for task in prepare.bank()['tasks']}:
        raise ValueError('Unknown task packet')
    if packet['bank_lock_sha256'] != report['locks']['task_definitions_lock_sha256']:
        raise ValueError('Task packet is bound to a different task bank')
    workspace = packet_path / 'workspace'
    if not workspace.is_dir():
        raise ValueError('Task workspace is missing')
    task_root = _new_private_directory(Path(runtime_directory) / 'task-editors' / task_id)
    user_data, extensions = _profile(task_root)
    command = [report['editor']['path'], '--new-window', '--disable-extensions', '--sync', 'off',
               '--user-data-dir', str(user_data), '--extensions-dir', str(extensions), str(workspace)]
    recipe = {'kind': 'unlaunched_editor_recipe_not_task_attempt', 'task_id': task_id,
              'condition': packet.get('condition'), 'command': command, 'gui_launched': False,
              'settings_sha256': prepare.sha(user_data / 'User/settings.json'),
              'operator_verification_pending': True}
    _write(task_root / 'launch.json', recipe)
    return recipe


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--editor', default=DEFAULT_EDITOR)
    args = parser.parse_args()
    report = prepare_runtime(args.directory, args.editor)
    print(json.dumps({'report': str(args.directory / 'report.json'), 'kind': report['kind'],
                      'execution_ready': False, 'gui_launched': False}))


if __name__ == '__main__':
    main()
