#!/usr/bin/env python3
"""Freeze a private conditional specification offline; never launch a study or model.

Readiness is evidence-based metadata, not authorization or operating-system isolation.
Promotion writes a new directory and preserves the original schedule exactly.
"""

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path

import availability
import prepare
import runtime
import schedule
import timer

ROOT = Path(__file__).resolve().parent
DEFAULT_CODEX_METADATA = ROOT / 'sessions/codex-binding-v1'
COMPONENTS = ('freeze.py', 'schedule.py', 'runtime.py', 'availability.py', 'prepare.py',
              'session.configured.json', 'bank-lock.json', 'session-controls.lock.json',
              'codex.study.json', 'NO-AI-INSTRUCTIONS.md', 'attempt-attestation.template.json',
              '../../coding-session-readiness.md')


def _context(runtime_directory, codex_metadata_directory):
    bank = prepare.verify()
    current = prepare.bank()['source']
    observed = runtime.verify_runtime(runtime_directory)
    controls = prepare.load(ROOT / 'session-controls.lock.json')
    configured = prepare.load(ROOT / 'session.configured.json')
    profile = prepare.load(ROOT / 'codex.study.json')
    metadata_directory = Path(codex_metadata_directory).resolve()
    metadata = prepare.load(metadata_directory / 'report.json')
    plan = prepare.load(metadata_directory / 'local-overrides.json')
    executable = Path(plan['command_prefix'][0]).resolve(strict=True)
    expected = {'task_pool_sha256': bank['bank_lock_sha256'],
                'session_controls_sha256': prepare.sha(ROOT / 'session-controls.lock.json'),
                'repository_commit': current['commit'], 'repository_archive_sha256': current['archive_sha256'],
                'timing_logger_sha256': prepare.sha(ROOT / 'timer.py'),
                'ai_instructions_sha256': prepare.sha(ROOT / 'AI-INSTRUCTIONS.md'),
                'offline_codex_metadata_report_sha256': prepare.sha(metadata_directory / 'report.json')}
    if any(configured.get(key) != value for key, value in expected.items()):
        raise ValueError('Configured session identity differs from current artifacts')
    if controls['task_definitions_lock_sha256'] != bank['bank_lock_sha256'] or any(
            configured.get(key) != value for key, value in controls['settings'].items()):
        raise ValueError('Configured session differs from bound timing controls')
    for name, digest in controls['sha256'].items():
        if prepare.sha(ROOT / name) != digest:
            raise ValueError('Bound session control changed')
    binding = configured['ai_tool_and_model_binding']
    keys = ('tool', 'tool_version', 'model', 'model_provider', 'reasoning_effort', 'executable_sha256')
    if any(binding.get(key) != profile.get(key) for key in (*keys, 'configuration_overrides', 'future_cli_options')):
        raise ValueError('Configured Codex binding differs from profile')
    if (metadata.get('kind') != 'offline_codex_metadata_check_not_provider_session'
            or metadata.get('profile_sha256') != prepare.sha(ROOT / 'codex.study.json')
            or metadata.get('local_invocation_plan_sha256') != prepare.sha(metadata_directory / 'local-overrides.json')
            or metadata.get('all_mcp_servers_disabled_observed') is not True
            or metadata.get('provider_prompt_calls') != 0
            or any(metadata.get(key) != profile[key] for key in keys if key != 'model_provider')
            or prepare.sha(executable) != profile['executable_sha256']):
        raise ValueError('Codex metadata/profile/executable binding changed')
    required = sorted(key.removeprefix('features.') for key, value in profile['configuration_overrides'].items()
                      if key.startswith('features.') and value is False)
    if metadata.get('disabled_features_observed') != required:
        raise ValueError('Required disabled feature metadata is missing')
    archive = ROOT / 'sessions/quantsmith-2601cab/source.tar'
    if prepare.sha(archive) != current['archive_sha256']:
        raise ValueError('Prepared SDK archive differs from the task bank')
    paths = [ROOT / name for name in COMPONENTS] + [archive, executable,
             Path(runtime_directory).resolve() / 'report.json', metadata_directory / 'report.json',
             metadata_directory / 'local-overrides.json']
    return {'configured': configured, 'profile': profile, 'runtime': observed,
            'runtime_directory': str(Path(runtime_directory).resolve()),
            'codex_metadata_directory': str(metadata_directory), 'executable': str(executable),
            'component_sha256': {str(path.resolve()): prepare.sha(path) for path in paths}}


def _familiarity(value):
    value = deepcopy(value) if value is not None else {'status': 'unknown', 'implemented_task_ids': None}
    status, tasks = value.get('status'), value.get('implemented_task_ids')
    if status == 'unknown' and tasks is None:
        return value
    if status == 'no_prior_implementation_reported' and tasks == []:
        return value
    if (status == 'prior_implementation_tasks_reported' and isinstance(tasks, list) and tasks
            and len(tasks) == len(set(tasks)) and all(task in schedule.TASK_IDS for task in tasks)):
        return value
    raise ValueError('Familiarity must preserve unknowns or explicitly identify prior implementations')


def _availability(directory, context):
    if directory is None:
        return None
    out = Path(directory).resolve()
    receipt, plan = prepare.load(out / 'receipt.json'), prepare.load(out / 'plan.json')
    profile = context['profile']
    expected_command = [context['executable'], 'exec', '--ignore-user-config', '--ephemeral',
                        '--skip-git-repo-check', '--sandbox', 'read-only', '--json',
                        '--output-last-message', str(out / 'last-message.txt'), '-C', str(out / 'empty-workspace')]
    for key, value in profile['configuration_overrides'].items():
        expected_command.extend(['-c', key + '=' + json.dumps(value)])
    expected_command.append(availability.PROMPT)
    if plan.get('command') != expected_command or plan.get('profile_path') != str(ROOT / 'codex.study.json'):
        raise ValueError('Availability plan is not the pinned generic tool-free probe')
    for record in (receipt, plan):
        if (record.get('requested_model') != profile['model'] or record.get('requested_provider') != profile['model_provider']
                or record.get('profile_sha256') != prepare.sha(ROOT / 'codex.study.json')
                or record.get('executable_sha256') != profile['executable_sha256']
                or record.get('outer_retries') != 0 or record.get('model_or_provider_fallback') is not False):
            raise ValueError('Availability identity, retry, or fallback binding differs')
    raw = {name: prepare.sha(out / name) for name in ('stdout.jsonl', 'stderr.txt', 'last-message.txt')}
    if (receipt.get('kind') != 'availability_not_experiment_result'
            or receipt.get('plan_sha256') != prepare.sha(out / 'plan.json') or receipt.get('raw_artifact_sha256') != raw):
        raise ValueError('Availability receipt or raw artifacts changed')
    parsed = availability.parse_events((out / 'stdout.jsonl').read_text(), (out / 'last-message.txt').read_bytes(),
                                      receipt.get('exit_code'), receipt.get('timed_out'), requested_model=profile['model'])
    if not parsed['available'] or any(receipt.get(key) != value for key, value in parsed.items()):
        raise ValueError('Availability receipt does not match a successful tool-free raw transcript')
    return {'directory': str(out), 'receipt_sha256': prepare.sha(out / 'receipt.json'),
            'available': True, 'returned_model_ids': parsed['returned_model_ids'],
            'usage': parsed['usage'], 'cost_usd': parsed['cost_usd']}


def _save(out, context, schedule_bytes, familiarity, online, *, previous=None):
    familiarity = _familiarity(familiarity)
    data = json.loads(schedule_bytes)
    schedule.validate_schedule(data)
    configured = context['configured']
    if any(data[key] != configured[key] for key in ('task_pool_sha256', 'session_controls_sha256')):
        raise ValueError('Schedule refers to different locked artifacts')
    blockers = ([] if familiarity['status'] == 'no_prior_implementation_reported' else ['prior_implementation_familiarity_unresolved'])
    if online is None:
        blockers.append('later_authorized_online_availability_unverified')
    directory = runtime._new_private_directory(out)
    schedule.write_schedule(directory / 'schedule.json', data)
    if (directory / 'schedule.json').read_bytes() != schedule_bytes:
        raise ValueError('Schedule serialization must preserve frozen bytes')
    session = deepcopy(configured)
    now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    session.update({'kind': 'frozen_execution_specification_not_results', 'execution_ready': not blockers,
                    'offline_only': online is None, 'frozen_at_utc': now, 'execution_environment_frozen': True,
                    'session_id': previous['session_id'] if previous else configured['session_id'] + '-' + directory.name,
                    'initial_specification_frozen_at_utc': previous['initial_specification_frozen_at_utc'] if previous else now,
                    'participant_session_slots': 'participant_initiated; record actual start before each attempt',
                    'familiarity': familiarity, 'readiness_blockers': blockers,
                    'environment_and_tools': context['runtime'], 'runtime_directory': context['runtime_directory'],
                    'codex_metadata_directory': context['codex_metadata_directory'],
                    'component_sha256': context['component_sha256'], 'availability_evidence': online,
                    'randomization_seed': data['seed'], 'randomization_algorithm': data['algorithm'],
                    'schedule_sha256': prepare.sha(directory / 'schedule.json'), 'condition_assignments': data['condition_assignments'],
                    'documentation_snapshot': {'archive_sha256': configured['repository_archive_sha256'], 'same_for_both_conditions': True},
                    'permitted_assistance': 'Common isolated editor, terminal, source/docs/tests; bound Codex only in AI condition',
                    'artifact_and_privacy_rules': 'Retain raw private artifacts in ignored sessions/runs; redact before publication',
                    'attempt_operator_checks_required': ['verify packet/source integrity and schedule position',
                        'fresh editor profile with AI features/extensions disabled; other AI apps closed',
                        'stop external work at timer cap; retain deviations'],
                    'sequence_amendment': 'Draw before the live availability gate; conceal assignments until prior familiarity is captured. All eight tasks fixed before outcomes.',
                    'remaining_execution_inputs': blockers})
    session['ai_tool_and_model_binding']['live_availability_verified'] = online is not None
    if previous:
        session['promotion_of_session_sha256'] = previous['_saved_sha256']
    availability.write_private(directory / 'session.frozen.json', session)
    report = {'kind': 'conditional_freeze_not_study_result', 'execution_ready': session['execution_ready'],
              'readiness_blockers': blockers, 'schedule_sha256': session['schedule_sha256'],
              'session_sha256': prepare.sha(directory / 'session.frozen.json'), 'empirical_observations': 0,
              'assignments_disclosure_permitted': familiarity['status'] == 'no_prior_implementation_reported',
              'limitations': ['No task/model launched by freeze; GUI checks remain per attempt.',
                             'Availability is not runtime isolation, model snapshot verification, or coding reliability.']}
    availability.write_private(directory / 'freeze-report.json', report)
    return report


def freeze_session(out, runtime_directory, familiarity=None, availability_directory=None,
                   codex_metadata_directory=DEFAULT_CODEX_METADATA):
    if Path(out).exists():
        raise FileExistsError('Freeze output already exists; use promotion into a new directory')
    familiarity = _familiarity(familiarity)
    context = _context(runtime_directory, codex_metadata_directory)
    online = _availability(availability_directory, context)
    data = schedule.generate(task_pool_sha256=context['configured']['task_pool_sha256'],
                             session_controls_sha256=context['configured']['session_controls_sha256'])
    # Use the canonical serializer without exposing assignments to stdout.
    payload = (json.dumps(data, indent=2, sort_keys=True) + '\n').encode()
    return _save(out, context, payload, familiarity, online)


def verify_frozen(directory):
    directory = Path(directory).resolve()
    session, report = prepare.load(directory / 'session.frozen.json'), prepare.load(directory / 'freeze-report.json')
    if report.get('session_sha256') != prepare.sha(directory / 'session.frozen.json'):
        raise ValueError('Frozen session changed')
    context = _context(session['runtime_directory'], session['codex_metadata_directory'])
    if (session.get('kind') != 'frozen_execution_specification_not_results'
            or session.get('execution_environment_frozen') is not True or not timer.valid_utc(session.get('frozen_at_utc'))):
        raise ValueError('Session freeze markers are invalid')
    if session['component_sha256'] != context['component_sha256'] or session['environment_and_tools'] != context['runtime']:
        raise ValueError('Frozen component or runtime binding changed')
    fixed = ('repository_commit', 'repository_archive_sha256', 'acceptance_checks_sha256',
             'timing_logger_sha256', 'ai_instructions_sha256', 'offline_codex_metadata_report_sha256',
             'participant_id', 'selected_stages', 'active_author_cap_seconds_per_task', 'wall_cap_seconds_per_task',
             'timing_method', 'warmup_rule', 'correction_and_followup_rule')
    if any(session.get(key) != context['configured'].get(key) for key in fixed):
        raise ValueError('Frozen source, timing, participant, or stage settings changed')
    original_binding = context['configured']['ai_tool_and_model_binding']
    if any(session['ai_tool_and_model_binding'].get(key) != value for key, value in original_binding.items()
           if key != 'live_availability_verified'):
        raise ValueError('Frozen Codex configuration changed')
    data = prepare.load(directory / 'schedule.json')
    schedule.validate_schedule(data)
    if any(data[key] != context['configured'][key] for key in ('task_pool_sha256', 'session_controls_sha256')):
        raise ValueError('Schedule refers to different current locked artifacts')
    for key, value in (('schedule_sha256', prepare.sha(directory / 'schedule.json')),
                       ('condition_assignments', data['condition_assignments']), ('randomization_seed', data['seed']),
                       ('randomization_algorithm', data['algorithm']), ('task_pool_sha256', data['task_pool_sha256']),
                       ('session_controls_sha256', data['session_controls_sha256'])):
        if session.get(key) != value:
            raise ValueError('Frozen schedule or assignment binding changed')
    if report.get('schedule_sha256') != session['schedule_sha256']:
        raise ValueError('Freeze report refers to a different schedule')
    _familiarity(session['familiarity'])
    evidence = session['availability_evidence']
    if evidence is not None and evidence != _availability(evidence['directory'], context):
        raise ValueError('Frozen availability evidence changed')
    expected_ready = session['familiarity']['status'] == 'no_prior_implementation_reported' and evidence is not None
    expected_blockers = ([] if session['familiarity']['status'] == 'no_prior_implementation_reported'
                         else ['prior_implementation_familiarity_unresolved'])
    if evidence is None:
        expected_blockers.append('later_authorized_online_availability_unverified')
    if (session.get('execution_ready') != expected_ready or report.get('execution_ready') != expected_ready
            or session.get('readiness_blockers') != expected_blockers
            or report.get('readiness_blockers') != expected_blockers
            or session.get('remaining_execution_inputs') != expected_blockers
            or report.get('assignments_disclosure_permitted') != (session['familiarity']['status'] == 'no_prior_implementation_reported')
            or session.get('offline_only') != (evidence is None)
            or session['ai_tool_and_model_binding'].get('live_availability_verified') != (evidence is not None)):
        raise ValueError('Readiness differs from frozen evidence')
    if expected_ready:
        first = data['slots'][0]
        timer.validate_manifest(session, first['task_id'], first['condition'])
    return session


def finalize_session(frozen_directory, new_out, familiarity=None, availability_directory=None):
    previous = verify_frozen(frozen_directory)
    context = _context(previous['runtime_directory'], previous['codex_metadata_directory'])
    online_directory = availability_directory or (previous['availability_evidence'] or {}).get('directory')
    online = _availability(online_directory, context)
    previous['_saved_sha256'] = prepare.sha(Path(frozen_directory) / 'session.frozen.json')
    return _save(new_out, context, (Path(frozen_directory) / 'schedule.json').read_bytes(),
                 familiarity if familiarity is not None else previous['familiarity'], online, previous=previous)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True)
    parser.add_argument('--runtime-directory', required=True)
    parser.add_argument('--codex-metadata-directory', default=DEFAULT_CODEX_METADATA)
    args = parser.parse_args()
    print(json.dumps(freeze_session(args.out, args.runtime_directory,
                                   codex_metadata_directory=args.codex_metadata_directory), indent=2))


if __name__ == '__main__':
    main()
