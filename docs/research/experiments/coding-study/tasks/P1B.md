# P1B — dbt finding counts by rule and severity

Task type: small reporting feature. Pair: P1. Condition: **unassigned**.

Base: QuantSmith commit `2601cabd74622c832e99457a9a84ddb4a11f073c`.

## Request

Add `summarize_by_rule(findings)` to `src/quantsmith/pipelines/dbt_review.py`, using the existing `Finding` records. No dbt installation, warehouse, or model execution is needed.

## Acceptance contract

- Return a list of dictionaries containing exactly `rule`, `severity`, and `count`, one per observed `(rule, severity)` combination.
- Count every input finding, including repeated findings or multiple findings for one node. Do not deduplicate by node, message, or object identity.
- Sort rows lexicographically by rule, then severity. Only severities `error` and `warn` are valid. Rules must be nonempty strings after checking for whitespace-only text; do not trim or rename valid rules. Invalid severity/rule values raise `ValueError`.
- Empty input returns `[]`. Do not invent zero-count combinations. Returned data must be JSON serializable, deterministic for any permutation of the same findings, and independent of node/message wording.
- Do not mutate the sequence or its records. Preserve the existing `summarize(findings)` result `(errors, warnings)` and `review_manifest` behavior.

## Scope and checks

Change the production dbt-review module and focused tests only. Add no dependencies or external I/O. Acceptance checks are `acceptance/test_p1b.py`; existing dbt regressions are in SDK `tests/test_data_eng_tooling.py`.

All acceptance inputs are synthetic. This is a new reporting contract, not an assertion that the original API is defective. No condition, participant result, or independent quality assessment is assigned by this brief. Follow the [personal protocol](../../../coding-experiment-protocol.md).
