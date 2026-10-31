"""Public requirements for P3B; synthetic changes, no reference implementation."""

import json

import pytest

from quantsmith.pipelines import schema_evolution as subject


def api():
    helper = getattr(subject, "summarize_compatibility", None)
    assert callable(helper), "P3B requires summarize_compatibility"
    return helper


def mixed_report():
    return subject.Compatibility((
        subject.Change("z", "type_changed", "synthetic", True, True),
        subject.Change("x", "added", "synthetic", True, False),
        subject.Change("x", "default_changed", "synthetic", False, False),
        subject.Change("y", "added", "synthetic", False, False),
        subject.Change("a", "removed", "synthetic", False, True),
    ))


def test_p3b_existing_classifier_regression():
    old = subject.Schema("s", "1", (subject.Field("x", "int"),))
    new = subject.Schema("s", "2", (subject.Field("x", "long"),))
    report = subject.compatibility(old, new)
    assert report.backward and not report.forward and not report.full
    assert subject.check(old, new, "backward") == []
    assert len(subject.check(old, new, "forward")) == 1


def test_p3b_mixed_changes_have_exact_record_counts_and_stable_kinds():
    out = api()(mixed_report())
    assert out == {
        "total_changes": 5, "backward": False, "forward": False, "full": False,
        "by_kind": [{"kind": "added", "count": 2},
                    {"kind": "default_changed", "count": 1},
                    {"kind": "removed", "count": 1},
                    {"kind": "type_changed", "count": 1}],
        "breaks_backward": 2, "breaks_forward": 2,
        "breaks_both": 1, "breaks_neither": 2,
    }
    assert json.loads(json.dumps(out, allow_nan=False)) == out


def test_p3b_empty_report_is_fully_compatible():
    assert api()(subject.Compatibility(())) == {
        "total_changes": 0, "backward": True, "forward": True, "full": True,
        "by_kind": [], "breaks_backward": 0, "breaks_forward": 0,
        "breaks_both": 0, "breaks_neither": 0,
    }


def test_p3b_summary_uses_real_classification_without_changing_report():
    old = subject.Schema("s", "1", (subject.Field("x", "int"),))
    new = subject.Schema("s", "2", (subject.Field("x", "long"),
                                    subject.Field("optional", "string", nullable=True)))
    report = subject.compatibility(old, new)
    original = report.changes
    out = api()(report)
    assert out["total_changes"] == 2
    assert out["backward"] is report.backward
    assert out["forward"] is report.forward
    assert out["full"] is report.full
    assert report.changes == original


def test_p3b_input_order_is_preserved_and_result_is_detached():
    report = mixed_report()
    original = report.changes
    first = api()(report)
    second = api()(subject.Compatibility(tuple(reversed(report.changes))))
    assert first == second
    first["by_kind"][0]["count"] = 999
    assert api()(report)["by_kind"][0]["count"] == 2
    assert report.changes == original


@pytest.mark.parametrize("value", [None, [], {}, "report"])
def test_p3b_wrong_input_type_is_explicit(value):
    helper = api()
    with pytest.raises(TypeError):
        helper(value)
