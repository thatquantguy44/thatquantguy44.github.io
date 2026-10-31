#!/usr/bin/env python3
"""Offline append-only research ledger. No provider calls, orders, or notarization."""

import argparse
import fcntl
import hashlib
import json
import math
import os
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
PROTOCOL = ROOT.parents[1] / "trading-experiment-protocol.md"
VERSION = "0.1.0"
NY = ZoneInfo("America/New_York")
CONDITIONS = ("llm", "dictionary", "momentum", "no_signal")
STATUSES = ("completed", "timeout", "invalid_output", "provider_error", "budget_exhausted", "missing_inputs")


def require(test, message):
    if not test:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def pairs(items):
    value = {}
    for key, item in items:
        require(key not in value, f"Duplicate JSON key: {key}")
        value[key] = item
    return value


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def finite_float(value):
    result = float(value)
    require(math.isfinite(result), "Non-finite JSON number")
    return result


def loads(text):
    return json.loads(text, object_pairs_hook=pairs, parse_float=finite_float,
                      parse_constant=lambda x: require(False, f"Non-finite JSON value: {x}"))


def load(path):
    return loads(Path(path).read_text())


def stamp(now=None):
    return (now or datetime.now(timezone.utc)).astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def time(value):
    require(isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z", value) is not None, "Timestamp must be full UTC date/time ending in Z")
    return datetime.fromisoformat(value[:-1] + "+00:00")


def fingerprint():
    files = [ROOT / x for x in ("ledger.py", "prediction-log.schema.json", "manifest.example.json", "prompt.txt")]
    return digest({p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files + [PROTOCOL]})


def field(kind, nullable=False, **extra):
    return {"type": [kind, "null"] if nullable else kind, **extra}


STRING = field("string", minLength=1)
UTC = field("string", format="date-time")
HASH = field("string", pattern="^[0-9a-f]{64}$")
NULL_HASH = field("string", True, pattern="^[0-9a-f]{64}$")
NULL_UTC = field("string", True, format="date-time")
NULL_STRING = field("string", True, minLength=1)
NONNEG = field("number", minimum=0)
NULL_NONNEG = field("number", True, minimum=0)


def obj(properties, required=None):
    return {"type": "object", "properties": properties,
            "required": list(properties) if required is None else required, "additionalProperties": False}


PREDICTION = obj({"status": field("string", enum=list(STATUSES)),
                  "p_outperform": field("number", True, minimum=0, maximum=1)})
COMMON = {"record_type": STRING, "record_id": field("string", pattern="^[a-zA-Z0-9_-]{1,120}$")}
OPPORTUNITY = {**COMMON, "issuer_id": STRING, "fiscal_period": STRING,
               "eligibility": field("string", enum=["eligible", "excluded", "unresolved"]),
               "reason": field("string"), "document_url": NULL_STRING,
               "document_sha256": NULL_HASH, "packet_sha256": NULL_HASH,
               "source_public_at_utc": NULL_UTC, "source_first_seen_utc": NULL_UTC,
               "download_completed_utc": NULL_UTC, "packet_finalized_utc": NULL_UTC,
               "source_timing_verified": field("boolean"), "source_timing_evidence_ref": NULL_STRING,
               "source_ref": NULL_STRING, "momentum20_excess": field("number", True),
               "price_features_asof_utc": NULL_UTC,
               "prediction_cutoff_utc": NULL_UTC, "entry_window_start_utc": NULL_UTC,
               "entry_window_end_utc": NULL_UTC, "exit_window_start_utc": NULL_UTC,
               "exit_window_end_utc": NULL_UTC}
FORECAST = {**COMMON, "opportunity_id": STRING,
            "predictions": obj({c: PREDICTION for c in CONDITIONS}),
            "model_snapshot": NULL_STRING, "model_started_utc": NULL_UTC,
            "model_completed_utc": NULL_UTC, "request_count": field("integer", minimum=0),
            "model_cost_usd": NULL_NONNEG, "model_response_sha256": NULL_HASH,
            "model_response_ref": NULL_STRING, "error": field("string")}
OUTCOME = {**COMMON, "prediction_id": STRING, "status": field("string", enum=["completed", "unavailable"]),
           "stock_total_return": field("number", True, minimum=-1),
           "benchmark_total_return": field("number", True, minimum=-1),
           "price_observed_at_utc": NULL_UTC, "price_artifact_sha256": NULL_HASH,
           "price_artifact_ref": NULL_STRING, "reason": field("string")}
ANNOTATION = {**COMMON, "target_record_id": STRING, "reason": STRING, "evidence_ref": NULL_STRING}
PAYLOADS = {"opportunity": obj(OPPORTUNITY), "prediction": obj(FORECAST),
            "outcome": obj(OUTCOME), "annotation": obj(ANNOTATION)}


def schema():
    variants = []
    for name, body in PAYLOADS.items():
        variant = loads(json.dumps(body))
        variant["properties"]["record_type"] = {"const": name}
        variants.append(variant)
    return {"$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "Trading study event payload (cross-record rules are in ledger.py)", "oneOf": variants}


def validate_shape(value, spec, path="payload"):
    kind = "null" if value is None else "boolean" if type(value) is bool else "integer" if type(value) is int else "number" if type(value) is float else "string" if isinstance(value, str) else "object" if isinstance(value, dict) else "unknown"
    kinds = spec.get("type", [])
    kinds = [kinds] if isinstance(kinds, str) else kinds
    require(kind in kinds or (kind == "integer" and "number" in kinds), f"{path}: wrong type")
    if value is None:
        return
    if kind in ("integer", "number"):
        require(number(value), f"{path}: number must be finite")
    if number(value):
        require("minimum" not in spec or value >= spec["minimum"], f"{path}: below minimum")
        require("maximum" not in spec or value <= spec["maximum"], f"{path}: above maximum")
    if "enum" in spec:
        require(value in spec["enum"], f"{path}: invalid enum")
    if kind == "string":
        require(len(value) >= spec.get("minLength", 0), f"{path}: empty string")
        require("pattern" not in spec or re.fullmatch(spec["pattern"], value) is not None, f"{path}: invalid format")
        if spec.get("format") == "date-time":
            time(value)
    if kind == "object":
        props = spec["properties"]
        require(set(spec["required"]).issubset(value) and set(value).issubset(props), f"{path}: missing or extra fields")
        for key, item in value.items():
            validate_shape(item, props[key], f"{path}.{key}")


def validate_manifest(manifest, mode, received):
    require(isinstance(manifest, dict), "Manifest must be an object")
    require(manifest.get("protocol_version") == VERSION, "Wrong manifest version")
    require(isinstance(manifest.get("study_id"), str) and manifest["study_id"].strip(), "Missing study ID")
    require(mode in ("development", "prospective"), "Invalid session mode")
    if mode == "development":
        return
    string_fields = ("model_provider", "model_snapshot", "document_provider", "price_provider", "corporate_action_provider", "universe_provider", "calendar_provider", "dictionary_use_basis", "external_receipt_method")
    hashes = ("universe_sha256", "calendar_sha256", "dictionary_sha256", "prompt_sha256", "input_builder_sha256", "baseline_implementation_sha256", "collection_adapter_sha256")
    for key in string_fields:
        require(isinstance(manifest.get(key), str) and bool(manifest[key].strip()), f"Unbound manifest: {key}")
    for key in hashes:
        require(isinstance(manifest.get(key), str) and re.fullmatch("[0-9a-f]{64}", manifest[key]) is not None, f"Unbound manifest hash: {key}")
    require(manifest["prompt_sha256"] == hashlib.sha256((ROOT / "prompt.txt").read_bytes()).hexdigest(), "Prompt hash mismatch")
    require(manifest.get("dictionary_use_authorized") is True, "Dictionary use not resolved")
    cohort = manifest.get("cohort_issuer_ids")
    require(isinstance(cohort, list) and len(cohort) == 30 and all(isinstance(x, str) and x for x in cohort) and len(set(cohort)) == 30, "Freeze exactly 30 unique issuer IDs")
    start, end = date.fromisoformat(manifest["study_start_date"]), date.fromisoformat(manifest["study_end_date"])
    require(start >= time(received).astimezone(NY).date() and end == start + timedelta(days=42), "Pilot dates must start now/later and span 42 days")
    require(isinstance(manifest.get("model_parameters"), dict) and bool(manifest["model_parameters"]), "Missing frozen model parameters")
    require(isinstance(manifest.get("model_pricing"), dict) and bool(manifest["model_pricing"]), "Missing model pricing")
    params, prices = manifest["model_parameters"], manifest["model_pricing"]
    require(number(params.get("temperature")), "Missing temperature")
    for key in ("max_input_tokens", "max_output_tokens"):
        require(type(params.get(key)) is int and params[key] > 0, f"Missing model limit: {key}")
    require(isinstance(params.get("reasoning_configuration"), dict) and bool(params["reasoning_configuration"]), "Missing reasoning configuration")
    require(params.get("seed_support") in ("supported", "unsupported"), "Missing seed support policy")
    require("seed" in params and (params["seed"] is None or type(params["seed"]) is int), "Missing seed value or explicit null")
    require(params["seed_support"] != "supported" or type(params["seed"]) is int, "Supported seed must be bound")
    require(time(prices.get("effective_at_utc")) <= time(received), "Pricing must already be effective at freeze")
    for key in ("input_usd_per_million", "output_usd_per_million"):
        require(number(prices.get(key)) and prices[key] >= 0, f"Missing model price: {key}")
    for key in ("reasoning_billing_policy", "cache_billing_policy", "tool_billing_policy"):
        require(isinstance(prices.get(key), str) and bool(prices[key].strip()), f"Missing billing policy: {key}")
    require(manifest.get("benchmark_security_id") == "SPY", "Protocol benchmark mismatch")


def write_new(path, value):
    with Path(path).open("x") as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())


def initialize(directory, manifest, mode, now=None):
    received = stamp(now)
    validate_manifest(manifest, mode, received)
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=False)
    session = {"protocol_version": VERSION, "mode": mode, "frozen_at_utc": received,
               "manifest": manifest, "manifest_sha256": digest(manifest), "package_fingerprint": fingerprint()}
    write_new(path / "session.json", session)
    (path / "events.jsonl").touch(exist_ok=False)
    return session


def reference(records, key, record_type):
    matches = [r for r in records if r["payload"]["record_id"] == key and r["payload"]["record_type"] == record_type]
    require(len(matches) == 1, f"Missing/invalid {record_type} reference: {key}")
    return matches[0]


def derive(payload, records, session, received):
    require(isinstance(payload, dict), "Payload must be an object")
    name = payload.get("record_type")
    require(name in PAYLOADS, "Unknown record_type")
    validate_shape(payload, PAYLOADS[name])
    require(not any(r["payload"]["record_id"] == payload["record_id"] for r in records), "Duplicate record_id")
    now = time(received)
    if name == "opportunity":
        if payload["eligibility"] != "eligible":
            require(bool(payload["reason"].strip()), "Excluded/unresolved opportunity needs a reason")
            return {"primary_eligible_claim": False}
        require(not any(r["payload"]["record_type"] == "opportunity" and r["payload"]["eligibility"] == "eligible" and (r["payload"]["issuer_id"], r["payload"]["fiscal_period"]) == (payload["issuer_id"], payload["fiscal_period"]) for r in records), "Issuer/fiscal period already registered; log duplicates as excluded")
        for key in ("document_url", "document_sha256", "packet_sha256", "source_first_seen_utc", "download_completed_utc", "packet_finalized_utc", "source_ref", "prediction_cutoff_utc", "entry_window_start_utc", "entry_window_end_utc", "exit_window_start_utc", "exit_window_end_utc"):
            require(payload[key] is not None, f"Eligible opportunity missing {key}")
        first, downloaded, finalized = [time(payload[x]) for x in ("source_first_seen_utc", "download_completed_utc", "packet_finalized_utc")]
        require(first <= downloaded <= finalized <= now, "Source/packet timestamps out of order or in future")
        public = time(payload["source_public_at_utc"]) if payload["source_public_at_utc"] is not None else None
        require(public is None or public <= first, "Publication cannot follow first-seen time")
        cutoff, entry, entry_end, exit_start, exit_end = [time(payload[x]) for x in ("prediction_cutoff_utc", "entry_window_start_utc", "entry_window_end_utc", "exit_window_start_utc", "exit_window_end_utc")]
        require(cutoff >= finalized and entry - cutoff == timedelta(minutes=15), "Cutoff/entry schedule inconsistent with protocol")
        require(entry_end - entry == timedelta(minutes=5) and exit_start > entry_end and exit_end - exit_start == timedelta(minutes=5), "Invalid price windows")
        if payload["price_features_asof_utc"] is not None:
            require(time(payload["price_features_asof_utc"]) <= finalized, "Future price feature")
        require(payload["momentum20_excess"] is None or payload["price_features_asof_utc"] is not None, "Price feature missing as-of evidence")
        if payload["source_timing_verified"]:
            require(public is not None and payload["source_timing_evidence_ref"] is not None, "Source-timing attestation lacks evidence")
        if session["mode"] == "prospective":
            require(payload["issuer_id"] in session["manifest"]["cohort_issuer_ids"], "Issuer outside frozen cohort")
            if public is not None:
                start = date.fromisoformat(session["manifest"]["study_start_date"])
                end = date.fromisoformat(session["manifest"]["study_end_date"])
                require(time(session["frozen_at_utc"]) <= public and start <= public.astimezone(NY).date() < end, "Eligible publication outside frozen collection window")
        return {"primary_eligible_claim": payload["source_timing_verified"] and public is not None,
                "calendar_and_source_attestations_require_external_audit": True}
    if name == "prediction":
        opportunity_record = reference(records, payload["opportunity_id"], "opportunity")
        event = opportunity_record["payload"]
        require(event["eligibility"] == "eligible", "Cannot predict an excluded/unresolved opportunity")
        require(not any(r["payload"]["record_type"] == "prediction" and r["payload"]["opportunity_id"] == payload["opportunity_id"] for r in records), "Opportunity already has a prediction; annotate instead of replacing")
        for condition, prediction in payload["predictions"].items():
            require((prediction["p_outperform"] is not None) == (prediction["status"] == "completed"), f"{condition}: failed probability must be null; completed probability is required")
        constant = payload["predictions"]["no_signal"]
        require(constant == {"status": "completed", "p_outperform": .5}, "no_signal must be completed with probability 0.5")
        llm = payload["predictions"]["llm"]
        if payload["model_started_utc"] is not None:
            require(time(opportunity_record["received_at_utc"]) <= time(payload["model_started_utc"]) <= now, "Model started before opportunity registration or in future")
        if payload["model_completed_utc"] is not None:
            require(payload["model_started_utc"] is not None and time(payload["model_started_utc"]) <= time(payload["model_completed_utc"]) <= now, "Invalid model completion timing")
        if llm["status"] == "completed":
            require(payload["request_count"] >= 1 and all(payload[k] is not None for k in ("model_snapshot", "model_started_utc", "model_completed_utc", "model_response_sha256", "model_response_ref")), "Completed LLM forecast missing raw response or call evidence")
        else:
            require(bool(payload["error"].strip()), "Failed LLM forecast needs an error reason")
        if session["mode"] == "prospective" and payload["model_snapshot"] is not None:
            require(payload["model_snapshot"] == session["manifest"]["model_snapshot"], "Model snapshot changed; start a new session")
        on_time = now < time(event["prediction_cutoff_utc"])
        deadline = None
        if payload["model_started_utc"] is not None and payload["model_completed_utc"] is not None:
            deadline = (time(payload["model_completed_utc"]) - time(payload["model_started_utc"])).total_seconds() <= 120
        if llm["status"] == "timeout":
            deadline = False
        return {"locally_before_cutoff": on_time, "timing_class": "local_before_cutoff" if on_time else "late",
                "independent_timing_verified": False, "session_mode": session["mode"],
                "request_limit_compliant": payload["request_count"] <= 1,
                "inference_deadline_compliant": deadline,
                "cost_limit_compliant": None if payload["model_cost_usd"] is None else payload["model_cost_usd"] <= .5}
    if name == "outcome":
        prediction = reference(records, payload["prediction_id"], "prediction")
        event = reference(records, prediction["payload"]["opportunity_id"], "opportunity")["payload"]
        require(now >= time(event["exit_window_end_utc"]), "Outcome cannot be recorded before exit window ends")
        require(not any(r["payload"]["record_type"] == "outcome" and r["payload"]["prediction_id"] == payload["prediction_id"] for r in records), "Outcome already recorded; append an annotation instead")
        if payload["status"] == "completed":
            require(all(payload[k] is not None for k in ("stock_total_return", "benchmark_total_return", "price_observed_at_utc", "price_artifact_sha256", "price_artifact_ref")), "Completed outcome lacks price evidence")
            require(time(event["exit_window_end_utc"]) <= time(payload["price_observed_at_utc"]) <= now, "Outcome price retrieval time is inconsistent")
            return {"target_outperform": int(payload["stock_total_return"] > payload["benchmark_total_return"]),
                    "prospective_verification": "requires_independent_timing_and_data_audit"}
        require(payload["stock_total_return"] is None and payload["benchmark_total_return"] is None and bool(payload["reason"].strip()), "Unavailable outcomes need null returns and a reason")
        return {"target_outperform": None}
    require(any(r["payload"]["record_id"] == payload["target_record_id"] for r in records), "Annotation target does not exist")
    return {"replaces_prior_record": False}


def _inspect_unlocked(directory):
    path = Path(directory)
    session = load(path / "session.json")
    require(session["manifest_sha256"] == digest(session["manifest"]), "Frozen manifest changed")
    require(session["package_fingerprint"] == fingerprint(), "Protocol/package changed; use archived package or start new session")
    previous, records = digest(session), []
    last_time = time(session["frozen_at_utc"])
    with (path / "events.jsonl").open() as handle:
        for sequence, line in enumerate(handle, 1):
            require(bool(line.strip()), "Blank/truncated ledger line")
            record = loads(line)
            require(set(record) == {"sequence", "received_at_utc", "previous_sha256", "payload", "derived", "record_sha256"}, "Invalid record envelope")
            body = {k: v for k, v in record.items() if k != "record_sha256"}
            require(record["sequence"] == sequence and record["previous_sha256"] == previous and record["record_sha256"] == digest(body), "Broken hash chain")
            require(time(record["received_at_utc"]) >= last_time, "Receipt clock moved backwards")
            require(record["derived"] == derive(record["payload"], records, session, record["received_at_utc"]), "Derived fields changed")
            previous, last_time = record["record_sha256"], time(record["received_at_utc"])
            records.append(record)
    return session, records, previous


def inspect(directory):
    with (Path(directory) / ".append.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_SH)
        return _inspect_unlocked(directory)


def append(directory, payload, now=None):
    path = Path(directory)
    with (path / ".append.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        session, records, previous = _inspect_unlocked(path)
        received = stamp(now)
        latest = records[-1]["received_at_utc"] if records else session["frozen_at_utc"]
        require(time(received) >= time(latest), "Receipt clock moved backwards")
        derived = derive(payload, records, session, received)
        body = {"sequence": len(records) + 1, "received_at_utc": received,
                "previous_sha256": previous, "payload": payload, "derived": derived}
        record = {**body, "record_sha256": digest(body)}
        with (path / "events.jsonl").open("a") as handle:
            handle.write(json.dumps(record, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        return record


def sentiment_probability(positive_count, negative_count):
    require(type(positive_count) is int and positive_count >= 0 and type(negative_count) is int and negative_count >= 0, "Counts must be nonnegative integers")
    return (1 + (positive_count - negative_count) / (positive_count + negative_count + 20)) / 2


def momentum_probability(excess_return):
    require(number(excess_return), "Momentum must be finite")
    return (1 + min(1, max(-1, excess_return / .10))) / 2


def brier_loss(probability, target):
    if probability is None or target is None:
        return None
    require(number(probability) and 0 <= probability <= 1, "Invalid forecast probability")
    require(type(target) is int and target in (0, 1), "Target must be integer zero or one")
    return (probability - target) ** 2


def paper_long_return(gross_return, probability, per_side_bps=10):
    # Apply this only after timing/compliance checks. It does not certify a fill.
    require(number(per_side_bps) and 0 <= per_side_bps < 10000, "Invalid proportional side cost")
    require(probability is None or (number(probability) and 0 <= probability <= 1), "Invalid forecast probability")
    if gross_return is None:
        return None
    require(number(gross_return) and gross_return >= -1, "Invalid realized gross return")
    if probability is None or probability <= .55:
        return 0.0
    cost = per_side_bps / 10000
    return (1 + gross_return) * (1 - cost) / (1 + cost) - 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    schema_cmd = commands.add_parser("schema")
    schema_cmd.add_argument("--out", required=True)
    init = commands.add_parser("init")
    init.add_argument("--session", required=True)
    init.add_argument("--manifest", required=True)
    init.add_argument("--mode", choices=("development", "prospective"), default="development")
    add = commands.add_parser("append")
    add.add_argument("--session", required=True)
    add.add_argument("--payload", required=True)
    verify = commands.add_parser("verify")
    verify.add_argument("--session", required=True)
    args = parser.parse_args()
    if args.command == "schema":
        write_new(args.out, schema())
        result = {"saved": args.out}
    elif args.command == "init":
        result = initialize(args.session, load(args.manifest), args.mode)
        result = {"session": args.session, "mode": result["mode"], "events": 0,
                  "independent_timing_verified": False}
    elif args.command == "append":
        result = append(args.session, load(args.payload))
    else:
        session, records, head = inspect(args.session)
        result = {"chain_valid": True, "events": len(records), "mode": session["mode"],
                  "head_sha256": head, "independent_timing_verified": False,
                  "scope": "Local chain and recorded-field validation, not data or timestamp authentication"}
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        sys.exit(2)
