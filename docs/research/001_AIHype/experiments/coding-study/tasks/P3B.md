# P3B — Summarize schema compatibility

Pair: P3, diagnostic helpers. Base: QuantSmith commit `2601cabd74622c832e99457a9a84ddb4a11f073c`.

Add one reporting helper to `src/quantsmith/pipelines/schema_evolution.py`, plus participant-authored tests. This is an extension of existing diagnostics, not a reproduced schema-classification defect. Do not change compatibility decisions, change ordering, schema migration, or unrelated study tasks.

## Required public API

Add `summarize_compatibility(report)` taking an existing `Compatibility` object and returning exactly:

- `total_changes`: number of `Change` records, including multiple records for one field.
- `backward`, `forward`, `full`: the existing report's boolean verdicts, unchanged.
- `by_kind`: a list of `{kind, count}` dictionaries, lexicographically sorted by kind; include only observed kinds.
- `breaks_backward`, `breaks_forward`, `breaks_both`, `breaks_neither`: numbers of change records meeting those descriptions. A record breaking both directions contributes to each directional count as well as `breaks_both`; these fields are not mutually exclusive.

An empty report has zero counts, an empty `by_kind` list, and all three compatibility verdicts true. Counts are over change records, not distinct fields. Accept the existing valid `Change`/`Compatibility` model; no new enum or reclassification is needed. Raise `TypeError` when the argument is not a `Compatibility` object.

The helper must be deterministic, produce detached ordinary dictionaries/lists, and serialize using `json.dumps(..., allow_nan=False)`. It must not mutate or reorder the original changes. It consumes an already computed report: do not recompute compatibility, migrate rows, or hide individual changes in existing APIs.

## Acceptance and regression scope

`acceptance/test_p3b.py` checks empty and mixed reports, repeated kinds/fields, direction-count semantics, ordering, detachment, wrong input type, and actual existing classifier results. Existing `tests/test_change_safety.py` behavior must remain intact. Public checks are task criteria, not an independent human quality certification.

Start from the clean base. Retain your patch, tests, effort records, failed attempts, and deviations. Condition assignment and timing come from the study session.
