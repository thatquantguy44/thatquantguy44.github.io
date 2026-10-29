"""Synthetic software checks. Injected clocks/records are never research evidence."""

import json
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import ledger


def clock(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def opportunity():
    return {"record_type": "opportunity", "record_id": "synthetic-opportunity",
            "issuer_id": "SYNTHETIC_NOT_A_SECURITY", "fiscal_period": "synthetic-period",
            "eligibility": "eligible", "reason": "Synthetic software fixture",
            "document_url": "https://example.invalid/synthetic", "document_sha256": "a" * 64,
            "packet_sha256": "b" * 64, "source_public_at_utc": "2026-10-27T12:00:30Z",
            "source_first_seen_utc": "2026-10-27T12:01:00Z", "download_completed_utc": "2026-10-27T12:01:05Z",
            "packet_finalized_utc": "2026-10-27T12:01:10Z", "source_timing_verified": True,
            "source_timing_evidence_ref": "synthetic-evidence", "source_ref": "synthetic-source",
            "momentum20_excess": .02, "price_features_asof_utc": "2026-10-26T20:00:00Z",
            "prediction_cutoff_utc": "2026-10-27T13:20:00Z", "entry_window_start_utc": "2026-10-27T13:35:00Z",
            "entry_window_end_utc": "2026-10-27T13:40:00Z", "exit_window_start_utc": "2026-11-03T14:35:00Z",
            "exit_window_end_utc": "2026-11-03T14:40:00Z"}


def prediction():
    return {"record_type": "prediction", "record_id": "synthetic-prediction", "opportunity_id": "synthetic-opportunity",
            "predictions": {"llm": {"status": "completed", "p_outperform": .6},
                            "dictionary": {"status": "completed", "p_outperform": .4},
                            "momentum": {"status": "completed", "p_outperform": .6},
                            "no_signal": {"status": "completed", "p_outperform": .5}},
            "model_snapshot": "synthetic-model-not-a-provider", "model_started_utc": "2026-10-27T12:03:00Z",
            "model_completed_utc": "2026-10-27T12:03:10Z", "request_count": 1, "model_cost_usd": .01,
            "model_response_sha256": "c" * 64, "model_response_ref": "synthetic-response", "error": ""}


def outcome():
    return {"record_type": "outcome", "record_id": "synthetic-outcome", "prediction_id": "synthetic-prediction",
            "status": "completed", "stock_total_return": .02, "benchmark_total_return": .01,
            "price_observed_at_utc": "2026-11-03T14:50:00Z", "price_artifact_sha256": "d" * 64,
            "price_artifact_ref": "synthetic-prices", "reason": "Synthetic software fixture"}


def bound_shape(manifest):
    """Synthetically filled configuration, not verified provider/price evidence."""
    result = json.loads(json.dumps(manifest))
    for key in ("model_provider", "document_provider", "price_provider", "corporate_action_provider", "universe_provider", "calendar_provider", "dictionary_use_basis", "external_receipt_method"):
        result[key] = "synthetic-test-binding"
    for key in ("universe_sha256", "calendar_sha256", "dictionary_sha256", "input_builder_sha256", "baseline_implementation_sha256", "collection_adapter_sha256"):
        result[key] = "f" * 64
    result.update(model_snapshot="synthetic-model-not-a-provider", dictionary_use_authorized=True,
                  cohort_issuer_ids=["SYNTHETIC_NOT_A_SECURITY"] + [f"SYNTHETIC_{i}" for i in range(29)],
                  study_start_date="2026-10-27", study_end_date="2026-12-08",
                  model_parameters={"temperature": 0, "max_input_tokens": 4096, "max_output_tokens": 512,
                                    "reasoning_configuration": {"mode": "synthetic"}, "seed_support": "unsupported", "seed": None},
                  model_pricing={"effective_at_utc": "2026-10-26T00:00:00Z", "input_usd_per_million": 1,
                                 "output_usd_per_million": 1, "reasoning_billing_policy": "synthetic",
                                 "cache_billing_policy": "synthetic", "tool_billing_policy": "synthetic"})
    return result


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "session"
        self.manifest = ledger.load(ledger.ROOT / "manifest.example.json")
        ledger.initialize(self.path, self.manifest, "development", clock("2026-10-27T12:00:00Z"))

    def tearDown(self):
        self.temp.cleanup()

    def add_opportunity(self, value=None):
        return ledger.append(self.path, value or opportunity(), clock("2026-10-27T12:02:00Z"))

    def add_prediction(self, value=None, at="2026-10-27T12:04:00Z"):
        return ledger.append(self.path, value or prediction(), clock(at))

    def prepare(self):
        self.add_opportunity()
        self.add_prediction()

    def test_empty_development_session_is_not_a_live_series(self):
        session, rows, _ = ledger.inspect(self.path)
        self.assertEqual(session["mode"], "development")
        self.assertEqual(rows, [])

    def test_concurrent_writers_preserve_all_unique_records(self):
        def worker(index):
            value = opportunity()
            value['record_id'] = f'synthetic-opportunity-{index}'
            value['issuer_id'] = f'SYNTHETIC_{index}'
            return ledger.append(self.path, value, clock('2026-10-27T12:02:00Z'))
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(worker, range(8)))
        self.assertEqual(len({r['sequence'] for r in results}), 8)
        self.assertEqual(len(ledger.inspect(self.path)[1]), 8)

    def test_unbound_manifest_cannot_start_prospective_series(self):
        with self.assertRaisesRegex(ValueError, "Unbound manifest"):
            ledger.initialize(Path(self.temp.name) / "live", self.manifest, "prospective")

    def test_complete_synthetic_binding_can_freeze_but_is_not_notarized(self):
        path = Path(self.temp.name) / "synthetic-bound-session"
        session = ledger.initialize(path, bound_shape(self.manifest), "prospective", clock("2026-10-27T12:00:00Z"))
        self.assertEqual(session["mode"], "prospective")
        ledger.append(path, opportunity(), clock("2026-10-27T12:02:00Z"))
        result = ledger.append(path, prediction(), clock("2026-10-27T12:04:00Z"))
        self.assertFalse(result["derived"]["independent_timing_verified"])

    def test_pilot_window_and_dictionary_permission_are_required(self):
        for key, value in (("study_end_date", "2026-10-28"), ("dictionary_use_authorized", False)):
            manifest = bound_shape(self.manifest)
            manifest[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                ledger.initialize(Path(self.temp.name) / "bad-binding", manifest, "prospective", clock("2026-10-27T12:00:00Z"))

    def test_live_model_change_requires_a_new_session(self):
        path = Path(self.temp.name) / "synthetic-bound-session"
        ledger.initialize(path, bound_shape(self.manifest), "prospective", clock("2026-10-27T12:00:00Z"))
        ledger.append(path, opportunity(), clock("2026-10-27T12:02:00Z"))
        value = prediction()
        value["model_snapshot"] = "different-synthetic-model"
        with self.assertRaisesRegex(ValueError, "Model snapshot changed"):
            ledger.append(path, value, clock("2026-10-27T12:04:00Z"))

    def test_session_cannot_be_overwritten(self):
        with self.assertRaises(FileExistsError):
            ledger.initialize(self.path, self.manifest, "development")

    def test_saved_schema_matches_validator_contract(self):
        self.assertEqual(ledger.load(ledger.ROOT / "prediction-log.schema.json"), ledger.schema())

    def test_synthetic_three_stage_path_and_hash_chain(self):
        self.prepare()
        result = ledger.append(self.path, outcome(), clock("2026-11-03T15:00:00Z"))
        self.assertEqual(result["derived"]["target_outperform"], 1)
        _, rows, head = ledger.inspect(self.path)
        self.assertEqual(len(rows), 3)
        self.assertEqual(head, result["record_sha256"])
        self.assertFalse(rows[1]["derived"]["independent_timing_verified"])

    def test_future_outcome_is_rejected_without_appending(self):
        self.prepare()
        with self.assertRaisesRegex(ValueError, "before exit"):
            ledger.append(self.path, outcome(), clock("2026-10-27T12:05:00Z"))
        self.assertEqual(len(ledger.inspect(self.path)[1]), 2)

    def test_outcome_field_cannot_be_injected_into_prediction(self):
        self.add_opportunity()
        value = prediction()
        value["stock_total_return"] = .02
        with self.assertRaisesRegex(ValueError, "extra fields"):
            self.add_prediction(value)

    def test_payload_cannot_supply_a_fake_receipt(self):
        value = opportunity()
        value["received_at_utc"] = "2020-01-01T00:00:00Z"
        with self.assertRaisesRegex(ValueError, "extra fields"):
            self.add_opportunity(value)

    def test_probabilities_reject_out_of_range_and_boolean(self):
        self.add_opportunity()
        for probability in (1.1, -.1, True):
            value = prediction()
            value["predictions"]["llm"]["p_outperform"] = probability
            with self.subTest(probability=probability), self.assertRaises(ValueError):
                self.add_prediction(value)

    def test_failed_forecast_is_retained_with_unknown_cost(self):
        self.add_opportunity()
        value = prediction()
        value["predictions"]["llm"] = {"status": "timeout", "p_outperform": None}
        value["model_cost_usd"] = None
        value["error"] = "Synthetic timeout"
        result = self.add_prediction(value)
        self.assertIsNone(result["derived"]["cost_limit_compliant"])
        self.assertFalse(result["derived"]["inference_deadline_compliant"])
        self.assertEqual(len(ledger.inspect(self.path)[1]), 2)

    def test_failed_forecast_cannot_have_a_probability(self):
        self.add_opportunity()
        value = prediction()
        value["predictions"]["llm"]["status"] = "provider_error"
        value["error"] = "Synthetic error"
        with self.assertRaisesRegex(ValueError, "failed probability"):
            self.add_prediction(value)

    def test_late_forecast_is_retained_and_classified_late(self):
        self.add_opportunity()
        result = self.add_prediction(at="2026-10-27T13:21:00Z")
        self.assertEqual(result["derived"]["timing_class"], "late")
        self.assertFalse(result["derived"]["locally_before_cutoff"])
        self.assertFalse(result["derived"]["independent_timing_verified"])

    def test_deadline_is_strict_at_cutoff(self):
        self.add_opportunity()
        result = self.add_prediction(at="2026-10-27T13:20:00Z")
        self.assertFalse(result["derived"]["locally_before_cutoff"])

    def test_duplicate_record_id_rejected(self):
        self.add_opportunity()
        with self.assertRaisesRegex(ValueError, "Duplicate record_id"):
            self.add_opportunity()

    def test_duplicate_issuer_period_is_not_a_fresh_opportunity(self):
        self.add_opportunity()
        value = opportunity()
        value["record_id"] = "duplicate-original-release"
        with self.assertRaisesRegex(ValueError, "fiscal period already"):
            self.add_opportunity(value)
        value["eligibility"] = "excluded"
        value["reason"] = "Duplicate release"
        self.add_opportunity(value)
        self.assertEqual(len(ledger.inspect(self.path)[1]), 2)

    def test_second_prediction_cannot_replace_the_first(self):
        self.prepare()
        value = prediction()
        value["record_id"] = "replacement-forecast"
        with self.assertRaisesRegex(ValueError, "already has a prediction"):
            self.add_prediction(value)

    def test_correction_is_an_annotation_not_an_overwrite(self):
        self.prepare()
        ledger.append(self.path, outcome(), clock("2026-11-03T15:00:00Z"))
        value = outcome()
        value["record_id"] = "replacement-outcome"
        with self.assertRaisesRegex(ValueError, "Outcome already recorded"):
            ledger.append(self.path, value, clock("2026-11-03T15:01:00Z"))
        ledger.append(self.path, {"record_type": "annotation", "record_id": "correction-note", "target_record_id": "synthetic-outcome", "reason": "Synthetic correction requires versioned reanalysis", "evidence_ref": None}, clock("2026-11-03T15:02:00Z"))
        self.assertEqual(len(ledger.inspect(self.path)[1]), 4)

    def test_modified_line_breaks_chain(self):
        self.add_opportunity()
        path = self.path / "events.jsonl"
        row = json.loads(path.read_text())
        row["payload"]["reason"] = "Changed after append"
        path.write_text(json.dumps(row) + "\n")
        with self.assertRaisesRegex(ValueError, "Broken hash chain"):
            ledger.inspect(self.path)

    def test_manifest_change_is_detected(self):
        path = self.path / "session.json"
        session = ledger.load(path)
        session["manifest"]["study_id"] = "changed"
        path.write_text(json.dumps(session))
        with self.assertRaisesRegex(ValueError, "Frozen manifest changed"):
            ledger.inspect(self.path)

    def test_future_source_or_feature_is_rejected(self):
        for key in ("packet_finalized_utc", "price_features_asof_utc"):
            value = opportunity()
            value[key] = "2026-10-28T12:00:00Z"
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.add_opportunity(value)

    def test_model_cannot_start_before_registration(self):
        self.add_opportunity()
        value = prediction()
        value["model_started_utc"] = "2026-10-27T12:01:30Z"
        with self.assertRaisesRegex(ValueError, "before opportunity registration"):
            self.add_prediction(value)

    def test_budget_and_request_violations_are_retained(self):
        self.add_opportunity()
        value = prediction()
        value["request_count"] = 2
        value["model_cost_usd"] = .6
        result = self.add_prediction(value)
        self.assertFalse(result["derived"]["request_limit_compliant"])
        self.assertFalse(result["derived"]["cost_limit_compliant"])

    def test_backwards_receipt_clock_rejected(self):
        self.add_opportunity()
        with self.assertRaisesRegex(ValueError, "clock moved backwards"):
            ledger.append(self.path, prediction(), clock("2026-10-27T12:01:00Z"))

    def test_tied_returns_are_not_outperformance(self):
        self.prepare()
        value = outcome()
        value["stock_total_return"] = value["benchmark_total_return"]
        result = ledger.append(self.path, value, clock("2026-11-03T15:00:00Z"))
        self.assertEqual(result["derived"]["target_outperform"], 0)

    def test_unknown_outcomes_do_not_turn_into_zero_returns(self):
        self.prepare()
        value = outcome()
        value.update(status="unavailable", stock_total_return=None, benchmark_total_return=None, price_observed_at_utc=None, price_artifact_sha256=None, price_artifact_ref=None, reason="Synthetic missing price")
        result = ledger.append(self.path, value, clock("2026-11-03T15:00:00Z"))
        self.assertIsNone(result["derived"]["target_outperform"])

    def test_schema_requires_all_four_forecast_conditions(self):
        self.add_opportunity()
        value = prediction()
        del value["predictions"]["momentum"]
        with self.assertRaisesRegex(ValueError, "missing or extra fields"):
            self.add_prediction(value)

    def test_no_signal_probability_cannot_be_tuned(self):
        self.add_opportunity()
        value = prediction()
        value["predictions"]["no_signal"]["p_outperform"] = .6
        with self.assertRaisesRegex(ValueError, "no_signal"):
            self.add_prediction(value)


class FormulaTests(unittest.TestCase):
    def test_brier_difference_and_unknown_values(self):
        self.assertAlmostEqual(ledger.brier_loss(.6, 1), .16)
        self.assertAlmostEqual(ledger.brier_loss(.6, 1) - ledger.brier_loss(.4, 1), -.20)
        self.assertIsNone(ledger.brier_loss(None, 1))
        self.assertIsNone(ledger.brier_loss(.6, None))

    def test_prefunded_capital_and_both_notional_fees(self):
        entry_stock_notional = Decimal(1) / Decimal('1.001')
        exit_proceeds = entry_stock_notional * Decimal('1.02')
        expected = exit_proceeds - exit_proceeds * Decimal('.001') - Decimal(1)
        self.assertAlmostEqual(ledger.paper_long_return(.02, .6), float(expected))
        self.assertAlmostEqual(ledger.paper_long_return(.02, .6, 0), .02)

    def test_cash_does_not_pay_stock_fees_and_missing_return_stays_unknown(self):
        self.assertEqual(ledger.paper_long_return(.02, .55), 0)
        self.assertEqual(ledger.paper_long_return(.02, None), 0)
        self.assertIsNone(ledger.paper_long_return(None, .6))

    def test_dictionary_zero_matches_and_smoothing(self):
        self.assertEqual(ledger.sentiment_probability(0, 0), .5)
        self.assertAlmostEqual(ledger.sentiment_probability(10, 0), 2 / 3)
        self.assertAlmostEqual(ledger.sentiment_probability(0, 10), 1 / 3)
        with self.assertRaises(ValueError):
            ledger.sentiment_probability(True, 0)

    def test_momentum_scale_and_clipping(self):
        self.assertAlmostEqual(ledger.momentum_probability(.02), .6)
        self.assertEqual(ledger.momentum_probability(.9), 1)
        self.assertEqual(ledger.momentum_probability(-.9), 0)

    def test_json_and_time_formats_are_strict(self):
        for text in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":1e999}'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                ledger.loads(text)
        with self.assertRaises(ValueError):
            ledger.time("2026-10-27")


if __name__ == "__main__":
    unittest.main()
