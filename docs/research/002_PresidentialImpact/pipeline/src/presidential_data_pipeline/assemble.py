from __future__ import annotations

from datetime import date
import csv
import calendar
import math
from pathlib import Path
from typing import Literal

from .config import PipelineConfig
from .provenance import canonical_json, sha256_file, write_json
from .quality import Issue, check_annual_coverage, check_controls, check_monthly_returns, read_csv


class BuildError(ValueError):
    pass


def _month_end(year: int, month: int) -> date:
    return date(year, month, calendar.monthrange(year, month)[1])


def _monthly_levels(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    level = 100.0
    output: list[dict[str, object]] = []
    for row in sorted(rows, key=lambda item: item["date"]):
        level *= 1 + float(row["market_return_decimal"])
        if not math.isfinite(level) or level <= 0:
            raise BuildError(f"Cumulative market level became invalid at {row['date']}")
        output.append({"date": row["date"], "value": level, "sourceId": row["source_id"]})
    return output


def _control_at(controls: list[dict[str, str]], decision_date: str) -> dict[str, str] | None:
    for control in controls:
        if control["startDate"] <= decision_date < control["endDate"]:
            return control
    return None


def _source_catalog(config: PipelineConfig, market_source_id: str, controls: list[dict[str, str]]) -> list[dict[str, object]]:
    used = {market_source_id, *(row["sourceId"] for row in controls)}
    records: list[dict[str, object]] = []
    for source in config.sources:
        if source.id in used:
            records.append({"id": source.id, "title": source.title, "locator": source.url, "note": f"{source.role}; {source.authority}"})
    missing = used - {record["id"] for record in records}
    if missing:
        raise BuildError(f"Controls reference source IDs absent from source config: {', '.join(sorted(missing))}")
    return records


def _errors(issues: list[Issue]) -> list[Issue]:
    return [issue for issue in issues if issue.severity == "ERROR"]


def build_annual_dataset(
    config: PipelineConfig,
    market_path: Path,
    controls_path: Path,
    decision_policy: Literal["window_start", "calendar_year_start"],
) -> tuple[dict[str, object], dict[str, object]]:
    market = read_csv(market_path)
    controls = read_csv(controls_path)
    issues = check_monthly_returns(market) + check_annual_coverage(market, config.annual_start_year - 1, config.annual_end_year) + check_controls(controls)
    errors = _errors(issues)
    if errors:
        message = "; ".join(f"{item.check_id}: {item.message}" for item in errors[:5])
        raise BuildError(f"Cannot build research dataset: {message}")
    levels = _monthly_levels(market)
    level_dates = {row["date"] for row in levels}
    windows: list[dict[str, object]] = []
    required_decisions: list[str] = []
    for year in range(config.annual_start_year, config.annual_end_year + 1):
        start = date(year - 1, 12, 31).isoformat()
        end = date(year, 12, 31).isoformat()
        if start not in level_dates or end not in level_dates:
            raise BuildError(f"Required exact December endpoint unavailable for annual return {year}")
        decision = start if decision_policy == "window_start" else date(year, 1, 1).isoformat()
        required_decisions.append(decision)
        windows.append({"id": f"annual-{year}", "label": str(year), "kind": "CALENDAR_YEAR", "startDate": start, "endDate": end, "decisionDate": decision, "complete": True})
    missing_controls = [decision for decision in required_decisions if _control_at(controls, decision) is None]
    if missing_controls:
        raise BuildError(f"No reviewed political control interval covers decision date(s): {', '.join(missing_controls[:10])}")
    inputs = {"market_sha256": sha256_file(market_path), "controls_sha256": sha256_file(controls_path), "config_sha256": sha256_file(config.path)}
    market_source_ids = {str(row["source_id"]) for row in market}
    if len(market_source_ids) != 1:
        raise BuildError("Monthly market table must contain one declared source ID")
    dataset = {
        "schemaVersion": 1,
        "id": f"annual-crsp-market-proxy-{config.annual_start_year}-{config.annual_end_year}",
        "title": f"Public CRSP-market-proxy annual reconstruction, {config.annual_start_year}–{config.annual_end_year}",
        "kind": "USER_SUPPLIED",
        "currency": config.currency,
        "nominalReal": "NOMINAL",
        "returnBasis": "TOTAL_RETURN",
        "sources": _source_catalog(config, next(iter(market_source_ids)), controls),
        "levels": levels,
        "controls": controls,
        "windows": windows,
        "fundamentals": [],
    }
    manifest = {
        "schema_version": 1,
        "dataset_kind": "PUBLIC_CRSP_MARKET_PROXY_RECONSTRUCTION",
        "exact_replication": False,
        "reason": "The seed article's annual S&P 500 inputs and political assignment convention are unavailable.",
        "decision_policy": decision_policy,
        "inputs": inputs,
        "dataset_sha256": __import__("hashlib").sha256(canonical_json(dataset).encode()).hexdigest(),
        "quality_issues": [issue.as_dict() for issue in issues],
    }
    return dataset, manifest


def write_dataset(output: Path, dataset: dict[str, object], manifest: dict[str, object]) -> None:
    write_json(output, dataset)
    write_json(output.with_suffix(".manifest.json"), manifest)


def write_controls_template(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["id", "startDate", "endDate", "presidentId", "presidentName", "presidentParty", "houseControl", "senateControl", "sourceId"]
    if path.exists():
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
