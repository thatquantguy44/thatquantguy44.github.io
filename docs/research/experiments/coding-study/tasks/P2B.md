# P2B — Optional categorical allowed-values validation

Task type: input-compatibility/validation maintenance. Pair: P2. Condition: **unassigned**.

Base: QuantSmith commit `2601cabd74622c832e99457a9a84ddb4a11f073c`.

## Request

Extend `validate_ingestion` in `src/quantsmith/pipelines/ingestion_data_contract.py` with a keyword-only parameter `allowed_values=None`. Retain its existing four positional parameters and return model. This is local row validation, without data fetching.

## Acceptance contract

- `allowed_values` is `None` or a mapping from declared **string-type** column names to a nonempty list/tuple of strings. Values are case-sensitive, exact strings; empty strings and duplicate allowed entries are permitted. `None` and an empty mapping add no domain restrictions.
- Invalid configuration raises `ValueError`, even for an empty row set: nonmapping configuration, unknown/non-string-schema column names, a string/set/empty sequence instead of a nonempty list/tuple, or any non-string category entry.
- For each present non-null string value outside its configured domain, append `SchemaViolation(row_index, column, "value not in allowed values")`.
- Null and absent values follow existing nullable/missingness behavior. They do not generate an additional categorical violation. Non-string values retain existing type violations and do not generate an additional categorical violation.
- Preserve deterministic violation order by row, then schema-column order. Domain configuration order must not affect it. Do not mutate rows, schema, rules, or the allowed-value mapping/sequences.
- Preserve duplicate-key counting, missingness fractions and quality-rule results, and `is_clean`. A categorical violation makes `is_clean` false. Existing calls without the keyword, or with `None`/`{}`, retain their results.

## Scope and checks

Change the ingestion-contract production module and focused tests only. Do not broaden the rule to numeric/cross-column expressions, add dependencies, or perform external I/O. Acceptance checks are `acceptance/test_p2b.py`; existing regressions are SDK `tests/test_ingestion_data_contract.py`.

All rows are synthetic. This brief specifies an extension, not a defect claim about the original signature. No AI/no-AI assignment or measured result exists. Follow the [personal protocol](../../../coding-experiment-protocol.md).
