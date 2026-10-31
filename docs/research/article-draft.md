# AI’s Missing Denominator

*What would establish the value of autonomous agents, multi-agent systems, coding assistants, and AI trading signals?*

> **Working draft — not ready for publication.** Written from the retained [evidence inventory](evidence-matrix.md). Primary-text verification remains open; numerical study effects are withheld. Citations identify the sources to check, not newly verified full texts. Proposed experiments have produced no original performance findings. Paragraph comments support the separate [draft review record](article-draft-review.md).

<!-- D01 | EDITORIAL -->
A demonstration has an appealing numerator: a completed report, a working patch, a plausible forecast. The denominator is harder to see. How many attempts failed? How much supervision and checking did the output require? What resources did the comparison receive? Could the system have known the answer through information that would have been unavailable at the decision date? These questions determine what a successful example establishes.

<!-- D02 | EDITORIAL -->
For this article, overhype means asking a result to support a larger claim than its evaluation can carry. That definition leaves room for substantial progress and useful applications. It also requires a precise proposition. Completing a difficult task, reducing delivery effort, and producing a profitable decision are different achievements. Evidence for one can motivate investigation of another without establishing it.

<!-- D03 | EDITORIAL -->
The questions here concern four possibilities: agents owning workflows, multiple agents improving performance, coding assistants raising productivity, and language models producing useful trading signals. These are evaluation questions, not a measured account of what every vendor or researcher promises. Each needs its own outcome, comparison, resource boundary, and information set. There is no single denominator that turns them into a technology ranking.

## Autonomous agents: who owns the checking?

<!-- D04 | AIH-A02 | S-A02 S-A03 -->
Here, an agent means a model-driven process that chooses actions and tool calls across multiple steps; a multi-agent system coordinates several such processes. An agent’s task-completion horizon is easy to read as a duration of dependable unattended work. METR’s methodology gives it a more specific meaning: a success-probability threshold applied to tasks whose difficulty is represented by human completion time. Human task duration supplies the difficulty scale. It does not tell us how long the model runs, how much supervision a deployment needs, or how much labor it saves. [METR methodology](https://metr.org/time-horizons/), [limitations note](https://metr.org/notes/2026-01-22-time-horizon-limitations/).

<!-- D05 | AIH-A02 | AUTHOR-INTERPRETATION -->
That distinction preserves the measurement’s value. Solving harder tasks at a specified success threshold would be a capability improvement. The additional deployment question is whether the resulting operating policy is worthwhile. A workflow with a cheap, reliable acceptance check can tolerate a different pattern of failures from one whose output requires lengthy expert investigation. A horizon alone does not choose between those settings.

<!-- D06 | AIH-A01 | S-A01 -->
The reliability literature provides another useful separation. *Towards a Science of AI Agent Reliability* examines consistency, robustness, predictability, and safety alongside capability. Its reported evaluation describes limited reliability gains alongside capability gains. That is a finding about its benchmarks and configurations, not a randomized estimate of business outcomes. It challenges the inference that improved task accuracy establishes operational dependability. [Reliability study, v3](https://arxiv.org/abs/2602.16666v3).

<!-- D07 | AIH-A01 AIH-A03 | AUTHOR-INTERPRETATION -->
For a workflow owner, the accounting extends beyond the final answer. An operating policy must account for error detection, retry decisions, requests for missing context, and verification of repairs. When a human performs that work, its time belongs in the labor accounting. If work moves from visible implementation into less visible checking, the process may still be valuable, but its labor savings remain a separate empirical question. A successful output does not reveal that accounting by itself.

<!-- D08 | AIH-A03 | PROPOSED-METHOD -->
Our proposed experiment treats supervision as a condition to measure. Two conditions would use the same base agent policy, with a predefined human checkpoint added to one. Document reconciliation, calculation reproduction, and sourced synthesis would share task material, tools, logging, and acceptance rules. The comparison would retain intervention time, final verification, retries, failures, and consumed resources. No empirical effect from this experiment is available yet. [Agent protocol](agent-experiment-protocol.md).

<!-- D09 | AIH-A03 | PROPOSED-METHOD -->
Cost per verified completion would need the costs of failed attempts as well as successful ones. A cheaper request is not necessarily a cheaper accepted result. Nor would a common spending ceiling guarantee equal actual spending. The protocol therefore calls for actual usage and charges where available, separate human-effort accounting, and explicit unknowns. A budget is a constraint on an experiment, not an observed cost estimate.

<!-- D10 | AIH-A01 AIH-A03 | AUTHOR-INTERPRETATION -->
The positive case deserves a fair test: bounded tasks with clear inputs and economical verification could make autonomy useful. The skeptical case is that apparent delegation may leave substantial ownership with a human. Evidence that would distinguish them is repeated, accepted work at lower total effort under a stated supervision policy. Our current offline software checks establish neither outcome.

## Multi-agent systems: does collaboration earn its cost?

<!-- D11 | AIH-M01 AIH-M04 | AUTHOR-INTERPRETATION -->
Splitting work among agents offers a plausible mechanism for improvement when useful subtasks can be separated. The same design creates questions when later work depends on an earlier correction, intermediate outputs conflict, or aggregation needs another verification pass. Architecture should therefore be evaluated against the dependencies of the task. The number of agents is an incomplete description of the treatment.

<!-- D12 | AIH-M01 | S-M01 -->
The retained findings from *Towards a Science of Scaling Agent Systems* report gains on some decomposable tasks and losses on other tasks. Both directions matter. Favorable results justify investigating where collaboration helps; unfavorable results caution against transferring those gains to arbitrary workflows. The relevant unit of interpretation is a task, architecture, and resource setting, rather than an undifferentiated effect of adding agents. [Scaling study, v3](https://arxiv.org/abs/2512.08296v3).

<!-- D13 | AIH-M02 AIH-M03 | S-M01 -->
Predicting which tested architecture performs best is a selection problem, distinct from completing work successfully. Its accuracy cannot become a general agent-success rate. Quantitative interpretation also requires coherent paper, blog, and code versions; companions sharing observations do not supply independent replications. Candidate numerical results remain withheld pending those checks. [Scaling study](https://arxiv.org/abs/2512.08296v3), [source-version queue](source-notes.md#verification-backlog).

<!-- D14 | AIH-M04 | ILLUSTRATIVE-METHOD -->
Consider an illustrative document workflow. Workers could examine separate documents against a common question and return evidence for synthesis. If a correction in one document changes how another must be interpreted, the work has a dependency that a clean-looking split might obscure. The coordinator would need to resolve the correction before relying on downstream calculations. This example explains why task structure belongs in the comparison; it is not an observation that an architecture succeeds or fails.

<!-- D15 | AIH-M04 | PROPOSED-METHOD -->
Our planned comparison makes a single agent with self-review the primary alternative to orchestration. Comparing only with a single-pass answer would leave an ambiguity: did multiple agents help because of their architecture, or because they supplied more review? The proposed conditions also include an autonomous agent, a human-checkpoint condition, and a fixed workflow. The contrasts separate model self-review, human intervention, and collaboration more explicitly. [Comparison protocol](agent-experiment-protocol.md).

<!-- D16 | AIH-M04 | PROPOSED-METHOD -->
Coordination, repeated inputs, worker outputs, aggregation, and retries would all consume the condition’s resources. The same underlying model, tools, and source material would apply where appropriate, alongside a declared spending limit. Actual expenditure and completion would still need reporting. A nominally equal budget does not establish equal computation, and an architecture that leaves budget unused should not be charged for imaginary requests.

<!-- D17 | AIH-M04 AIH-F04 | CURRENT-STATUS -->
The current harness exercises these policies with scripted responses and synthetic fixtures. It has not run a live model comparison, measured a collaboration effect, or demonstrated parallel latency gains. Its value is preparatory: it makes accounting and failure handling reviewable before collection. Collaboration’s practical case remains a testable proposition, with favorable and unfavorable outcomes both admissible.

## Coding assistants: what counts as productivity?

<!-- D18 | AIH-C01 AIH-C02 AIH-C04 | MEASUREMENT -->
Coding productivity needs an explicit outcome. Time to complete a task, completed tasks over a period, accepted quality, perceived usefulness, and business value answer different questions. A claim about one should not quietly become a claim about the others. The comparison also needs to identify who is coding, what work they are doing, and which tools and access policy they receive.

<!-- D19 | AIH-C01 | S-C01 -->
METR’s early-2025 experiment on experienced developers working in familiar open-source repositories reported a slowdown with AI access in that setting. That result is relevant to a strong claim that assistance necessarily reduces task time. Its population, maintenance work, repository familiarity, and tool period constrain the inference. It does not establish a permanent effect for every developer using later tools. [METR study, v2](https://arxiv.org/abs/2507.09089v2).

<!-- D20 | AIH-C02 | S-C02 -->
The positive evidence belongs beside it. *The Effects of Generative AI on High-Skilled Work* reports development-output gains across enterprise field experiments. Its completed-task outcome addresses development throughput in those settings. That is a different outcome and setting from task-completion time in familiar repositories. Task counts alone do not establish business value or capture every review cost, but the reported gains are substantive positive evidence. The two studies cannot be combined into a universal verdict by subtracting their headline percentages. [Enterprise field experiments](https://doi.org/10.1287/mnsc.2025.00535).

<!-- D21 | AIH-C02 | MEASUREMENT -->
Access and adoption introduce another distinction. Random assignment to receive a tool does not ensure that everyone uses it. An estimate of offering access and an estimate attributed to adoption need not answer the same question. Before interpreting a headline causally, we need its treatment, estimator, outcome definition, and uncertainty. Reconciling the enterprise paper and supplement remains part of our source audit. [Paper supplement](https://pubsonline.informs.org/doi/suppl/10.1287/mnsc.2025.00535/suppl_file/mnsc.2025.00535.sm1.pdf).

<!-- D22 | AIH-C03 | S-C03 -->
Tool changes do not make measurement problems disappear. METR subsequently described selection and timing difficulties that complicated its follow-up estimates. That update limits confident extrapolation in either direction: the earlier slowdown is not a timeless verdict, while selected follow-up observations do not establish a reliable magnitude for the current effect. The amended measurement problem is part of the evidence. [METR follow-up](https://metr.org/blog/2026-02-24-uplift-update/).

<!-- D23 | AIH-C04 | S-C04 -->
Perceived usefulness can still inform decisions. A developer may value assistance with exploration or unfamiliar work even when its effect on a specified task-time measure is uncertain. But a survey of experiences supplies different evidence from randomized access and measured performance. METR’s self-report study belongs in that separate category. It should not be presented as an experimental estimate of delivered productivity. [Self-report study](https://metr.org/blog/2026-05-11-ai-usage-survey/).

<!-- D24 | AIH-C05 | PROPOSED-METHOD -->
Our planned contribution is deliberately modest: a personal case study with one developer, distinct paired tasks, frozen conditions, and predefined acceptance checks. It would record implementation, author verification, and correction effort, while keeping waits and interruptions separate. Acceptance is planned as automated checks plus author assessment; independent reviewer access is unconfirmed. The study can describe this developer’s experience without estimating a population-wide effect. [Personal protocol](coding-experiment-protocol.md).

<!-- D25 | AIH-C05 | CURRENT-STATUS -->
No measured task observations are available yet. Preparing the study and completing an unrelated warm-up do not establish a coding-productivity result. Prior familiarity with planning and task briefs must remain visible, as must failed attempts, time limits, and later defects. A useful report would show those boundaries beside any apparent saving, rather than presenting an accepted patch as a complete account of delivery effort.

## Trading signals: what could the model know?

<!-- D26 | AIH-F01 | AUTHOR-INTERPRETATION -->
A historical date inside a prompt does not establish a model’s historical information set. Restricting the supplied documents addresses one source of leakage; it does not, by itself, demonstrate that the model lacks information about later outcomes. A historical forecasting evaluation therefore needs an audit of potentially internalized information as well as the inputs visibly passed to the model.

<!-- D27 | AIH-F01 | S-F01 -->
*Detecting Lookahead Bias in LLM Forecasts* develops a diagnostic relevant to that problem. Its revised version motivates checking whether forecasting benefits from knowledge of realized outcomes. A diagnostic is not direct inspection of training data, and its identification assumptions need examination. It does not license a conclusion that every language-model strategy is contaminated, or that every historical result is worthless. [Lookahead study, v2](https://arxiv.org/abs/2512.23847v2).

<!-- D28 | AIH-F02 | S-F02 -->
The information boundary also exists in the data itself. The Federal Reserve staff paper *Total Recall?* examines macroeconomic knowledge, including the problem of values, vintages, reference periods, and release availability. A later revision to an economic series is different from the information available at an earlier decision. This research motivates a timing audit; it does not measure contamination or trading performance in our proposed earnings signal. [Federal Reserve staff paper](https://www.federalreserve.gov/econres/feds/total-recall-evaluating-the-macroeconomic-knowledge-of-large-language-models.htm).

<!-- D29 | AIH-F03 | PROPOSED-METHOD -->
Our proposed alternative is prospective collection for a frozen forecasting process. The signal would use archived earnings-release material, with predictions recorded before outcomes. Eligibility, the model and prompt, forecast target, baselines, and execution assumptions would be fixed before collection. Changes would create a new documented version rather than rewrite earlier predictions. This is a proposed test; there is no prospective prediction series to report. [Trading protocol](trading-experiment-protocol.md).

<!-- D30 | AIH-F03 | PROPOSED-METHOD -->
Forecast quality and trading economics would receive separate evaluations. Each forecast would assign a probability that the stock’s five-session total return exceeds SPY’s over identical entry and exit windows. The design uses a next-eligible-session execution proxy rather than an assumed instantaneous trade. Forecasts would be compared with dictionary sentiment, momentum, and a constant no-signal baseline. Brier loss, the squared difference between a probability and the binary outcome, would assess forecast quality. These are proposed measurement choices; an improvement would still need a separate economic evaluation.

<!-- D31 | AIH-F03 | MEASUREMENT -->
For an economic evaluation, execution timing, costs, exposure, and the available opportunity set matter. In the proposed design, assumed transaction costs are sensitivity scenarios, not measured spreads or guaranteed fills. Model fees and human effort need a stated economic scale of their own; a currency charge cannot simply be subtracted from a percentage return. Beating a broad-market comparator also does not, by itself, establish factor-adjusted alpha.

<!-- D32 | AIH-F03 | PROPOSED-METHOD -->
Prospective records need an audit trail worth trusting. A local timestamp is a claim by a local clock. A hash chain can help detect changes against a retained reference, but does not prevent someone controlling the files from rebuilding the chain. The protocol therefore requires independently auditable timing evidence before describing live records as independently verified prospective observations. Local test signatures do not satisfy that requirement. [Timing and record contract](trading-experiment-protocol.md#append-only-record-contract).

<!-- D33 | AIH-F03 | PROPOSED-METHOD -->
Observation count is another incomplete denominator. Events from the same issuer or nearby market dates can be dependent, and holding windows can overlap. The proposed analysis must account for those structures rather than treat every row as a fresh independent trial. A short operational pilot would help diagnose the pipeline and plan subsequent collection; it would not establish durable alpha or guarantee adequate statistical precision.

<!-- D34 | AIH-F03 | PROPOSED-METHOD -->
Coverage needs its own accounting. Comparing only events with valid forecasts from the LLM and its primary dictionary baseline answers a conditional question. It leaves out the operational effect of a system that sometimes fails to produce a forecast. The proposed report would retain every eligible opportunity, attempted cost, failure status, and available outcome. A missing forecast can imply no trade under a declared rule; a missing realized outcome must remain unknown. Those cases cannot both become zero returns, and a favorable score on the successful subset cannot silently describe the entire workflow.

<!-- D35 | AIH-F01 AIH-F02 AIH-F03 | AUTHOR-INTERPRETATION -->
The positive hypothesis remains open: a frozen, auditable process could add incremental information and survive realistic economic assumptions. So does the possibility that simpler rules perform as well at lower operating cost. Distinguishing those possibilities requires forecasts, outcomes, costs, and failures collected under the declared rules. Our synthetic integration checks supply none of those empirical answers.

## What would justify the promise?

<!-- D36 | EDITORIAL -->
The accounting lens is useful because it permits different verdicts. An agent could be helpful in a bounded workflow while requiring too much supervision elsewhere. Collaboration could earn its cost on decomposable work and lose on dependent work. Coding assistance could change outcomes differently across populations. A language model could improve a forecast measure without supporting an economical trading process. Those are possibilities for evidence to distinguish, not conclusions established here.

<!-- D37 | AIH-A03 AIH-M04 AIH-C05 AIH-F03 | METHOD -->
For each application, the demanding question is what would change our view. Repeatable accepted work at lower total effort would support delegation. Better completion at comparable resources beyond single-agent review would support orchestration. Lower delivery effort with maintained acceptance would support coding assistance in the studied setting. Incremental prospective forecast quality, followed by defensible economics, would support a trading use case.

<!-- D38 | AIH-F04 | CURRENT-STATUS -->
This draft offers a literature-based interpretation and proposed tests. It is not a systematic review or a report of completed original experiments. Primary-source verification remains unfinished, and quantitative study claims are withheld. Source support, numerical correctness, and the strength of an argument require separate checks; repeated assistant agreement supplies no substitute for them.

<!-- D39 | EDITORIAL -->
A useful result should make its denominator inspectable: the population, outcome, comparison, resources, information set, and failures. That gives the reader a way to decide how far the evidence travels. It also makes a skeptical thesis revisable. The purpose is to identify where a promise has been demonstrated, where it remains plausible, and what evidence would justify the next step.
