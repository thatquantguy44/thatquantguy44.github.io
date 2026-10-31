# P4A — Export lineage impact

Pair: P4, audit exports. Base: QuantSmith commit `2601cabd74622c832e99457a9a84ddb4a11f073c`.

Add a small export helper to `src/quantsmith/pipelines/provenance.py`, plus participant-authored tests. Reuse the existing impact query; no new graph traversal, graph mutation, storage, or external OpenLineage integration is in scope. The existing `to_openlineage` export describes transform runs, not this requested impact report.

## Required public API

Add `export_impact(graph, version)` taking an existing `LineageGraph` and `DatasetVersion`. Return an ordinary JSON-compatible dictionary with exactly:

```json
{
  "source_ref": "input@v1",
  "source_content_hash": "sha256:...",
  "downstream": [{"ref": "output@v1", "content_hash": "sha256:..."}],
  "count": 1
}
```

The example illustrates shape only; use actual registered refs/hashes from the supplied graph. Query downstream membership through `graph.impact(version)`, once. Emit each returned downstream reference once, sorted lexicographically by ref, with its registered content hash. Do not include the source itself unless the existing public query returns it. A source with no downstream versions has an empty list and count zero.

Metadata must describe the graph's registered versions, not unverified hash values on a caller-supplied object with the same ref. Unknown version refs raise `KeyError`, as the existing impact query does. Non-`LineageGraph`/non-`DatasetVersion` arguments raise `TypeError`. The valid graph is assumed internally consistent; this task does not add a graph-repair facility.

The export must be detached, deterministic across graph registration order, and round-trip through `json.dumps(..., sort_keys=True, allow_nan=False)` and `json.loads`. Do not alter versions, producers, runs, consumer edges, source records, `impact`, or existing citation/OpenLineage outputs. The task consumes an existing graph with synthetic records; it does not execute transforms or fetch data.

## Acceptance and regression scope

`acceptance/test_p4a.py` checks a branching/merging graph, no descendants, ordering/JSON round-trip, public-query delegation, canonical metadata, wrong/unknown inputs, and unchanged graph state. Existing `tests/test_provenance.py` must remain intact. Public fixtures are not an independent review or study observation.

Use the clean base and retain patches, participant tests, effort/failure logs, and deviations. Assignment and timing are provided by the study session, not this document.
