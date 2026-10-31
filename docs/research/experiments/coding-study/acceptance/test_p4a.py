"""Public requirements for P4A; synthetic lineage only, no reference implementation."""

from copy import deepcopy
import json

import pytest

from quantsmith.pipelines import provenance as subject


def api():
    helper = getattr(subject, "export_impact", None)
    assert callable(helper), "P4A requires export_impact"
    return helper


def graph_fixture(reverse=False):
    graph = subject.LineageGraph()
    source = subject.DatasetVersion.of("input", "v1", [{"x": 1}])
    alpha = subject.DatasetVersion.of("alpha", "v1", [{"x": 2}])
    zeta = subject.DatasetVersion.of("zeta", "v1", [{"x": 3}])
    merged = subject.DatasetVersion.of("merged", "v1", [{"x": 5}])
    graph.register_source(source, "synthetic", "2026-10-01T00:00:00Z")
    branches = [("ra", alpha), ("rz", zeta)]
    for run_id, output in reversed(branches) if reverse else branches:
        graph.record_run(subject.TransformRun(run_id, "synthetic", "fixture:1", (source,), (output,)))
    graph.record_run(subject.TransformRun("rm", "synthetic", "fixture:1", (alpha, zeta), (merged,)))
    return graph, source, alpha, zeta, merged


def test_p4a_existing_impact_regression():
    graph, source, _, _, merged = graph_fixture()
    assert graph.impact(source) == ("alpha@v1", "merged@v1", "zeta@v1")
    assert graph.impact(merged) == ()


def test_p4a_export_contains_canonical_sorted_unique_descendants():
    graph, source, alpha, zeta, merged = graph_fixture()
    out = api()(graph, source)
    assert out == {
        "source_ref": source.ref, "source_content_hash": source.content_hash,
        "downstream": [{"ref": alpha.ref, "content_hash": alpha.content_hash},
                       {"ref": merged.ref, "content_hash": merged.content_hash},
                       {"ref": zeta.ref, "content_hash": zeta.content_hash}],
        "count": 3,
    }
    assert json.loads(json.dumps(out, sort_keys=True, allow_nan=False)) == out


def test_p4a_leaf_has_an_explicit_empty_impact():
    graph, _, _, _, leaf = graph_fixture()
    assert api()(graph, leaf) == {"source_ref": leaf.ref, "source_content_hash": leaf.content_hash,
                                 "downstream": [], "count": 0}


def test_p4a_registration_order_does_not_change_export():
    first, source, *_ = graph_fixture()
    second, same_source, *_ = graph_fixture(reverse=True)
    helper = api()
    assert json.dumps(helper(first, source), sort_keys=True) == json.dumps(helper(second, same_source), sort_keys=True)


def test_p4a_calls_existing_public_impact_once(monkeypatch):
    graph, source, *_ = graph_fixture()
    original = graph.impact
    calls = []

    def traced(version):
        calls.append(version)
        return original(version)

    monkeypatch.setattr(graph, "impact", traced)
    assert api()(graph, source)["count"] == 3
    assert calls == [source]


def test_p4a_metadata_is_registered_and_export_does_not_mutate_graph():
    graph, source, *_ = graph_fixture()
    original = deepcopy(graph.__dict__)
    stale_object = subject.DatasetVersion(source.dataset, source.version, "unverified-caller-hash")
    out = api()(graph, stale_object)
    assert out["source_content_hash"] == source.content_hash
    out["downstream"][0]["content_hash"] = "changed-export-only"
    assert graph.__dict__ == original
    assert api()(graph, source)["downstream"][0]["content_hash"] != "changed-export-only"


def test_p4a_unknown_ref_preserves_key_error():
    graph, *_ = graph_fixture()
    helper = api()
    with pytest.raises(KeyError):
        helper(graph, subject.DatasetVersion.of("unknown", "v1", []))


@pytest.mark.parametrize("graph,version", [(None, None), ({}, None),
                                          (subject.LineageGraph(), "input@v1")])
def test_p4a_wrong_argument_types_are_explicit(graph, version):
    helper = api()
    with pytest.raises(TypeError):
        helper(graph, version)
