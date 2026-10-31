# P2A — Namespace-qualified JUnit input

Task type: input-compatibility maintenance. Pair: P2. Condition: **unassigned**.

Base: QuantSmith commit `2601cabd74622c832e99457a9a84ddb4a11f073c`.

## Request

Extend the existing `parse_junit(xml_text)` in `src/quantsmith/test_engineering/junit.py` to parse namespace-qualified JUnit elements as well as existing unqualified reports. Keep the function signature and `TestResult` output model.

## Acceptance contract

- Recognize `testcase`, `error`, `failure`, and `skipped` elements with no namespace, a default namespace, or an explicit prefix. Namespace URI/prefix choice must not change the results. One document may mix qualified and unqualified test cases.
- Keep test cases in document order and preserve existing ID construction (`classname::name`, or just `name`), file attribute, duration conversion, and status/message behavior.
- Preserve precedence `error` before `failure` before `skipped`, regardless of child order. Continue to support existing attribute-based status forms, fallback from missing failure/error message attributes to element text, whitespace stripping, and 2,000-character message truncation.
- Existing duration behavior stays compatible: invalid nonnumeric text becomes `0.0`. This task does not add a new duration-validation policy.
- Empty text returns `[]`; an XML document without test cases returns `[]`. Malformed XML still raises a parse error. Keep the existing maximum-input-byte rejection.
- Do not change messages or attributes merely because their text contains colons or namespace-like strings. No remote XML resources, new dependencies, external I/O, or test execution.

## Scope and checks

Change the JUnit production module and focused tests only. Acceptance checks are `acceptance/test_p2a.py`; existing parser regressions are in SDK `tests/test_test_engineering.py`.

All input XML is synthetic. The initial curator inspection has already exposed the module/topic; do not claim task naivety or reviewer blinding. No solution or condition assignment is included. Follow the [personal protocol](../../../coding-experiment-protocol.md).
