# Coding case study: bound AI and timing settings

Prepared: 2026-10-29 (America/New_York)

This session addendum binds AI-tool choice, time caps, and timing method for the [personal case-study protocol](coding-experiment-protocol.md). It supersedes the earlier unbound timing/tool placeholders without changing the [locked task definitions](experiments/coding-study/bank-lock.json), acceptance checks, or stage order. The user selected Codex for a **later online session**, with preparation remaining offline. No coding/model session or participant task has started.

## Bound settings

| Setting | Binding |
| --- | --- |
| AI interface | Codex CLI **0.160.0**, current local binary pinned by SHA-256 |
| Model | **`gpt-6.1-sol`**, reasoning effort **`high`**, taken from saved local preferences |
| Context | Fresh standalone context per task; no resume/fork, subagents, cross-attempt memory, or separate review agents |
| Additional services | Study overrides request disabled web search/tool networking; plugins and all configured MCP servers disabled; no hook-trust bypass |
| Active-author cap | **3,600 seconds (60 minutes) per initial task attempt** |
| Elapsed cap | **5,400 seconds (90 minutes) per initial task attempt**, including passive waits and interruptions |
| Warm-up | **10 minutes elapsed per condition**, once before that condition's first task, on unrelated unscored work; logged separately |
| Follow-up | **7 calendar days after submission** for defect observation; initial submission/status retained, follow-up findings and effort appended separately |
| Timing | `interactive_monotonic_intervals_v1`: one long-running local logger using `time.monotonic_ns()` with UTC event labels |

These caps are authored design choices, not observed durations or a sample-size justification. The initial active cap includes implementation/debugging, author verification, and correction/rework. If either cap is reached first, stop; retain the task as timed out and keep its consumed effort. A timeout is not time to accepted completion. No post-cap repair may silently rescue the original attempt.

The model name is a configured reference, not a verified immutable server snapshot or proof of current account access. Local version/help/features/MCP checks established the installed version, loaded overrides, disabled feature flags, and disabled server metadata. No current official documentation was fetched under the offline instruction, no provider prompt was issued, and runtime isolation/search/hook behavior has not been established by those checks. Record the actual returned model identity and exposed usage/cost at collection; missing usage/charges remain null. No automatic model/provider substitution is allowed.

The versioned [Codex profile](experiments/coding-study/codex.study.json) and [AI instructions](experiments/coding-study/AI-INSTRUCTIONS.md) apply to AI-enabled tasks only. Both conditions use the same frozen source/docs, editor, terminal, and local tests. Static editor/language tooling may be common; AI completion/chat/agents must be disabled in the no-AI condition. Ordinary tool setup and the permitted editor/extensions still require a practical preflight before execution freeze.

## Interval categories and clock behavior

The logger records exactly one primary category at a time:

- Active: `implementation_debugging`, `author_verification`, `correction_rework`.
- Passive: `model_wait`, `other_wait`, `interruption`.

Prompting, reading AI output, understanding the task, debugging, and checking results count as active work. Waiting idly for a model counts as passive model wait. If useful work continues while a model generates, switch to the appropriate active category and note the overlap; do not add concurrent model latency to author effort a second time. Calendar/attempt elapsed time continues through every category. Logging overhead remains in the current interval; it is not silently subtracted.

Start before new task-specific reading/investigation. Prior exposure to task themes, briefs, source, and checks must still be recorded; the timer cannot erase curator/participant familiarity. Generic environment setup and unrelated warm-up are separate. Category selection is manual and self-reported; this is not automatic detection of attention or independent timing verification.

The watchdog checks caps about every 250 milliseconds and again on transitions/finish. Timeout takes precedence over a competing finish command. Actual detected overrun is retained rather than clamped away. The logger signals stop; it cannot stop an external editor, shell command, or remote model. Record any work continuing after the signal as a deviation.

Avoid system sleep during an attempt. UTC-versus-monotonic drift over five seconds or backwards clocks marks the timing incomplete/abandoned; the affected open interval stays unknown and previously closed effort is only a known lower bound. These checks cannot prove the absence of sleep or distraction. A hard process failure can leave no final summary: preserve raw records as incomplete, never infer the missing tail, and do not resume an old monotonic session across processes/reboots.

## Follow-up and acceptance

`finish accepted` is a participant-reported status, not an automatic test/quality pass. Retain check outputs, author assessment, and source/packet audit separately. Independent review remains unconfirmed.

Within the seven-day follow-up window, append known defect findings and separately measured verification effort. Keep initial acceptance/time unchanged; report any later defects alongside it. Missing or unperformed follow-up remains missing, not “no defects.” Repairs after submission or the cap are separately labeled later work, not part of the original success. Report initial author effort and any extended observed follow-up effort separately; neither establishes total team/reviewer cost.

## Use and readiness

The [configured session](experiments/coding-study/session.configured.json) binds these components but deliberately retains `execution_ready: false`. Actual slots, familiarity inventory, comparable tooling/runtime checks, online availability, final randomization/schedule, and execution freeze remain pending. P1/P2 must precede P3/P4; the timer checks assignments, while stage completion/order requires operator/schedule control.

Safe preparation commands, from the website repository root, use fresh output paths:

```sh
python3 docs/research/experiments/coding-study/codex_binding.py --out /tmp/coding-codex-check
python3 docs/research/experiments/coding-study/timer.py smoke --out /tmp/coding-timer-smoke
python3 -m unittest discover -s docs/research/experiments/coding-study -p 'test_*.py' -v
```

The Codex checker invokes only local version/features/MCP metadata commands; its private invocation prefix is not launched. It changes no user configuration and retains no raw tokens/headers. Smoke output is explicitly synthetic, with no real participant/task ID. Neither command is a study attempt.

After the actual session is frozen, the regular timer command is:

```sh
python3 docs/research/experiments/coding-study/timer.py run --session /path/to/frozen-session.json --task P1A --condition ai_enabled --out /path/to/new-private-timing-directory
```

That condition is an example, not an assignment. The logger refuses unready/unfrozen manifests, missing/full-pair assignment problems, or a condition mismatch. Commands are `impl`, `verify`, `rework`, `model_wait`, `other_wait`, `break`, `status`, `note TEXT`, and `finish accepted|rejected|abandoned`. Store raw records privately; copy observed fields to the observation record, preserving unknowns and supporting evidence. Keep original task-bank/packet identities and the session-controls identity together; the new session controls override old unbound placeholders in preparation copies.
