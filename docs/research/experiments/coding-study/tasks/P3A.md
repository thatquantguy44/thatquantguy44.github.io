# P3A — Explain a partition plan

Pair: P3, diagnostic helpers. Base: QuantSmith commit `2601cabd74622c832e99457a9a84ddb4a11f073c`.

This is a new reporting helper, not a claim that the existing planner is defective. Implement only in `src/quantsmith/pipelines/distributed_compute.py`, plus participant-authored tests. Do not change `plan_partitions`, skew/salting logic, exports, dependencies, or other study tasks.

## Required public API

Add `explain_partitions(total_bytes, target_bytes=128 * MiB, min_partitions=1, max_partitions=None)` returning a JSON-compatible dictionary with exactly:

| Key | Meaning |
| --- | --- |
| `total_bytes`, `target_bytes`, `min_partitions`, `max_partitions` | The validated input values; optional maximum stays null |
| `size_based_partitions` | Ceiling of total bytes divided by target bytes, before minimum/maximum bounds; zero bytes gives zero |
| `partitions` | The count selected by the existing public `plan_partitions` function |
| `binding_bound` | `minimum` if the minimum increases the size-based count; `maximum` if the maximum decreases it; otherwise null. Equality alone is not binding |
| `estimated_bytes_per_partition` | Total bytes divided by selected partitions, as a finite number; zero bytes gives zero |

For this helper, every supplied numeric input must be an actual Python integer, excluding booleans. Require total bytes >= 0, target bytes > 0, minimum >= 1, and maximum either null or >= minimum. Raise `ValueError` for any violation. The helper's stricter input contract must not change existing planner behavior. Normal study inputs are bounded integers representable in ordinary JSON; no new arbitrary-precision serialization facility is required.

The result must be detached, deterministic, and serializable with `json.dumps(..., allow_nan=False)`. Reuse the existing public planner for the selected count; this task adds an explanation, not another planning algorithm. No external service, file access, or wall-clock value is needed.

## Acceptance and regression scope

The supplied `acceptance/test_p3a.py` checks ordinary sizing, lower/upper binding, equality, zero bytes, defaults, invalid inputs, JSON serialization, and reuse of the existing planner. Existing `tests/test_data_eng_tooling.py` behavior must remain intact. Hidden or independent human acceptance is not implied; the public checks define the task contract.

Start from the clean base; retain your patch, tests, measured effort, failures, and any deviation. AI/no-AI assignment and timing are set by the study session, not this brief.
