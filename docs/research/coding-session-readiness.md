# Coding session: runtime checks and conditional freeze

Prepared: 2026-10-29 (America/New_York)

This readiness record follows the [bound AI/timing settings](coding-session-settings.md) and the user's request to complete runtime checks, restricted randomization, and a versioned session freeze. It does not start a task or lift the instruction to keep preparation offline.

## Common runtime

Use **VS Code 1.143.1**, commit `e646868227c3e3a9e3f24277c8c7220be42c0be7`, in both conditions. A separate study profile has AI chat/inline suggestions disabled, sync/update/telemetry settings disabled, and an empty installed-extension directory. Each task gets a fresh profile derived from those settings. Existing personal editor profiles and the source QuantSmith working checkout remain untouched.

Installed Python 3.12.0, pytest 8.4.2, NumPy 2.4.6, macOS/architecture, shell, and editor file hashes are recorded privately. The common source and documentation are the pinned QuantSmith archive, with installed local language/library help available equally in both conditions. No new dependencies or external documentation/data are introduced during tasks.

The local editor CLI's metadata commands confirm the chosen version, supported flags, configured settings names, and empty installed-extension inventory. They do not verify effective GUI behavior, built-in feature state, absence of other applications, or OS isolation. Operator checks remain required immediately before each timed attempt. The [attestation template](experiments/coding-study/attempt-attestation.template.json) keeps those unobserved fields null.

Only the bound Codex CLI is permitted additional assistance in AI-enabled tasks. [No-AI instructions](experiments/coding-study/NO-AI-INSTRUCTIONS.md) prohibit AI consultation during the control attempt. Use the same clean packet, editor, local docs/tests, and timing procedure. Retain deviations rather than replacing difficult or contaminated attempts.

## Schedule and freeze sequence

The [scheduler](experiments/coding-study/schedule.py) draws and saves one private 128-bit seed after the task and timing definitions have been locked. It keeps P1/P2 before P3/P4, shuffles pair order within each stage, assigns one AI and one no-AI task per pair, and balances AI-first versus no-AI-first pairs within each stage. All eight task IDs appear exactly once; pair tasks remain contiguous.

This readiness step refines the original freeze sequence: a private, conditional schedule/specification can be committed before the task-free online availability check, with assignments withheld while prior familiarity is unresolved. The availability prompt contains no task inputs and cannot be used to select a favorable assignment. Any later promotion of the frozen specification preserves the original schedule bytes/seed, with new evidence in a new immutable directory. Do not silently redraw, overwrite, or condition stage 2 inclusion on stage 1 results.

The author has seen themes, briefs, and source structure in preparation. Independent prior implementation exposure must be recorded from the participant, not inferred from silence. Unknown exposure stays unknown and blocks execution-ready promotion. If already-solved task IDs are reported, resolve eligibility through a documented task-bank amendment before revealing assignments or collecting outcomes.

Calendar appointments need not be fabricated: use participant-initiated slots, preserve the frozen order, and record actual start/end UTC in each attempt. This selects a recording policy, not dates or a promise that every task will be completed. Keep nonstarted and failed assignments visible.

## Later generic availability check

An [offline probe plan](experiments/coding-study/availability.py) is prepared for the pinned Codex binary/model, using an empty directory and this complete prompt:

> Do not use tools or read files. Reply with exactly READY.

Execution requires a separate explicit change to the offline-only preparation boundary. The runner performs one Codex process with a 120-second timeout, no outer retries or caller model/provider fallback, read-only sandbox settings, no task inputs, and preserved JSONL/stderr/final-message evidence. Internal transport retries remain unobserved. It checks exact `READY`, exit success, no recorded tool/unknown events, and any exposed model identity. Unexposed usage/cost/model ID remain null; identity differences require review. Availability is not a coding-quality, reliability, or isolation result.

The runner defaults to plan-only behavior. The online form is deliberately gated:

```sh
python3 docs/research/experiments/coding-study/availability.py run --out /path/to/new-private-probe-directory --allow-online-probe
```

That command is documentation of a later action, not permission to execute it during offline preparation. No login changes, task solutions, or new dependencies are part of the probe.

## Readiness interpretation

A saved frozen specification is distinct from `execution_ready: true`. Promotion requires valid source/control/runtime hashes, a consistent saved schedule, actual participant familiarity/eligibility information, and a passing authorized availability receipt. Frozen parameter values do not prove effective runtime controls. Per-attempt source/editor/assistance/order attestations and quality evidence are still required; the timer alone cannot authenticate them.

The [package README](experiments/coding-study/README.md) and private freeze report identify the current artifacts and blockers. The public commitment can expose their hashes without exposing condition assignments prematurely. No model session or timed coding observation follows from offline verification, schedule creation, or freezing files.
