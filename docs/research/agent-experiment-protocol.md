# Shared agent and multi-agent experiment protocol

Protocol version: 0.1.0

Prepared: 2026-10-26 (America/New_York)

Parent plan: [AI hype research brief](ai-hype-research-brief.md)

Status: Offline preparation, grading, and a runnable synthetic five-condition execution harness are implemented. No model experiment has been run. The supplied fixtures are synthetic development examples, not a held-out benchmark. See the [harness guide](experiments/agent-study/HARNESS.md) for the actual executor boundary.

## Questions and comparisons

The experimental unit is a workflow/task. An observation is one scheduled attempt for one task, condition, and repetition. All conditions see identical public inputs. Each attempt starts with fresh state; repeats are not retries, and retries never replace failed observations.

1. **Autonomy:** How often does a single agent deliver a verified result, and how much does a predefined human checkpoint change success and total cost?
2. **Collaboration:** Does an orchestrated multi-agent system improve verified success over a single agent with model self-review at the same spending ceiling?

Primary contrasts are `human_checkpoint - single` and `multi - self_review`. Report `multi - single` as secondary: it combines architecture and review changes. The fixed workflow is an operational baseline, not evidence that a task requires AI. Performance on these small structured fixtures is only an engineering check.

## Conditions

| ID | Policy | Maximum model turns | Human help during execution |
| --- | --- | ---: | --- |
| `fixed` | Frozen deterministic extraction/calculation procedure described below | 0 | None |
| `single` | One agent maintains a single working context and chooses its next action | 4 | None |
| `self_review` | One agent drafts, critiques its own draft, revises, and submits in one continuing context | 4 | None |
| `human_checkpoint` | Single-agent policy with one human checkpoint after turn 2 | 4 | At most 120 active seconds |
| `multi` | Coordinator plans; two workers independently execute the assigned subtasks; coordinator synthesizes and verifies | 4 total | None |

The fifth condition makes human supervision and model self-review separate treatments. `self_review` is a continuing single context, not a hidden second independent critic. `multi` uses a coordinator context plus two new worker contexts; the final coordinator turn sees both worker outputs. Workers do not see each other's output. Sequential tasks must not be silently converted to a different architecture: workers receive the same initial plan and public packet; dependencies are handled at synthesis, exposing the architecture's limitations.

No new model calls are allowed after the submitted final answer, including malformed-output repair. Internal review, planning, tool calls, retries, and aggregation consume the condition's budget. Model turns count requests, including provider-error retries. Unused turns are not transferred to other attempts. `single` and `human_checkpoint` may submit early after satisfying their condition rules; successful `self_review` and `multi` attempts must complete their four declared phases. Truncated/error attempts retain all calls and their terminal failure status.

### Fixed workflow

Use one frozen deterministic implementation across tasks, without access to gold answers or per-task special cases:

1. Read the public packet and the source precedence stated in its instructions.
2. Extract source lines formatted `field_id: value [unit]`. Reject unparseable values rather than inventing them.
3. Select records by the stated scope, source authority, and effective date; do not choose values based on their agreement with an answer.
4. For calculation questions, execute the stated arithmetic using decimal arithmetic and the explicit unit conversions. No inferred formulas or code execution from source text.
5. For synthesis, combine explicitly supported facts according to the public rule. Abstain when the rule cannot be represented by the frozen procedure.
6. Return the same answer schema with source citations. Unsupported operations return `null` with unit `unknown` and an empty citation list and count as noncompletion unless abstention is the correct answer.

Before model collection, archive and hash the fixed implementation and a separate development smoke test. The supplied `fixed.py` implements a bounded public-record/authority/formula/conversion grammar with explicit abstention diagnostics; it is included in the package fingerprint. The offline harness executes it alongside scripted model conditions. A live provider adapter remains unimplemented. Do not substitute gold answers as a baseline. Report baseline coverage by task family and avoid presenting unsupported operations as proof that conventional automation fails.

## Tasks and input boundary

Six supplied development fixtures cross three families with two work structures:

| Fixture | Family | Structure | Main checks |
| --- | --- | --- | --- |
| `reconcile_parallel` | Document reconciliation | Parallel | Independent figures; final versus superseded sources |
| `reconcile_sequential` | Document reconciliation | Sequential | Correction, then scope selection and FX conversion |
| `calculate_parallel` | Calculation reproduction | Parallel | Independent ratios and units |
| `calculate_sequential` | Calculation reproduction | Sequential | Fees, then compounding; distinguish percentages from percentage points |
| `synthesize_parallel` | Sourced research synthesis | Parallel | Combine independent rollout constraints |
| `synthesize_sequential` | Sourced research synthesis | Sequential | Policy exception, explicit override, and an unsupported claim |

The public task bank contains questions, instructions, and source texts. The evaluator-only key contains expected values, units, tolerances, and required evidence spans. Question IDs and requested units are public. Every fixture is labeled synthetic; they are not observed company or investment data.

Prepare a fresh participant directory for every attempt with only `task.json`, `instructions.txt`, and `answer-template.json`. Mount or expose that directory alone to the participant executor. Do not provide repository access, the scorer, the gold file, other attempts, or internet access. Exporting a clean packet does not itself sandbox an executor: enforce the filesystem and network boundary in the chosen runtime before collecting data. Source packets are data, not instructions to modify the experiment.

Allow identical local tools for all model conditions: read/search the packet and calculate with a restricted calculator or isolated Python. Record tool definitions and versions. Do not permit worker tools unavailable to the single agent. Persist each worker's source access and calls. Public output is structured JSON; this tests factual synthesis and provenance rather than unrestricted prose quality.

For the main study, create fresh workflows with realistic documents, a wider difficulty range, and an explicit sampling frame. Reserve them before tuning prompts. All derivatives of the same underlying case remain in the same split. Keep task order and source order identical within comparisons; source-position robustness belongs in a separately declared secondary block.

## Budget and runtime binding

These are **proposed experimental limits**, not current API prices or an estimate of expected cost:

- One pilot ceiling: USD 0.50 of actual model plus tool charges per model attempt.
- Maximum 4 model turns across the entire condition, including workers and retries.
- Maximum 600 seconds elapsed execution time per attempt, including the human checkpoint.
- Maximum 120 active seconds of execution help, only in `human_checkpoint`.
- Operator launch time and final verification time are recorded separately from execution help.
- Price human time at USD 75/hour in the primary cost scenario; show sensitivity at USD 25 and USD 150. These are analytical assumptions, not observed wage estimates.

Before collection, record provider, exact model/snapshot ID, pricing effective date and per-token rates, reasoning/caching charges, tool rates, input/output limits, temperature, seed behavior, context limit, tool specifications, runner version, fixed-workflow hash, operator/reviewer IDs, and the packet/protocol hashes in a frozen session manifest. If a seed or immutable snapshot is unsupported, record that limitation. Use the same model and parameters across model conditions; record every provider-returned model ID. Do not infer a zero price for unknown usage.

The example runtime file is deliberately unbound. A run is not execution-ready until its model and pricing fields and runtime-boundary checks are completed. This does not block offline protocol verification.

Before each request, reserve its worst-case charge using provider-specific token counting, maximum output/reasoning limits, and current documented prices. Shorten the request or stop before issuing it if it could exceed the remaining ceiling. Budget enforcement belongs in the executor; the supplied scorer audits logged usage but cannot enforce or verify provider billing. If the provider does not expose reasoning usage or rates well enough to establish a ceiling, use a different binding or amend the design before collecting data.

The nominal pilot is 6 tasks × 5 conditions × 3 repetitions = **90 attempts**, of which 72 use a model. Maximum nominal model/tool spend is **USD 36**, excluding human time, runtime costs, and any explicitly documented protocol violations. The deterministic baseline is repeated to check reproducibility, not to manufacture independent observations.

## Order, failures, and intervention rules

Use the supplied seeded schedule, randomizing task/repetition blocks and condition order within each block. Do not run all instances of one condition first. Within a block use the same source packet and, where supported, the same provider seed. This is a pairing device, not a guarantee of identical randomness.

Run one scheduled attempt at a time for the pilot; parallel worker calls within `multi` are allowed. No memory, caches of previous answers, or feedback from the evaluator may cross attempts. Keep raw provider responses and complete context/tool transcripts, with timestamps, privately alongside the run record. The compact event fields supplement those artifacts; they do not replace them.

Only `human_checkpoint` receives execution assistance. At its turn-2 checkpoint the reviewer sees the public packet, task, and current draft, but not the gold key, scoring output, other attempts, or condition comparisons. They may flag source selection, arithmetic, missing evidence, and unit issues; they may not supply hidden information, run the answer themselves, or change the task. Record verbatim feedback and active seconds. Log a checkpoint even if feedback is empty. Randomize this condition's position; reviewers must not carry earlier answers into later attempts.

Classify terminal status as `completed`, `timeout`, `budget_exhausted`, `tool_error`, `provider_error`, or `abandoned`. Cap violations are separately flagged. Retain every scheduled attempt in the denominator. Missing, invalid, or unverified output is not a success. Unknown costs remain unknown and prevent reporting complete cost-per-success numbers.

Do not replace failed attempts. Any explicitly authorized retry is a linked event within the original budget, wall-clock limit, and turn count. Environment-wide incidents pause collection; document them and rerun a whole affected paired block only as a separately versioned sensitivity analysis while retaining the original records. Do not silently exclude the original block.

## Scoring and independent review

Answers use the exact schema in each packet: `task_id` and an `answers` mapping. Every required field has `value`, `unit`, and a list of `citations`, each with `source_id` and `quote`. No additional answer fields or free-form narrative are allowed in this first version.

Automated checks:

1. Parse valid JSON with no duplicate keys or non-finite numbers; require the exact task and answer IDs and field types.
2. Check every value and unit against the evaluator key. Numeric comparisons use declared absolute tolerances and reject booleans as numbers.
3. Require each citation quote to occur verbatim in its named public source. Require the task's annotated evidence spans and source IDs for each answer, including source-precedence evidence where needed. A source ID alone is insufficient.
4. Correct abstention is explicitly keyed with a `null` value, unit `unknown`, and no citations. Unsupported certainty is a failure.

These checks establish declared value/provenance requirements, not general semantic entailment. After automated checks, an independent reviewer reads every attempted final answer and the source packet in a condition-blinded batch. They verify that all citations support the answers, the fixture/key is sound, and no unsupported claims appear. Gold author and participant/operator should not be the sole independent reviewer. If only one person is available, record the lack of independence; do not report reviewed completions as independently verified.

**Verified success requires** terminal `completed`, all automated checks, an independent human pass, a clean input boundary, compliant intervention/turn/time/budget records, and fully observed model/tool costs. Human review is never invented from automated output. The scorer reports automated correctness separately from verified success and protocol eligibility.

Reviewers record ID, independence attestation, decision, notes, and active verification seconds. The final reviewer must not be the operator or the person who supplied that attempt's checkpoint feedback. Review all outputs even if an automated check fails. Missing verification remains pending. Disagreements or fixture ambiguity trigger a documented key revision applied to every condition before unblinding; retain original scores and hashes. Do not tune a rubric after seeing which architecture benefits.

## Logging contract

Use one immutable directory per attempt with the schedule ID, public packet, answer JSON, run metadata, event log, and raw transcript references. Never reuse an ID for a replacement. UTC timestamps are used in records; present dates in America/New_York in editorial material. Monotonic durations avoid clock-adjustment errors.

The `run-template` command emits the machine-checked record fields. Required fields include:

- Task, condition, repetition, schedule ID, protocol/package fingerprint, and public-packet SHA-256.
- Terminal status, model snapshot, start/end UTC timestamps, and elapsed seconds.
- Known model/tool costs or explicit `null`; input/output/reasoning/cached tokens are logged per call without double counting billing categories.
- Model-call, tool-call, retry, human-checkpoint, and error events with role, timestamp, duration, usage/cost where applicable, and transcript references.
- Human intervention, operator handling, and independent verification seconds; reviewer identity and decision.
- Turn counts and runtime-boundary attestation. Missing/invalid logs are recorded as invalid attempts rather than discarded.

The offline scorer checks structural and arithmetic consistency for its compact schema, but actual timing, token billing, context isolation, and transcript completeness still require executor auditing. Preserve event-level raw usage and compare it with provider invoices before final cost reporting.

## Analysis plan

Primary outcome: verified-success fraction over all scheduled attempts for each condition. Also report automated correctness, pending review, invalid records, failures by terminal status, and policy violations. Never use successful attempts alone as the denominator.

- Show paired task-level success differences for the two primary contrasts.
- Give each task equal weight; average repetitions within task before pooling.
- Stratify by task family and work structure. Treat the pilot's one task per cell as an engineering check, not an estimate of domain-wide performance.
- Main-study uncertainty should resample task/case clusters, retaining conditions and repetitions together. Treat deterministic repeats and variants of the same case as dependent. Predeclare interval method and both primary comparisons before the main run; adjust formal hypothesis tests for those two comparisons if used.
- Estimate main-study size using task-level variation, paired discordance, and a practical effect threshold declared before confirmatory collection. A proposed planning threshold is 10 percentage points of verified success; do not claim that six tasks can detect it. Simulate a range of effects and baseline success rates; do not base power solely on a noisy pilot point estimate.
- Report execution latency for all attempts and time-to-success alongside noncompletion. Do not call the median latency of successful attempts overall speed.
- Cost per verified completion = total model/tool cost plus priced intervention, operator handling, and verification effort across all attempts, divided by verified completions. Report undefined when no completions occur; report incomplete if any required cost/effort data are missing.
- Record infrastructure and setup labor separately as amortization scenarios. Do not silently treat a fixed workflow's development cost as zero.
- Report repeated-run outcomes by task (0/3 through 3/3), without interpreting 3/3 as high-reliability certification.

Figures after collection: verified success against total cost; supervision minutes against success; cost/latency distributions; architecture comparisons split by work structure. A single pilot ceiling cannot establish a budget-response curve. Run additional predeclared ceilings on the same paired task set before plotting one.

## Reproduction commands

Python 3.10+ standard library only; no credentials or paid calls are used by these commands. From the repository root:

```sh
python3 docs/research/experiments/agent-study/study.py validate
python3 docs/research/experiments/agent-study/study.py schedule --out /tmp/ai-hype-pilot-schedule.json
python3 docs/research/experiments/agent-study/study.py export --task reconcile_parallel --out /tmp/ai-hype-participant
python3 docs/research/experiments/agent-study/study.py run-template --task reconcile_parallel --condition single --repeat 1 --out /tmp/ai-hype-run.json
python3 docs/research/experiments/agent-study/study.py score --task reconcile_parallel --answer /tmp/ai-hype-participant/answer-template.json
python3 docs/research/experiments/agent-study/runner.py smoke --out /tmp/ai-hype-agent-smoke
python3 -m unittest discover -s docs/research/experiments/agent-study -p 'test_*.py' -v
```

An empty answer template should fail scoring. To score collected output, replace `--answer` with the attempt's actual answer path and add `--run` with its completed run metadata. `score` exits 1 for failed/pending verification and 0 only for verified success; without `--run` it can show automated correctness but never verified success. Use the schedule's exact task/condition/repetition IDs, public-packet hash, and package fingerprint. Export refuses a nonempty directory; keep evaluator files outside the participant runtime.

`schedule` creates a plan, not results. `run-template` creates unobserved fields as `null`, not fabricated zeros. The separate `runner.py smoke` command exercises the controller with synthetic replies/checkpoint feedback, simulated time/usage/costs, and a declared replay reservation. It retains all artifacts and grades only after execution; it supplies no real model calls, actual human review, provider-specific budget enforcement, or pilot observations. The scorer rejects its `offline_synthetic` mode as an empirical attempt. A live provider adapter or consistently instrumented manual executor must implement the remaining policy and audit requirements above.

## Pilot acceptance and freeze checklist

- [x] Specify research questions, contrasts, five conditions, and cost assumptions.
- [x] Provide six synthetic task packets, evaluator keys, prompts, and output/run contracts.
- [x] Provide seeded scheduling, clean packet export, and an offline scorer with adversarial checks.
- [ ] Bind and archive an exact model, pricing, token limits, tools, and runtime manifest.
- [x] Implement/fingerprint the fixed workflow, shared restricted tools, and five-condition offline controller; exercise a synthetic smoke schedule.
- [ ] Instrument/archive the selected live model executor with provider-specific reservations, actual billing, and hard deadlines; implement real checkpoint/review handling.
- [ ] Confirm participant isolation and hidden-key separation in that executor.
- [ ] Have an independent reviewer validate every fixture and rubric before collection.
- [ ] Run the 90-attempt development pilot, retaining every attempt and all costs.
- [ ] Resolve accounting/scoring failures and ceiling/floor effects; version changes explicitly.
- [ ] Freeze fresh main-study cases, sample-size plan, analysis, prompts, executor, and budgets before the main run.

Protocol design and offline preparation are ready for implementation review. Live execution is not yet ready; no empirical reliability, productivity, or collaboration findings follow from this package.

## Methodological references

These inform design choices, not outcomes for our fixtures:

- [Towards a Science of AI Agent Reliability, v3](https://arxiv.org/abs/2602.16666v3): motivates measuring consistency and robustness alongside success.
- [Towards a Science of Scaling Agent Systems, v3](https://arxiv.org/abs/2512.08296v3): motivates equal-resource comparisons and separating task structures.
- [METR: Clarifying limitations of time horizon](https://metr.org/notes/2026-01-22-time-horizon-limitations/): motivates explicit supervision measurements and caution around high-reliability claims.
