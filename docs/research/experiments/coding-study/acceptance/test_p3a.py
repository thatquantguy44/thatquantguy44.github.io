"""Public requirements for P3A; synthetic fixtures, no reference implementation."""

import json

import pytest

from quantsmith.pipelines import distributed_compute as subject


KEYS = {"total_bytes", "target_bytes", "min_partitions", "max_partitions",
        "size_based_partitions", "partitions", "binding_bound",
        "estimated_bytes_per_partition"}


def api():
    helper = getattr(subject, "explain_partitions", None)
    assert callable(helper), "P3A requires explain_partitions"
    return helper


def test_p3a_existing_planner_regression():
    assert subject.plan_partitions(1000, target_bytes=300) == 4
    assert subject.plan_partitions(1000, target_bytes=300, max_partitions=3) == 3
    assert subject.plan_partitions(0) == 1


def test_p3a_ordinary_plan_has_exact_schema_and_json_roundtrip():
    out = api()(1000, target_bytes=300)
    assert set(out) == KEYS
    assert out == {"total_bytes": 1000, "target_bytes": 300, "min_partitions": 1,
                   "max_partitions": None, "size_based_partitions": 4,
                   "partitions": 4, "binding_bound": None,
                   "estimated_bytes_per_partition": 250}
    assert json.loads(json.dumps(out, allow_nan=False)) == out


@pytest.mark.parametrize("total,target,minimum,maximum,size,count,bound", [
    (1, 100, 4, None, 1, 4, "minimum"),
    (1000, 100, 1, 3, 10, 3, "maximum"),
    (400, 100, 4, 9, 4, 4, None),
    (900, 100, 1, 9, 9, 9, None),
    (0, 100, 1, None, 0, 1, "minimum"),
])
def test_p3a_bounds_are_explained_without_treating_equality_as_binding(
        total, target, minimum, maximum, size, count, bound):
    out = api()(total, target, minimum, maximum)
    assert out["size_based_partitions"] == size
    assert out["partitions"] == count
    assert out["binding_bound"] == bound
    assert out["estimated_bytes_per_partition"] == pytest.approx(total / count)


def test_p3a_defaults_match_public_planner():
    out = api()(subject.MiB)
    assert out["target_bytes"] == 128 * subject.MiB
    assert out["partitions"] == subject.plan_partitions(subject.MiB)
    assert out["size_based_partitions"] == 1
    assert out["binding_bound"] is None


@pytest.mark.parametrize("args", [
    (-1,), (1, 0), (1, 10, 0), (1, 10, 3, 2),
    (True,), (1.5,), (1, False), (1, 10, True), (1, 10, 1, True),
    (1, 10, 1, 3.5), (float("nan"),), (float("inf"),),
])
def test_p3a_invalid_helper_inputs_raise_value_error(args):
    helper = api()
    with pytest.raises(ValueError):
        helper(*args)


def test_p3a_selected_count_delegates_existing_planner(monkeypatch):
    helper = api()
    original = subject.plan_partitions
    calls = []

    def traced(*args, **kwargs):
        calls.append((args, kwargs))
        return original(*args, **kwargs)

    monkeypatch.setattr(subject, "plan_partitions", traced)
    assert helper(900, 100, 1, 4)["partitions"] == 4
    assert len(calls) == 1
