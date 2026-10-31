"""Public requirements for P4B; direct synthetic report objects, no pipeline runs."""

from copy import deepcopy
import json

import pytest

from quantsmith.pipelines import data_pipeline
from quantsmith.pipelines import pipeline_observability as subject


def api():
    helper = getattr(subject, "export_observability", None)
    assert callable(helper), "P4B requires export_observability"
    return helper


def report_fixture(reverse=False):
    ready = subject.StepHealth("alpha", 4, 2, 0, 1, 1, True, False)
    stale = subject.StepHealth("zeta", None, 0, 1, 0, 3, False, True)
    steps = [stale, ready] if not reverse else [ready, stale]
    return subject.ObservabilityReport(
        steps, ["zeta", "alpha", "zeta"], ["zeta"], False,
        ["zeta: stale", "alpha: SLA"],
        {"zeta": ["b", "a", "a"], "alpha": []} if not reverse else
        {"alpha": [], "zeta": ["a", "b", "a"]},
    )


def test_p4b_existing_report_regression():
    report = report_fixture()
    assert report.status() == "degraded"
    assert report.health_of("alpha").fresh
    assert report.health_of("missing") is None


def test_p4b_exact_export_keeps_nulls_status_and_all_diagnostics():
    out = api()(report_fixture())
    assert out == {
        "status": "degraded", "sla_ok": False,
        "steps": [
            {"step": "alpha", "latest_ok_partition": 4, "ok": 2, "failed": 0,
             "skipped": 1, "max_attempts": 1, "fresh": True, "downtime": False, "issues": []},
            {"step": "zeta", "latest_ok_partition": None, "ok": 0, "failed": 1,
             "skipped": 0, "max_attempts": 3, "fresh": False, "downtime": True,
             "issues": ["stale", "downtime"]},
        ],
        "freshness_breaches": ["alpha", "zeta", "zeta"], "downtime_steps": ["zeta"],
        "sla_breaches": ["alpha: SLA", "zeta: stale"],
        "lineage": {"alpha": [], "zeta": ["a", "a", "b"]},
    }
    assert json.loads(json.dumps(out, sort_keys=True, allow_nan=False)) == out


def test_p4b_equivalent_ordering_has_identical_canonical_json():
    helper = api()
    assert json.dumps(helper(report_fixture()), sort_keys=True) == json.dumps(helper(report_fixture(True)), sort_keys=True)


def test_p4b_empty_report_keeps_declared_sla_instead_of_inventing_data():
    helper = api()
    for sla_ok, status in ((True, "healthy"), (False, "degraded")):
        report = subject.ObservabilityReport([], [], [], sla_ok, [])
        assert helper(report) == {"status": status, "sla_ok": sla_ok, "steps": [],
                                  "freshness_breaches": [], "downtime_steps": [],
                                  "sla_breaches": [], "lineage": {}}


def test_p4b_issues_are_derived_from_each_flag_independently():
    report = subject.ObservabilityReport([
        subject.StepHealth("stale_only", 1, 1, 0, 0, 1, False, False),
        subject.StepHealth("down_only", 1, 1, 1, 0, 2, True, True),
    ], [], [], False, [])
    out = api()(report)
    assert [(row["step"], row["issues"]) for row in out["steps"]] == [
        ("down_only", ["downtime"]), ("stale_only", ["stale"])]


def test_p4b_output_is_detached_and_report_not_reordered():
    report = report_fixture()
    original = deepcopy(report)
    out = api()(report)
    assert list(out["lineage"]) == ["alpha", "zeta"]
    out["steps"][0]["issues"].append("changed")
    out["freshness_breaches"].append("changed")
    out["lineage"]["zeta"].append("changed")
    assert report == original
    assert "changed" not in api()(report)["lineage"]["zeta"]


def test_p4b_no_pipeline_execution_or_observation(monkeypatch):
    helper = api()

    def forbidden(*args, **kwargs):
        raise AssertionError("Exporter must not execute or re-observe a pipeline")

    monkeypatch.setattr(subject, "observe", forbidden)
    monkeypatch.setattr(data_pipeline, "run", forbidden)
    assert helper(report_fixture())["status"] == "degraded"


def test_p4b_duplicate_step_names_are_rejected():
    helper = api()
    same = subject.StepHealth("same", None, 0, 0, 0, 0, False, False)
    report = subject.ObservabilityReport([same, same], [], [], False, [])
    with pytest.raises(ValueError):
        helper(report)


@pytest.mark.parametrize("value", [None, {}, [], "report"])
def test_p4b_wrong_report_type_is_explicit(value):
    helper = api()
    with pytest.raises(TypeError):
        helper(value)
