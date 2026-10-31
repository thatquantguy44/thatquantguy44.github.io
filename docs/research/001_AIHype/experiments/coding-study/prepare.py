#!/usr/bin/env python3
"""Offline source copying, task-packet export, and preflight. Never runs a study."""

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent


def load(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(Path(path).read_text(), object_pairs_hook=unique,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError(f"Invalid JSON: {x}")))


def write(path, data):
    with Path(path).open('x') as handle:
        json.dump(data, handle, indent=2, allow_nan=False)
        handle.write('\n')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def bank():
    return load(ROOT / 'task-bank.json')


def core_files():
    return [ROOT / 'task-bank.json', ROOT / 'prepare.py', ROOT.parents[1] / 'coding-experiment-protocol.md'] + \
           sorted((ROOT / 'tasks').glob('*.md')) + sorted((ROOT / 'acceptance').glob('test_*.py'))


def current_hashes():
    return {os.path.relpath(p, ROOT): sha(p) for p in core_files()}


def verify():
    data = bank()
    lock = load(ROOT / 'bank-lock.json')
    if current_hashes() != lock['sha256']:
        raise ValueError('Task-bank content changed; archive/version and relock before use')
    ids = [t['task_id'] for t in data['tasks']]
    expected = [f'P{i}{letter}' for i in range(1, 5) for letter in 'AB']
    if ids != expected or len(ids) != len(set(ids)):
        raise ValueError('Expected eight unique tasks in agreed stage/pair order')
    for task in data['tasks']:
        for field in ('brief', 'acceptance'):
            path = (ROOT / task[field]).resolve()
            if not path.is_relative_to(ROOT) or not path.is_file():
                raise ValueError('Invalid task artifact path')
    return {'kind': 'verified_prepared_task_definitions_not_execution_ready', 'tasks': len(ids),
            'bank_lock_sha256': sha(ROOT / 'bank-lock.json'), 'condition_assignments': None}


def extract(archive, destination):
    """Reject links, device files, and path escapes before writing archive content."""
    destination = Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    with tarfile.open(archive) as handle:
        for member in handle.getmembers():
            if not (member.isfile() or member.isdir()) or member.issym() or member.islnk():
                raise ValueError(f'Unsupported source member: {member.name}')
            if not (destination / member.name).resolve().is_relative_to(destination):
                raise ValueError(f'Unsafe source member: {member.name}')
        # Prechecked members contain only regular files/directories; Python 3.10+.
        options = {'filter': 'data'} if hasattr(tarfile, 'data_filter') else {}
        handle.extractall(destination, **options)


def check_snapshot(directory):
    data = bank()
    archive = Path(directory) / 'source.tar'
    if sha(archive) != data['source']['archive_sha256']:
        raise ValueError('Source archive hash does not match the pinned bank')
    return archive


def snapshot(repository, directory):
    verify()
    data = bank()
    out = Path(directory).resolve()
    out.mkdir(parents=True, exist_ok=False)
    archive = out / 'source.tar'
    subprocess.run(['git', '-C', str(Path(repository).resolve()), 'archive', '--format=tar',
                    '--output', str(archive), data['source']['commit']], check=True)
    check_snapshot(out)
    extract(archive, out / 'base')
    write(out / 'snapshot.json', {'kind': 'isolated_source_snapshot_not_study_run',
                                 'repository_commit': data['source']['commit'],
                                 'source_archive_sha256': sha(archive),
                                 'source_working_changes_included': False})
    return {'snapshot': str(out), 'repository_commit': data['source']['commit']}


def source_hashes(workspace):
    ignored = {'__pycache__', '.pytest_cache'}
    return {str(p.relative_to(workspace)): sha(p) for p in sorted(workspace.rglob('*'))
            if p.is_file() and not ignored.intersection(p.relative_to(workspace).parts)}


def export(snapshot_directory, task_id, directory):
    verified = verify()
    task = next((t for t in bank()['tasks'] if t['task_id'] == task_id), None)
    if task is None:
        raise ValueError(f'Unknown task: {task_id}')
    archive = check_snapshot(snapshot_directory)
    out = Path(directory).resolve()
    out.mkdir(parents=True, exist_ok=False)
    extract(archive, out / 'workspace')
    (out / 'acceptance').mkdir()
    shutil.copyfile(ROOT / task['acceptance'], out / 'acceptance' / 'test_acceptance.py')
    protocol = ROOT.parents[1] / 'coding-experiment-protocol.md'
    # Source-repository links are context references, not permission to read
    # outside this packet. Keep the exported protocol self-contained prose.
    protocol_text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', protocol.read_text())
    (out / 'PROTOCOL.md').write_text(protocol_text)
    brief = (ROOT / task['brief']).read_text().replace('../../../coding-experiment-protocol.md', 'PROTOCOL.md')
    (out / 'TASK.md').write_text(brief)
    packet = {'kind': 'unassigned_preparation_copy_not_observation', 'task_id': task_id,
              'condition': None, 'repository_commit': bank()['source']['commit'],
              'bank_lock_sha256': verified['bank_lock_sha256'], 'source_archive_sha256': sha(archive),
              'allowed_changed_paths': [task['target'], f"tests/test_case_study_{task_id.lower()}.py"],
              'workspace_sha256': source_hashes(out / 'workspace'),
              'packet_sha256': {name: sha(out / name) for name in ('TASK.md', 'PROTOCOL.md', 'acceptance/test_acceptance.py')}}
    write(out / 'packet.json', packet)
    return {'exported': str(out), 'task_id': task_id, 'condition': None,
            'warning': 'Clean source copying is not an operating-system sandbox or a timed study attempt'}


def audit(directory):
    out = Path(directory).resolve()
    packet = load(out / 'packet.json')
    actual = source_hashes(out / 'workspace')
    original = packet['workspace_sha256']
    changed = sorted(name for name in set(actual) | set(original) if actual.get(name) != original.get(name))
    altered_packet = [name for name, digest in packet['packet_sha256'].items() if not (out / name).is_file() or sha(out / name) != digest]
    unexpected = [name for name in changed if name not in packet['allowed_changed_paths']]
    return {'task_id': packet['task_id'], 'changed_paths': changed, 'unexpected_changed_paths': unexpected,
            'altered_packet_artifacts': altered_packet, 'local_integrity_pass': not unexpected and not altered_packet,
            'note': 'Local comparison only; does not authenticate identity, time, or the operator-supplied metadata'}


GUARDED_PYTEST = r'''
import importlib, json, pathlib, socket, sys
attempts = []
def blocked(*args, **kwargs):
    attempts.append('network')
    raise RuntimeError('Network prohibited during offline preflight')
class BlockedSocket(socket.socket):
    def __new__(cls, *args, **kwargs):
        return blocked(*args, **kwargs)
socket.socket = BlockedSocket
socket.create_connection = blocked
socket.getaddrinfo = blocked
module = importlib.import_module('quantsmith')
expected = pathlib.Path(sys.argv[1]).resolve()
observed = pathlib.Path(module.__file__).resolve()
if not observed.is_relative_to(expected):
    raise RuntimeError('SDK imported outside the isolated snapshot: ' + str(observed))
print(json.dumps({'sdk_import': str(observed), 'offline_socket_guard': True}))
import pytest
result = pytest.main(sys.argv[2:])
for name, loaded in list(sys.modules.items()):
    if name.startswith('quantsmith.') and getattr(loaded, '__file__', None):
        if not pathlib.Path(loaded.__file__).resolve().is_relative_to(expected):
            raise RuntimeError('SDK submodule imported outside snapshot: ' + name)
if attempts:
    raise RuntimeError('Preflight attempted network access')
sys.exit(result)
'''


def test_counts(path):
    root = ET.parse(path).getroot()
    suites = [root] if root.tag == 'testsuite' else list(root.iter('testsuite'))
    return {key: sum(int(s.get(key, '0')) for s in suites) for key in ('tests', 'failures', 'errors', 'skipped')}


def pytest_run(workspace, selectors, out, name):
    xml = out / f'{name}.xml'
    env = dict(os.environ)
    env.update(PYTHONPATH=str(workspace / 'src'), PYTHONDONTWRITEBYTECODE='1', PYTEST_DISABLE_PLUGIN_AUTOLOAD='1')
    args = [sys.executable, '-B', '-c', GUARDED_PYTEST, str(workspace / 'src'), '-q', '--noconftest',
            '--import-mode=importlib', '-p', 'no:cacheprovider', '--rootdir', str(workspace),
            '--junitxml', str(xml), *selectors]
    try:
        completed = subprocess.run(args, cwd=workspace, env=env, capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired as exc:
        (out / f'{name}.log').write_text(str(exc))
        return {'exit_code': None, 'setup_error': 'preflight command exceeded 60 seconds'}
    (out / f'{name}.log').write_text(completed.stdout + completed.stderr)
    result = {'exit_code': completed.returncode, 'log': f'{name}.log', 'junit': f'{name}.xml'}
    if xml.exists():
        result.update(test_counts(xml))
    else:
        result['setup_error'] = 'No JUnit result; inspect command log'
    return result


def preflight(snapshot_directory, directory):
    verified = verify()
    archive = check_snapshot(snapshot_directory)
    out = Path(directory).resolve()
    out.mkdir(parents=True, exist_ok=False)
    extract(archive, out / 'workspace')
    workspace = out / 'workspace'
    before = source_hashes(workspace)
    baseline = pytest_run(workspace, bank()['baseline_selectors'], out, 'baseline')
    baseline_ok = baseline.get('exit_code') == 0 and baseline.get('tests', 0) > 0 and not baseline.get('errors') and not baseline.get('skipped')
    requirements = []
    if baseline_ok:
        # Deliberately run P1/P2 first, then P3/P4; these are preparation checks only.
        for task in bank()['tasks']:
            result = pytest_run(workspace, [str(ROOT / task['acceptance'])], out, task['task_id'])
            result['task_id'] = task['task_id']
            result['expected_new_requirement_failure'] = result.get('exit_code') == 1 and result.get('failures', 0) > 0 and result.get('errors') == 0 and result.get('skipped') == 0
            requirements.append(result)
    pristine = before == source_hashes(workspace)
    result = {'kind': 'setup_checks_not_coding_productivity_results', **verified,
              'baseline': baseline, 'requirements': requirements, 'source_unchanged': pristine,
              'prepared_bank_preflight_pass': baseline_ok and pristine and len(requirements) == 8 and all(r['expected_new_requirement_failure'] for r in requirements),
              'python': sys.version, 'dependencies': {p: importlib.metadata.version(p) for p in ('pytest', 'numpy')},
              'limitations': ['No solution/reference implementation was generated or validated.',
                              'Expected baseline failures establish gaps, not sufficiency or satisfiability of all checks.',
                              'Python socket guard and copying are not OS-level isolation.',
                              'No participant timing, AI/no-AI assignment, or live AI call.']}
    # Do not let verification metadata relabel a setup record as study results.
    result['kind'] = 'setup_checks_not_coding_productivity_results'
    write(out / 'preflight.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('verify')
    snap = sub.add_parser('snapshot')
    snap.add_argument('--repo', required=True)
    snap.add_argument('--out', required=True)
    for command in ('export', 'preflight'):
        child = sub.add_parser(command)
        child.add_argument('--snapshot', required=True)
        child.add_argument('--out', required=True)
        if command == 'export':
            child.add_argument('--task', required=True)
    check = sub.add_parser('audit')
    check.add_argument('--packet', required=True)
    args = parser.parse_args()
    if args.command == 'verify':
        result = verify()
    elif args.command == 'snapshot':
        result = snapshot(args.repo, args.out)
    elif args.command == 'export':
        result = export(args.snapshot, args.task, args.out)
    elif args.command == 'audit':
        result = audit(args.packet)
    else:
        result = preflight(args.snapshot, args.out)
    print(json.dumps(result, indent=2, allow_nan=False))
    return 1 if result.get('prepared_bank_preflight_pass') is False or result.get('local_integrity_pass') is False else 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
        print(json.dumps({'error': str(exc)}), file=sys.stderr)
        sys.exit(2)
