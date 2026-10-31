# Coding case study: repository and task recommendations

Prepared: 2026-10-29 (America/New_York)

Parents: [personal protocol](coding-experiment-protocol.md), [access decision](coding-study-decision.md). **Update, 2026-10-30: the user accepted the isolated QuantSmith SDK and all four pairs, with P1/P2 first, then P3/P4.** The [prepared bank](experiments/coding-study/task-bank.json) provides exact briefs/checks, and the [ready handoff](coding-session-ready.md) records the frozen assignments and completed familiarity/availability gates. Source/preflight checks are setup validation, not participant attempts. No task solution or productivity result has been generated.

## Repository recommendation

Use an isolated snapshot of the **QuantSmith Python SDK**, scoped to selected local utility modules and synthetic inputs. The source checkout is `qf_workflow_sdk_public`; selected commit is `2601cabd74622c832e99457a9a84ddb4a11f073c`. A `git archive` copy excludes working changes and is pinned by SHA-256 in the task bank. The original working checkout remains untouched.

The committed `pyproject.toml` specifies Python 3.10+, NumPy, and pytest in development dependencies. The inspected reporting, XML, manifest, schema, and pipeline utilities provide bounded maintenance surfaces with existing tests. Selected offline preflight now passes on the isolated import path: 36 existing regressions pass, while new-requirement checks fail on intended missing behavior. No dependency was installed, and full-suite/execution readiness is not claimed. See the [validation record](experiments/coding-study/VALIDATION.md).

| Alternative | Assessment |
| --- | --- |
| `agent-skills` | Credible fallback if Node tooling is preferable: `scripts/*-test.js` use built-in test/assert facilities and local temporary fixtures. Its existing behavioral eval tasks publish solution-oriented expectations and may invoke model runs; exclude them. Markdown edits measure a different activity from code maintenance. |
| This website | Less suitable as the primary setting: Jekyll/Ruby/theme setup and visual acceptance add variability. Its website check uses Jekyll plus html-proofer. The recently coauthored agent/trading apparatus has prior solution exposure and should stay out of the study task bank. |

These are local manifest/source-structure observations, not a benchmark of repository quality. QuantSmith familiarity must be recorded; it does not establish familiarity with every selected task.

## Proposed distinct task pairs

All rows are selected maintenance/extension briefs, expanded into exact task contracts in the prepared bank. Their new behavior is absent at the pinned base; no existing defect is claimed merely by listing an enhancement. Similarity of difficulty remains a preflight judgment, not an observed fact.

| Pair | Task A | Task B | Why consider the match |
| --- | --- | --- | --- |
| P1 — Reporting features | Add a bounded slow-test summary over existing `TestResult` records in `test_engineering/report.py`, with declared duration threshold, result limit, and tie handling | Add a grouped dbt-finding summary by rule and severity in `pipelines/dbt_review.py`, preserving existing summary behavior | Small reporting APIs over existing records; sorting/selection versus grouped aggregation, not the same repair twice |
| P2 — Input compatibility | Extend `test_engineering/junit.py` to accept a specified namespace-qualified JUnit fixture while preserving existing status/message handling | Extend `pipelines/ingestion_data_contract.py` with an optional categorical allowed-values rule and explicit null/missing behavior | Structured-input maintenance in XML versus row/schema validation; distinct parsers, data, and failure cases |
| P3 — Diagnostic helpers | Add a partition-plan explanation helper in `pipelines/distributed_compute.py`, reporting the requested size, resulting partition count, and whether a declared bound constrains it | Add a compatibility-summary helper in `pipelines/schema_evolution.py`, exposing change categories and backward/forward impact without altering compatibility decisions | Bounded explanatory APIs over existing computation; arithmetic/bounds versus schema-change classification |
| P4 — Audit exports | Add a deterministic, serializable export of the existing lineage-impact result in `pipelines/provenance.py`; no new graph traversal | Add a serializable per-step health/diagnostic export in `pipelines/pipeline_observability.py` over synthetic report objects; no pipeline execution | Small export contracts over different structures: graph-impact references versus step-health diagnostics |

The scope is deliberately narrow. Existing public result types may be shared across modules; record that familiarity. Separate worktrees prevent patch transfer but cannot remove learned conventions. The selected tasks would support a case about these maintenance features, not all coding work or quant research productivity.

**Accepted scope:** all four pairs, P1/P2 before P3/P4. Preparation/preflight follows that order. The frozen execution schedule preserves those stages, with randomization only within permitted stages/pairs. All eight definitions were fixed before outcomes; P3/P4 inclusion does not depend on earlier results. This is not a power calculation. The bound caps are 60 minutes active and 90 minutes elapsed per initial attempt. Participant-initiated execution dates are recorded when attempts start; the original schedule must not be redrawn based on results.

## Preflight before accepting any pair

1. Confirm each requested behavior is genuinely new or unsupported at the candidate base. If already present, drop/rewrite the candidate before assignment; do not manufacture a broken baseline or present an enhancement as a reproduced bug. Include actual bug-fix tasks only when fresh failures can be reproduced and paired appropriately.
2. Specify the exact input/output API, defaults, error behavior, acceptance fixtures, and permitted changes. Freeze checks for ordinary, boundary, and regression cases before randomization. Do not give the participant an implementation patch or scoring answers.
3. Match expected operation type, module surface, dependency/setup burden, familiarity, and acceptance/test effort. Bound each task to one main behavior and typically one production module plus tests; split or reject substantially larger work before freezing the bank.
4. Verify the frozen environment runs the selected baseline tests offline, without credentials or live data. Existing tests should pass; a task-specific new requirement may have a failing check. Do not run a provider/behavioral eval as setup.
5. Record prior task/solution exposure and curator overlap. This discussion exposes themes and module locations; it does not establish task naivety. Avoid tasks already implemented during this research conversation or recently solved by the participant.
6. Freeze task pool/pairs, base commit, acceptance checks, and workload. Then generate and archive randomization and order. Each task starts from the same clean base; no shared answer memory, prior patch, or AI transcript is carried into a control task.

Exact briefs and public acceptance checks are prepared for all eight tasks; [package instructions](experiments/coding-study/README.md) explain snapshot reproduction and fresh exports. Difficulty matching remains provisional: P1A has more input validation than P1B, P2B spans more validation branches than P2A, and P4B has a richer report shape than P4A. Retain these declared asymmetries when interpreting results; do not infer equal effort from similar file counts. Tool/timing/runtime bindings and assignments are frozen, and the participant reports no prior implementation beyond planning, briefs, and source discussion. Warm-up and per-attempt source/editor/order/assistance checks remain; independent review is unconfirmed. P1B/no-AI is first, with no task timer or coding observation started.
