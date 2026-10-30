# Agent execution harness

Prepared: 2026-10-29 (America/New_York)

Status: **runnable offline synthetic harness**. This is implementation validation, not the model pilot or an empirical experiment. Follow the [protocol](../../agent-experiment-protocol.md) and [package README](README.md) for the research design and live-readiness requirements.

## Run it

Python 3.10+ standard library only, from the repository root:

```sh
python3 docs/research/experiments/agent-study/runner.py smoke --out /tmp/ai-hype-agent-smoke
python3 docs/research/experiments/agent-study/runner.py run --task reconcile_parallel --condition multi --out /tmp/ai-hype-agent-multi
python3 -m unittest discover -s docs/research/experiments/agent-study -p 'test_*.py' -v
```

Use a fresh output path each time. The smoke command consumes the seeded schedule: by default, six tasks × five conditions × three repetitions = 90 **synthetic execution checks**. `--repeats 1` gives 30 checks. These counts are not new model observations. A schedule and all attempt artifacts are retained; failed outputs are not replaced. An interrupted process can leave an incomplete directory: preserve it and its schedule membership, classify it as incomplete/invalid, and use a new version/path for any later sensitivity run.

CLI exit 0 means the harness finished and wrote its artifacts. Inspect `terminal_status`, `answer_errors`, and `run_errors`; it does not mean the attempt succeeded. CLI exit 2 means an input/filesystem/processing error. The existing `study.py score` retains its stricter exit convention, returning 0 only for verified success, which offline harness output cannot achieve.

## Policies actually executed

| Condition | Context and submission policy |
| --- | --- |
| `fixed` | Frozen deterministic public-record procedure; zero model requests |
| `single` | One continuing context, at most four requests; an explicit final response can submit early |
| `self_review` | One continuing context through draft, critique, revision, and final; early final flags do not skip phases |
| `human_checkpoint` | One continuing context; early final flags do not skip two requests and one checkpoint; supplied synthetic feedback enters only after request two |
| `multi` | Coordinator plan, two fresh worker contexts, coordinator final; both workers receive the original plan, each sees only its own history, and the final coordinator receives both outputs |

Workers run **sequentially** in this implementation. Their contexts remain independent. Both receive the coordinator's plan and plan-phase tool results; the final coordinator receives each worker's text and tool results. Worker outputs never enter the other worker's context. The harness does not claim a parallel-latency benefit. Every model condition gets the same public packet and tools: `read_source`, literal `search_sources`, and a restricted Decimal `calculate`. Tools cannot open arbitrary paths, access evaluator data, execute Python/source code, or use the network. The calculator accepts bounded decimal literals, parentheses, and `+ - * /`; its shared definition records precision and magnitude limits.

This process still runs in the repository's environment. Clean participant files and limited tool functions do **not** establish an operating-system sandbox. `boundary_verified` stays false. Real provider and tool execution requires a separately verified boundary before collection.

## Replay contract and failure injection

`ReplayBackend` is a data-only test backend, recreated per attempt. The default backend returns generic synthetic prose in intermediate phases and unsupported/null answers at final submission. It is deliberately not a solver. Neither gold answers nor evaluator feedback are passed to it. Gold is parsed for scoring only after execution ends; the evaluator-side package fingerprint includes a hash of the key, never its contents in participant inputs.

`runner.py run --script /path/to/script.json` accepts:

```json
{
  "responses": [
    {
      "content": "Synthetic draft",
      "final": false,
      "model_snapshot": "offline-replay-v1",
      "cost_usd": 0.01,
      "elapsed_seconds": 1,
      "usage": {"input_tokens": 10, "output_tokens": 5, "reasoning_tokens": 0, "cached_tokens": 0},
      "tool_calls": [{"name": "calculate", "arguments": {"expression": "0.1 + 0.2"}}]
    },
    {
      "content": "{}",
      "final": true,
      "model_snapshot": "offline-replay-v1",
      "cost_usd": 0.01,
      "elapsed_seconds": 1,
      "usage": {"input_tokens": 10, "output_tokens": 5, "reasoning_tokens": 0, "cached_tokens": 0}
    }
  ]
}
```

The example intentionally submits an invalid answer schema, which must fail automated grading. It is not a positive research result. Responses use an explicit final flag; final content must be strict JSON without duplicate keys/non-finite values. Malformed final text remains in the response transcript, the parsed answer is null, and no repair request is issued after submission.

Optional response `error` values such as `provider_error`, `tool_error`, and `timeout` inject failures. Missing/invalid usage remains visible and prevents further completion. Unknown charges remain null and stop additional requests because remaining spending capacity cannot be established. An exhausted replay script becomes a provider error with unknown charge, not an invented zero-cost response.

The top-level optional `checkpoint` object contains `feedback`, `active_seconds`, and `reviewer_id`. It is accepted only for `human_checkpoint`; all values are scripted, including the synthetic identity. Feedback and its elapsed/active time are retained verbatim. A scenario over 120 active seconds terminates the attempt; checkpoint time also consumes the 600-second scenario ceiling. A checkpoint is logged even for empty feedback. It is never an actual human intervention or independent review.

Retries are disabled by default. `--allow-provider-retry` permits linked retries of **known-charge provider errors only**, in `single`/`human_checkpoint`. The failed request and retry both count toward four requests and the original spending/time ceiling. Mandatory review/multi phases cannot repeat under the current protocol's strict phase sequence, so retry authorization for those conditions is rejected. A future change requires a protocol revision, not a silent retry policy.

## Accounting and deadlines

Before each replay request the controller reserves a declared worst-case charge (USD 0.125 by default). It refuses a request if reservation plus known prior charges could exceed the proposed USD 0.50 ceiling. A returned charge above its reservation is retained and stops the attempt. This exercises the reservation mechanism; the replay constant is **not provider pricing or provider-specific token counting**.

All response costs, token counts, response durations, checkpoint active time, and derived timestamps in these records are **scenario inputs**, not invoices, model usage, observed service latency, or observed human effort. Default zero replay costs/tokens describe the script; no paid model call occurs. `timing_basis` is `simulated`. `observed_runner_seconds` separately measures local wall execution and must not be interpreted as agent latency. Operator handling and independent verification remain null because neither was measured.

The virtual clock makes deadline and checkpoint failure tests deterministic without sleeping. It checks before requests, after responses, and after checkpoints. It cannot prove hard cancellation of a live blocking provider call. A live adapter must supply trustworthy worst-case token/billing reservation, hard request/tool deadlines, actual usage/cost capture, and interruption/cancellation behavior. No live adapter is enabled by this CLI.

## Artifacts and evaluation boundary

Each fresh attempt directory contains:

- `participant/`: only `task.json`, common/assigned instructions, and an empty answer template.
- `session-manifest.json`: synthetic mode, limits, model identity, tools, worker/retry policy, package fingerprint, and executor file hashes; `live_ready` is false.
- `transcripts/`: exact request contexts, responses, tool inputs/outputs/errors, fixed-workflow coverage, checkpoint feedback, and error/retry records. Requests are written before response processing.
- `events.jsonl`: append-only compact events while executing, then the same events in `run.json`.
- `answer.json`, `run.json`, `score.json`: retained output (or null), terminal reason, known/unknown scenario accounting, and separate automated versus verified grading.
- `artifacts.json`: byte hashes of the files written before this final integrity record. This detects local changes when checked; it is not independent proof of time, immutable storage, or review.

Output creation refuses existing attempt directories. There is no overwrite/resume or replacement-attempt path. Hard filesystem/process failures may leave partial files, which must remain failures/invalid records in the scheduled denominator. Local hashes do not authenticate provider invoices or human attestations.

All runs carry `execution_mode: offline_synthetic`. The scorer rejects that mode as an empirical attempt even if someone fills in review/boundary fields. Review decisions and reviewer/operator identity remain unobserved by default; software success cannot supply human independence. Keep collected data private outside tracked repository files.

## Fixed baseline coverage

`fixed.py` reads only the public packet. It handles a bounded grammar of `field_id: decimal [unit]` records, explicitly stated final-over-draft/correction-over-original authority, explicit percent-ratio formulas with compatible units, and requested one-hop currency conversion. Decimal arithmetic and whole-source verbatim citations preserve input/rule provenance. It does not load evaluator keys, select values by agreement with gold, or branch on fixture/task IDs.

It abstains on ambiguous records/rates, unparseable fields, unsupported dated/entity/tier selection, prose/boolean synthesis, and unsupported arithmetic such as prose compounding. `transcripts/*-fixed.json` records per-question coverage and its reason. Correctness remains evaluator-side. Unsupported coverage is a limitation of this frozen procedure, not evidence that conventional automation cannot solve the task. Freeze/archive this implementation before any later model comparison; changes require a new package fingerprint and schedule/session artifacts.

## Remaining live-readiness work

1. Bind and implement the exact provider/model, pricing/token estimator, response mapping, real clock/deadlines, and actual tool billing; archive them with tools and prompts.
2. Verify filesystem/network isolation, task-only access, no cross-attempt state, and retained raw provider/transcript artifacts in that runtime.
3. Implement a real checkpoint operator interface and condition-blinded independent output review without exposing evaluator feedback during execution.
4. Obtain independent fixture/key review, measure operator/setup effort, and freeze the live manifest and schedule.
5. Run the development pilot, retain every failure, and use variability to plan fresh main-study cases and size. Do not count this smoke run as that pilot.
