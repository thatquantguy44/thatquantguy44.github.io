from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .config import PipelineConfig
from .fetch import FetchError, fetch_sources, latest_artifact
from .parsers import ParseError, output_name, parse_payload, write_rows
from .provenance import read_json, sha256_file, write_json
from .quality import (
    check_annual_coverage,
    check_monthly_returns,
    check_political_candidates,
    check_policy_rates,
    check_shiller_context,
    read_csv,
)


def initialize_workspace(workspace: Path) -> None:
    for name in ("raw", "normalized", "inputs", "output", "quality"):
        (workspace / name).mkdir(parents=True, exist_ok=True)
    controls = workspace / "inputs" / "controls.csv"
    if not controls.exists():
        controls.write_text(
            "id,startDate,endDate,presidentId,presidentName,presidentParty,houseControl,senateControl,sourceId\n",
            encoding="utf-8",
        )
    terms = workspace / "inputs" / "terms.csv"
    if not terms.exists():
        terms.write_text("id,label,startDate,endDate,decisionDate,complete,sourceId\n", encoding="utf-8")


def parse_sources(workspace: Path, config: PipelineConfig, source_ids: Iterable[str] | None = None) -> list[dict[str, object]]:
    requested = set(source_ids or ())
    if requested - {source.id for source in config.sources}:
        unknown = requested - {source.id for source in config.sources}
        raise ParseError(f"Unknown source ID(s): {', '.join(sorted(unknown))}")
    statuses: list[dict[str, object]] = []
    for source in config.sources:
        if not source.enabled or (requested and source.id not in requested):
            continue
        try:
            artifact = latest_artifact(workspace, source.id)
            raw = workspace / str(artifact["relative_path"])
            payload = raw.read_bytes()
            if sha256_file(raw) != artifact["sha256"]:
                raise ParseError("raw file hash differs from fetch manifest")
            rows = parse_payload(source.parser, payload, source.id)
            output = workspace / "normalized" / output_name(source.parser)
            write_rows(output, rows)
            statuses.append({
                "source_id": source.id,
                "status": "PARSED",
                "rows": len(rows),
                "output": str(output.relative_to(workspace)),
                "raw_sha256": artifact["sha256"],
            })
        except (FetchError, ParseError, OSError) as exc:
            statuses.append({"source_id": source.id, "status": "FAILED", "message": str(exc)})
    # A targeted re-parse must not erase the last known status of every other
    # source.  Merge by source ID, then retain the catalog's stable order.
    status_path = workspace / "normalized" / "parse_status.json"
    prior = read_json(status_path, {"sources": []})
    by_source = {
        str(item.get("source_id")): item
        for item in prior.get("sources", [])
        if isinstance(item, dict) and item.get("source_id")
    }
    by_source.update({str(item["source_id"]): item for item in statuses})
    combined = [by_source[source.id] for source in config.sources if source.id in by_source]
    write_json(status_path, {"schema_version": 1, "sources": combined})
    return statuses


def validate_workspace(workspace: Path, config: PipelineConfig) -> dict[str, object]:
    issues: list[dict[str, object]] = []
    parse_status = read_json(workspace / "normalized" / "parse_status.json", {"sources": []})
    statuses = {str(status.get("source_id")): status for status in parse_status.get("sources", []) if isinstance(status, dict)}
    checker_by_parser = {
        "fama_french_monthly_zip": lambda rows: check_monthly_returns(rows) + check_annual_coverage(rows, config.annual_start_year - 1, config.annual_end_year),
        "fred_csv": check_policy_rates,
        "shiller_xls": check_shiller_context,
        "house_party_government_html": check_political_candidates,
    }
    for source in config.sources:
        if not source.enabled:
            continue
        status = statuses.get(source.id)
        if not status or status.get("status") != "PARSED":
            message = "No parse status recorded" if not status else str(status.get("message", "Source did not parse"))
            issues.append({"check_id": "source.parse", "severity": "ERROR", "message": message, "location": source.id})
            continue
        output = workspace / "normalized" / output_name(source.parser)
        if not output.exists():
            issues.append({"check_id": "source.output", "severity": "ERROR", "message": "Parse status has no normalized output file", "location": source.id})
            continue
        checks = checker_by_parser[source.parser](read_csv(output))
        issues.extend(issue.as_dict() for issue in checks)
    report = {
        "schema_version": 1,
        "errors": sum(item["severity"] == "ERROR" for item in issues),
        "warnings": sum(item["severity"] == "WARNING" for item in issues),
        "issues": issues,
    }
    write_json(workspace / "quality" / "report.json", report)
    return report


def fetch_then_record(workspace: Path, config: PipelineConfig, source_ids: Iterable[str] | None = None) -> list[dict[str, object]]:
    initialize_workspace(workspace)
    return fetch_sources(workspace, config, source_ids)
