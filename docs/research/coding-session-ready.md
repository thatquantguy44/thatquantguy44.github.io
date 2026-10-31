# Coding study: preparation and first-task handoff

The v2 specification is technically ready. The participant confirmed no prior implementation of any of the eight tasks, retaining earlier exposure to planning, briefs, and source discussion. One authorized, task-free Codex check returned `READY`. The original assignments and source are unchanged. **No study task or task timer has started; there are zero coding observations.**

This is the current status addendum to the frozen [settings](coding-session-settings.md) and [original readiness record](coding-session-readiness.md). Their earlier pending-gate language describes preparation history. Keep those files intact for verification; use this handoff for current operational status.

The first assignment is **P1B, no AI**. The [full schedule](experiments/coding-study/ASSIGNMENTS.md), [ready commitment](experiments/coding-study/session-ready.commitment.json), and [protocol](coding-experiment-protocol.md) retain the design. This is an exploratory personal case study with one participant; independent review is unconfirmed.

## Prepared locally

From the website repository root, the private setup folder is:

```text
docs/research/experiments/coding-study/sessions/participant-setup-v1/
```

It contains a generic `AI-Hype-Study-Setup/` workspace, an environment check, `PREPARATION.md`, and launchers:

| File | Action when the participant runs it |
| --- | --- |
| `OPEN-SETUP.command` | Open unrelated practice files in a fresh study editor profile; no timer |
| `CHECK-ENVIRONMENT.command` | Check local Python, pytest, and NumPy; no network or timer |
| `OPEN-P1B-EDITOR.command` | Open the first packet's source in a fresh study editor profile; no timer |
| `START-P1B-TIMER.command` | Validate the frozen bindings and completed attestation, request an explicit start, then run the real timer |

These local files are ignored by Git and are not website content. They have been prepared, not run as study attempts. A fresh short profile is created at each editor launch, so a cleared temporary cache does not require changing the frozen specification. Do not use the earlier long-profile `launch.prepared.json` editor command.

## Before P1B

1. Run the environment check. Preparation observed Python **3.12.0**, pytest **8.4.2**, and NumPy **2.4.6**; a changed environment requires review before proceeding.
2. Open the setup workspace. Verify the dedicated profile, disabled AI features/inline suggestions, and absence of installed study extensions. Do not use an existing personal editor window for the task.
3. Complete your own **10-minute elapsed no-AI warm-up** on unrelated, unscored work in `scratch.py`. Record actual UTC start/end and elapsed duration in the supplied blank warm-up record. Setup checks and assistant work do not count as your warm-up.
4. Open the P1B editor to check its profile, without inspecting task code, acceptance checks, or the brief. Keep other tasks and AI assistance out of task work. Complete `runs/session-v2/P1B/attempt-attestation.json` honestly after the visible checks. Automatic source/runtime checks do not establish attention or isolation.
5. When ready, run `START-P1B-TIMER.command`. Only after the logger reports that it has started, read `TASK.md` and the current public acceptance checks and begin investigation. The launcher's confirmation is a participant action; preparation has not started the timer.

During P1B, use the [no-AI instructions](experiments/coding-study/NO-AI-INSTRUCTIONS.md). This conversation can help with administration, but implementation hints, code review, and solutions would be unexpected assistance and must be recorded as a deviation. Do not replace a task because of difficulty, failure, or a deviation.

## Timing and retained evidence

The first cap reached ends the initial attempt: **60 minutes active** or **90 minutes elapsed**. Task reading, debugging, verification, and correction count as active work. The logger signals a stop; the participant must stop external work.

| Timer input | Meaning |
| --- | --- |
| `impl`, `verify`, `rework` | Active implementation, author verification, or correction |
| `other_wait`, `break` | Passive wait or interruption; elapsed time continues |
| `status`, `note TEXT` | Inspect totals or retain an event note |
| `finish accepted`, `finish rejected`, `finish abandoned` | End with a participant-reported status |

Retain raw intervals, terminal status, all test attempts/output, patch, deviations, and the observation record. A reported `accepted` status is not an automatic quality pass. Keep the original result even if later work repairs it; append the separate **seven-day defect follow-up**. Missing measurements stay null. The first task's timing directory must be new; never resume or overwrite an interrupted attempt.

## Editor delivery observations

The original deep profile path exceeds macOS's editor socket limit. The separate [delivery adaptor](experiments/coding-study/editor_delivery.py) copies the frozen settings exactly into a fresh short `/private/tmp/aih-*` profile before launch. It leaves the source, assignments, model, caps, and frozen runtime files unchanged.

A generic setup-only native launch starts without that socket error. Startup then changes `extensions.autoUpdate` from boolean `false` to string `"off"`; the setup audit retains before/after hashes and that exact difference. Do not claim the launched profile stays byte-identical. Other prepared settings matched in the audit. Built-in editor extensions and shared VS Code application state can still be used; a separate user-data/extensions directory is not complete OS or account isolation.

The UI tool selected existing personal windows, so the isolated window's visible AI/profile state remains a participant check. Launch metadata and local settings are not proof of effective GUI behavior or network isolation. Preserve any unexpected difference as a deviation before work.

The successful Codex probe establishes point-in-time availability only. It exposed neither a returned immutable model identifier nor a monetary cost. Its permission covered that single generic check. Preparation remains offline; the later AI-enabled warm-up and coding sessions need their own execution authorization and must use the frozen binding.

See the [validation record](experiments/coding-study/VALIDATION.md) for setup tests and limitations. Versioned documents record the preparation state; participant packets, raw logs, and local launchers remain under ignored directories.
