# AI's Missing Denominator

Working subtitle: Autonomous Agents, Multi-Agent Swarms, Coding Productivity, and Trading Alpha

Created: 2026-10-26 (America/New_York)

Status: Research scope and editorial plan. Literature reconnaissance has begun; the proposed experiments have not been run. No original empirical findings are claimed here.

## Editorial direction

Central question: How much of AI's headline performance survives verification, human effort, fair compute budgets, and realistic evaluation?

Treat "overhyped" as a hypothesis to investigate. For each topic, specify the claim, comparison, measurements, limitations, and evidence that would change the skeptical interpretation. Preserve positive findings and distinguish study settings rather than forcing a common verdict.

Selected topics, using the original shortlist numbering:

| Original item | Topic | Main question |
| --- | --- | --- |
| 1 | Autonomous agents | Can an agent reliably own a workflow with little supervision? |
| 2 | Multi-agent swarms | Does collaboration outperform a single agent under a fair resource budget? |
| 3 | AI coding productivity | Does faster generation reduce total effort to deliver accepted software? |
| 10 | AI trading signals | Does predictive value survive temporal contamination checks and realistic trading costs? |

## 1. Autonomous agents: Who is doing the supervision?

### Claim and research question

Claim to test: Agents can reliably own entire workflows with little supervision.

Investigate whether successful demonstrations obscure the human effort needed to make autonomous systems dependable. Separate the ability to complete a task sometimes from consistent, economical execution.

### Evidence to examine

- [Towards a Science of AI Agent Reliability](https://arxiv.org/abs/2602.16666): evaluates consistency, robustness, predictability, and safety rather than relying on one success score. Reliability improvements in its evaluated settings lag capability gains.
- [Princeton's reliability dashboard](https://hal.cs.princeton.edu/reliability/): accompanying results and evaluation qualifications. Check the evaluated version and harness corrections before extracting numbers.
- [METR task-completion time horizons](https://metr.org/time-horizons/): distinguishes success probabilities such as 50% and 80%. The horizon describes task difficulty in human completion time, not the duration of unattended agent operation.
- [METR's limitations note](https://metr.org/notes/2026-01-22-time-horizon-limitations/): explains limits to interpretation and to estimating very high reliability.

### Proposed experiment

Compare an autonomous agent, an agent with predefined human checkpoints, and a fixed script or conventional workflow on the same bounded tasks.

Candidate tasks:

- Reproduce a calculation from supplied files and document the inputs.
- Reconcile conflicting figures across documents.
- Prepare a research summary whose factual claims can be verified against a fixed source set.

Define acceptance criteria, tool access, time limits, and resource budgets in advance. Repeat tasks, retain failed attempts, and independently verify outputs. Include modest input perturbations or controlled tool failures to test robustness.

### Measurements and figure

- Verified completion rate and repeated-run consistency.
- Human intervention and verification minutes.
- Total cost, including failed runs, retries, and human effort at a stated hourly rate.
- Completion-time variability and consequential errors.
- Cost per verified completion: total cost across all attempts divided by accepted completions; report it as undefined if there are none.

Main figure: Cost per verified completion against required human supervision, with task complexity distinguished.

### Evidence that would weaken the skeptical case

Agents consistently complete unfamiliar workflows with little intervention and lower total cost than the alternatives.

### Scope limits

Keep this section about workflow ownership. Coding assistance belongs in section 3. A bounded pilot cannot establish reliability across arbitrary real-world tasks; report uncertainty and account for repeated observations of the same task.

## 2. Multi-agent swarms: Does collaboration pay for itself?

### Claim and research question

Claim to test: Adding specialized agents consistently improves performance over one capable agent.

Investigate whether apparent gains come from collaboration, additional compute, different tools, or a stronger verification step. Distinguish task decomposition from simply giving a model several opportunities to answer.

### Evidence to examine

- [Towards a Science of Scaling Agent Systems](https://arxiv.org/abs/2512.08296): studies multiple architectures with standardized tools and compute. Its results indicate that the value of coordination depends on task structure and model capability; collaboration can help or hurt.
- [Google Research's explanation](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/): useful framing of parallelizable tasks, sequential planning, coordination overhead, and error propagation.
- [Accompanying code and release notes](https://github.com/ybkim95/agent-scaling/): inspect version changes and analysis corrections before attempting reproduction. Use results from a clearly identified paper and code version rather than mixing releases.

### Proposed experiment

Compare these conditions on the same tasks:

1. One capable agent.
2. One agent with additional attempts or self-review.
3. Independent agents whose outputs are aggregated.
4. An orchestrator that assigns subtasks and verifies the final output.

Use the same underlying model, tools, source material, and total token or dollar budget. Include orchestration and aggregation in the budget. Report elapsed latency separately because parallel execution changes wall-clock time. If feasible, include a stronger single model at the same total spend as a practical alternative.

Separate task families:

- Parallelizable: independent document analyses followed by a synthesis.
- Sequential: a chain of dependent transformations or planning steps.
- Shared evidence: agents must resolve conflicting interpretations of the same material.

Repeat tasks and score final outputs using predefined criteria. Keep the final scoring process common across conditions; measure each architecture's internal verification as part of that architecture.

### Measurements and figure

- Verified final accuracy or completion rate.
- Total tokens, cost, and elapsed latency.
- Orchestration and communication overhead.
- Redundant work, contradictory outputs, and errors propagated into the final answer.
- Human effort needed to resolve disagreements.

Main figure: Verified performance versus total spend, with separate curves for single-agent and multi-agent approaches and separate panels for parallel and sequential tasks.

### Evidence that would weaken the skeptical case

Collaboration produces repeatable gains at equal total spend, beyond the gains obtainable from single-agent retries or stronger verification, particularly on naturally decomposable tasks.

### Scope limits

Avoid a universal "more agents are worse" conclusion. Document architecture, prompts, model version, and budgets. Distinguish this architectural comparison from section 1's question about supervision and workflow reliability.

## 3. AI coding productivity: Count the review, too

### Claim and research question

Claim to test: Faster code generation translates directly into large improvements in software productivity.

Investigate total effort to deliver accepted changes, including implementation, review, debugging, correction, and rework. Examine differences by task type, developer experience, and repository familiarity.

### Evidence to examine

- [The Effects of Generative AI on High-Skilled Work](https://doi.org/10.1287/mnsc.2025.00535): three field experiments involving 4,867 developers estimate approximately 26% more completed tasks among developers using the tool. Examine adoption, estimands, uncertainty, and outcome definitions before interpreting the headline estimate.
- [METR's early-2025 experienced-developer study](https://arxiv.org/abs/2507.09089): 16 experienced open-source maintainers completed 246 tasks; AI access increased completion time by 19% in that setting.
- [METR's February 2026 update](https://metr.org/blog/2026-02-24-uplift-update/): selection and time-measurement problems make the follow-up estimates unreliable; the original result is not a current universal verdict.
- [METR's May 2026 survey](https://metr.org/blog/2026-05-11-ai-usage-survey/): self-reported value and speed are distinct constructs. Keep survey evidence separate from randomized measurements.

Do not average effects measured on completed-task output and task-completion time, or treat different populations and tools as interchangeable. Record the study period separately from the publication date.

### Proposed experiment

Randomize AI access across comparable development tasks, balancing developer experience, AI familiarity, and repository familiarity. Avoid asking a participant to solve the same task twice. Include maintenance work alongside bounded implementation tasks.

Specify acceptance checks in advance and use reviewers unaware of the assignment where practical. Track author and reviewer time separately. Retain abandoned tasks, timeouts, and failures rather than analyzing successful tasks alone.

### Measurements and figure

- Total author and reviewer effort to accepted completion.
- Calendar time to acceptance, reported separately from labor time.
- Defects, rework, and noncompletion.
- Perceived time savings compared with observed outcomes.
- Differences across task types and developer experience.

Main figure: Implementation, review, and correction time by condition, alongside completion rates. Do not make incomplete tasks disappear from time comparisons.

### Evidence that would weaken the skeptical case

AI reduces total effort while maintaining quality, including on difficult maintenance tasks, with benefits that persist after review and correction.

### Scope limits

A personal experiment can illustrate mechanisms. Broad causal claims require multiple participants and a design with adequate power. Account for repeated tasks within developers when estimating uncertainty. Neither code volume nor tool usage alone establishes productivity.

## 10. AI trading signals: Did the model already know the answer?

### Claim and research question

Claim to test: Strong LLM backtests demonstrate a durable predictive edge.

Investigate whether measured forecasting ability survives model-training contamination, realistic information availability, conventional backtest controls, and execution costs.

### Evidence to examine

- [Detecting Lookahead Bias in LLM Forecasts](https://arxiv.org/abs/2512.23847): develops a lookahead-contamination test and applies it to financial forecasting tasks. Read the revised version before implementing its procedure.
- [Federal Reserve: Total Recall?](https://www.federalreserve.gov/econres/feds/total-recall-evaluating-the-macroeconomic-knowledge-of-large-language-models.htm): documents problems involving data vintages and information that was not yet available at the simulated forecast date.

These sources establish evaluation risks; they do not show that every LLM trading signal is invalid. A historical prompt asking a contemporary model to act as if it were in a prior year does not establish a clean historical test.

### Proposed experiment

Start with one narrowly defined signal, such as a score extracted from earnings announcements, and one predefined prediction horizon.

1. Freeze the model version where possible, prompt, signal mapping, universe rules, horizon, and trading rule. Log model updates if a version cannot be held fixed.
2. Use timestamped source documents, point-in-time inputs, and historically valid universe membership.
3. Audit possible training exposure, data revisions, survivorship bias, overlapping outcomes, and tuning on the test period.
4. Compare against simple text-sentiment and conventional quantitative baselines using the same available information.
5. Record predictions prospectively before outcomes occur; preserve inputs, outputs, timestamps, and every tested variant.
6. Evaluate execution from the first realistically available price after input collection and processing, including transaction costs and turnover.

Treat pre-cutoff versus post-cutoff historical comparisons as diagnostics, not proof of a clean temporal boundary. Post-training, retrieval, and uncertain cutoff disclosures may introduce additional information.

### Measurements and figure

- Incremental predictive value over predefined baselines.
- Exposure-adjusted returns and uncertainty.
- Turnover, drawdown, and sensitivity to transaction costs.
- Stability across time periods and sensitivity to multiple testing.
- Historical versus prospective performance.

Main figure: Historical and prospective performance, before and after costs, with uncertainty. Clearly distinguish the sample lengths and market regimes; do not imply that differences alone identify contamination.

### Evidence that would weaken the skeptical case

A frozen signal adds predictive value prospectively and remains economically useful after realistic costs, with sufficient observations to assess uncertainty.

### Scope limits

A short prospective pilot verifies the process, not durable alpha. Keep original results separate from published research, and do not imply a profitable strategy before testing one.

## Proposed article structure

Target: approximately 2,500–3,000 words, plus sources and a concise methods appendix. This expands the original three-topic outline to include multi-agent systems.

| Part | Purpose | Approximate words |
| --- | --- | ---: |
| Opening | Introduce headline performance versus verified value | 200 |
| Autonomous agents | Reliability, supervision, and workflow ownership | 500 |
| Multi-agent swarms | Coordination benefits under equal resource budgets | 500 |
| Coding productivity | Conflicting evidence and total delivery effort | 550 |
| Trading alpha | Temporal contamination and economic value | 650 |
| Closing | State which claims survive and what remains unproven | 200 |

### Possible opening

> An agent finishes a research task. A team of agents produces a polished report. A coding assistant delivers a working patch. A language model generates a profitable historical trading signal. Each result looks impressive. Each leaves a question unanswered: how much supervision did the agent require, did the team beat a single agent at the same cost, how much review did the patch need, and what information did the trading model already possess?

### Editorial guardrails

- Separate observed findings, interpretations, hypotheses, and proposed experiments.
- Include credible positive evidence and explain differences in study settings.
- Cite primary sources near factual claims; verify versions and results before publication.
- Predefine baselines and evaluation rules before running original experiments.
- Report failures, total resource use, uncertainty, and material limitations.
- Avoid interpreting a small demonstration as a broad deployment result.
- Use actual results to determine whether each claim deserves the "overhyped" label.

## Execution plan

### Priority 1: shared agent experiment protocol

**The next priority is to turn the agent and multi-agent sections into one runnable experiment protocol.** They can share tasks, logging, and evaluation, making them the most practical source of original results for the write-up. Keep their research questions distinct: workflow ownership and supervision in section 1, and the incremental value of collaboration in section 2.

Implementation update: [Protocol v0.1.0](agent-experiment-protocol.md) and the [offline development package](experiments/agent-study/README.md) are prepared. They specify the comparisons and include six synthetic fixtures, separate evaluator keys, condition prompts, a seeded 90-attempt pilot schedule, participant-packet export, answer/run validation, and an unbound runtime template. The two primary contrasts are human checkpoint versus single agent, and multi-agent orchestration versus continuing-context single-agent self-review. The original four conditions are retained, with self-review added as a fifth condition to separate collaboration from extra review.

The synthetic fixtures are for setup validation only. No model pilot has been run. Live collection still requires a bound model/pricing manifest, instrumented fixed and model executors, verified participant isolation, and independent fixture review. The proposed nominal model/tool ceiling is USD 36 for the 72 model attempts in the development pilot, excluding human and infrastructure costs; this is a design limit, not observed spend or a price quote.

Before running anything, define:

- **Tasks:** Document reconciliation, calculation reproduction, and sourced research synthesis. Include both parallelizable and sequential work.
- **Conditions:** Fixed workflow, single autonomous agent, single agent with review, and orchestrated multi-agent system.
- **Controls:** Same underlying model, tools, source material, and total spending limit where applicable. Count orchestration, aggregation, and retries within the budget; report human effort separately and include it in total-cost comparisons.
- **Scoring:** Acceptance criteria defined in advance and checked independently.
- **Logs:** Every attempt, failure, retry, token cost, elapsed time, and human intervention.

Start with a small pilot to find problems in the setup. Use its variability to choose the main experiment's size; do not treat pilot results as evidence of broad reliability.

### Priorities and completion criteria

| Priority | Deliverable | Completion criterion |
| --- | --- | --- |
| **1. Agent experiment protocol** | [Protocol](agent-experiment-protocol.md), [task fixtures, prompts, and offline utilities](experiments/agent-study/README.md) prepared | Offline setup is reproducible; live execution must satisfy the protocol's runtime-binding and independent-review checklist |
| **2. Trading protocol and prospective log** | Frozen signal, baselines, timestamps, execution assumptions | Predictions are recorded before outcomes occur |
| **3. Evidence matrix** | Primary-source findings for all four topics | Every numerical claim has a study setting, outcome definition, uncertainty, and limitation |
| **4. Coding experiment decision** | Participant-based study or explicitly narrow personal case study | Scope matches the participants and measurement access available |
| **5. Main experiments** | Results, failure analysis, costs, and uncertainty | Predefined comparisons are complete, including failed attempts |
| **6. Article and figures** | Draft, reproducibility appendix, source checks | Conclusions follow the evidence and distinguish original results from published findings |

**Start the trading log early**, because prospective observations take calendar time. It can continue while the agent experiments run and the literature sections are drafted. A short observation period should remain a pilot rather than support a durable-alpha claim.

For coding, resolve participant access early. Without it, a careful literature synthesis plus a labeled personal experiment is a defensible contribution.

The immediate concrete deliverables are **an experiment specification and evidence matrix**. The experiment specification and offline preparation package are now saved; the evidence matrix remains pending under priority 3. Before live execution, complete the runtime-binding checklist in the protocol. The evidence matrix should record the claim, study period, model/tool version, sample, comparison, outcome, result, uncertainty, and limitations for each source.

Draft the literature-backed article with clear placeholders for original results. Replace those placeholders only with verified results, build the planned figures, and recheck sources immediately before publication. Publication need not wait for a claim of durable trading alpha.

### Progress checklist

- [x] Prepare a versioned shared agent and multi-agent protocol with explicit comparisons, budgets, scoring, and failure rules.
- [x] Prepare six synthetic development fixtures, separate evaluator keys, prompts, scheduling/export utilities, and an offline answer/run validator.
- [ ] Bind the model/prices/tools, implement and archive the executors, verify participant isolation, obtain independent fixture review, and freeze the live session manifest.
- [ ] Verify complete attempt logging and independent scoring in the actual execution runtime.
- [ ] Run the setup pilot and use its variability to plan the main experiment.
- [ ] Freeze the trading protocol and start the prospective prediction log.
- [ ] Complete the primary-source evidence matrix for all four topics.
- [ ] Resolve participant access and scope the coding experiment accordingly.
- [ ] Complete the main experiments, retaining failures and reporting uncertainty.
- [ ] Finish the article, figures, reproducibility appendix, and source checks.

## Deferred ideas from the original shortlist

| Original item | Topic | Research angle |
| --- | --- | --- |
| 4 | Reasoning models | Does additional inference-time computation improve correctness enough to justify its cost? |
| 5 | Leaderboard-driven releases | Do public benchmark rankings transfer to fresh, practical tasks? |
| 6 | Retrieval-augmented generation | Do retrieved sources and citations actually support the generated claims? |
| 7 | Large context windows | How does usable understanding differ from maximum accepted input length? |
| 8 | Synthetic data | How do replacement, accumulation, and filtering affect real-data generalization? |
| 9 | LLMs replacing classical ML | When do general-purpose language models outperform strong structured-data baselines? |

## Current state

- Selected: original items 1, 2, 3, and 10.
- Saved: research questions, initial sources, proposed experiments, figures, counterevidence criteria, article outline, prioritized execution plan, completion criteria, progress checklist, [shared experiment protocol](agent-experiment-protocol.md), and [offline development package](experiments/agent-study/README.md).
- Priority 1 status: protocol design and offline preparation are ready for implementation review; model runtime binding and independent review are still required before live collection.
- Next execution deliverables: instrumented executors and a frozen session manifest. Priority 2's trading protocol/log and priority 3's evidence matrix remain pending.
- Pending: detailed evidence extraction, original data collection, live experiments, charts, and article drafting. Software validation is not empirical evidence for the article.
- Publication: this file is under `docs/`, which the current Jekyll configuration excludes from the generated website. It is a repository research brief, not a published post.
