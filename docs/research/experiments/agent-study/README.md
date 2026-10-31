# Agent study development package

Read the [experiment protocol](../../agent-experiment-protocol.md) for hypotheses, conditions, budgets, scoring, analysis, and execution rules. The [parent brief](../../ai-hype-research-brief.md) tracks the overall article.

This package provides six synthetic development fixtures, evaluator keys, condition prompts, an unbound runtime template, seeded scheduling, clean participant export, offline answer/run validation, and a runnable synthetic execution harness for all five conditions. Python 3.10+ standard library only. No provider is called and no empirical model pilot has run. See the [harness guide](HARNESS.md) for execution policies, failure injection, accounting, and limitations.

## Files and access

| File | Purpose | Participant access |
| --- | --- | --- |
| `task-bank.json` | Six synthetic public tasks, questions, and sources | Only the current task, via export |
| `gold.json` | Expected answers, units, tolerances, required evidence spans | Never |
| `prompts.json` | Common and condition-specific instructions | Only assigned policy and common instructions |
| `runtime.example.json` | Fields to bind before live collection | Executor metadata; no evaluator key |
| `study.py` | Offline preparation and evaluator-side checking | Never |
| `runner.py` | Five-condition controller, offline replay backend, artifacts and post-execution grading | Controller only; sends public inputs to backend |
| `fixed.py` | Frozen deterministic baseline with explicit unsupported coverage | Public packet only |
| `tools.py` | Shared packet read/search and bounded Decimal arithmetic | Same tool definitions in every model condition |
| `test_study.py` | Software checks with explicitly synthetic positive controls | Never |
| `test_runner.py`, `test_fixed.py`, `test_tools.py` | Execution-policy, baseline, and restricted-tool checks | Never |

`gold.json` is evaluator-only during execution, not a secret in this repository. Never give a participant the repository checkout. Export to a fresh directory and enforce that directory's isolation in the selected executor. Do not upload runtime credentials, collected transcripts, or real participant data to the public website repository. Local `runs/` and `sessions/` are ignored; the protocol's `docs/` location is excluded from website output, but that does not make tracked files private on GitHub.

## Offline preparation

From the repository root:

```sh
python3 docs/research/experiments/agent-study/study.py validate
python3 -m unittest discover -s docs/research/experiments/agent-study -p 'test_*.py' -v
python3 docs/research/experiments/agent-study/study.py schedule --out /tmp/ai-hype-pilot-schedule.json
python3 docs/research/experiments/agent-study/study.py export --task reconcile_parallel --out /tmp/ai-hype-participant
python3 docs/research/experiments/agent-study/study.py run-template --task reconcile_parallel --condition single --repeat 1 --out /tmp/ai-hype-run.json
python3 docs/research/experiments/agent-study/runner.py smoke --out /tmp/ai-hype-agent-smoke
```

Exports and output files refuse overwrites. Use fresh paths for subsequent checks. A schedule is a plan, not evidence of completed observations. A run template uses `null` for unobserved costs, times, outcomes, and review decisions.

The nominal empirical pilot has 90 attempts: six tasks, five conditions, three repetitions. It contains 72 model attempts and a proposed USD 36 maximum nominal model/tool budget at USD 0.50 each. Human time and infrastructure are additional. The harness smoke executes the same schedule with scripted responses; it does not perform those model attempts. No money has been spent by these utilities.

## Output and run contracts

The participant fills the exported `answer-template.json`. Every requested answer must contain exactly `value`, `unit`, and `citations`. Each citation has exactly `source_id` and `quote`; the quote must occur verbatim in the named source and supply the required evidence. For a conclusion needing several inputs, include each supporting input. Correct abstention requires `null`, `unknown`, and an empty citation list.

The executor fills every observed field in the generated run template. Leave genuinely unknown fields `null`; do not invent a zero. Use `study.digest()` on the parsed answer object for `answer_sha256`. This is canonical-JSON hashing, not the raw file's byte hash. The public task hash uses the same function. The package fingerprint hashes the core data, prompts, runtime template, evaluator, three executor/tool modules, and protocol; session manifests have a separate SHA-256. The offline harness explicitly labels scripted usage/cost/time fields and keeps actual human review/handling fields pending.

Common event fields: `kind`, `at_utc` (UTC ending in `Z`), `elapsed_seconds`, and a nonempty `transcript_ref` pointing to the retained raw record. Events are ordered by request-start timestamp, not response arrival.

| Event kind | Additional required fields |
| --- | --- |
| `model_call` | `role`, `model_snapshot`, `cost_usd`, `input_tokens`, `output_tokens`, `reasoning_tokens`, `cached_tokens` |
| `tool_call` | `cost_usd`; tool name, inputs, outputs, and failures in the referenced raw record |
| `human_checkpoint` | `active_seconds`, verbatim `feedback`, `reviewer_id` |
| `retry` | Nonempty `reason`; the retried request also gets its own billed model/tool event |
| `error` | Error details and affected request in the referenced raw record |

Token counts are nonnegative integers. `input_tokens` includes its cached subset; reasoning counts may overlap billed output depending on the provider. Do not add overlapping usage categories to recompute a bill. Record the provider's billing policy in the frozen session manifest and log each call's actual charge. Sum call costs, not token categories, for run-level totals. Unknown usage or charges prevent verified completion/cost claims in this version.

Roles are `single` for both single-agent and human-checkpoint conditions; `draft`, `critique`, `revision`, `final` for continuing-context self-review; and `coordinator_plan`, `worker_1`, `worker_2`, `coordinator_final` for multi-agent execution. Either worker may start first. The human checkpoint occurs after two model calls. Keep execution assistance distinct from final independent verification and operator handling.

The independent review record contains `reviewer_id`, `independent`, `passed`, `verification_seconds`, and `notes`. A reviewer cannot be the run's operator or its checkpoint reviewer; the complete protocol adds fixture-author independence and condition blinding. These are attestations that require real review and audit; the software cannot establish human independence from identity strings alone.

## Evaluation

```sh
python3 docs/research/experiments/agent-study/study.py score --task reconcile_parallel --answer /path/to/answer.json --run /path/to/run.json
```

- Exit 0: all answer and record checks pass, completed status, independent-review attestation passes.
- Exit 1: incorrect output, failed/pending verification, or record/policy violations.
- Exit 2: invalid JSON, file/argument problems, or otherwise unprocessable records. Retain the scheduled attempt as invalid; never discard it from the denominator.

Without `--run`, the scorer can establish automated correctness only and exits 1 even for a correct answer. It rejects `offline_synthetic` harness records as empirical attempts. It does not contact a provider, verify invoices/transcript contents, sandbox a model, or validate a manifest hash against the actual manifest. Those are executor/audit responsibilities. Do not interpret a passing synthetic software test as a real verified completion.

## Before the pilot

The fixed workflow, shared tools, and synthetic controller are implemented and fingerprinted. Bind/implement the live model adapter, prices, token reservation, hard deadlines, tools, and runtime limits; verify actual isolation; implement real checkpoint/review handling; obtain independent fixture review; then freeze the live session manifest and execute the schedule. The current fixtures are development examples. New realistic cases and a task-level sample-size plan are required before main-study claims.
