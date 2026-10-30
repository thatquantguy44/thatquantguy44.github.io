# Source notes and admission record

Prepared: 2026-10-28 (America/New_York)

Companions: [evidence matrix](evidence-matrix.md), [claim-linked article outline](article-outline.md), [research brief](ai-hype-research-brief.md).

## Evidence boundary

This pass uses the earlier conversation's source excerpts/metadata and the saved research documents. It does not fetch sources, clone/fetch repositories, run provider calls, or execute experiments. Prior retrieval timestamps and original response bytes were not archived. The dates below identify publication/revision dates retained in context, not a new access date. There is no paper-file SHA-256 to report; hashing this note would not supply one.

Bounded local searches for the named arXiv/FEDS identifiers found links in the existing brief/protocols, not full primary papers. The website project has no configured governed market-research catalog for QuantSmith's `knowledge://market_research/...` interface. That lookup was **not executed**; this is not an empty catalog result and cannot establish that a field is underexplored. The source set is a bounded prior-art inventory, not a systematic or current literature review.

The empirical comparisons are contested within this source set, particularly for coding productivity and coordination. No conclusion about the completeness of the broader literature is made. QuantSmith's prior-art guidance supplies a handoff to `research_analyst` for the already scoped research plans; its backtest guidance supplies review questions, not a completed production-readiness approval.

## Related Approaches

| Topic | Approaches already represented | Unanswered question |
| --- | --- | --- |
| Agents | Capability horizons; multidimensional reliability evaluations | Net effort and verified success under a specified supervision policy |
| Multi-agent systems | Controlled architecture comparisons; task decomposition; single-agent baselines | Incremental value beyond self-review at comparable resources |
| Coding | Randomized task-time studies; enterprise output studies; self-reports | Total delivery effort and quality in our chosen population |
| Trading | Lookahead diagnostics; data-vintage audits; prospective forecasting | Incremental predictive and economic value for a frozen signal |

## Source registry

### S-A01

- **Identity:** [Towards a Science of AI Agent Reliability, arXiv:2602.16666v3](https://arxiv.org/abs/2602.16666v3).
- **Version/date:** submitted February 18, 2026; v3 revised June 2, 2026. Retained metadata says accepted at ICML 2026; proceedings/final-text identity still needs checking.
- **Family / role:** `princeton-reliability`; primary study, abstract/metadata carryover.
- **Locator retained:** abstract; measures consistency, robustness, predictability, and safety alongside capability. Full experimental tables, configurations, and intervals are unavailable here.
- **Admission task:** G01. Earlier model counts and later dashboard results must not be silently combined with v3.

### S-A02

- **Identity:** [METR task-completion time horizons](https://metr.org/time-horizons/).
- **Version/date:** dynamic measurement/methodology page; no versioned local dataset or original retrieval timestamp.
- **Family / role:** `metr-time-horizon`; primary measurement definition and data landing page.
- **Locator retained:** definition/methodology explaining fitted success probability against human completion time. Current scores and model coverage are not admitted.
- **Admission task:** G05. A model-specific figure requires a dated dataset/method snapshot and its uncertainty.

### S-A03

- **Identity:** [METR: Clarifying limitations of time horizon](https://metr.org/notes/2026-01-22-time-horizon-limitations/).
- **Version/date:** January 22, 2026 research note, described by the publisher as less reviewed than its research posts.
- **Family / role:** `metr-time-horizon`; author methodological caveats, not an independent study of deployment savings.
- **Locator retained:** interpretation of probability-conditioned horizons, supervision requirements, modeling assumptions, and difficulty of estimating very high reliability.
- **Admission task:** G05. Do not use this note to certify a general sample-size rule or today's frontier horizon.

### S-A04

- **Identity:** [Princeton HAL reliability dashboard](https://hal.cs.princeton.edu/reliability/).
- **Version/date:** dynamic companion; no archived page or dataset hash.
- **Family / role:** `princeton-reliability`; companion to S-A01, not independent replication.
- **Locator retained:** discussion of updated models, outcome-consistency corrections, and evaluation-harness fixes. No live table values are admitted.
- **Admission task:** G01/G05. Match a specific dashboard/data release to the paper before combining populations or scores.

### S-M01

- **Identity:** [Towards a Science of Scaling Agent Systems, arXiv:2512.08296v3](https://arxiv.org/abs/2512.08296v3).
- **Version/date:** original December 9, 2025; v3 revised April 8, 2026.
- **Family / role:** `kim-agent-scaling`; primary study, versioned-abstract metadata carryover.
- **Locator retained:** controlled architecture comparisons and task-dependent gains/losses. Numerical endpoints and architecture-selection percentage remain candidates pending exact tables/denominators.
- **Admission task:** G02. Configuration counts, relative-change units, budgets, repetitions, and held-out procedure must come from one coherent version.

### S-M02

- **Identity:** [Google Research: Towards a science of scaling agent systems](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/).
- **Version/date:** January 28, 2026 author explanation; earlier than S-M01 v3.
- **Family / role:** `kim-agent-scaling`; derivative explanation of the same study, not a second empirical sample.
- **Locator retained:** architecture/task alignment and coordination overhead. Its earlier configuration/benchmark counts must not label revised-paper results.
- **Admission task:** G02. Do not silently reuse earlier regression, error-amplification, or performance numbers.

### S-M03

- **Identity:** [ybkim95/agent-scaling code repository](https://github.com/ybkim95/agent-scaling/).
- **Version/date:** no local clone or inspected commit. An earlier session retained a README describing a later publication and script corrections.
- **Family / role:** `kim-agent-scaling`; reproducibility/code-version lead, not a separate study.
- **Locator retained:** README/release-note carryover only. No reproduction or correction-impact audit has been performed.
- **Admission task:** G02. Resolve publication, tag/commit, scripts, and data together; do not present a moving README as a pinned replication.

### S-C01

- **Identity:** [METR: Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity, arXiv:2507.09089v2](https://arxiv.org/abs/2507.09089v2).
- **Version/date:** original arXiv submission July 12, 2025; v2 revised July 25. Tool period and sample metadata are retained in the matrix.
- **Family / role:** `metr-developer-productivity`; primary randomized study, abstract/metadata carryover.
- **Locator retained:** study summary. S-C03 repeats the original effect/interval; no full local table or explicit interval-level locator.
- **Admission task:** G03. Recover assignment, model mix, task-time definition, clustering/uncertainty method, and exact confidence-interval level.

### S-C02

- **Identity:** [The Effects of Generative AI on High-Skilled Work: Evidence from Three Field Experiments with Software Developers](https://doi.org/10.1287/mnsc.2025.00535).
- **Version/date:** Management Science, online February 27, 2026; earlier preprints also exist. Publication date does not establish treatment dates.
- **Family / role:** `cui-enterprise-coding`; primary pooled field experiments. Publisher abstract and supplement excerpts were retained earlier; full specifications are not local.
- **Locator retained:** headline result/SE; [supplement](https://pubsonline.informs.org/doi/suppl/10.1287/mnsc.2025.00535/suppl_file/mnsc.2025.00535.sm1.pdf) discusses ITT estimates and imperfect adoption.
- **Admission task:** G03. Reconcile access assignment versus adoption/IV estimates, output definitions, experiment dates, weighting, and intervals before quoting a causal effect.

### S-C03

- **Identity:** [METR: We are Changing our Developer Productivity Experiment Design](https://metr.org/blog/2026-02-24-uplift-update/).
- **Version/date:** February 24, 2026; follow-up began August 2025.
- **Family / role:** `metr-developer-productivity`; author update, partly overlapping participants with S-C01.
- **Locator retained:** original-result recap and explanation of follow-up selection/time-measurement limitations. Raw follow-up subgroup estimates are not a clean current-effect estimate.
- **Admission task:** G03. Recover subgroup counts, metric/sign convention, and uncertainty; distinguish original recap from new observations.

### S-C04

- **Identity:** [METR: Measuring the Self-Reported Impact of Early-2026 AI on Technical Worker Productivity](https://metr.org/blog/2026-05-11-ai-usage-survey/).
- **Version/date:** May 11, 2026; retained summary dates collection to February–April 2026.
- **Family / role:** `metr-technical-worker-survey`; survey, not the randomized studies above. Treat respondent overlap as unknown rather than asserting independence.
- **Locator retained:** summary and distinction between self-reported speed and value. No numerical uplift is admitted.
- **Admission task:** G04. Verify sampling, response/completion, question wording, retrospective comparisons, and missingness.

### S-F01

- **Identity:** [Detecting Lookahead Bias in LLM Forecasts, arXiv:2512.23847v2](https://arxiv.org/abs/2512.23847v2).
- **Version/date:** original December 29, 2025; v2 revised June 12, 2026. Earlier retained material used a different title/method description.
- **Family / role:** `llm-lookahead-diagnostic`; primary methodological/empirical paper, incomplete abstract/metadata carryover.
- **Locator retained:** v2 abstract opening describes date-only firm/date recall queries for Lookahead Propensity. Exact datasets, models, assumptions, and tests need the full v2 text.
- **Admission task:** G06. Do not combine the earlier pretraining-membership description with the later method or infer a strategy's net alpha.

### S-F02

- **Identity:** [Total Recall? Evaluating the Macroeconomic Knowledge of Large Language Models](https://www.federalreserve.gov/econres/feds/total-recall-evaluating-the-macroeconomic-knowledge-of-large-language-models.htm), [paper PDF](https://www.federalreserve.gov/econres/feds/files/2025044pap.pdf).
- **Version/date:** FEDS 2025-044, June 2025 staff working paper. No local full-text snapshot.
- **Family / role:** `fed-macro-recall`; primary task-specific evidence about macroeconomic information sets.
- **Locator retained:** abstract discussion of mixing data vintages/reference periods and release-date availability. No quantitative error rate or trading result is admitted.
- **Admission task:** G06. Recover model/series/task definitions and limitations; keep inference scoped to the studied recall setting.

## Verification backlog

| Gate | Work required | Closure evidence |
| --- | --- | --- |
| G01 | Pin the reliability study and any companion scores | Archived versioned primary text/data; exact populations, model/task definitions, table/section locators, uncertainty; dashboard relationship recorded |
| G02 | Reconcile agent-scaling paper, older blog, and code | One paper/data/code version set; exact relative-effect denominators, resource controls, held-out selection procedure, and correction impact checked |
| G03 | Reconcile coding study designs and estimates | Primary methods/tables for both studies; experiment dates, model/tool versions, access-versus-adoption estimand, output/time units, clustering, SE/CI interpretation and METR follow-up limitations |
| G04 | Verify survey claims | Archived methods/questions/sample flow; missingness, overlap and response selection; self-report clearly separated from measured effects |
| G05 | Pin dynamic measurement definitions before quantitative use | Dated source/data/harness snapshot; exact model coverage and fit/interval method; no implied current ranking from an older page |
| G06 | Verify financial-diagnostic scope and method versions | Full v2 lookahead paper and macro-recall paper; models/data/windows, identification assumptions, error definitions, and limits on transferring findings to a trading strategy |

All six gates remain open. A previously seen source URL, a working matrix, or another agent repeating a claim does not close them. No new retrieval is authorized by creating this queue; the offline-only choice remains in effect.

## Workflow provenance and review scope

Local repos were read without fetching, installing, changing their configuration, or editing their files. The selected guidance files were clean at inspection:

| Repository | Inspected local commit | Guidance applied |
| --- | --- | --- |
| [QuantSmith](https://github.com/thatquantguy44/QuantSmith/tree/3fdb484d49f0da309d3ef7e547c5abf1a23fac55) | `3fdb484d49f0da309d3ef7e547c5abf1a23fac55` | `agents/research_analyst/`, `agents/role_operations/prior_art_scanner/`, `agents/backtest_review/`; model-validation, point-in-time, and honest-reporting standards |
| [agent-skills](https://github.com/thatquantguy44/agent-skills/tree/f63ec56a3cc936408d792956ae583c3c96a825bd) | `f63ec56a3cc936408d792956ae583c3c96a825bd` | Skill discovery, `documentation-and-adrs`, scoped documentation, and explicit verification/readiness |

The current assistant applied these role contracts/checklists sequentially. No separate specialist process, independent human reviewer, QuantSmith runtime/catalog, or cross-model review was executed. These repos are workflow provenance, **not empirical evidence** that AI systems or our strategies work. Their repository-wide development rules were not copied into this website project.

## Findings

1. **Publication blocker:** exact numerical headlines need primary snapshots and locators; the offline ledger cannot close that gap.
2. **Interpretation blocker:** task time, task output, self-report, architecture selection, benchmark accuracy, forecast loss, and economic return have distinct denominators.
3. **Version blocker:** agent-scaling and lookahead sources have material version differences; dynamic dashboards add another boundary.
4. **Experiment blocker:** there are no original empirical trials. Simulation/test artifacts cannot be admitted as research observations.

## Required Tests

For this documentation pass: check claim/source IDs, cross-links, topic coverage, candidate numerical units, explicit uncertainty gaps, and consistency with the existing protocols. Confirm no source hash or independent review is invented. Runtime tests do not substitute for these checks.

For eventual experiments: follow the already saved protocols, with independent source/fixture review, retained failures, frozen configuration, and dependence-aware inference. The backtest review must revisit availability, universe selection, execution, costs, overlapping exposures, and benchmark choice.

## Assumptions To Revisit

- The first article can be a literature synthesis with proposed tests; an empirical article needs actual observations.
- The bounded prior source set may omit important positive or negative studies.
- A nominal resource ceiling is not equal observed cost; an abstract's stated controls are not a reproduced comparison.
- A broad-market comparator is not a factor-risk adjustment, and a paper's contamination diagnostic is not an audit of our model.

## Production Blockers

Agent and trading live source/model bindings and independently trusted timing receipts remain unresolved. The coding study has one confirmed participant and a [technically ready frozen session](coding-session-ready.md): tool/timing/runtime bindings, a no-prior-implementation self-report, and one authorized task-free Codex availability receipt are recorded, with the original schedule preserved. No study-task editor or task timer has started; warm-up and per-attempt editor/source/order/assistance attestations remain, independent review is unconfirmed, and coding observations remain zero. The availability check supplies no coding-quality, model-snapshot, or production-readiness result. Its single-check authorization permits no further provider calls; remaining preparation stays offline. No production-promotion decision is made here.

## Decision Recommendation

Use the matrix to write a scoped first draft and direct the primary-verification work. Hold numerical headlines and original-results claims. Do not merge methodological hypotheses into findings merely to complete the article.

## Open Questions

Which source artifacts can be supplied or retrieved within a later authorized workflow? Which exact main-study populations and models will be frozen? Who will independently review primary extraction and eventual experiments?

## Handoff

The prior-art inventory feeds QuantSmith's `research_analyst` role and the existing research brief. Financial-performance claims require `backtest_review` before any production-promotion decision. This assistant-authored literature pass is not that independent review.
