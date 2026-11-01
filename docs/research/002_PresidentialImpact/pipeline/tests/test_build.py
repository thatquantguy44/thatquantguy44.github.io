from __future__ import annotations

import csv
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from presidential_data_pipeline.assemble import BuildError, build_annual_dataset
from presidential_data_pipeline.config import ConfigError, load_config
from presidential_data_pipeline.pipeline import prepare_control_review, validate_controls_file
from presidential_data_pipeline.quality import check_monthly_returns
from presidential_data_pipeline.provenance import read_json


def month_end(year: int, month: int) -> date:
    if month == 12:
        return date(year, 12, 31)
    return date.fromordinal(date(year, month + 1, 1).toordinal() - 1)


class BuildTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(__file__).resolve().parents[1]
        self.config = load_config(self.root / "config" / "sources.toml")

    def write_market(self, path: Path) -> None:
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=["date", "market_return_decimal", "source_id"])
            writer.writeheader()
            for year in range(1935, 2024):
                for month in range(1, 13):
                    writer.writerow({"date": month_end(year, month).isoformat(), "market_return_decimal": "0.001", "source_id": "FF_MKT_001"})

    def write_controls(self, path: Path, overlapping: bool = False, source_id: str = "CTRL_074_A") -> None:
        fields = ["id", "startDate", "endDate", "presidentId", "presidentName", "presidentParty", "houseControl", "senateControl", "sourceId"]
        rows = [{"id": "reviewed-1", "startDate": "1935-01-01", "endDate": "2024-01-01", "presidentId": "reviewed-president", "presidentName": "Reviewed record", "presidentParty": "D", "houseControl": "D", "senateControl": "D", "sourceId": source_id}]
        if overlapping:
            rows.append({**rows[0], "id": "overlap", "startDate": "1940-01-01"})
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def test_builds_user_supplied_proxy_with_explicit_decision_policy(self) -> None:
        with TemporaryDirectory() as temporary:
            directory = Path(temporary)
            market, controls = directory / "market.csv", directory / "controls.csv"
            self.write_market(market)
            self.write_controls(controls)
            dataset, manifest = build_annual_dataset(self.config, market, controls, "window_start")
        self.assertEqual(dataset["kind"], "USER_SUPPLIED")
        self.assertEqual(dataset["returnBasis"], "TOTAL_RETURN")
        self.assertEqual(len(dataset["windows"]), 88)
        self.assertEqual(dataset["windows"][0]["decisionDate"], "1935-12-31")
        self.assertFalse(manifest["exact_replication"])
        self.assertEqual(manifest["decision_policy"], "window_start")

    def test_blocks_overlapping_controls_before_writing_research_data(self) -> None:
        with TemporaryDirectory() as temporary:
            directory = Path(temporary)
            market, controls = directory / "market.csv", directory / "controls.csv"
            self.write_market(market)
            self.write_controls(controls, overlapping=True)
            with self.assertRaisesRegex(BuildError, "controls.overlap"):
                build_annual_dataset(self.config, market, controls, "calendar_year_start")

    def test_registers_disabled_manual_control_evidence_without_fetching_it(self) -> None:
        source = self.config.source("CTRL_074_A")
        self.assertFalse(source.enabled)
        self.assertEqual(source.parser, "manual_reviewed_control_evidence")
        self.assertEqual(source.captured_at, "2026-10-31T17:54:33Z")
        self.assertEqual(source.captured_sha256, "dd79cf46562091e216dccc7dfbf1ffb4fecf6561a94e8c930bd4d04c0b42dce3")
        self.assertIn("https://www.senate.gov/about/parties-leadership/party-division.htm", source.locators)
        self.assertEqual(source.captures[0].sha256, source.captured_sha256)
        self.assertEqual(len(source.captures), len(source.locators))
        general_bundle = self.config.source("CTRL_GOV_001")
        self.assertEqual(len(general_bundle.captures), 3)
        self.assertEqual(
            {capture.sha256 for capture in general_bundle.captures},
            {
                "7712424eb2ac8a7ca83a02e494d14a795253bccc0c6f9275c73e31822d692b55",
                "2be84a8b5cc5c71ba08ee3bf499712e6b5131a9ef8a215ac83c9c3b5625cf9f0",
                "65400bbe9f162a2b1b7d05df39b928f3ba4c4b6a0af1d7bbe71496232edfe17f",
            },
        )

    def test_exports_registered_manual_evidence_in_source_catalog(self) -> None:
        with TemporaryDirectory() as temporary:
            directory = Path(temporary)
            market, controls = directory / "market.csv", directory / "controls.csv"
            self.write_market(market)
            self.write_controls(controls, source_id="CTRL_074_A")
            dataset, _ = build_annual_dataset(self.config, market, controls, "window_start")
        bundle = next(record for record in dataset["sources"] if record["id"] == "CTRL_074_A")
        self.assertEqual(set(bundle), {"id", "title", "locator", "note"})
        self.assertIn("https://www.senate.gov/about/parties-leadership/party-division.htm", bundle["note"])
        self.assertIn("SHA-256 dd79cf46562091e216dccc7dfbf1ffb4fecf6561a94e8c930bd4d04c0b42dce3", bundle["note"])
        self.assertIn("evidence captures:", bundle["note"])

    def test_validates_registered_control_before_full_history_is_complete(self) -> None:
        with TemporaryDirectory() as temporary:
            controls = Path(temporary) / "controls.csv"
            self.write_controls(controls, source_id="CTRL_074_A")
            report = validate_controls_file(self.config, controls)
        self.assertEqual(report["errors"], 0)

    def test_rejects_control_source_absent_from_catalog(self) -> None:
        with TemporaryDirectory() as temporary:
            controls = Path(temporary) / "controls.csv"
            self.write_controls(controls, source_id="UNKNOWN_SOURCE")
            report = validate_controls_file(self.config, controls)
        self.assertEqual(report["errors"], 1)
        self.assertEqual(report["issues"][0]["check_id"], "controls.source_catalog")

    def test_rejects_candidate_source_as_a_control_source(self) -> None:
        with TemporaryDirectory() as temporary:
            directory = Path(temporary)
            market, controls = directory / "market.csv", directory / "controls.csv"
            self.write_market(market)
            self.write_controls(controls, source_id="HOUSE_GOV_001")
            report = validate_controls_file(self.config, controls)
            with self.assertRaisesRegex(BuildError, "controls.source_role"):
                build_annual_dataset(self.config, market, controls, "window_start")
        self.assertEqual(report["errors"], 1)
        self.assertEqual(report["issues"][0]["check_id"], "controls.source_role")

    def test_rejects_duplicate_calendar_month_with_different_dates(self) -> None:
        issues = check_monthly_returns([
            {"date": "1936-01-30", "market_return_decimal": "0.01", "source_id": "FF_MKT_001"},
            {"date": "1936-01-31", "market_return_decimal": "0.02", "source_id": "FF_MKT_001"},
        ])
        self.assertEqual({issue.check_id for issue in issues}, {"market.valid", "market.unique"})

    def test_rejects_manual_evidence_bundle_with_unpinned_locator(self) -> None:
        with TemporaryDirectory() as temporary:
            config_path = Path(temporary) / "sources.toml"
            config_path.write_text(
                """[pipeline]
schema_version = 1
project_id = "test"
currency = "USD"
annual_start_year = 1936
annual_end_year = 2023

[[source]]
id = "CTRL_TEST"
title = "Test evidence"
url = "https://example.test/evidence"
locators = ["https://example.test/evidence"]
parser = "manual_reviewed_control_evidence"
authority = "Test authority"
role = "manual_reviewed_political_control_evidence"
enabled = false
""",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ConfigError, "without a content-pinned capture"):
                load_config(config_path)

    def test_prepares_review_only_candidates_without_promoting_them_to_controls(self) -> None:
        fields = ["congress", "start_year", "end_year", "house_party", "senate_party", "president_party", "president_label", "source_id", "review_status"]
        rows = [
            {"congress": "73", "start_year": "1933", "end_year": "1935", "house_party": "D", "senate_party": "D", "president_party": "D", "president_label": "Roosevelt", "source_id": "HOUSE_GOV_001", "review_status": "CANDIDATE_REQUIRES_DATED_REVIEW"},
            {"congress": "74", "start_year": "1935", "end_year": "1937", "house_party": "D", "senate_party": "D", "president_party": "D", "president_label": "Roosevelt", "source_id": "HOUSE_GOV_001", "review_status": "CANDIDATE_REQUIRES_DATED_REVIEW"},
            {"congress": "118", "start_year": "2023", "end_year": "2025", "house_party": "R", "senate_party": "D", "president_party": "D", "president_label": "Biden", "source_id": "HOUSE_GOV_001", "review_status": "CANDIDATE_REQUIRES_DATED_REVIEW"},
            {"congress": "119", "start_year": "2025", "end_year": "2027", "house_party": "R", "senate_party": "R", "president_party": "R", "president_label": "Trump", "source_id": "HOUSE_GOV_001", "review_status": "CANDIDATE_REQUIRES_DATED_REVIEW"},
        ]
        wikipedia_fields = [
            "congress", "start_year", "end_year", "senate_total", "senate_democrat_count", "senate_republican_count", "senate_other_count", "senate_vacancies",
            "house_total", "house_democrat_count", "house_republican_count", "house_other_count", "house_vacancies", "president_label", "trifecta_label",
            "within_congress_variation_hint", "source_id", "review_status",
        ]
        wikipedia_rows = [
            {"congress": "74", "start_year": "1935", "end_year": "1937", "senate_total": "96", "senate_democrat_count": "69", "senate_republican_count": "25", "senate_other_count": "2", "senate_vacancies": "—", "house_total": "435", "house_democrat_count": "322", "house_republican_count": "103", "house_other_count": "10", "house_vacancies": "—", "president_label": "", "trifecta_label": "Yes", "within_congress_variation_hint": "FALSE", "source_id": "WIKI_CONGRESS_001", "review_status": "SECONDARY_CROSSCHECK_ONLY"},
            {"congress": "118", "start_year": "2023", "end_year": "2025", "senate_total": "100", "senate_democrat_count": "47/48", "senate_republican_count": "49", "senate_other_count": "3/4", "senate_vacancies": "—", "house_total": "435", "house_democrat_count": "212/213", "house_republican_count": "222/220", "house_other_count": "—", "house_vacancies": "2/1", "president_label": "", "trifecta_label": "No", "within_congress_variation_hint": "TRUE", "source_id": "WIKI_CONGRESS_001", "review_status": "SECONDARY_CROSSCHECK_ONLY"},
        ]
        with TemporaryDirectory() as temporary:
            directory = Path(temporary)
            candidates, wikipedia, output = directory / "candidates.csv", directory / "wikipedia.csv", directory / "control_review_candidates.csv"
            with candidates.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)
            with wikipedia.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=wikipedia_fields)
                writer.writeheader()
                writer.writerows(wikipedia_rows)
            result = prepare_control_review(self.config, candidates, wikipedia, output)
            with output.open(newline="", encoding="utf-8") as handle:
                review_rows = list(csv.DictReader(handle))
            manifest = read_json(output.with_suffix(".manifest.json"), {})
        self.assertEqual(result["candidates"], 2)
        self.assertEqual([row["congress"] for row in review_rows], ["74", "118"])
        self.assertNotIn("startDate", review_rows[0])
        self.assertIn("mid-Congress changes", review_rows[0]["reviewRequired"])
        self.assertEqual(review_rows[1]["wikipediaVariationHint"], "TRUE")
        self.assertFalse(manifest["controls_file_eligible"])
        self.assertEqual(manifest["decision_window"]["first_decision_date"], "1935-12-31")
