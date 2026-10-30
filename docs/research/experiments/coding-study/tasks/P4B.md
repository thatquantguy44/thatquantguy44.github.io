# P4B — Export per-step observability

Pair: P4, audit exports. Base: QuantSmith commit `2601cabd74622c832e99457a9a84ddb4a11f073c`.

Add one helper to `src/quantsmith/pipelines/pipeline_observability.py`, plus participant-authored tests. It exports an already constructed report: no pipeline execution, recomputed SLA, live metrics, or changes to `observe` are in scope.

## Required public API

Add `export_observability(report)` accepting an existing `ObservabilityReport`. Return exactly these top-level keys:

- `status`: the existing `report.status()` value, unchanged.
- `sla_ok`: the existing boolean verdict.
- `steps`: dictionaries sorted lexicographically by step name. Each contains all eight existing `StepHealth` fields (`step`, `latest_ok_partition`, `ok`, `failed`, `skipped`, `max_attempts`, `fresh`, `downtime`) plus `issues`. The `issues` list contains `stale` when `fresh` is false, followed by `downtime` when `downtime` is true; otherwise it is empty.
- `freshness_breaches`, `downtime_steps`, `sla_breaches`: sorted copies of the existing lists, preserving duplicate entries rather than silently deduplicating.
- `lineage`: a dictionary with lexicographically ordered step keys and sorted copies of each dependency list; preserve duplicate dependencies if supplied.

The existing StepHealth model has **eight** fields; the exported step has those eight plus `issues`, for nine keys total. Preserve `latest_ok_partition=None` as JSON null, not zero. Do not infer SLA verdicts from counts or emptiness. A valid empty report preserves its declared status/SLA verdict and empty collections.

Raise `TypeError` for a non-`ObservabilityReport` input. Raise `ValueError` if the report contains duplicate step names; do not silently drop a step or create ambiguous diagnostics. Inputs otherwise follow the existing report model; this task does not add a general validator for every internal field.

All returned lists/dictionaries must be detached from the input. The output must round-trip through `json.dumps(..., sort_keys=True, allow_nan=False)` and `json.loads` without custom serializers. Canonical serialization must be identical for reports differing only in list/key ordering, while preserving actual duplicate counts and diagnostic content. Do not alter `status`, `health_of`, or `observe`. No pipeline run or external access is needed for the synthetic report fixtures.

## Acceptance and regression scope

`acceptance/test_p4b.py` checks exact per-step fields/issues, nulls, sorted diagnostics/lineage, JSON round-trip, empty reports, declared-verdict preservation, duplicate names, detached output, input errors, and no call to `observe` or pipeline execution. Existing `tests/test_pipeline_observability.py` behavior must remain intact. These are public acceptance criteria, not independent human quality review.

Use the clean base. Keep patches, participant tests, observed effort/failures, and deviations. Conditions and timing are assigned by the study session.
