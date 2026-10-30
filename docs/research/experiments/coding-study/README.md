# Personal coding-study records

Read the [protocol](../../coding-experiment-protocol.md), [AI/timing settings](../../coding-session-settings.md), original [runtime/conditional-freeze record](../../coding-session-readiness.md), current [ready handoff](../../coding-session-ready.md), and [access decision](../../coding-study-decision.md). One developer is confirmed. The private v2 session verifies as technically ready: task/tool/runtime bindings, the participant's no-prior-implementation self-report, and one authorized task-free Codex availability receipt are recorded. The original eight-task schedule is unchanged. Warm-up and per-attempt editor/source/order/assistance attestations remain; no study-task editor, task timer, or coding observation has started. Independent review is unconfirmed. The online exception covered only the generic check; further provider calls remain unauthorized and preparation stays offline.

- `session.example.json`: freeze the actual tasks, time limits, tools, acceptance, and assignment before collection. Proposed workload is in the protocol; unbound fields stay null.
- `session.prepared.json`: the selected source/task-bank bindings and observed preflight environment, with actual slots/caps/AI/assignment still null. It is not execution-ready.
- `session.configured.json` and `session-controls.lock.json`: Codex/time/timer bindings and their file hashes, separate from the unchanged task-bank lock. The configured manifest remains an unready historical preparation stage; use the promoted frozen session for current readiness and assignments.
- `observation.template.json`: copy once per scheduled task into a private `runs/` directory. Blank/null entries are not observations. Retain one record for each assignment, including failure and not-started status.
- `task-bank.json` and `bank-lock.json`: all eight definitions, source commit/archive hash, fixed stages, baseline selectors, and file hashes. The lock identifies prepared definitions, not a frozen execution session.
- `tasks/` and `acceptance/`: per-task public briefs and synthetic acceptance checks. No production solutions or reference patches are included.
- `prepare.py`: offline snapshot reproduction, clean task export, preflight, and local change audit. It does not implement the tasks, assign AI access, time the participant, or run a study.
- `timer.py`: offline manual interval logger with active/wall cap signalling and clock-anomaly handling. Regular use requires a ready frozen session and matching assignment; smoke is synthetic only.
- `codex.study.json`, `codex_binding.py`, `AI-INSTRUCTIONS.md`: selected Codex CLI/model/effort and isolated-context policy. The checker reads local metadata and writes a private future command prefix; it never launches a model/coding session or edits user configuration.
- `runtime.py`: pinned VS Code/environment metadata and dedicated settings/empty extensions, with fresh per-task editor recipes; no GUI launch. `NO-AI-INSTRUCTIONS.md` and the blank attempt attestation specify common/manual controls.
- `editor_delivery.py`: offline short-path native-editor launch preparation for macOS IPC socket limits. It copies the frozen settings bytes to a fresh short cache, verifies their hash and an empty extensions directory, and records an unlaunched recipe; it does not verify GUI behavior or alter the frozen runtime.
- `schedule.py`: reproducible restricted randomization with one AI and one no-AI task per pair and balanced first conditions within each stage. The original draw is preserved; [disclosed assignments](ASSIGNMENTS.md) follow the confirmed familiarity record.
- `availability.py`: plan-only by default; an explicitly authorized generic `READY` probe is opt-in, task-free, one process, and limited to 120 seconds. The single authorized check passed; raw evidence is retained, and unexposed model identity/cost remain null. This is not permission for another call.
- `freeze.py`: private conditional freeze, actual artifact verification, and promotion to a new directory without changing the original schedule/seed. The [original commitment](session-freeze.commitment.json) and [ready commitment](session-ready.commitment.json) preserve the two stages; [frozen assignments](assignments.frozen.json) record the disclosed order.
- [Validation record](VALIDATION.md): preparation checks, expected new-requirement failures, and remaining limitations.

## Task order

| Stage | Pair | Task A | Task B |
| --- | --- | --- | --- |
| 1 | P1 | [Slow-test summary](tasks/P1A.md) | [Grouped dbt findings](tasks/P1B.md) |
| 1 | P2 | [Namespace-qualified JUnit](tasks/P2A.md) | [Categorical allowed values](tasks/P2B.md) |
| 2 | P3 | [Partition explanation](tasks/P3A.md) | [Schema compatibility summary](tasks/P3B.md) |
| 2 | P4 | [Lineage-impact export](tasks/P4A.md) | [Per-step health export](tasks/P4B.md) |

Stage 1 precedes stage 2. The saved randomized pair/task order and AI/no-AI assignment obey that restriction; the first assignment is **P1B/no-AI**. All eight tasks were selected before outcomes; stage 2 does not depend on stage 1 performance. Difficulty matching is provisional, with scope asymmetries noted in the [task-selection record](../../coding-task-recommendations.md).

## Reproduce preparation

Python 3.10+ for the preparation helper; selected SDK checks require locally available NumPy/pytest. No dependency is fetched or installed. From the website repository root, use fresh output paths:

```sh
python3 docs/research/experiments/coding-study/prepare.py verify
python3 docs/research/experiments/coding-study/prepare.py snapshot --repo "/path/to/local/QuantSmith" --out /tmp/coding-sdk-source
python3 docs/research/experiments/coding-study/prepare.py preflight --snapshot /tmp/coding-sdk-source --out /tmp/coding-sdk-preflight
python3 docs/research/experiments/coding-study/prepare.py export --snapshot /tmp/coding-sdk-source --task P1A --out /tmp/coding-P1A
python3 docs/research/experiments/coding-study/prepare.py audit --packet /tmp/coding-P1A
python3 -m unittest discover -s docs/research/experiments/coding-study -p 'test_prepare.py' -v
```

The snapshot uses `git archive` at the pinned commit, excludes dirty working changes, and verifies its SHA-256. It never fetches. Each export re-extracts that archive into `workspace/`, adds only the current brief/check and a self-contained protocol copy, and refuses existing output directories. `packet.json` retains original file hashes and permitted change paths. Public acceptance artifacts must not be edited to force a pass; focused participant tests may use the recorded `tests/test_case_study_<task_id>.py` path.

`preflight` runs the selected existing regression checks, then each new acceptance suite in P1/P2/P3/P4 order. It disables pytest plugin auto-loading, checks that SDK imports come from the isolated source, disables cache writes, and blocks Python socket construction/connection/DNS lookup. A 60-second subprocess limit applies to these setup commands. This is not an OS sandbox and does not enforce future participant/AI-tool access or task deadlines.

Success means unchanged baseline tests pass and new requirements fail for intended missing behavior, with no collection/import errors or source changes. Read the retained logs: expected failure alone cannot establish that every test is sound, satisfiable, or sufficient. Logs and pytest case durations are software setup evidence, never participant effort/results. `audit` compares local packet/source hashes and flags unexpected changed paths, ignoring Python/pytest cache directories; it cannot authenticate the operator, metadata, or time.

The local prepared copy is under ignored `sessions/quantsmith-2601cab/`; retained preflight logs are under `sessions/`. Use fresh exports for actual timed attempts only after the session is frozen. No condition is assigned by exporting a task.

## Observation recording

Current binding: Codex CLI 0.160.0, model `gpt-6.1-sol`, reasoning effort `high`; 60 minutes active and 90 minutes elapsed per initial task. Warm-up is 10 minutes per condition; follow-up is a separate seven-calendar-day defect observation. See the settings addendum for precise accounting and the [ready handoff](../../coding-session-ready.md) for current status and the completed single-check online exception. The configured model name remains distinct from a verified immutable server snapshot.

```sh
python3 docs/research/experiments/coding-study/codex_binding.py --out /tmp/coding-codex-check
python3 docs/research/experiments/coding-study/timer.py smoke --out /tmp/coding-timer-smoke
python3 -m unittest discover -s docs/research/experiments/coding-study -p 'test_*.py' -v
```

These are safe preparation checks, not timed tasks. The normal `timer.py run` command requires the ready frozen session and actual assigned condition; it intentionally rejects the historical `session.configured.json`. Do not start or resume an AI session during offline preparation. Before a timed export is used, supply its current session controls/AI instructions alongside the original task/acceptance/protocol and retain both task-definition and controls hashes; current controls supersede old unbound placeholders. Use fresh output directories.

## Current ready session and historical conditional freeze

Private `sessions/frozen-session-v1/` preserves the original conditional schedule, `session.frozen.json`, and redacted freeze report. Its then-unresolved familiarity/availability gates and false readiness remain historical. Private `sessions/frozen-session-v2/` contains the promoted specification and verifies `execution_ready: true`. Both retain the same schedule SHA-256, `d214735dc35d71f113d2939ad6ea5a9281373808e653107ebecd38ec971f7f89`; promotion did not redraw or change the order. There are eight assignments and zero coding observations.

The editor is VS Code 1.143.1 with a fresh study profile and empty installed extensions; shared Python 3.12.0, pytest 8.4.2, NumPy 2.4.6, shell, and source/docs metadata are recorded. The existing personal editor profile is untouched. Metadata checks do not prove effective GUI/OS controls, which require per-attempt operator checks.

Familiarity is now **no prior implementation reported**, retaining known exposure to planning, briefs, and source discussion. The one authorized generic online check returned exactly `READY`, exited successfully, and recorded no observed tools. A returned model ID and monetary cost were not exposed. The raw receipt supports availability only; it does not establish coding quality, runtime isolation, or immutable model identity. The regular timer accepts the promoted manifest's readiness/assignment schema, while operator checks and actual attempt initiation remain separate. No study-task editor or task timer has started; no participant warm-up is recorded.

The new `editor_delivery.py` addresses long macOS Unix-domain socket paths by preparing a fresh short user-data/extensions cache under `/private/tmp`, conservatively checking its main-socket path length, and copying the frozen settings **byte for byte**. Its native-editor recipe disables extensions/sync and removes inherited `VSCODE_*`/`ELECTRON_RUN_AS_NODE` only from the copied child environment. It retains an unlaunched delivery report; that report's `execution_ready: false` describes the unverified delivery, not a change to the frozen session. No GUI behavior has been verified. Per-attempt operator attestations must establish the effective editor state before timing; frozen settings remain untouched. A generic setup-only native launch starts without the socket error, but the UI tool could not select its window to verify effective AI/profile state. The setup profile migrated `extensions.autoUpdate` from boolean `false` to string `"off"`; the operational audit records the exact change and before/after hashes. Built-in extensions activate and shared application state is accessed, so separate user-data/extensions paths do not establish complete isolation. The frozen template and study source remain unchanged. Local participant launchers create and check a fresh short profile instead of blindly reusing an ephemeral cache.

Additional offline helpers can be exercised without model use:

```sh
python3 docs/research/experiments/coding-study/availability.py plan --out /tmp/coding-availability-plan
python3 -m unittest discover -s docs/research/experiments/coding-study -p 'test_*.py' -v
python3 -m pytest docs/research/experiments/coding-study/test_runtime.py -q --noconftest -p no:cacheprovider
```

Actual freeze verification uses `freeze.verify_frozen(private_directory)`; it returns private session content, so retain raw output privately. `freeze.finalize_session(old_directory, new_directory, familiarity=..., availability_directory=...)` validates updated evidence and retains the exact original schedule bytes. No helper launches a timer, editor, or study task as part of freezing. Use the current handoff for the already-promoted session rather than repeating the online check or drawing another schedule.

## Recording observed intervals

Record intervals with UTC timestamps and the bound monotonic logger, with one primary category at a time. Active categories are `implementation_debugging`, `author_verification`, and `correction_rework`; passive model/other wait and interruptions remain separate. Retain `events.jsonl`, `intervals.jsonl`, and `summary.json`. Copy observed active totals/waits into the observation template and reference the raw intervals. Clock anomalies or hard process failure leave incomplete timing rather than an invented recovery tail. The logger signals caps but does not stop external tools, randomize tasks, or verify code quality.

Use terminal status `accepted`, `rejected`, `timeout`, `abandoned`, or `not_started`; an unfilled template stays null. Conditions are `ai_enabled` or `no_ai`. Record automated checks and author acceptance separately, and keep review status distinct. Freeze active/wall caps and any correction/follow-up window in the session before assignment.

Keep collected source code, transcripts, timing intervals, identifying information, and results out of tracked files. Local `runs/` and `sessions/` are ignored; tracked research documents remain public in the repository even though excluded from the generated website. Use new files for revisions with references to previous records; preserve original observations.

`null` means unbound/unobserved/unknown according to the accompanying status/notes. Use an observed zero only when measured. The confirmed participant count of one is access information, not evidence that a study task occurred. No original coding-productivity result follows from these templates.
