#!/usr/bin/env python3
"""Pure offline adapters and a synthetic integration run. No network transports."""

import argparse
import hashlib
import json
from datetime import timedelta
from decimal import Decimal
from pathlib import Path

import ledger

ROOT = Path(__file__).resolve().parent


def schedule_windows(calendar, packet_finalized_utc):
    """Choose from supplied sessions; never invent weekdays/holidays or shift for model latency."""
    ledger.require(isinstance(calendar, dict) and isinstance(calendar.get("sessions"), list), "Missing session calendar")
    sessions = calendar["sessions"]
    finalized = ledger.time(packet_finalized_utc)
    previous = None
    session_dates = set()
    for session in sessions:
        opened, closed = ledger.time(session["open_utc"]), ledger.time(session["close_utc"])
        ledger.require(opened < closed and (previous is None or opened >= previous), "Unordered, overlapping or invalid sessions")
        ledger.require(opened.astimezone(ledger.NY).date().isoformat() == session["session_date"], "Session date/timezone mismatch")
        ledger.require(session["session_date"] not in session_dates and closed.astimezone(ledger.NY).date().isoformat() == session["session_date"], "Duplicate or cross-date regular session")
        ledger.require(opened + timedelta(minutes=10) <= closed, "Session cannot support price window")
        previous = closed
        session_dates.add(session["session_date"])
    index = next((i for i, s in enumerate(sessions) if ledger.time(s["open_utc"]) >= finalized + timedelta(minutes=10)), None)
    ledger.require(index is not None and index + 5 < len(sessions), "Calendar does not cover entry and five-session exit")
    opened = ledger.time(sessions[index]["open_utc"])
    exit_open = ledger.time(sessions[index + 5]["open_utc"])
    return {"entry_session_date": sessions[index]["session_date"], "exit_session_date": sessions[index + 5]["session_date"],
            "prediction_cutoff_utc": ledger.stamp(opened - timedelta(minutes=10)),
            "entry_window_start_utc": ledger.stamp(opened + timedelta(minutes=5)),
            "entry_window_end_utc": ledger.stamp(opened + timedelta(minutes=10)),
            "exit_window_start_utc": ledger.stamp(exit_open + timedelta(minutes=5)),
            "exit_window_end_utc": ledger.stamp(exit_open + timedelta(minutes=10)),
            "calendar_sha256": ledger.digest(calendar)}


def window_vwap(bars, start_utc, end_utc, retrieved_at_utc, expected_feed):
    """Aggregate normalized left-labelled minute bars; no feed fallback or missing-bar fill."""
    start, end, retrieved = [ledger.time(x) for x in (start_utc, end_utc, retrieved_at_utc)]
    ledger.require(end - start == timedelta(minutes=5) and retrieved >= end, "Invalid/incomplete five-minute observation window")
    ledger.require(isinstance(expected_feed, str) and expected_feed, "Declare an expected feed")
    expected = {start + timedelta(minutes=i) for i in range(5)}
    selected = {}
    for bar in bars:
        at = ledger.time(bar["start_utc"])
        ledger.require(bar.get("feed") == expected_feed, "Feed changed or fallback attempted")
        ledger.require(at in expected and at not in selected, "Unexpected or duplicate minute bar")
        ledger.require(ledger.number(bar["vwap"]) and bar["vwap"] > 0, "Invalid minute VWAP")
        ledger.require(type(bar["volume"]) is int and bar["volume"] >= 0, "Invalid minute volume")
        selected[at] = bar
    ledger.require(set(selected) == expected, "Missing minute bars; do not forward-fill")
    volume = sum(bar["volume"] for bar in selected.values())
    ledger.require(volume > 0, "Zero observed window volume")
    weighted = sum(Decimal(str(bar["vwap"])) * Decimal(bar["volume"]) for bar in selected.values())
    return {"vwap": float(weighted / Decimal(volume)), "volume": volume, "feed": expected_feed,
            "start_utc": start_utc, "end_utc": end_utc, "retrieved_at_utc": retrieved_at_utc,
            "bars_sha256": ledger.digest(bars)}


def momentum_feature(stock, benchmark, packet_finalized_utc):
    """Requires 21 matched, explicitly as-of total-return levels for a 20-session feature."""
    ledger.require(len(stock) == len(benchmark) == 21, "Momentum requires 21 observed levels")
    finalized = ledger.time(packet_finalized_utc)
    dates = []
    for lhs, rhs in zip(stock, benchmark):
        ledger.require(lhs["session_date"] == rhs["session_date"], "Momentum session mismatch")
        for row in (lhs, rhs):
            ledger.require(row.get("asof_adjustments_verified") is True, "As-of corporate-action convention not verified")
            ledger.require(ledger.number(row["total_return_level"]) and row["total_return_level"] > 0, "Invalid total-return level")
            ledger.require(ledger.time(row["available_at_utc"]) <= finalized and ledger.time(row["session_close_utc"]) <= ledger.time(row["available_at_utc"]), "Future or inconsistent momentum input")
            ledger.require(ledger.time(row["session_close_utc"]).astimezone(ledger.NY).date().isoformat() == row["session_date"], "Momentum date/time mismatch")
        dates.append(lhs["session_date"])
    ledger.require(dates == sorted(set(dates)), "Duplicate/unordered momentum sessions")
    stock_return = stock[-1]["total_return_level"] / stock[0]["total_return_level"] - 1
    benchmark_return = benchmark[-1]["total_return_level"] / benchmark[0]["total_return_level"] - 1
    return {"momentum20_excess": stock_return - benchmark_return,
            "price_features_asof_utc": max([r["available_at_utc"] for r in stock + benchmark], key=ledger.time)}


def sentiment(text, dictionary):
    import re
    ledger.require(isinstance(text, str) and isinstance(dictionary, dict), "Missing text/dictionary")
    groups = []
    for name in ("positive", "negative"):
        words = dictionary.get(name)
        ledger.require(isinstance(words, list) and all(isinstance(w, str) and re.fullmatch(r"[A-Z]+", w) for w in words), "Dictionary must contain normalized uppercase tokens")
        ledger.require(len(words) == len(set(words)), "Duplicate dictionary tokens")
        groups.append(set(words))
    ledger.require(not groups[0].intersection(groups[1]), "Ambiguous positive/negative token overlap")
    tokens = re.findall(r"[A-Z]+", text.upper())
    positive = sum(t in groups[0] for t in tokens)
    negative = sum(t in groups[1] for t in tokens)
    return {"positive_count": positive, "negative_count": negative,
            "p_outperform": ledger.sentiment_probability(positive, negative),
            "dictionary_sha256": ledger.digest(dictionary)}


def build_packet(release, raw_bytes, features, windows):
    """Text-only local release normalization; unsupported formats fail rather than truncate."""
    ledger.require(release.get("media_type") == "text/plain", "This adapter requires audited plain-text extraction")
    text = raw_bytes.decode("utf-8")
    ledger.require(bool(text.strip()) and len(text) <= 200000, "Empty/oversize release; no silent truncation")
    normalized = "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")).strip()
    finalized = ledger.time(release["packet_finalized_utc"])
    ledger.require(ledger.time(release["first_seen_utc"]) <= ledger.time(release["download_completed_utc"]) <= finalized, "Invalid release chronology")
    ledger.require(ledger.time(features["price_features_asof_utc"]) <= finalized, "Future packet feature")
    ledger.require(ledger.time(windows["prediction_cutoff_utc"]) >= finalized, "Packet finalized after target cutoff")
    return {"packet_version": "0.1.0", "synthetic": release.get("synthetic") is True,
            "issuer_id": release["issuer_id"], "fiscal_period": release["fiscal_period"],
            "document_sha256": hashlib.sha256(raw_bytes).hexdigest(),
            "source_url": release["url"], "packet_finalized_utc": release["packet_finalized_utc"],
            "sources": [{"source_id": "earnings_release", "text": normalized}],
            "asof_features": features, "windows": windows}


def parse_forecast(raw_text, packet):
    forecast = ledger.loads(raw_text)
    ledger.require(isinstance(forecast, dict) and set(forecast) == {"p_outperform", "rationale", "evidence"}, "Invalid forecast fields")
    ledger.require(ledger.number(forecast["p_outperform"]) and 0 <= forecast["p_outperform"] <= 1, "Invalid probability")
    ledger.require(isinstance(forecast["rationale"], str) and bool(forecast["rationale"].strip()), "Missing rationale")
    evidence = forecast["evidence"]
    ledger.require(isinstance(evidence, list) and bool(evidence), "Missing evidence")
    sources = {s["source_id"]: s["text"] for s in packet["sources"]}
    for cite in evidence:
        ledger.require(isinstance(cite, dict) and set(cite) == {"source_id", "quote"}, "Invalid evidence fields")
        ledger.require(isinstance(cite["source_id"], str) and cite["source_id"] in sources and isinstance(cite["quote"], str) and bool(cite["quote"].strip()) and cite["quote"] in sources[cite["source_id"]], "Non-verbatim or unknown evidence source")
    # This validates literal support, not whether the inference is economically justified.
    return forecast


def price_return(entry_price, exit_price, corporate_action_status):
    ledger.require(corporate_action_status == "verified_none", "Corporate-action return adapter required; do not assume no actions")
    ledger.require(ledger.number(entry_price) and entry_price > 0 and ledger.number(exit_price) and exit_price >= 0, "Invalid price inputs")
    return float(Decimal(str(exit_price)) / Decimal(str(entry_price)) - 1)


def forecast_conditions(raw_text, packet, dictionary):
    """Retain bad model output as a failed condition while preserving valid baselines."""
    baseline = sentiment(packet["sources"][0]["text"], dictionary)
    error = ""
    try:
        model = parse_forecast(raw_text, packet)
        llm = {"status": "completed", "p_outperform": model["p_outperform"]}
    except (ValueError, TypeError, KeyError) as exc:
        llm = {"status": "invalid_output", "p_outperform": None}
        error = str(exc)
    return {"llm": llm, "dictionary": {"status": "completed", "p_outperform": baseline["p_outperform"]},
            "momentum": {"status": "completed", "p_outperform": ledger.momentum_probability(packet["asof_features"]["momentum20_excess"])},
            "no_signal": {"status": "completed", "p_outperform": .5}}, error


def dry_run(directory, fixture=None):
    """All clocks, sources, prices, forecasts, and model-call metadata are invented fixtures."""
    fixture = fixture if fixture is not None else ledger.load(ROOT / "offline-fixture.json")
    ledger.require(fixture.get("synthetic") is True and fixture.get("empirical_evidence") is False, "Dry-run inputs must be explicitly synthetic")
    path = Path(directory)
    ledger.require(not path.exists(), "Dry-run output must be a new directory")
    path.mkdir(parents=True)
    windows = schedule_windows(fixture["calendar"], fixture["release"]["packet_finalized_utc"])
    features = momentum_feature(fixture["stock_history"], fixture["benchmark_history"], fixture["release"]["packet_finalized_utc"])
    packet = build_packet(fixture["release"], fixture["release_text"].encode(), features, windows)
    ledger.write_new(path / "synthetic-packet.json", packet)
    predictions, model_error = forecast_conditions(fixture["mock_model_output"], packet, fixture["toy_dictionary"])
    manifest = ledger.load(ROOT / "manifest.example.json")
    manifest["study_id"] = "SYNTHETIC_OFFLINE_INTEGRATION_ONLY"
    manifest["notes"] = "All observations and clock values in this session are software fixtures, not prospective research."
    ledger.initialize(path / "session", manifest, "development", ledger.time("2026-10-27T12:00:00Z"))
    template = ledger.load(ROOT / "opportunity.template.json")
    template.update(record_id="synthetic-opportunity", issuer_id=packet["issuer_id"], fiscal_period=packet["fiscal_period"],
                    eligibility="eligible", reason="Synthetic integration fixture only", document_url=packet["source_url"],
                    document_sha256=packet["document_sha256"], packet_sha256=ledger.digest(packet),
                    source_public_at_utc=None, source_first_seen_utc=fixture["release"]["first_seen_utc"],
                    download_completed_utc=fixture["release"]["download_completed_utc"], packet_finalized_utc=fixture["release"]["packet_finalized_utc"],
                    source_timing_verified=False, source_timing_evidence_ref=None, source_ref="synthetic-packet.json", **features)
    template.update({k: windows[k] for k in ("prediction_cutoff_utc", "entry_window_start_utc", "entry_window_end_utc", "exit_window_start_utc", "exit_window_end_utc")})
    ledger.append(path / "session", template, ledger.time("2026-10-27T12:02:00Z"))
    (path / "synthetic-model-output.txt").write_text(fixture["mock_model_output"])
    prediction = ledger.load(ROOT / "prediction.template.json")
    prediction.update(record_id="synthetic-prediction", opportunity_id="synthetic-opportunity",
                      predictions=predictions,
                      model_snapshot="SYNTHETIC_MOCK_NOT_A_PROVIDER_MODEL", model_started_utc="2026-10-27T12:03:00Z",
                      model_completed_utc="2026-10-27T12:03:01Z", request_count=1, model_cost_usd=0,
                      model_response_sha256=hashlib.sha256(fixture["mock_model_output"].encode()).hexdigest(),
                      model_response_ref="synthetic-model-output.txt", error=model_error)
    receipt = ledger.append(path / "session", prediction, ledger.time("2026-10-27T12:04:00Z"))
    prices = {}
    for key, bars in fixture["bars"].items():
        side = "entry" if key.endswith("entry") else "exit"
        prices[key] = window_vwap(bars, windows[f"{side}_window_start_utc"], windows[f"{side}_window_end_utc"], fixture["price_retrieved_at_utc"], "SYNTHETIC_CONSOLIDATED_FIXTURE")
    stock_return = price_return(prices["stock_entry"]["vwap"], prices["stock_exit"]["vwap"], "verified_none")
    benchmark_return = price_return(prices["benchmark_entry"]["vwap"], prices["benchmark_exit"]["vwap"], "verified_none")
    ledger.write_new(path / "synthetic-prices.json", prices)
    outcome = ledger.load(ROOT / "outcome.template.json")
    outcome.update(record_id="synthetic-outcome", prediction_id="synthetic-prediction", status="completed",
                   stock_total_return=stock_return, benchmark_total_return=benchmark_return,
                   price_observed_at_utc=fixture["price_retrieved_at_utc"], price_artifact_sha256=ledger.digest(prices),
                   price_artifact_ref="synthetic-prices.json", reason="Invented integration prices; no real security or observation")
    ledger.append(path / "session", outcome, ledger.time("2026-11-03T15:01:00Z"))
    _, records, head = ledger.inspect(path / "session")
    target = int(stock_return > benchmark_return)
    report = {"synthetic": True, "empirical_evidence": False, "network_requests": 0, "external_model_requests": 0,
              "simulated_model_requests": 1, "real_predictions": 0, "independent_timing_verified": False,
              "events": len(records), "prediction_record_sha256": receipt["record_sha256"], "head_sha256": head,
              "conditions": {c: {"brier_loss": ledger.brier_loss(v["p_outperform"], target),
                                  "paper_return_at_10bps_per_side": ledger.paper_long_return(stock_return, v["p_outperform"])} for c, v in prediction["predictions"].items()},
              "note": "These numbers only validate software wiring. Do not use them as article findings or prospective forecasts."}
    ledger.write_new(path / "synthetic-report.json", report)
    return report


def readiness():
    bindings = ledger.load(ROOT / "bindings.example.json")
    return {"execution_policy": bindings["execution_policy"], "live_requests_enabled": False,
            "live_ready": False, "missing_bindings": [name for name, value in bindings["sources"].items() if value["status"] != "verified"],
            "ledger_core_fingerprint": ledger.fingerprint(),
            "offline_component_sha256": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in ("pipeline.py", "receipts.py", "offline-fixture.json", "bindings.example.json")},
            "scope": "Local configuration assessment; no credential values read and no connection probes performed"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("readiness")
    run = commands.add_parser("dry-run")
    run.add_argument("--out", required=True)
    args = parser.parse_args()
    result = readiness() if args.command == "readiness" else dry_run(args.out)
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as exc:
        import sys
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        sys.exit(2)
