"""Offline restricted randomization; a saved schedule contains no study results.

Keep the generated file private until the participant's prior task familiarity
has been recorded. This module never starts a task or contacts an AI provider.
"""

import argparse
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import re
import secrets


ALGORITHM = 'restricted_staged_pairs_v1'
TASK_POOL_SHA256 = '6843e3030176373005a8fc6cfc26ff44c8b84b2f5cdeda230afceb25e42fee3f'
SESSION_CONTROLS_SHA256 = '81426e51c112d3103067b1d8fa2697d16c279799f1831544905c68dfe9444c62'
STAGES = {1: ('P1', 'P2'), 2: ('P3', 'P4')}
CONDITIONS = ('ai_enabled', 'no_ai')
TASK_IDS = frozenset(f'P{pair}{letter}' for pair in range(1, 5) for letter in 'AB')
CONSTRAINTS = {
    'all_eight_tasks_exactly_once': True,
    'stages': [{'stage': 1, 'pairs': ['P1', 'P2']},
               {'stage': 2, 'pairs': ['P3', 'P4']}],
    'stage_1_before_stage_2': True,
    'pair_order_randomized_within_stage': True,
    'pair_tasks_contiguous': True,
    'one_ai_and_one_no_ai_task_per_pair': True,
    'task_identity_randomized_within_pair': True,
    'one_ai_first_and_one_no_ai_first_pair_per_stage': True,
    'all_tasks_selected_before_outcomes': True,
    'stage_2_not_conditional_on_stage_1_results': True,
}
ALGORITHM_DESCRIPTION = (
    'Use an isolated random.Random(integer_seed). For each stage in ascending '
    'order, shuffle its two pair IDs, shuffle [ai_enabled, no_ai] to assign '
    'the first condition to each pair, then shuffle each pair\'s [A, B] task '
    'IDs. Emit the first task under the assigned first condition and the '
    'second task under the other condition. Pairs remain contiguous.'
)


def _hash(value, name):
    if not isinstance(value, str) or re.fullmatch(r'[0-9a-f]{64}', value) is None:
        raise ValueError(f'{name} must be a lowercase SHA-256 hex digest')


def _seed(value):
    if type(value) is not int or value < 0:
        raise ValueError('seed must be a nonnegative integer')


def _slots_for_seed(seed):
    rng = random.Random(seed)
    slots = []
    for stage, stage_pairs in STAGES.items():
        pairs = list(stage_pairs)
        rng.shuffle(pairs)
        first_conditions = list(CONDITIONS)
        rng.shuffle(first_conditions)
        for pair, first_condition in zip(pairs, first_conditions):
            tasks = [pair + 'A', pair + 'B']
            rng.shuffle(tasks)
            other_condition = 'no_ai' if first_condition == 'ai_enabled' else 'ai_enabled'
            for task_id, condition in zip(tasks, (first_condition, other_condition)):
                slots.append({'position': len(slots) + 1, 'stage': stage,
                              'pair_id': pair, 'task_id': task_id,
                              'condition': condition})
    return slots


def generate(seed=None, *, task_pool_sha256=TASK_POOL_SHA256,
             session_controls_sha256=SESSION_CONTROLS_SHA256):
    """Return a deterministic schedule, or draw and retain a fresh 128-bit seed.

    Callers must verify the supplied digests against their frozen lock files;
    digest syntax validation cannot establish the contents of those files.
    """
    _hash(task_pool_sha256, 'task_pool_sha256')
    _hash(session_controls_sha256, 'session_controls_sha256')
    source = 'caller_supplied' if seed is not None else 'secrets.randbits(128)'
    if seed is None:
        seed = secrets.randbits(128)
    _seed(seed)
    slots = _slots_for_seed(seed)
    data = {
        'kind': 'schedule_not_results',
        'schema_version': '1.0.0',
        'algorithm': ALGORITHM,
        'algorithm_description': ALGORITHM_DESCRIPTION,
        'rng': 'python.random.Random',
        'python_implementation': platform.python_implementation(),
        'python_version': platform.python_version(),
        'seed': seed,
        'seed_source': source,
        'task_pool_sha256': task_pool_sha256,
        'session_controls_sha256': session_controls_sha256,
        'constraints': deepcopy(CONSTRAINTS),
        'planned_task_count': 8,
        'empirical_observations': 0,
        'interpretation': 'Assignments are plans. No task counts as an observation until performed and logged.',
        'disclosure_gate': 'Record editor choice and prior task implementation familiarity before revealing assignments.',
        'slots': slots,
        'condition_assignments': {slot['task_id']: slot['condition'] for slot in slots},
    }
    validate_schedule(data)
    return data


def validate_schedule(data):
    """Raise ValueError for an invalid or seed-inconsistent schedule; else True."""
    if not isinstance(data, dict):
        raise ValueError('schedule must be an object')
    for key, expected in (('kind', 'schedule_not_results'), ('schema_version', '1.0.0'),
                          ('algorithm', ALGORITHM),
                          ('algorithm_description', ALGORITHM_DESCRIPTION),
                          ('rng', 'python.random.Random'), ('constraints', CONSTRAINTS)):
        if data.get(key) != expected:
            raise ValueError(f'unsupported or missing {key}')
    for key in ('task_pool_sha256', 'session_controls_sha256'):
        _hash(data.get(key), key)
    _seed(data.get('seed'))
    if data.get('seed_source') not in ('caller_supplied', 'secrets.randbits(128)'):
        raise ValueError('unknown seed_source')
    for key in ('python_implementation', 'python_version', 'interpretation', 'disclosure_gate'):
        if not isinstance(data.get(key), str) or not data[key].strip():
            raise ValueError(f'missing {key}')
    if type(data.get('planned_task_count')) is not int or data['planned_task_count'] != 8:
        raise ValueError('planned_task_count must be 8')
    if type(data.get('empirical_observations')) is not int or data['empirical_observations'] != 0:
        raise ValueError('a schedule must contain zero empirical observations')
    slots = data.get('slots')
    if not isinstance(slots, list) or len(slots) != 8:
        raise ValueError('slots must contain all eight tasks')
    seen = set()
    assignments = {}
    for position, slot in enumerate(slots, 1):
        if not isinstance(slot, dict):
            raise ValueError('each slot must be an object')
        task_id = slot.get('task_id')
        if not isinstance(task_id, str) or task_id not in TASK_IDS or task_id in seen:
            raise ValueError('task identities must be valid and occur exactly once')
        seen.add(task_id)
        if type(slot.get('position')) is not int or slot['position'] != position:
            raise ValueError('slot positions must be consecutive and match list order')
        pair = task_id[:2]
        stage = 1 if pair in STAGES[1] else 2
        if slot.get('pair_id') != pair:
            raise ValueError('task identity does not match pair_id')
        if type(slot.get('stage')) is not int or slot['stage'] != stage:
            raise ValueError('task identity does not match stage')
        if stage != (1 if position <= 4 else 2):
            raise ValueError('stage 1 must precede stage 2')
        if slot.get('condition') not in CONDITIONS:
            raise ValueError('unknown condition')
        assignments[task_id] = slot['condition']
    if seen != TASK_IDS:
        raise ValueError('schedule must include every task identity')
    for offset in (0, 4):
        first_conditions = []
        pairs = []
        for first, second in (slots[offset:offset + 2], slots[offset + 2:offset + 4]):
            if first['pair_id'] != second['pair_id']:
                raise ValueError('pair tasks must be contiguous')
            pairs.append(first['pair_id'])
            if {first['condition'], second['condition']} != set(CONDITIONS):
                raise ValueError('each pair must contain one task per condition')
            first_conditions.append(first['condition'])
        if len(set(pairs)) != 2 or set(first_conditions) != set(CONDITIONS):
            raise ValueError('each stage must balance AI-first and no-AI-first pairs')
    if data.get('condition_assignments') != assignments:
        raise ValueError('condition_assignments must exactly match slots')
    if slots != _slots_for_seed(data['seed']):
        raise ValueError('slots do not reproduce from the recorded seed and algorithm')
    return True


def write_schedule(path, data):
    """Save validated canonical JSON privately without overwriting; return SHA-256."""
    validate_schedule(data)
    payload = (json.dumps(data, indent=2, sort_keys=True) + '\n').encode('utf-8')
    path = Path(path)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'wb') as handle:
        handle.write(payload)
    return hashlib.sha256(payload).hexdigest()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=int)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--task-pool-sha256', default=TASK_POOL_SHA256)
    parser.add_argument('--session-controls-sha256', default=SESSION_CONTROLS_SHA256)
    args = parser.parse_args(argv)
    try:
        data = generate(args.seed, task_pool_sha256=args.task_pool_sha256,
                        session_controls_sha256=args.session_controls_sha256)
        digest = write_schedule(args.out, data)
    except (ValueError, OSError) as error:
        parser.exit(2, f'{error}\n')
    print(f'Saved private schedule: {args.out}\nSHA-256: {digest}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
