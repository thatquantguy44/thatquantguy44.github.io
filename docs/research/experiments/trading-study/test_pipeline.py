"""Offline adapter tests; all inputs are invented and cannot support research claims."""

import copy
import json
import socket
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch

import ledger
import pipeline


class OfflinePipelineTests(unittest.TestCase):
    def setUp(self):
        self.fixture = ledger.load(pipeline.ROOT / "offline-fixture.json")
        self.finalized = self.fixture["release"]["packet_finalized_utc"]
        self.windows = pipeline.schedule_windows(self.fixture["calendar"], self.finalized)

    def test_calendar_indices_handle_dst_without_calendar_day_arithmetic(self):
        self.assertEqual(self.windows["entry_session_date"], "2026-10-27")
        self.assertEqual(self.windows["exit_session_date"], "2026-11-03")
        self.assertEqual(ledger.time(self.windows["entry_window_start_utc"]).hour, 13)
        self.assertEqual(ledger.time(self.windows["exit_window_start_utc"]).hour, 14)

    def test_packet_too_late_for_open_selects_next_supplied_session(self):
        windows = pipeline.schedule_windows(self.fixture["calendar"], "2026-10-27T13:21:00Z")
        self.assertEqual(windows["entry_session_date"], "2026-10-28")
        self.assertEqual(windows["exit_session_date"], "2026-11-04")

    def test_incomplete_calendar_does_not_invent_exit(self):
        cal = copy.deepcopy(self.fixture["calendar"])
        cal["sessions"] = cal["sessions"][:5]
        with self.assertRaisesRegex(ValueError, "does not cover"):
            pipeline.schedule_windows(cal, self.finalized)

    def test_early_close_uses_supplied_close(self):
        cal = copy.deepcopy(self.fixture["calendar"])
        cal["sessions"][0]["close_utc"] = "2026-10-27T17:00:00Z"
        self.assertEqual(pipeline.schedule_windows(cal, self.finalized)["entry_session_date"], "2026-10-27")

    def test_multiple_core_sessions_on_one_date_are_rejected(self):
        cal = copy.deepcopy(self.fixture["calendar"])
        cal['sessions'][0]['close_utc'] = '2026-10-27T16:00:00Z'
        cal['sessions'].insert(1, {'session_date': '2026-10-27', 'open_utc': '2026-10-27T17:00:00Z', 'close_utc': '2026-10-27T20:00:00Z'})
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            pipeline.schedule_windows(cal, self.finalized)

    def test_vwap_weights_prices_by_observed_volume(self):
        bars = copy.deepcopy(self.fixture["bars"]["stock_entry"])
        for i, bar in enumerate(bars):
            bar.update(vwap=100 + i, volume=10 * (i + 1))
        result = pipeline.window_vwap(bars, self.windows["entry_window_start_utc"], self.windows["entry_window_end_utc"], self.fixture["price_retrieved_at_utc"], "SYNTHETIC_CONSOLIDATED_FIXTURE")
        self.assertAlmostEqual(result["vwap"], 15400 / 150)
        self.assertEqual(result["volume"], 150)

    def test_missing_bar_and_feed_fallback_are_not_silently_accepted(self):
        for mode in ("missing", "wrong_feed", "duplicate", "zero_volume"):
            bars = copy.deepcopy(self.fixture["bars"]["stock_entry"])
            if mode == "missing":
                bars.pop()
            elif mode == "wrong_feed":
                bars[0]["feed"] = "SINGLE_VENUE_FALLBACK"
            elif mode == "duplicate":
                bars.append(copy.deepcopy(bars[0]))
            else:
                for bar in bars:
                    bar["volume"] = 0
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                pipeline.window_vwap(bars, self.windows["entry_window_start_utc"], self.windows["entry_window_end_utc"], self.fixture["price_retrieved_at_utc"], "SYNTHETIC_CONSOLIDATED_FIXTURE")

    def test_cannot_observe_price_window_before_it_finishes(self):
        with self.assertRaises(ValueError):
            pipeline.window_vwap(self.fixture["bars"]["stock_entry"], self.windows["entry_window_start_utc"], self.windows["entry_window_end_utc"], self.windows["entry_window_start_utc"], "SYNTHETIC_CONSOLIDATED_FIXTURE")

    def test_momentum_uses_matched_asof_total_return_levels(self):
        value = pipeline.momentum_feature(self.fixture["stock_history"], self.fixture["benchmark_history"], self.finalized)
        self.assertAlmostEqual(value["momentum20_excess"], .12 - .10)
        self.assertEqual(value["price_features_asof_utc"], "2026-10-26T20:30:00Z")

    def test_future_or_unverified_momentum_input_is_rejected(self):
        for mode in ("future", "unverified", "mismatched"):
            stock = copy.deepcopy(self.fixture["stock_history"])
            if mode == "future":
                stock[-1]["available_at_utc"] = "2026-10-28T20:30:00Z"
            elif mode == "unverified":
                stock[-1]["asof_adjustments_verified"] = False
            else:
                stock[-1]["session_date"] = "2026-10-25"
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                pipeline.momentum_feature(stock, self.fixture["benchmark_history"], self.finalized)

    def test_repeated_dictionary_tokens_and_smoothing(self):
        result = pipeline.sentiment("profit PROFIT loss", self.fixture["toy_dictionary"])
        self.assertEqual((result["positive_count"], result["negative_count"]), (2, 1))
        self.assertAlmostEqual(result["p_outperform"], (1 + 1 / 23) / 2)

    def test_ambiguous_dictionary_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "overlap"):
            pipeline.sentiment("PROFIT", {"positive": ["PROFIT"], "negative": ["PROFIT"]})

    def packet(self):
        features = pipeline.momentum_feature(self.fixture["stock_history"], self.fixture["benchmark_history"], self.finalized)
        return pipeline.build_packet(self.fixture["release"], self.fixture["release_text"].encode(), features, self.windows)

    def test_packet_and_model_output_remain_literal_and_traceable(self):
        packet = self.packet()
        forecast = pipeline.parse_forecast(self.fixture["mock_model_output"], packet)
        self.assertEqual(forecast["p_outperform"], .7)
        self.assertTrue(packet["synthetic"])

    def test_bad_model_output_cannot_enter_a_valid_forecast(self):
        for mode in ("extra_outcome", "fabricated_quote", "boolean", "empty_evidence"):
            value = json.loads(self.fixture["mock_model_output"])
            if mode == "extra_outcome":
                value["future_return"] = .02
            elif mode == "fabricated_quote":
                value["evidence"][0]["quote"] = "Guaranteed outperformance."
            elif mode == "boolean":
                value["p_outperform"] = True
            else:
                value["evidence"] = []
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                pipeline.parse_forecast(json.dumps(value), self.packet())

    def test_unhandled_corporate_actions_cannot_be_assumed_away(self):
        self.assertAlmostEqual(pipeline.price_return(100, 102, "verified_none"), .02)
        for status in (None, "unknown", "dividend", "split"):
            with self.subTest(status=status), self.assertRaises(ValueError):
                pipeline.price_return(100, 102, status)

    def test_integration_succeeds_with_network_creation_disabled(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "synthetic"
            with patch.object(socket, "socket", side_effect=AssertionError("Network forbidden")), patch.object(socket, "getaddrinfo", side_effect=AssertionError("DNS forbidden")):
                report = pipeline.dry_run(out)
            self.assertTrue(report["synthetic"])
            self.assertFalse(report["empirical_evidence"])
            self.assertEqual(report["network_requests"], 0)
            self.assertEqual(report["external_model_requests"], 0)
            self.assertEqual(report["events"], 3)
            session, rows, _ = ledger.inspect(out / "session")
            self.assertEqual(session["mode"], "development")
            self.assertFalse(rows[0]["derived"]["primary_eligible_claim"])
            self.assertFalse(rows[1]["derived"]["independent_timing_verified"])
            with self.assertRaises(ValueError):
                pipeline.dry_run(out)

    def test_readiness_does_not_promote_documentation_to_account_access(self):
        result = pipeline.readiness()
        self.assertEqual(result["execution_policy"], "offline_only")
        self.assertFalse(result["live_ready"])
        self.assertFalse(result["live_requests_enabled"])
        self.assertIn("model", result["missing_bindings"])

    def test_invalid_model_output_is_logged_as_failure_without_losing_baselines(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["mock_model_output"] = 'not valid JSON'
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / 'synthetic-invalid-output'
            report = pipeline.dry_run(out, fixture)
            _, rows, _ = ledger.inspect(out / 'session')
            conditions = rows[1]['payload']['predictions']
            self.assertEqual(conditions['llm'], {'status': 'invalid_output', 'p_outperform': None})
            self.assertEqual(conditions['dictionary']['status'], 'completed')
            self.assertIsNone(report['conditions']['llm']['brier_loss'])
            self.assertEqual((out / 'synthetic-model-output.txt').read_text(), 'not valid JSON')


if __name__ == "__main__":
    unittest.main()
