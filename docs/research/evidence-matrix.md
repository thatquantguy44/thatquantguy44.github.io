# AI hype research: evidence matrix

Prepared: 2026-10-28 (America/New_York)

Scope: original shortlist items 1, 2, 3, and 10. Parent: [research brief](ai-hype-research-brief.md). Source identities, prior-session provenance, workflow guidance, and the verification backlog are in [source notes](source-notes.md). The [article outline](article-outline.md) maps sections to the claim IDs below; the [first draft](article-draft.md) and [review record](article-draft-review.md) use this inventory without closing its primary-text gates.

**Status: offline working evidence inventory, not a completed primary-text audit.** No fresh literature retrieval, provider/model calls, or experiments were performed for this matrix. The earlier conversation contains primary-source excerpts and metadata, but this checkout contains no archived full papers or original research datasets. A repository note or remembered result is not promoted to a newly verified source. Unavailable details are marked **not retained**, not filled by inference.

## Reading and admission rules

| Label | Meaning | Allowed use |
| --- | --- | --- |
| `DRAFT-QUAL` | A bounded qualitative statement is supported by retained earlier-session source material | Scoped first-draft wording with its citation; final source/locator check still required |
| `DEFINITION` | A measurement definition, not a measured improvement | Explain the denominator; do not attach an unverified current model score |
| `HOLD-NUM` | Candidate numerical result whose publication admission is incomplete | Keep in this working ledger; do not put the number in article prose or a chart yet |
| `VERSION-GATE` | Source versions or artifacts must be aligned first | Explain the mismatch in research notes, not as proof that the study is invalid |
| `NO-RESULT` | Our experiment has no empirical observations | Describe a hypothesis or proposed test only |
| `METHOD` | An authored evaluation rule or classification distinction | Label as our method, not an externally observed result |

These labels describe evidence handling, not invented confidence scores. All literature entries remain subject to the source-refresh and primary-text tasks in [G01–G06](source-notes.md#verification-backlog). Source families are not independent replications: an author's paper, blog, dashboard, code, and follow-up can reuse observations.

## Claim index

| Claim ID | Question or assertion under examination | Admission |
| --- | --- | --- |
| AIH-A01 | Do accuracy improvements establish dependable agent operation? | DRAFT-QUAL |
| AIH-A02 | What does a task-completion time horizon measure? | DEFINITION |
| AIH-A03 | Do autonomous agents reduce total effort after supervision? | NO-RESULT |
| AIH-M01 | Does collaboration help across all task structures? | HOLD-NUM |
| AIH-M02 | What does the reported architecture-selection percentage mean? | HOLD-NUM |
| AIH-M03 | Are blog, revised paper, and code numbers comparable? | VERSION-GATE |
| AIH-M04 | Do our multi-agent systems beat single-agent self-review? | NO-RESULT |
| AIH-C01 | Did AI slow experienced maintainers in METR's early-2025 setting? | HOLD-NUM |
| AIH-C02 | Did enterprise field experiments find greater development output? | HOLD-NUM |
| AIH-C03 | Does METR's follow-up establish today's productivity effect? | DRAFT-QUAL |
| AIH-C04 | Can self-reported speed or value establish measured productivity? | DRAFT-QUAL |
| AIH-C05 | Have we measured total coding and review effort ourselves? | NO-RESULT |
| AIH-F01 | Can historical LLM forecasting contain lookahead information? | DRAFT-QUAL |
| AIH-F02 | Can vintage and release-date errors distort simulated information sets? | DRAFT-QUAL |
| AIH-F03 | Have we demonstrated a prospective, economically useful trading signal? | NO-RESULT |
| AIH-F04 | Do passing software checks establish predictive value? | METHOD |

## Autonomous agents

### AIH-A01 — Accuracy and operational reliability

- **Sources / family:** [S-A01](source-notes.md#s-a01), with dynamic companion [S-A04](source-notes.md#s-a04); one Princeton reliability evidence family.
- **Population, task, model, period:** the retained v3 abstract describes 15 agentic models across two benchmarks. Exact model configurations, evaluation dates, grading changes, and task counts are not retained locally. Do not substitute an older model count or the later dashboard's population.
- **Comparison and metric:** benchmark capability/accuracy versus consistency, robustness, predictability, and safety measurements. This is not a randomized comparison of business deployment outcomes.
- **Reported result / uncertainty:** the abstract reports limited reliability gains alongside capability gains. No pooled effect size, interval, or uncertainty estimate was retained; none is reconstructed.
- **Limits and counterevidence:** benchmark and harness choices constrain transfer. Capability gains are real within the reported evaluation; particular constrained workflows may still be valuable. The dynamic dashboard mentions evaluation corrections, so its current numbers cannot be mixed with the pinned abstract.
- **Safe draft wording:** “In this evaluation, gains in task accuracy did not establish comparable gains across operational reliability measures.”
- **Do not claim / next check:** not “agents cannot work reliably.” G01 must recover the exact v3 benchmark/method/results locators; G05 must reconcile any dashboard figures before use.

### AIH-A02 — Time horizon is a probability-conditioned task-difficulty measure

- **Sources / family:** [S-A02](source-notes.md#s-a02), [S-A03](source-notes.md#s-a03); METR time-horizon methodology, distinct from its developer-productivity experiments.
- **Population, task, model, period:** software-task evaluations with human expert completion-time estimates; model list, sample size, and current measurement coverage are not retained. The live page is not a pinned dataset snapshot.
- **Comparison and metric:** fitted success probability versus human task duration. The 50% and 80% horizons are probability thresholds, not accuracy gains or time spent unattended by an agent.
- **Reported result / uncertainty:** this entry admits the definition only. Model-specific horizons, doubling times, fitted intervals, and frontier rankings are not admitted.
- **Limits and counterevidence:** human timing, task sampling, grading, and curve assumptions matter. Increasing capability remains relevant; translating it into net labor savings needs separate supervision measurements.
- **Safe draft wording:** “A task horizon conditions on success probability and uses human task difficulty; it does not by itself measure unattended operation or labor saved.”
- **Do not claim / next check:** not “a four-hour horizon means four hours of dependable automation.” G05 is required before any model-specific number or extrapolation.

### AIH-A03 — Our autonomy and supervision effect

- **Source:** [our agent protocol](agent-experiment-protocol.md), an authored design rather than literature evidence.
- **Population / comparison:** proposed bounded workflows; `human_checkpoint - single` is the primary supervision contrast. Runtime/model binding and independent fixture review are pending.
- **Metric, result, uncertainty:** intended verified completion, total cost, and human effort. No empirical effect, interval, or population reliability estimate exists. The synthetic development fixtures are not model trials.
- **Countercase / falsifier:** repeatable lower total effort at an acceptable success rate would weaken the skeptical interpretation.
- **Safe draft wording:** “Our proposed test counts intervention and verification effort alongside completed tasks.” Describe the protocol as proposed; results remain absent.

## Multi-agent systems

### AIH-M01 — Collaboration depends on the task and architecture

- **Sources / family:** [S-M01](source-notes.md#s-m01); use the pinned v3 paper. [S-M02](source-notes.md#s-m02) explains an earlier version of the same research.
- **Population, task, model, period:** retained revised-abstract metadata describes 260 configurations, six benchmarks, five architectures, and three model families. Exact model snapshots, evaluation dates, repetitions, and budget normalization need the full text.
- **Comparison and metric:** multi-agent versus single-agent performance under the study's stated resource/tool controls. Candidate abstract values span +80.8% on decomposable financial reasoning to -70.0% on sequential planning; they are task-specific **relative changes**, not percentage-point changes or a pooled treatment effect.
- **Reported uncertainty:** no task-level interval or full denominator was retained. Both numerical endpoints stay on hold; do not average them or infer a significance test.
- **Limits and counterevidence:** the positive endpoint is an essential countercase. Configuration selection, task decomposability, verifier design, and actual resource use can change the comparison.
- **Safe draft wording:** “The study reports benefits on some decomposable tasks and losses on others; collaboration's value depends on the tested architecture and task.”
- **Do not claim / next check:** neither “swarms always help” nor “multi-agent systems are universally worse.” G02 must align the abstract, tables, budget definitions, and code before numerical use.

### AIH-M02 — Architecture prediction is a different outcome from task success

- **Source / setting:** [S-M01](source-notes.md#s-m01), same configurations and evidence family as AIH-M01.
- **Metric and candidate result:** the retained abstract reports 87% selection of the best-performing architecture on held-out configurations. The target is **architecture choice**, not an agent's probability of completing arbitrary work.
- **Uncertainty / gaps:** held-out sample count, split construction, selection ties, interval, and whether this is nested validation are not retained. Article use is on hold.
- **Limits and countercase:** predictive architecture selection could be useful, but its validation set is not a production workflow population.
- **Safe draft wording:** “Choosing the architecture is itself an evaluation problem.”
- **Do not claim / next check:** not “agents are 87% reliable.” G02 must establish the exact denominator and held-out protocol.

### AIH-M03 — Align source versions before comparing results

- **Sources / setting:** [S-M01](source-notes.md#s-m01), [S-M02](source-notes.md#s-m02), and [S-M03](source-notes.md#s-m03) are one evolving study, not three replications.
- **Version difference retained:** the January 2026 author blog describes 180 configurations/four benchmarks; later v3 abstract metadata describes 260/six. A later code README also reports analysis-script corrections. Exact release/tag commits and a reproduction have not been inspected locally.
- **Result / uncertainty:** these are provenance differences, not new effect estimates. Do not copy the earlier blog's performance or regression figures into a table labeled v3.
- **Limits / countercase:** revisions and corrections can improve a study. Their existence does not establish that its substantive conclusions are wrong.
- **Safe draft wording:** keep this as an editorial gate until aligned. G02 owns paper/code matching and reconciliation of superseded figures.

### AIH-M04 — Our incremental value of collaboration

- **Source / population:** [our agent protocol](agent-experiment-protocol.md); no real trials yet.
- **Comparison:** `multi - self_review` is primary, with the same declared model, tools, and spending ceiling; actual spend and human effort still need measurement. `multi - single` is secondary because it also changes review structure.
- **Metric, result, uncertainty:** intended verified-success difference and total cost. No measured gain, interval, or scaling curve exists.
- **Countercase / falsifier:** repeatable benefits beyond single-agent review at comparable total resources, especially on parallel tasks, would count against a blanket skeptical claim.
- **Safe draft wording:** “We will test collaboration against a single agent that can review and revise.” Do not describe planned contrasts as observations.

## Coding productivity

### AIH-C01 — Early-2025 tools on familiar maintenance work

- **Sources / family:** [S-C01](source-notes.md#s-c01); the original effect and interval are also repeated in the author update [S-C03](source-notes.md#s-c03). These are not separate replications of that result.
- **Population, task, model, period:** 16 experienced open-source developers, 246 tasks in mature repositories; February–June 2025 frontier tools. Exact model/tool mix, assignment details, and time-measurement protocol are not retained locally.
- **Comparison and result:** randomized AI access versus no AI; reported **completion time increased 19%** in this setting. This is a relative time effect, not a 19-percentage-point accuracy change or a universal productivity effect.
- **Reported uncertainty:** the retained author update repeats a confidence interval from +2% to +39% completion time. The interval level is not explicit in the retained excerpt and must be verified; do not silently label it 95%.
- **Limits and counterevidence:** small developer cluster count, repository familiarity, task mix, and tool vintage limit transfer. AI could help other populations/tasks or later tools. Full-study treatment/measurement details must be checked.
- **Safe draft wording:** “METR's early-2025 maintenance-work experiment found a slowdown in its studied setting.” Hold exact numbers for G03.
- **Do not claim:** not “AI coding tools make developers 19% less productive today.” Do not equate percentage changes in duration and output.

### AIH-C02 — Enterprise field experiments report output gains

- **Source / family:** [S-C02](source-notes.md#s-c02), including its supplement; one pooled field-experiment evidence family.
- **Population, task, model, period:** 4,867 developers across Microsoft, Accenture, and an anonymous Fortune 100 company, in three experiments. Exact study periods, tool/model versions, and harmonized task-output definitions are not retained. Publication in 2026 is not the experiment date.
- **Comparison and candidate result:** randomized access with imperfect adoption; the headline pooled estimate is 26.08% more completed tasks under the paper's estimator. This must not be restated as the unconditional effect of assigning access or as a universal delivery-time reduction.
- **Reported uncertainty:** standard error 10.3 on the percentage-effect scale; this is an SE, not a confidence interval. Exact main-table estimator, weighting, IV/adoption interpretation, and ITT results need reconciliation with the supplement.
- **Limits and counterevidence:** output counts do not by themselves measure total delivered business value or all review/maintenance costs. The result is substantive positive evidence that the article must retain.
- **Safe draft wording:** “Other field experiments report development-output gains, which makes the task, population, and outcome definition central to interpretation.” Exact figures stay on hold for G03.
- **Do not claim:** not “all developers ship software 26% faster,” and not a direct percentage comparison with AIH-C01.

### AIH-C03 — METR's follow-up does not settle the current effect

- **Source / family:** [S-C03](source-notes.md#s-c03), February 24, 2026 update; follow-up began in August 2025 and partly reuses the earlier participant population.
- **Population and metric:** returning and newly recruited developers; task-time estimates. Subgroup sample counts and a normalized effect convention are not retained.
- **Retained finding / uncertainty:** the authors describe participant/task selection and timing problems that make the follow-up an unreliable estimate of the current effect. Raw signed subgroup estimates and intervals appear in the update, but are not admitted here as clean causal effects.
- **Limits and countercase:** authors believe speedups may have improved; that belief and selected raw data do not identify their magnitude. Neither a permanent slowdown claim nor a confident current speedup follows.
- **Safe draft wording:** “METR subsequently warned that selection and measurement issues complicated its follow-up estimates.”
- **Next check:** G03 must capture subgroup definitions, sign/units, intervals, missingness, and the amended design before using follow-up numbers.

### AIH-C04 — Self-report, task speed, and value are different measures

- **Source / setting:** [S-C04](source-notes.md#s-c04), May 11, 2026 survey report; retained summary describes 349 technical workers surveyed in February–April 2026. Sampling and response details need the full report.
- **Comparison and metric:** self-reported AI usage, speed, and value; not randomized measured task completion. No numerical productivity uplift is admitted from the retained material.
- **Uncertainty / limits:** selection, recall, changing task choices, and perceived-versus-measured differences matter. No causal interval was retained. Do not sum occupation subgroups as if exhaustive or mutually exclusive.
- **Countercase:** perceived usefulness can be operationally informative; it remains a separate outcome from causal productivity gains.
- **Safe draft wording:** “Perceived speed, time spent, and value created answer different questions.” G04 must establish survey methods before any estimates are used.

### AIH-C05 — Our coding experiment is not yet an observation

- **Source / population:** [personal coding protocol](coding-experiment-protocol.md), selected through the [access decision](coding-study-decision.md): one confirmed author. Source/tasks, Codex/caps/timing, common editor/runtime, and the [promoted frozen session](coding-session-ready.md) are technically ready, with P1/P2 before P3/P4 and the original schedule unchanged. The participant reports no prior implementation beyond planning, briefs, and source discussion; one authorized generic Codex availability check passed with no observed tools. The unrelated no-AI warm-up is measured and participant-confirmed; the later AI-condition warm-up and per-attempt editor/source/order/assistance attestations remain. Independent review is unconfirmed.
- **Comparison / metric:** proposed randomized access on comparable tasks, counting author/reviewer effort, rework, defects, and noncompletion.
- **Result / uncertainty:** no signed task attestation or task-timing record is saved at the drafting checkpoint, and measured coding-task observations remain zero; there is no measured effect or interval. The generic readiness check establishes availability only, with no returned model ID or monetary cost exposed. Building the apparatus or completing unrelated practice does not establish coding productivity.
- **Countercase / falsifier:** lower total delivery effort with maintained quality would weaken the skeptical claim. A personal case study must remain labeled personal and exploratory.
- **Safe draft wording:** “Our proposed personal case study records implementation, author verification, and correction effort.” It remains exploratory, with automated checks plus author assessment planned. It supplies neither a population effect nor independent reviewer-time evidence.

## Trading signals and temporal validity

### AIH-F01 — Historical forecast evaluation needs a lookahead audit

- **Source / family:** [S-F01](source-notes.md#s-f01), v2 revised June 12, 2026. The retained v2 abstract begins with date-only firm/date recall queries to estimate Lookahead Propensity; do not replace this with the earlier version's description without checking.
- **Population, task, model, period:** financial forecasting applications include headline/stock-return and earnings-call/capital-expenditure tasks in earlier retained summaries. Exact samples, model snapshots, horizons, and version-specific results require the v2 paper.
- **Metric and result admitted:** a proposed diagnostic for whether forecasts benefit from internalized realized-outcome information. No strategy-return effect, Sharpe ratio, or quantified contamination correction is admitted.
- **Uncertainty / limits:** diagnostic assumptions, identification, and regime comparisons need review; a proxy is not direct inspection of training data. This does not prove every backtest is contaminated or every language-model signal is useless.
- **Countercase:** a genuinely prospective frozen signal could add useful information. That hypothesis remains open.
- **Safe draft wording:** “Historical LLM forecasting needs an audit of information potentially embedded in the model as well as the supplied prompt.” G06 owns exact v2 methods/results.

### AIH-F02 — Vintage and release-time errors change the information set

- **Source / setting:** [S-F02](source-notes.md#s-f02), Federal Reserve staff working paper FEDS 2025-044, June 2025. It examines macroeconomic recall and information availability, not our earnings strategy.
- **Metric / retained result:** recall of values, vintages, and release dates; the source describes mixing revised/initial data and information from different reference periods. No numerical trading edge or portfolio outcome is retained.
- **Uncertainty / limits:** models, series coverage, exact dates, and error rates must be recovered. A staff working paper is not an institutional investment recommendation, and its macro-task findings do not quantify contamination in our signal.
- **Countercase:** task-specific extraction with auditable as-of inputs may be useful; this study alone does not establish its performance.
- **Safe draft wording:** “Macroeconomic recall research illustrates why release timing and data vintages must be audited.” G06 is required before a model-specific/error-rate claim.

### AIH-F03 — Prospective predictive value and economic value remain unmeasured

- **Source / contract:** [trading protocol](trading-experiment-protocol.md); fixed-cohort earnings-release design with a five-session market-relative target and separate paper-cost assumptions. Providers, cohort, permissions, and trusted receipts remain unbound.
- **Comparison / metrics:** planned paired Brier loss against dictionary sentiment, momentum, and no-signal; separate long-only event-payoff and coverage sensitivities. SPY-relative return is not a factor-adjusted alpha estimate.
- **Result / uncertainty:** no empirical forecasts, returns, effect sizes, intervals, or durable-alpha evidence. Local receipt signatures from a test CA do not change that state.
- **Countercase / falsifier:** incremental prospective accuracy and economical results after realistic costs would support a useful signal; the study must retain adverse and missing outcomes too.
- **Safe draft wording:** “The proposed experiment records predictions before outcomes and separates forecasting quality from trading economics.” Do not report the synthetic demo as a finding.

### AIH-F04 — Software verification is a different evidence category

- **Sources:** [agent validation](experiments/agent-study/VALIDATION.md), [trading validation](experiments/trading-study/VALIDATION.md), and [offline setup](experiments/trading-study/OFFLINE-SETUP.md).
- **Population / metric:** deterministic checks and explicitly synthetic fixtures; pass/fail evidence about selected software contracts, not a sample of real model or market behavior.
- **Result / uncertainty:** no inference about agent reliability, developer productivity, or trading alpha is licensed. Test counts are not research sample sizes; additional edge cases and independent reviews remain relevant.
- **Safe draft wording:** “We have checked the offline apparatus; empirical model and market results are still pending.”

## What can be drafted now

- Agents: distinguish capability thresholds from unattended reliability and net labor savings.
- Multi-agent systems: describe task/architecture dependence without a pooled “swarm effect.”
- Coding: present positive and negative settings together; explain different outcomes and the follow-up's limitations.
- Trading: explain information-set risks and the proposed prospective test without claiming a strategy result.

The [outline](article-outline.md) uses these narrow statements. No cross-study leaderboard, pooled uplift number, current frontier ranking, or synthetic-performance chart is justified by this inventory.

## Stop conditions

- Do not admit a numerical headline without its version, population, unit, estimator/denominator, uncertainty, and primary locator.
- Do not mix revised papers with earlier blog numbers, or count derivative sources as independent corroboration.
- Do not infer a current universal effect from a dated, selected task population.
- Do not turn design thresholds, scenario costs, or software tests into observed performance.
- Do not publish the article as independently verified empirical research while original experiments and source admission remain incomplete.

## Open Questions

1. Which primary snapshots and exact locators support the held numerical claims? See G01–G06.
2. Can each coding attempt satisfy the frozen warm-up and editor/source/order/assistance controls, and can independent reviewer access be obtained? Technical readiness is verified; no coding observations exist.
3. Will a later authorized workflow permit live model/data trials, and on what independently auditable terms? The single generic coding availability exception is complete; further provider calls remain unauthorized and other preparation stays offline.
4. Is the first article a literature synthesis with a proposed experiment appendix, or a later empirical report? The current evidence supports the former draft posture.

## Next Actions

1. Use the claim-linked outline to draft a literature-led article with numbers held until admission.
2. Reconcile the numerical/source-version backlog when primary copies are available within the allowed workflow; preserve the source and locator rather than relying on a conversation summary.
3. Hand the completed source review to QuantSmith's `research_analyst` role for updating the existing experiment plans, and to `backtest_review` before any eventual production-promotion decision. The latter is not completed by this literature matrix.
