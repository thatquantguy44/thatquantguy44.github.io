"""Public P1B requirements over synthetic findings; no SDK implementation."""

from copy import deepcopy
import json

import pytest

from quantsmith.pipelines import dbt_review


def feature():
    function = getattr(dbt_review, "summarize_by_rule", None)
    assert callable(function), "P1B requires dbt_review.summarize_by_rule"
    return function


def test_counts_duplicate_findings_and_sorts_observed_groups():
    duplicate = dbt_review.Finding("model.a", "ownership", "warn", "missing owner")
    findings = [duplicate, dbt_review.Finding("model.b", "primary_key", "error", "no key"),
                duplicate, dbt_review.Finding("model.a", "ownership", "error", "different issue")]
    expected = [{"rule": "ownership", "severity": "error", "count": 1},
                {"rule": "ownership", "severity": "warn", "count": 2},
                {"rule": "primary_key", "severity": "error", "count": 1}]
    function = feature()
    assert function(findings) == expected
    assert function(list(reversed(findings))) == expected
    assert json.loads(json.dumps(function(findings))) == expected


def test_empty_and_no_input_mutation():
    function = feature()
    assert function([]) == []
    findings = [dbt_review.Finding("n", "custom rule", "warn", "message")]
    original = deepcopy(findings)
    assert function(findings) == [{"rule": "custom rule", "severity": "warn", "count": 1}]
    assert findings == original


@pytest.mark.parametrize("severity", ["info", "ERROR", "", None, 1])
def test_invalid_severity_rejected(severity):
    function = feature()
    with pytest.raises(ValueError):
        function([dbt_review.Finding("n", "rule", severity, "text")])


@pytest.mark.parametrize("rule", ["", "  ", None, 1])
def test_invalid_rule_rejected(rule):
    function = feature()
    with pytest.raises(ValueError):
        function([dbt_review.Finding("n", rule, "warn", "text")])


def test_valid_rule_text_is_not_normalized():
    assert feature()([dbt_review.Finding("n", " rule ", "error", "text")]) == [
        {"rule": " rule ", "severity": "error", "count": 1}]


def test_existing_summary_and_manifest_review_remain_compatible():
    findings = [dbt_review.Finding("n", "ownership", "warn", "a"),
                dbt_review.Finding("m", "key", "error", "b")]
    assert dbt_review.summarize(findings) == (1, 1)
    assert dbt_review.review_manifest({}) == []
