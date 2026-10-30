#!/usr/bin/env python3
"""Inspect local Codex metadata/controls only. Never launches a coding/model session."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def file_hash(path):
    hasher = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            hasher.update(block)
    return hasher.hexdigest()


def metadata(executable, args):
    result = subprocess.run([str(executable), *args], capture_output=True, text=True, timeout=30)
    if result.returncode:
        # Do not copy raw configuration, headers, or environment values into logs.
        raise ValueError(f'Codex metadata command failed (exit {result.returncode})')
    return result.stdout


def servers(text):
    rows = json.loads(text)
    if not isinstance(rows, list):
        raise ValueError('Unexpected MCP metadata format')
    names = []
    for row in rows:
        name = row.get('name') if isinstance(row, dict) else None
        if not isinstance(name, str) or not re.fullmatch(r'[A-Za-z0-9_-]+', name) or name in names:
            raise ValueError('Server key needs explicit binding review; refusing ambiguous overrides')
        names.append(name)
    return rows, sorted(names)


def check(directory, executable=None):
    profile_path = ROOT / 'codex.study.json'
    profile = json.loads(profile_path.read_text())
    found = executable or shutil.which('codex')
    if not found:
        raise ValueError('Codex is not installed locally')
    executable = Path(found).resolve()
    if file_hash(executable) != profile['executable_sha256']:
        raise ValueError('Codex executable changed; rebind before collecting observations')
    observed_version = metadata(executable, ['--version']).strip()
    if observed_version != f"codex-cli {profile['tool_version']}":
        raise ValueError('Codex version differs from the study binding')
    overrides = []
    for key, value in profile['configuration_overrides'].items():
        overrides.extend(['-c', key + '=' + json.dumps(value)])
    # Disable plugins before discovery: plugin-provided servers are not user
    # configuration entries and cannot safely receive partial table overrides.
    _, names = servers(metadata(executable, [*overrides, 'mcp', 'list', '--json']))
    for name in names:
        overrides.extend(['-c', f'mcp_servers.{name}.enabled=false'])
    effective = metadata(executable, [*overrides, 'features', 'list'])
    required = {key.removeprefix('features.') for key, value in profile['configuration_overrides'].items()
                if key.startswith('features.') and value is False}
    flags = {parts[0]: parts[-1] for line in effective.splitlines() if len(parts := line.split()) >= 3}
    if any(flags.get(name) != 'false' for name in required):
        raise ValueError('Required feature controls are not disabled')
    effective_rows, effective_names = servers(metadata(executable, [*overrides, 'mcp', 'list', '--json']))
    if names != effective_names or any(row.get('enabled') is not False for row in effective_rows):
        raise ValueError('MCP configuration changed or a server is still enabled')
    out = Path(directory)
    out.mkdir(parents=True, exist_ok=False)
    local_plan = {'kind': 'future_invocation_prefix_not_launched',
                  'command_prefix': [str(executable), *profile['future_cli_options'], *overrides],
                  'instruction': 'Only use after the actual execution session is frozen; set current packet root and pass the frozen AI instructions. Do not launch during offline preparation.'}
    with (out / 'local-overrides.json').open('x') as handle:
        json.dump(local_plan, handle, indent=2)
        handle.write('\n')
    report = {'kind': 'offline_codex_metadata_check_not_provider_session', 'tool': profile['tool'],
              'tool_version': profile['tool_version'], 'executable_sha256': file_hash(executable),
              'model': profile['model'], 'reasoning_effort': profile['reasoning_effort'],
              'profile_sha256': file_hash(profile_path), 'disabled_features_observed': sorted(required),
              'configured_mcp_servers': len(names), 'all_mcp_servers_disabled_observed': True,
              'local_invocation_plan_sha256': file_hash(out / 'local-overrides.json'),
              'provider_prompt_calls': 0, 'live_model_available': None,
              'limitations': ['Metadata checks do not prove runtime isolation or hook/search/network enforcement.',
                              'Configured model name is not verified immutable or currently available.',
                              'Only local metadata subcommands were invoked; no coding/model session was launched.']}
    with (out / 'report.json').open('x') as handle:
        json.dump(report, handle, indent=2)
        handle.write('\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True)
    parser.add_argument('--codex', help='Explicit installed executable; version and hash must match')
    args = parser.parse_args()
    print(json.dumps(check(args.out, args.codex), indent=2))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError, TypeError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({'error': str(exc)}), file=sys.stderr)
        sys.exit(2)
