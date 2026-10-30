# Offline validation record

Updated: 2026-10-29 (America/New_York)

Assessment: **Runnable within offline synthetic scope**. Preparation, grading, fixed baseline, shared restricted tools, and the five-condition controller are implemented. Live experiment execution still needs the runtime and review steps listed below. Software tests and replay smoke checks are not agent-performance observations. See the [harness guide](HARNESS.md).

Protocol: [v0.1.0](../../agent-experiment-protocol.md)

Checked package fingerprint:

```text
1cf7496fcb85ed48c0cf5fce32e08dbc60b162165bbc836376bd5349d8a694f2
```

`study.py validate` recomputes the fingerprint from the core data/prompts/runtime/evaluator, `runner.py`, `fixed.py`, `tools.py`, and protocol. README, harness guide, tests, this record, and the parent brief are not included. New executor contents invalidate older fingerprints and require fresh schedule/session artifacts. The original preparation-only fingerprint is superseded.

## Checks performed

- All six synthetic fixtures cover the intended three families and two work structures. Public questions and evaluator answer IDs reconcile; annotated evidence spans occur in their specified public sources.
- Independently recalculated gross margin, conversion, corrected FX conversion, and compounded net return using decimal arithmetic. Agreement between key-derived positive controls and the scorer alone was not used as arithmetic verification.
- **93 unit tests pass**: 34 original preparation/scorer checks, 28 execution-controller checks, 16 fixed-baseline checks, and 15 shared-tool checks. These include wrong units, booleans masquerading as numbers, fractional/percent confusion, fabricated and irrelevant citations, missing derivation evidence, unsupported certainty, extra claims, duplicate JSON keys, and non-finite JSON values.
- Record checks reject unknown costs, unreconciled charges, excessive turns/spend/duration, improper human help, missing/nonindependent review, self-verification of checkpoint assistance, changed task/answer hashes, bad context-role sequences, and events extending beyond the recorded attempt.
- Seeded scheduling produces 90 unique attempts in 18 paired blocks, with all five conditions in every block. Seventy-two attempts use models; the other 18 are deterministic-baseline repetitions, not independent evidence.
- End-to-end CLI checks exported all six public packets into temporary participant directories and generated unobserved run templates. Each blank-answer/template run was correctly rejected as unverified. No gold files, scorer, or evaluator annotations were exported.
- Overwriting an existing schedule and exporting into a nonempty participant directory are rejected.
- The CLI smoke retained all 90 scheduled synthetic checks, 18 per condition, with 216 scripted request events. All final artifact byte hashes, packet/package fingerprints, event references, phase/cost checks, and schedule membership reconcile. Zero records are verified research successes. The smoke's remaining run-check errors are exactly the declared synthetic-mode, unverified-boundary, unmeasured-operator, and pending-independent-review blockers.
- Controller tests exercise isolated worker contexts, forward plan/worker tool results, continuing self-review, turn-two checkpoint feedback, final-submission rules, known-charge authorized retries, reservation/charge breaches, unknown accounting, model-ID/usage errors, exhausted scripts, timeouts, malformed final output without repair, no fifth request, fresh backend state, and overwrite refusal. A socket-denied smoke test also asserts that no socket construction/connection was attempted.
- Shared tools cannot read arbitrary files or execute code. Literal packet search and bounded AST/Decimal arithmetic reject names/calls/attributes, unsupported operators, excessive size/depth, bad arguments, division by zero, and extreme magnitudes.
- Fixed-workflow tests use independent public-style packets with changed values; they check authority, formulas, compatible dimensions, one-hop FX, ambiguity, and unsupported scope/synthesis. The implementation never imports or loads gold or branches on fixture IDs. Unsupported operations are disclosed abstentions, not a verdict on conventional automation.
- No credentials, provider calls, actual model outputs, human participant records, or empirical performance results were generated.

## Corrections made during review

- Separated human checkpoint assistance from continuing-context model self-review; multi-agent versus self-review is the primary collaboration contrast.
- Removed an answer-type/unit hint that would have disclosed which synthetic question required abstention.
- Kept unknown costs and durations as `null`, rather than assigning invented zeros.
- Required independent human review before the scorer labels a completed record verified.
- Distinguished protocol/packet preparation from actual runtime isolation and budget enforcement.
- Preserved the distinction between a small synthetic development pilot and a fresh, realistic main-study task set.
- A bounded assistant code review found missing worker tool results in the final coordinator handoff. The handoff now includes tool records; a regression test checks delivery while preserving worker isolation. This code review is not independent human fixture/output verification.
- Retried failures no longer leave a stale terminal error on a later completed replay; failed and retried request IDs remain linked and all scenario charges/turns are retained. The scorer explicitly rejects synthetic harness mode as an empirical attempt even if boundary/review attestations are filled in.

## Limits and remaining work

1. The controller executes all five policies with a fixed baseline and scripted model responses. Implement/archive the actual provider adapter, real checkpoint/review handling, billing reservation, raw usage capture, and hard request/tool deadlines before collection. Virtual scenario deadlines do not establish live cancellation behavior.
2. The runtime manifest is intentionally unbound. Model snapshot, prices, provider-specific billing/token limits, seed behavior, runner version, and identities must be set and frozen.
3. Participant export creates a clean input packet but does not establish filesystem/network isolation. Verify the boundary in the actual execution environment.
4. A separate reviewer must validate fixture semantics and keys before collection. The current authoring/software checks do not constitute independent human review.
5. Costs, tokens, durations, and derived timestamps in replay records are explicitly scripted scenarios. Actual local runner wall time is separate; operator handling and human verification remain unmeasured. The evaluator cannot authenticate invoices, raw transcript contents, or human identity. Audit original live artifacts before reporting results. Workers currently execute sequentially, so no parallel-latency result follows.
6. The six development cases are small and structured. They are unsuitable for broad reliability, productivity, or collaboration claims. Main-study cases, a sampling frame, and task-level precision/power planning remain required.
7. No development pilot or main experiment has been run; the USD 36 nominal model/tool ceiling is a proposed design bound, not observed expenditure.

## Recheck

From the repository root:

```sh
python3 docs/research/experiments/agent-study/study.py validate
python3 -m unittest discover -s docs/research/experiments/agent-study -p 'test_*.py' -v
python3 docs/research/experiments/agent-study/runner.py smoke --out /tmp/ai-hype-agent-smoke
```

Use fresh temporary paths for the scheduling, export, template, and scoring commands in the package README. Do not replace this validation record with fabricated pilot results.

## Pre-commit verification

On 2026-10-30 (America/New_York), all 93 unit tests and structural/package fingerprint validation passed again. The checked fingerprint is unchanged. This verification made no provider calls and collected no empirical agent observations.
