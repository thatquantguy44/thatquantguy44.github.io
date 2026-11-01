from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

from .config import PipelineConfig
from .fetch import FetchError, fetch_sources, latest_artifact
from .parsers import ParseError, output_name, parse_payload, write_rows
from .provenance import read_json, sha256_file, write_json
from .quality import (
    Issue,
    check_annual_coverage,
    check_controls,
    check_monthly_returns,
    check_political_candidates,
    check_policy_rates,
    check_shiller_context,
    check_wikipedia_congress_crosscheck,
    read_csv,
)


class ReviewError(ValueError):
    """Raised when the review-only political candidate handoff is unusable."""


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


def prepare_control_review(
    config: PipelineConfig, candidates_path: Path, wikipedia_crosscheck_path: Path, output_path: Path
) -> dict[str, object]:
    """Write a review-only Congress-candidate handoff for the annual sample.

    The House Historian source reports Congress-year ranges, not the dated
    presidential/House/Senate intervals required by ``build-annual``. This
    function intentionally produces a differently shaped artifact so it cannot
    be copied into ``controls.csv`` and accidentally treated as reviewed data.
    """
    candidates = read_csv(candidates_path)
    issues = check_political_candidates(candidates)
    errors = [issue for issue in issues if issue.severity == "ERROR"]
    if errors:
        message = "; ".join(f"{issue.check_id}: {issue.message}" for issue in errors[:5])
        raise ReviewError(f"Cannot prepare political-control review: {message}")
    wikipedia_rows = read_csv(wikipedia_crosscheck_path)
    wikipedia_issues = check_wikipedia_congress_crosscheck(wikipedia_rows)
    wikipedia_errors = [issue for issue in wikipedia_issues if issue.severity == "ERROR"]
    if wikipedia_errors:
        message = "; ".join(f"{issue.check_id}: {issue.message}" for issue in wikipedia_errors[:5])
        raise ReviewError(f"Cannot prepare political-control review: {message}")
    wikipedia_by_congress = {row["congress"]: row for row in wikipedia_rows}

    first_decision_year = config.annual_start_year - 1
    selected = [
        candidate
        for candidate in candidates
        if int(candidate["start_year"]) <= config.annual_end_year and int(candidate["end_year"]) > first_decision_year
    ]
    if not selected:
        raise ReviewError("No Congress candidates overlap the annual decision-date window")
    missing_crosscheck = [candidate["congress"] for candidate in selected if candidate["congress"] not in wikipedia_by_congress]
    if missing_crosscheck:
        raise ReviewError(f"Wikipedia cross-check lacks Congress candidate(s): {', '.join(missing_crosscheck[:10])}")
    fields = [
        "candidateId",
        "congress",
        "startYear",
        "endYear",
        "presidentLabelCandidate",
        "presidentPartyCandidate",
        "houseControlCandidate",
        "senateControlCandidate",
        "sourceId",
        "sourceReviewStatus",
        "wikipediaSenateCounts",
        "wikipediaHouseCounts",
        "wikipediaVariationHint",
        "wikipediaTrifectaLabel",
        "wikipediaSourceId",
        "wikipediaReviewStatus",
        "reviewRequired",
    ]
    review_required = "Verify dated president/House/Senate intervals, identity, ties, vacancies, and mid-Congress changes before creating controls.csv"
    output_rows = []
    for candidate in selected:
        wikipedia = wikipedia_by_congress[candidate["congress"]]
        output_rows.append({
            "candidateId": f"house-congress-{candidate['congress']}",
            "congress": candidate["congress"],
            "startYear": candidate["start_year"],
            "endYear": candidate["end_year"],
            "presidentLabelCandidate": candidate["president_label"],
            "presidentPartyCandidate": candidate["president_party"],
            "houseControlCandidate": candidate["house_party"],
            "senateControlCandidate": candidate["senate_party"],
            "sourceId": candidate["source_id"],
            "sourceReviewStatus": candidate["review_status"],
            "wikipediaSenateCounts": f"D={wikipedia['senate_democrat_count']}; R={wikipedia['senate_republican_count']}; Other={wikipedia['senate_other_count']}; Vacancies={wikipedia['senate_vacancies']}",
            "wikipediaHouseCounts": f"D={wikipedia['house_democrat_count']}; R={wikipedia['house_republican_count']}; Other={wikipedia['house_other_count']}; Vacancies={wikipedia['house_vacancies']}",
            "wikipediaVariationHint": wikipedia["within_congress_variation_hint"],
            "wikipediaTrifectaLabel": wikipedia["trifecta_label"],
            "wikipediaSourceId": wikipedia["source_id"],
            "wikipediaReviewStatus": wikipedia["review_status"],
            "reviewRequired": review_required,
        })
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(output_rows)
    manifest_path = output_path.with_suffix(".manifest.json")
    manifest = {
        "schema_version": 1,
        "artifact_kind": "POLITICAL_CONTROL_REVIEW_CANDIDATES",
        "controls_file_eligible": False,
        "reason": "Congress-year candidates are not dated, reviewed political-control intervals.",
        "candidate_count": len(output_rows),
        "decision_window": {
            "first_decision_date": f"{first_decision_year}-12-31",
            "last_decision_date": f"{config.annual_end_year}-12-31",
        },
        "inputs": {
            "candidates_path": str(candidates_path),
            "candidates_sha256": sha256_file(candidates_path),
            "wikipedia_crosscheck_path": str(wikipedia_crosscheck_path),
            "wikipedia_crosscheck_sha256": sha256_file(wikipedia_crosscheck_path),
            "config_sha256": sha256_file(config.path),
        },
        "required_reviewer_actions": [
            "Create dated half-open intervals in controls.csv; do not rename or copy this candidate artifact.",
            "Verify the president's full identity and party for each interval.",
            "Verify actual House and Senate control, including ties, vacancies, and mid-Congress changes.",
            "Record controlling primary source IDs for every approved interval.",
        ],
    }
    write_json(manifest_path, manifest)
    return {"candidates": len(output_rows), "output": output_path, "manifest": manifest_path}


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
        "wikipedia_congress_party_divisions_html": lambda rows: check_wikipedia_congress_crosscheck(
            rows, config.annual_start_year - 1, config.annual_end_year
        ),
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


def validate_controls_file(config: PipelineConfig, controls_path: Path) -> dict[str, object]:
    """Validate reviewed control rows without requiring full annual coverage.

    This is the promotion gate for one or more independently reviewed intervals.
    Full decision-date coverage remains a separate requirement of `build-annual`.
    """
    controls = read_csv(controls_path)
    issues = check_controls(controls)
    known_source_ids = {source.id for source in config.sources}
    for index, control in enumerate(controls, 2):
        source_id = control.get("sourceId", "").strip()
        if source_id and source_id not in known_source_ids:
            issues.append(Issue(
                "controls.source_catalog",
                "ERROR",
                f"sourceId is absent from config: {source_id}",
                f"row {index}",
            ))
        elif source_id and source_id not in config.manual_control_source_ids:
            issues.append(Issue(
                "controls.source_role",
                "ERROR",
                "sourceId is not registered as manual reviewed political-control evidence",
                f"row {index}",
            ))
    report = {
        "schema_version": 1,
        "errors": sum(issue.severity == "ERROR" for issue in issues),
        "warnings": sum(issue.severity == "WARNING" for issue in issues),
        "issues": [issue.as_dict() for issue in issues],
    }
    return report


def fetch_then_record(workspace: Path, config: PipelineConfig, source_ids: Iterable[str] | None = None) -> list[dict[str, object]]:
    initialize_workspace(workspace)
    return fetch_sources(workspace, config, source_ids)
