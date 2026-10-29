# Offline validation record

Assessment: **Ready within reviewed scope** for protocol implementation review and offline preparation. Live experiment execution still needs the runtime and review steps listed below. Software tests are not agent-performance observations.

Protocol: [v0.1.0](../../agent-experiment-protocol.md)

Checked package fingerprint:

```text
30b34d595c3e2c042d3817247bd2794f81e5e9323a0d5f15feac43073e811999
```

`study.py validate` recomputes the fingerprint from the core package files and protocol. README, tests, this record, and the parent brief are not included in that fingerprint. Their changes do not alter the planned treatment or evaluator inputs.

## Checks performed

- All six synthetic fixtures cover the intended three families and two work structures. Public questions and evaluator answer IDs reconcile; annotated evidence spans occur in their specified public sources.
- Independently recalculated gross margin, conversion, corrected FX conversion, and compounded net return using decimal arithmetic. Agreement between key-derived positive controls and the scorer alone was not used as arithmetic verification.
- Thirty-four unit tests pass, including wrong units, booleans masquerading as numbers, fractional/percent confusion, fabricated and irrelevant citations, missing derivation evidence, unsupported certainty, extra claims, duplicate JSON keys, and non-finite JSON values.
- Record checks reject unknown costs, unreconciled charges, excessive turns/spend/duration, improper human help, missing/nonindependent review, self-verification of checkpoint assistance, changed task/answer hashes, bad context-role sequences, and events extending beyond the recorded attempt.
- Seeded scheduling produces 90 unique attempts in 18 paired blocks, with all five conditions in every block. Seventy-two attempts use models; the other 18 are deterministic-baseline repetitions, not independent evidence.
- End-to-end CLI checks exported all six public packets into temporary participant directories and generated unobserved run templates. Each blank-answer/template run was correctly rejected as unverified. No gold files, scorer, or evaluator annotations were exported.
- Overwriting an existing schedule and exporting into a nonempty participant directory are rejected.
- No credentials, provider calls, actual model outputs, human participant records, or empirical performance results were generated.

## Corrections made during review

- Separated human checkpoint assistance from continuing-context model self-review; multi-agent versus self-review is the primary collaboration contrast.
- Removed an answer-type/unit hint that would have disclosed which synthetic question required abstention.
- Kept unknown costs and durations as `null`, rather than assigning invented zeros.
- Required independent human review before the scorer labels a completed record verified.
- Distinguished protocol/packet preparation from actual runtime isolation and budget enforcement.
- Preserved the distinction between a small synthetic development pilot and a fresh, realistic main-study task set.

## Limits and remaining work

1. The offline tools do not execute the fixed baseline or model conditions. Implement and archive both executors, their tools, and exact context policies before collection.
2. The runtime manifest is intentionally unbound. Model snapshot, prices, provider-specific billing/token limits, seed behavior, runner version, and identities must be set and frozen.
3. Participant export creates a clean input packet but does not establish filesystem/network isolation. Verify the boundary in the actual execution environment.
4. A separate reviewer must validate fixture semantics and keys before collection. The current authoring/software checks do not constitute independent human review.
5. Costs, timestamps, context identity, and review independence are checked as recorded. The evaluator cannot authenticate invoices, raw transcript contents, or human identity. Audit the original artifacts before reporting results.
6. The six development cases are small and structured. They are unsuitable for broad reliability, productivity, or collaboration claims. Main-study cases, a sampling frame, and task-level precision/power planning remain required.
7. No development pilot or main experiment has been run; the USD 36 nominal model/tool ceiling is a proposed design bound, not observed expenditure.

## Recheck

From the repository root:

```sh
python3 docs/research/experiments/agent-study/study.py validate
python3 -m unittest discover -s docs/research/experiments/agent-study -p 'test_*.py' -v
```

Use fresh temporary paths for the scheduling, export, template, and scoring commands in the package README. Do not replace this validation record with fabricated pilot results.
