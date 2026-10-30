#!/usr/bin/env python3
"""Prepare a short native-editor launch recipe; never launch or change a freeze."""

import argparse
import json
import os
from pathlib import Path
import tempfile

import runtime


def launch_environment(environment=None):
    """Copy the child environment, removing only inherited VS Code/node mode."""
    source = os.environ if environment is None else environment
    return {key: value for key, value in source.items()
            if not key.startswith('VSCODE_') and key != 'ELECTRON_RUN_AS_NODE'}


def _socket_length(user_data, version):
    # The full version is at least as long as the major/minor socket prefix.
    socket_path = user_data / f'{version}-main.sock'
    length = len(os.fsencode(socket_path))
    if length > 90:
        raise ValueError('Short editor IPC socket path exceeds the conservative 90-byte limit')
    return length


def prepare_delivery(runtime_directory, workspace, directory):
    """Copy frozen settings to a new short cache and return an unlaunched recipe."""
    source = Path(runtime_directory).resolve(strict=True)
    frozen = runtime.verify_runtime(source)
    workspace = Path(workspace).resolve(strict=True)
    if not workspace.is_dir():
        raise ValueError('Editor workspace must be an existing directory')
    settings = source / 'user-data/User/settings.json'
    settings_bytes = settings.read_bytes()
    settings_hash = runtime.prepare.sha(settings)
    if settings_hash != frozen['profile']['settings_sha256']:
        raise ValueError('Frozen editor settings hash changed')
    out = runtime._new_private_directory(directory)
    cache = Path(tempfile.mkdtemp(prefix='aih-', dir='/private/tmp')).resolve()
    user_data, extensions = cache / 'user-data', cache / 'extensions'
    length = _socket_length(user_data, frozen['editor']['version'])
    (user_data / 'User').mkdir(mode=0o700, parents=True)
    user_data.chmod(0o700)
    extensions.mkdir(mode=0o700)
    copied = user_data / 'User/settings.json'
    descriptor = os.open(copied, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'wb') as handle:
        handle.write(settings_bytes)
    if runtime.prepare.sha(copied) != settings_hash or any(extensions.iterdir()):
        raise ValueError('Short editor profile does not match the frozen settings')
    native = frozen['editor']['files']['executable']
    command = [native['path'], '--new-window', '--disable-extensions', '--sync', 'off',
               '--user-data-dir', str(user_data), '--extensions-dir', str(extensions), str(workspace)]
    report = {'kind': 'unlaunched_short_editor_delivery_not_task_attempt',
              'runtime_directory': str(source), 'runtime_report_sha256': runtime.prepare.sha(source / 'report.json'),
              'runtime_helper_sha256': runtime.prepare.sha(Path(runtime.__file__)),
              'delivery_helper_sha256': runtime.prepare.sha(Path(__file__)),
              'source_session_runtime_bindings': frozen['locks'],
              'settings_sha256': settings_hash, 'native_executable': native,
              'short_cache': str(cache), 'user_data': str(user_data), 'extensions': str(extensions),
              'conservative_main_socket_path_bytes': length, 'main_socket_path_limit_bytes': 90,
              'workspace': str(workspace), 'command': command,
              'environment_rule': 'Remove VSCODE_* and ELECTRON_RUN_AS_NODE from a copied child environment only.',
              'extensions_directory_empty_at_preparation': True, 'gui_launched': False,
              'provider_calls': 0, 'execution_ready': False, 'operator_verification_pending': True,
              'limitations': ['No GUI behavior, operating-system isolation, or network isolation is verified.',
                              'The short cache is ephemeral; reprepare a new delivery if it disappears.',
                              'This helper retains the cache and does not delete user files.']}
    runtime._write(out / 'report.json', report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('runtime_directory', type=Path)
    parser.add_argument('workspace', type=Path)
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    result = prepare_delivery(args.runtime_directory, args.workspace, args.directory)
    print(json.dumps({'report': str(args.directory / 'report.json'), 'gui_launched': result['gui_launched']}))


if __name__ == '__main__':
    main()
