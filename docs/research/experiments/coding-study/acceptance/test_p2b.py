"""Public P2B requirements over synthetic rows; no SDK implementation."""

from copy import deepcopy
import inspect

import pytest

from quantsmith.pipelines import ingestion_data_contract as ingestion


SCHEMA = [ingestion.ColumnSpec("id", "int", False),
          ingestion.ColumnSpec("region", "string", True),
          ingestion.ColumnSpec("desk", "string", False)]


def feature():
    function = ingestion.validate_ingestion
    parameter = inspect.signature(function).parameters.get("allowed_values")
    assert parameter is not None, "P2B requires optional allowed_values"
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY, "allowed_values must be keyword-only"
    assert parameter.default is None
    return function


def violations(result):
    return [(v.row_index, v.column, v.reason) for v in result.schema_violations]


def test_present_strings_checked_without_mutating_inputs():
    function = feature()
    rows = [{"id": 1, "region": "US", "desk": "A"},
            {"id": 2, "region": "us", "desk": "A"},
            {"id": 3, "region": "EU", "desk": "B"}]
    rules = {"region": ["US", "EU"]}
    original = deepcopy((rows, SCHEMA, rules))
    result = function(rows, SCHEMA, ["id"], [], allowed_values=rules)
    assert violations(result) == [(1, "region", "value not in allowed values")]
    assert not result.is_clean
    assert (rows, SCHEMA, rules) == original


def test_null_missing_and_type_errors_keep_existing_meaning():
    rows = [{"id": 1, "region": None, "desk": "A"}, {"id": 2, "desk": "A"},
            {"id": 3, "region": 5, "desk": "A"}, {"id": 4, "region": "US"}]
    result = feature()(rows, SCHEMA, ["id"], [], allowed_values={"region": ["US"], "desk": ["A"]})
    assert violations(result) == [(2, "region", "expected type 'string', got int"),
                                  (3, "desk", "null in non-nullable column")]
    assert result.missingness_by_column == {"id": 0.0, "region": 0.5, "desk": 0.25}


def test_multiple_domains_follow_row_then_schema_order():
    rows = [{"id": 1, "region": "XX", "desk": "X"}, {"id": 2, "region": "YY", "desk": "Y"}]
    result = feature()(rows, SCHEMA, ["id"], [], allowed_values={"desk": ["A"], "region": ["US"]})
    assert violations(result) == [(0, "region", "value not in allowed values"),
                                  (0, "desk", "value not in allowed values"),
                                  (1, "region", "value not in allowed values"),
                                  (1, "desk", "value not in allowed values")]


def test_default_none_empty_mapping_and_existing_quality_statistics():
    rows = [{"id": 1, "region": "US", "desk": "A"}, {"id": 1, "region": None, "desk": "B"}]
    missing = ingestion.QualityRule("region complete", "0 missing", "flag", "region", 0)
    baseline = ingestion.validate_ingestion(rows, SCHEMA, ["id"], [missing])
    function = feature()
    assert function(rows, SCHEMA, ["id"], [missing], allowed_values=None) == baseline
    assert function(rows, SCHEMA, ["id"], [missing], allowed_values={}) == baseline
    checked = function(rows, SCHEMA, ["id"], [missing], allowed_values={"region": ["US"]})
    assert checked == baseline
    assert checked.duplicate_key_count == 1
    assert not checked.rule_results[0].passed


def test_valid_empty_rows_and_empty_string_categories():
    function = feature()
    assert function([], SCHEMA, ["id"], [], allowed_values={"region": ["US"]}).is_clean
    assert function([{"id": 1, "region": "", "desk": "A"}], SCHEMA, ["id"], [],
                    allowed_values={"region": ("", "US", "US")}).is_clean


@pytest.mark.parametrize("rules", [[], "region", {"unknown": ["US"]}, {"id": ["1"]},
                                    {"region": []}, {"region": "US"}, {"region": {"US"}},
                                    {"region": [None]}, {"region": [1]}, {"region": [True]}])
def test_invalid_configuration_rejected_even_for_no_rows(rules):
    function = feature()
    with pytest.raises(ValueError):
        function([], SCHEMA, ["id"], [], allowed_values=rules)
