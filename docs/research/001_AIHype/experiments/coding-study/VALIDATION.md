# Coding task-bank preparation validation

Prepared: 2026-10-29 (America/New_York)

Current assessment: **prepared definitions and setup checks pass; the promoted v2 session verifies as technically ready.** The participant confirmed no prior implementation, and the single authorized task-free Codex availability check passed. The original staged schedule is unchanged. Warm-up and per-attempt editor/source/order/assistance attestations remain; independent review is unconfirmed. No SDK study solutions, reference implementations, participant task timings, or empirical productivity results were generated. No study-task editor or task timer has started. The sections below retain the earlier preparation findings and identify the later promotion explicitly.

## Frozen source and definition identity

- QuantSmith commit: `2601cabd74622c832e99457a9a84ddb4a11f073c`.
- Source tar SHA-256: `5401537cd79292ae4e677aeeda1ae61f794d7cd5bcdc8c6f820d3619024cd678`.
- The local archive contains 2,420 tracked files and excludes the source checkout's dirty/untracked FX changes. The source checkout remains untouched.
- [Bank lock](bank-lock.json) hashes the protocol, preparation helper, task metadata, all eight briefs, and acceptance files. `prepare.py verify` detects changes. It does not freeze unbound execution settings or prove independent timing.
- Final bank-lock SHA-256: `6843e3030176373005a8fc6cfc26ff44c8b84b2f5cdeda230afceb25e42fee3f`.
- Preflight observed Python 3.12.0, pytest 8.4.2, and NumPy 2.4.6. The later runtime freeze binds these versions; preflight itself did not establish effective participant GUI/OS controls.

## Checks and expected failures

**36 selected existing SDK regressions passed**, with zero failures/errors/skips. These cover existing report/JUnit, data-engineering, ingestion, schema-change, provenance, and observability behavior. The full SDK test suite was not run; compiler/provider/integration workflows are outside this preparation scope.

The public acceptance suites collected **109 cases** on the unchanged base:

| Task | Cases | Expected new-requirement failures | Existing-behavior controls passing |
| --- | ---: | ---: | ---: |
| P1A | 23 | 22 | 1 |
| P1B | 13 | 12 | 1 |
| P2A | 6 | 4 | 2 |
| P2B | 15 | 15 | 0 |
| P3A | 21 | 20 | 1 |
| P3B | 9 | 8 | 1 |
| P4A | 10 | 9 | 1 |
| P4B | 12 | 11 | 1 |
| **Total** | **109** | **101** | **8** |

All eight suites ran in agreed stage/pair order without import/collection errors or skips. Expected failures arise from missing helper APIs, unsupported namespace-qualified XML, or the absent ingestion keyword; they are task prerequisites, not production regressions or measured coding failures. SDK imports were checked against the isolated source, Python networking was guarded, and source file hashes were unchanged after preflight.

Eight preparation-tool unit tests cover safe tar extraction, links/path escapes, snapshot checksum rejection, hash-lock drift, current-task-only export, overwrite refusal, packet/source mutation audit, strict JSON keys, and classification of JUnit errors versus requirement failures. These tests do not exercise a live AI tool or prove OS isolation.

All eight unassigned packets were exported and audited: each contains 2,420 unchanged source files, only its own task brief/check, the matching bank lock identity, and a null condition. Local source/packet audits passed. The packets are setup artifacts, not timed attempts; the prepared session retains `execution_ready: false` and null slots/caps/AI/assignments.

Task authors performed bounded cross-checks of the other pairs' public contracts, object constructors, expected legacy semantics, and checks. They found no concrete contract/check inconsistency in that scope. This was assistant code/method review, not independent human assessment. No reference implementation was produced or validated; expected baseline failure does not prove all checks are sound, satisfiable, or sufficient.

## Scope and readiness limits

- Match quality is provisional. P1A has more validation than P1B; P2B touches more validation branches than P2A; P4B has a richer exported structure than P4A. The participant's no-prior-implementation self-report retains known planning/brief/source exposure; practical scope differences remain limitations. File/test counts are not difficulty or power measures.
- All eight tasks were selected before outcomes. P1/P2 precede P3/P4 by user choice; the saved randomized schedule preserves those stages and discloses the restriction.
- Clean copies, limited setup networking, and local hashes do not establish participant filesystem/network isolation or independent timestamps. Partial/failed exports must be retained as setup artifacts, not silently relabeled observations.
- Public checks are ordinary requirements, available in both conditions. The author has seen themes/source structure; no task-naivety claim is supported.
- At original task-bank preparation, execution settings and assignments were unbound. The later binding/runtime/promotion stages below supply the frozen controls and familiarity/availability evidence; actual participant starts and observed attempt costs/results remain unrecorded. No study attempt may be inferred from setup execution.

See [README](README.md) for reproduction commands and [protocol](../../coding-experiment-protocol.md) for measurement/claim limits.

## Historical AI and timing binding update

The [session addendum](../../coding-session-settings.md), configured manifest, and session-controls lock bind Codex CLI 0.160.0, `gpt-6.1-sol` with high reasoning effort, 3,600 active seconds and 5,400 elapsed seconds per initial task, plus the manual monotonic timing method. The original task-bank lock and source/acceptance definitions remain unchanged.

**33 preparation/timing tests pass**: eight preparation integrity tests, five fake-metadata Codex-binding tests, and 20 synthetic timer tests. Timer coverage includes nonoverlapping active/passive intervals, waiting/interruptions, deadline precedence, actual overruns, clock jumps/backwards/drift, partial failure, output refusal, POSIX nonblocking input, and manifest/assignment/cap matching. No test fixture supplies independent human review or a real coding outcome.

Local Codex version/configuration metadata checks succeeded with study overrides: subagent/plugin feature flags and both configured MCP servers were disabled in the inspected metadata. At this stage, no coding/model session was launched and no fresh official documentation or provider availability/billing check was made under the offline instruction. The later single authorized probe supplies availability evidence only. The configured model name is not a verified immutable snapshot; hook/search/network runtime enforcement remains unverified.

A real-clock timer smoke terminated at its short synthetic wall cap, retained actual overrun and interval records, and kept acceptance/review evidence null. It used no participant/task ID. The current configured session is explicitly rejected by the regular timer as not execution-ready, before creating a task directory. The logger cannot stop an external editor or remote model and cannot authenticate manual activity classifications.

This addendum supplied the earlier unbound AI/cap/timing placeholders. Participant familiarity, comparable runtime, online availability, restricted randomization, and final freeze were still pending at this historical stage; the subsequent sections record their disposition. No study observation exists.

## Historical offline runtime and conditional freeze update

The [readiness addendum](../../coding-session-readiness.md) binds VS Code 1.143.1 with a dedicated profile and empty installed extensions, shared local Python/test dependencies and shell, and the same source/docs archive for both conditions. Local version/help/extension metadata and file hashes verify; no GUI/model/task was launched. A local status command reports an existing ChatGPT Codex login, without retaining account details; this is not live availability evidence.

At this stage the suite contained **79 passing setup checks**: 67 unittest cases (the previous 33 plus 13 scheduler, 11 availability-parser/runner, and ten conditional-freeze checks), and 12 pytest editor-runtime checks. Synthetic runner tests do not make online calls. The availability plan itself had not been launched.

The private eight-slot schedule satisfies every declared constraint and reproduces from its retained seed. A versioned conditional v1 session and [original public hash commitment](session-freeze.commitment.json) preserve this stage. Source/control/runtime/schedule hashes verify; the regular timer rejects the historical v1 snapshot while readiness is false. No assignment or seed was disclosed at that conditional stage, and no study observation exists.

Familiarity was explicitly unknown and online availability was missing at v1. These historical blockers were not failed coding outcomes. Promotion had to verify raw receipt hashes/transcript, preserve the exact schedule/seed, and write a new directory. Expected initial feature failures and prior regression counts are unchanged.

## Current readiness promotion and editor delivery

The participant confirmed **no prior implementation**, retaining exposure to planning, briefs, and source discussion. One explicitly authorized generic online Codex check returned exactly `READY`, exited successfully, and recorded no observed tool use. Its raw artifacts and pinned invocation were verified for promotion. A returned model ID and monetary cost were not exposed; availability is not an immutable-model, coding-quality, reliability, or isolation result. That authorization covered this check only; further provider calls remain unauthorized and remaining preparation stays offline.

Private `sessions/frozen-session-v2/` now passes `freeze.verify_frozen` with `execution_ready: true`. The [ready commitment](session-ready.commitment.json), [disclosed assignments](ASSIGNMENTS.md), and [current handoff](../../coding-session-ready.md) describe the promoted specification. Its schedule SHA-256 is `d214735dc35d71f113d2939ad6ea5a9281373808e653107ebecd38ec971f7f89`, identical to v1; no redraw occurred. P1B/no-AI is first. No study-task editor or task timer has started, participant warm-up remains unrecorded, and coding observations remain zero. Technical readiness does not replace per-attempt source/editor/assistance/order attestations or independent quality review.

The new offline `editor_delivery.py` prepares a short native-editor launch recipe for the macOS IPC socket path limit. It revalidates the frozen runtime, copies the exact frozen settings bytes into a fresh short `/private/tmp` user-data cache, rechecks their hash, and checks the extensions directory is empty. A conservative main-socket path bound is recorded. The recipe removes inherited `VSCODE_*`/`ELECTRON_RUN_AS_NODE` from a copied child environment and leaves the frozen runtime/profile files unchanged. Its report records `gui_launched: false`, pending operator verification, and delivery readiness false; it does not revoke the promoted session's metadata readiness. No actual GUI behavior or OS/network isolation is claimed from preparing this workaround. Existing personal profiles are untouched.

## Participant preparation and delivery audit

The seven focused `test_editor_delivery.py` checks pass. These are synthetic delivery checks, additional to the earlier 79 setup checks; the complete earlier suite was not rerun for documentation/launcher preparation. The local operator check reverified v2, the original first assignment, pristine P1B source/packet, and absent task timing directory. Four private participant launchers and blank warm-up/attestation records are prepared; their non-launching check mode, environment/syntax checks, and pre-start refusal guards were exercised. Blank, future-dated, and inconsistent synthetic warm-up records were refused; a valid synthetic warm-up still could not pass a blank participant attestation. No fixture was written as a participant observation. No study attempt or additional provider call occurred.

A generic setup-only native editor launch starts with the short profile, without the original long Unix-socket error. Its startup logs/settings show exactly one settings migration: `extensions.autoUpdate: false` becomes `"off"`; other prepared setting values match. Before/after hashes and controlled observations are retained in private `sessions/participant-setup-v1/operational-audit.json`. Byte identity after editor startup is therefore false. The separate frozen template and v2 verification remain unchanged.

The empty installed-extension inventory does not mean all built-in extensions are inactive; built-in activation and access to shared VS Code application storage were observed. The UI tool selects existing personal windows, so effective visible profile/AI state is still a participant check. No complete OS, account, or network isolation is established. The current private launcher binds the adaptor/recipe/operator hashes, revalidates the frozen session, and creates and immediately checks a fresh short profile before launch; a cleared old cache is not used to create default settings silently. These delivery artifacts are operational addenda, not a redraw or change to experimental conditions.

## Pre-commit verification

On 2026-10-30 (America/New_York), all 67 coding unittest checks and 19 editor/runtime pytest checks passed again. Task-bank hashes verify, and the existing private v2 freeze remains valid with P1B pristine and its task timer absent. These 86 checks validate preparation software; no participant coding task or additional provider call was run.
