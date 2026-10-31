"""Public P1A requirements over synthetic records; no SDK implementation."""

from copy import deepcopy
import math

import pytest

from quantsmith.test_engineering import report


def feature():
    function = getattr(report, "slow_test_summary", None)
    assert callable(function), "P1A requires report.slow_test_summary"
    return function


def test_threshold_limit_order_and_all_statuses():
    results = [report.TestResult("z", "passed", 4), report.TestResult("a", "failed", 4),
               report.TestResult("slow", "error", 7), report.TestResult("edge", "skipped", 3),
               report.TestResult("fast", "passed", 2)]
    assert feature()(results, min_duration_s=3, limit=4) == [
        {"id": "slow", "status": "error", "duration_s": 7},
        {"id": "a", "status": "failed", "duration_s": 4},
        {"id": "z", "status": "passed", "duration_s": 4},
        {"id": "edge", "status": "skipped", "duration_s": 3},
    ]


def test_duplicates_keep_input_order_and_inputs_unchanged():
    results = [report.TestResult("same", "failed", 2), report.TestResult("same", "passed", 2)]
    original = deepcopy(results)
    assert feature()(results, limit=10) == [
        {"id": "same", "status": "failed", "duration_s": 2},
        {"id": "same", "status": "passed", "duration_s": 2},
    ]
    assert results == original


def test_empty_zero_limit_and_default_limit():
    function = feature()
    assert function([]) == []
    results = [report.TestResult(str(n), "passed", n) for n in range(12)]
    assert function(results, limit=0) == []
    assert len(function(results)) == 10
    assert function([report.TestResult("zero", "passed", 0)]) == [
        {"id": "zero", "status": "passed", "duration_s": 0}]


@pytest.mark.parametrize("threshold", [-1, True, "1", None, math.nan, math.inf, -math.inf])
def test_invalid_threshold_rejected(threshold):
    function = feature()
    with pytest.raises(ValueError):
        function([], min_duration_s=threshold)


@pytest.mark.parametrize("limit", [-1, True, 1.5, "2", None])
def test_invalid_limit_rejected(limit):
    function = feature()
    with pytest.raises(ValueError):
        function([], limit=limit)


@pytest.mark.parametrize("duration", [-1, True, "1", None, math.nan, math.inf, -math.inf])
def test_invalid_duration_rejected_even_if_filtered_or_limited(duration):
    function = feature()
    for limit in (0, 10):
        with pytest.raises(ValueError):
            function([report.TestResult("bad", "passed", duration)], min_duration_s=100, limit=limit)


def test_existing_summary_remains_compatible():
    results = [report.TestResult("a", "passed", 1), report.TestResult("b", "error", 2)]
    assert report.summarize(results) == {"passed": 1, "failed": 0, "error": 1, "skipped": 0, "total": 2}
