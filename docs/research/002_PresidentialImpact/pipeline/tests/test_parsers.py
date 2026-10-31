from __future__ import annotations

import io
import ssl
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from zipfile import ZipFile

from presidential_data_pipeline.parsers import (
    ParseError,
    parse_fama_french_monthly_zip,
    parse_fred_csv,
    parse_house_party_government_html,
    parse_shiller_xls,
)
from presidential_data_pipeline.fetch import certificate_context
from presidential_data_pipeline.quality import check_political_candidates, check_policy_rates, check_shiller_context


def factor_zip(text: str) -> bytes:
    payload = io.BytesIO()
    with ZipFile(payload, "w") as archive:
        archive.writestr("F-F_Research_Data_Factors.CSV", text)
    return payload.getvalue()


class ParserTests(unittest.TestCase):
    def test_certificate_context_keeps_tls_verification_enabled(self) -> None:
        context = certificate_context()
        self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)
        self.assertTrue(context.check_hostname)

    def test_compounds_market_excess_and_risk_free_without_renaming_the_proxy(self) -> None:
        rows = parse_fama_french_monthly_zip(factor_zip(
            "Notes\n,Mkt-RF,SMB,HML,RF\n193601, 2.00, 0.00, 0.00, 0.10\n193602,-1.00,0.00,0.00,0.05\nAnnual Factors: January-December\n"
        ), "FF_MKT_001")
        self.assertEqual(rows, [
            {"date": "1936-01-31", "market_return_decimal": "0.021", "source_id": "FF_MKT_001"},
            {"date": "1936-02-29", "market_return_decimal": "-0.0095", "source_id": "FF_MKT_001"},
        ])

    def test_rejects_factor_file_without_monthly_header(self) -> None:
        with self.assertRaisesRegex(ParseError, "header"):
            parse_fama_french_monthly_zip(factor_zip("No usable table\n"), "FF_MKT_001")

    def test_fred_parser_omits_missing_marks_without_turning_them_into_zero(self) -> None:
        rows = parse_fred_csv(b"observation_date,FEDFUNDS\n1970-01-01,8.98\n1970-02-01,.\n", "FEDFUNDS_001")
        self.assertEqual(rows, [{"date": "1970-01-01", "policy_rate_percent": "8.98", "source_id": "FEDFUNDS_001"}])

    def test_rejects_nonfinite_source_values(self) -> None:
        with self.assertRaisesRegex(ParseError, "Non-finite"):
            parse_fred_csv(b"observation_date,FEDFUNDS\n1970-01-01,NaN\n", "FEDFUNDS_001")

    def test_house_parser_keeps_candidate_status_and_ambiguous_party(self) -> None:
        html = b"""<table><tr><th>Congress</th><th>House Majority</th><th>Senate Majority</th><th>Presidency</th></tr>
        <tr><td>74th (1935-1937)</td><td>Democrats</td><td>Democrats</td><td>Democrat (Roosevelt)</td></tr>
        <tr><td>107th (2001-2003)</td><td>Republicans</td><td>Tied</td><td>Republican (Bush)</td></tr></table>"""
        rows = parse_house_party_government_html(html, "HOUSE_GOV_001")
        self.assertEqual(rows[0]["president_party"], "D")
        self.assertEqual(rows[1]["senate_party"], "TIED")
        self.assertTrue(all(row["review_status"] == "CANDIDATE_REQUIRES_DATED_REVIEW" for row in rows))

    def test_shiller_parser_keeps_na_cape_missing_and_normalizes_october(self) -> None:
        class Sheet:
            values = [
                ["Notice", "", ""],
                ["Date", "P", "CAPE"],
                ["1871.01", 4.44, "NA"],
                ["1871.1", 4.59, 12.3],
            ]
            nrows = len(values)
            ncols = 3

            def cell_value(self, row: int, column: int) -> object:
                return self.values[row][column]

        class Workbook:
            def sheet_by_name(self, name: str) -> Sheet:
                self_name = name
                if self_name != "Data":
                    raise AssertionError("unexpected worksheet")
                return Sheet()

        fake_xlrd = SimpleNamespace(open_workbook=lambda **_: Workbook())
        with patch.dict(sys.modules, {"xlrd": fake_xlrd}):
            rows = parse_shiller_xls(b"fixture", "SHILLER_001")
        self.assertEqual(rows, [
            {"date": "1871-01-31", "price": "4.44", "cape": "", "source_id": "SHILLER_001"},
            {"date": "1871-10-31", "price": "4.59", "cape": "12.3", "source_id": "SHILLER_001"},
        ])

    def test_context_quality_rules_preserve_missingness_and_candidate_status(self) -> None:
        self.assertEqual(check_shiller_context([
            {"date": "1871-01-31", "price": "4.44", "cape": ""},
        ]), [])
        self.assertTrue(any(issue.check_id == "policy.unique" for issue in check_policy_rates([
            {"date": "1970-01-01", "policy_rate_percent": "8.98"},
            {"date": "1970-01-01", "policy_rate_percent": "8.98"},
        ])))
        self.assertEqual(check_political_candidates([
            {
                "congress": "74", "start_year": "1935", "end_year": "1937",
                "house_party": "D", "senate_party": "D", "president_party": "D",
                "review_status": "CANDIDATE_REQUIRES_DATED_REVIEW",
            },
        ]), [])
