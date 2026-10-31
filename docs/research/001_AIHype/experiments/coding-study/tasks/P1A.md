# P1A — Slow-test reporting summary

Task type: small reporting feature. Pair: P1. Condition: **unassigned**.

Base: QuantSmith commit `2601cabd74622c832e99457a9a84ddb4a11f073c`.

## Request

Add `slow_test_summary(results, *, min_duration_s=0.0, limit=10)` to `src/quantsmith/test_engineering/report.py`. Work from the existing `TestResult` records; no test process should be launched.

## Acceptance contract

- Return a list of dictionaries containing exactly `id`, `status`, and `duration_s` for each selected record. Keep original record IDs/statuses/durations; do not group or deduplicate records.
- Include durations **greater than or equal to** `min_duration_s`. Sort by descending duration, then ascending ID. Equal duration/ID records retain their input order. Apply the limit after filtering and sorting.
- `min_duration_s` must be a finite nonnegative integer/float, excluding booleans. Each supplied result's duration must satisfy the same rule, including records excluded by the threshold or limit. Raise `ValueError` on invalid values.
- `limit` must be a nonnegative integer, excluding booleans. Zero returns an empty list after validating the request and durations. Invalid limits raise `ValueError`.
- Empty input returns `[]`. Results of any existing test status may qualify. Inputs must remain unchanged.
- Existing `summarize`, report verdicts, serialization, and other behavior must remain compatible.

## Scope and checks

Change the production report module and focused tests only. Preserve public APIs; add no dependencies or external I/O. Acceptance checks are `acceptance/test_p1a.py`; existing report/JUnit regressions are in the SDK's `tests/test_test_engineering.py`.

All acceptance inputs are synthetic. These requirements expose desired behavior, not a solution. No condition or timing observation is assigned by this brief. Record author implementation, verification, and rework separately under the [personal protocol](../../../coding-experiment-protocol.md).
