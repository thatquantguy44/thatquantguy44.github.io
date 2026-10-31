from __future__ import annotations

import csv
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from presidential_data_pipeline.assemble import BuildError, build_annual_dataset
from presidential_data_pipeline.config import load_config


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

    def write_controls(self, path: Path, overlapping: bool = False) -> None:
        fields = ["id", "startDate", "endDate", "presidentId", "presidentName", "presidentParty", "houseControl", "senateControl", "sourceId"]
        rows = [{"id": "reviewed-1", "startDate": "1935-01-01", "endDate": "2024-01-01", "presidentId": "reviewed-president", "presidentName": "Reviewed record", "presidentParty": "D", "houseControl": "D", "senateControl": "D", "sourceId": "HOUSE_GOV_001"}]
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
