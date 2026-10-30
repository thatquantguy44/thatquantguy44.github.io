#!/usr/bin/env python3
"""Offline protocol preparation and scoring. Never calls a model or the network."""

import argparse
import hashlib
import json
import math
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROTOCOL = ROOT.parents[1] / "agent-experiment-protocol.md"
VERSION = "0.1.0"
CONDITIONS = ("fixed", "single", "self_review", "human_checkpoint", "multi")
STATUSES = ("completed", "timeout", "budget_exhausted", "tool_error", "provider_error", "abandoned")


def fail(message):
    raise ValueError(message)


def unique_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            fail(f"Duplicate JSON key: {key}")
        obj[key] = value
    return obj


def load(path):
    return json.loads(Path(path).read_text(), object_pairs_hook=unique_object,
                      parse_float=lambda value: float(value) if math.isfinite(float(value)) else fail(f"Non-finite JSON value: {value}"),
                      parse_constant=lambda value: fail(f"Non-finite JSON value: {value}"))


def dump(path, data):
    # Refuse overwrites: an attempt or schedule must not silently replace history.
    with Path(path).open("x") as handle:
        json.dump(data, handle, indent=2, allow_nan=False)
        handle.write("\n")


def digest(data):
    raw = json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(raw).hexdigest()


def fingerprint():
    files = [ROOT / name for name in ("study.py", "prompts.json", "task-bank.json", "gold.json", "runtime.example.json", "runner.py", "fixed.py", "tools.py")]
    return digest({p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files + [PROTOCOL]})


def bank():
    public = load(ROOT / "task-bank.json")
    keys = load(ROOT / "gold.json")
    if public["fixture_version"] != VERSION or keys["fixture_version"] != VERSION:
        fail("Fixture version mismatch")
    return {t["task_id"]: t for t in public["tasks"]}, keys["tasks"]


def get_task(task_id):
    tasks, keys = bank()
    if task_id not in tasks:
        fail(f"Unknown task: {task_id}")
    return tasks[task_id], keys[task_id]


def finite_number(value):
    try:
        return type(value) in (int, float) and math.isfinite(value)
    except OverflowError:
        return False


def nonnegative(value):
    return finite_number(value) and value >= 0


def integer(value):
    return type(value) is int and value >= 0


def sha(value):
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def timestamp(value):
    if not isinstance(value, str) or not value.endswith("Z"):
        fail("UTC timestamp must end in Z")
    return datetime.fromisoformat(value[:-1] + "+00:00")


def check_answer(task, gold, answer):
    errors = []
    if not isinstance(answer, dict) or set(answer) != {"task_id", "answers"}:
        return ["Answer must contain exactly task_id and answers"]
    if answer["task_id"] != task["task_id"]:
        errors.append("Wrong task_id")
    values = answer["answers"]
    if not isinstance(values, dict) or set(values) != set(gold["answers"]):
        return errors + ["Missing or extra answer IDs"]
    sources = {s["source_id"]: s["text"] for s in task["sources"]}
    for aid, expected in gold["answers"].items():
        item = values[aid]
        if not isinstance(item, dict) or set(item) != {"value", "unit", "citations"}:
            errors.append(f"{aid}: invalid answer fields")
            continue
        target, value = expected["value"], item["value"]
        if finite_number(target):
            correct = finite_number(value) and abs(value - target) <= expected["absolute_tolerance"] + 1e-12
        else:
            correct = type(value) is type(target) and value == target
        if not correct:
            errors.append(f"{aid}: incorrect value or type")
        if item["unit"] != expected["unit"]:
            errors.append(f"{aid}: incorrect unit")
        citations = item["citations"]
        if not isinstance(citations, list):
            errors.append(f"{aid}: citations must be a list")
            continue
        valid = []
        for cite in citations:
            if not isinstance(cite, dict) or set(cite) != {"source_id", "quote"}:
                errors.append(f"{aid}: invalid citation fields")
                continue
            sid, quote = cite["source_id"], cite["quote"]
            if not isinstance(sid, str) or sid not in sources or not isinstance(quote, str) or not quote.strip() or quote not in sources[sid]:
                errors.append(f"{aid}: fabricated source or non-verbatim quote")
                continue
            valid.append(cite)
        for evidence in expected["required_evidence"]:
            if not any(c["source_id"] == evidence["source_id"] and evidence["span"] in c["quote"] for c in valid):
                errors.append(f"{aid}: missing required evidence from {evidence['source_id']}")
        if target is None and citations:
            errors.append(f"{aid}: correct abstention must have no citations")
    return errors


def run_template(task, condition, repeat):
    if repeat < 1:
        fail("repeat must be positive")
    return {
        "protocol_version": VERSION, "package_fingerprint": fingerprint(),
        "task_sha256": digest(task), "answer_sha256": None,
        "session_manifest_sha256": None,
        "attempt_id": f"{task['task_id']}__{condition}__r{repeat}",
        "task_id": task["task_id"], "condition": condition, "repeat": repeat,
        "terminal_status": None, "model_snapshot": None,
        "started_at_utc": None, "ended_at_utc": None, "elapsed_seconds": None,
        "model_cost_usd": None, "tool_cost_usd": None,
        "human_intervention_seconds": None, "operator_seconds": None,
        "boundary_verified": False, "operator_id": None,
        "review": {"reviewer_id": None, "independent": False, "passed": None,
                   "verification_seconds": None, "notes": None},
        "events": [],
    }


def check_run(task, answer, run):
    errors = []
    def require(test, message):
        if not test:
            errors.append(message)
    if not isinstance(run, dict):
        return ["Run record must be an object"]
    condition = run.get("condition")
    repeat = run.get("repeat")
    require(condition in CONDITIONS, "Unknown condition")
    require(integer(repeat) and repeat > 0, "Invalid repetition")
    require(run.get("attempt_id") == f"{task['task_id']}__{condition}__r{repeat}", "Attempt ID mismatch")
    require(run.get("task_id") == task["task_id"], "Run task mismatch")
    require(run.get("protocol_version") == VERSION, "Protocol version mismatch")
    require(run.get("package_fingerprint") == fingerprint(), "Package fingerprint mismatch")
    require(run.get("task_sha256") == digest(task), "Public packet hash mismatch")
    require(run.get("answer_sha256") == digest(answer), "Answer hash mismatch")
    require(sha(run.get("session_manifest_sha256")), "Missing frozen session manifest hash")
    require(run.get("terminal_status") in STATUSES, "Missing or invalid terminal status")
    require(run.get("execution_mode") != "offline_synthetic", "Synthetic harness output is not an empirical attempt")
    require(run.get("boundary_verified") is True, "Participant boundary not verified")
    require(isinstance(run.get("operator_id"), str) and bool(run["operator_id"].strip()), "Missing operator identity")
    elapsed = run.get("elapsed_seconds")
    require(nonnegative(elapsed) and elapsed <= 600, "Missing duration or wall-clock cap violation")
    start, end = None, None
    try:
        start, end = timestamp(run.get("started_at_utc")), timestamp(run.get("ended_at_utc"))
        require(end >= start and finite_number(elapsed) and abs((end - start).total_seconds() - elapsed) <= 1, "Timestamp/duration mismatch")
    except (ValueError, TypeError):
        errors.append("Invalid UTC start/end timestamps")
    for name in ("model_cost_usd", "tool_cost_usd", "human_intervention_seconds", "operator_seconds"):
        require(nonnegative(run.get(name)), f"Missing or invalid {name}")
    costs = (run.get("model_cost_usd"), run.get("tool_cost_usd"))
    if all(nonnegative(v) for v in costs):
        require(sum(costs) <= .5 + 1e-12, "Dollar cap violation")
    events = run.get("events")
    if not isinstance(events, list):
        return errors + ["events must be a list"]
    calls, checkpoints, billed = [], [], {"model_call": [], "tool_call": []}
    last_time = None
    calls_at_checkpoint = []
    for event in events:
        if not isinstance(event, dict):
            errors.append("Invalid event object")
            continue
        kind = event.get("kind")
        require(kind in ("model_call", "tool_call", "retry", "human_checkpoint", "error"), "Unknown event kind")
        try:
            at = timestamp(event.get("at_utc"))
            require(start is not None and end is not None and start <= at <= end, "Event outside attempt window")
            require(last_time is None or at >= last_time, "Events not chronological")
            last_time = at
            if end is not None and nonnegative(event.get("elapsed_seconds")):
                require(at + timedelta(seconds=event["elapsed_seconds"]) <= end + timedelta(seconds=1), "Event finishes after attempt end")
        except (ValueError, TypeError):
            errors.append("Invalid event timestamp")
        require(nonnegative(event.get("elapsed_seconds")), "Missing event duration")
        if nonnegative(event.get("elapsed_seconds")) and nonnegative(elapsed):
            require(event["elapsed_seconds"] <= elapsed, "Event duration exceeds attempt duration")
        require(isinstance(event.get("transcript_ref"), str) and bool(event["transcript_ref"].strip()), "Missing raw transcript reference")
        if kind in billed:
            billed[kind].append(event.get("cost_usd"))
            require(nonnegative(event.get("cost_usd")), "Unknown event cost")
        if kind == "model_call":
            calls.append(event)
            require(isinstance(run.get("model_snapshot"), str) and bool(run["model_snapshot"].strip()), "Missing model snapshot")
            require(event.get("model_snapshot") == run.get("model_snapshot"), "Model snapshot changed within attempt")
            for field in ("input_tokens", "output_tokens", "reasoning_tokens", "cached_tokens"):
                require(integer(event.get(field)), f"Missing or invalid {field}")
            if integer(event.get("input_tokens")) and integer(event.get("cached_tokens")):
                require(event["cached_tokens"] <= event["input_tokens"], "Cached tokens exceed input tokens")
        if kind == "human_checkpoint":
            checkpoints.append(event)
            calls_at_checkpoint.append(len(calls))
            require(isinstance(event.get("feedback"), str), "Missing verbatim checkpoint feedback")
            require(isinstance(event.get("reviewer_id"), str) and bool(event["reviewer_id"].strip()), "Missing checkpoint reviewer identity")
            require(nonnegative(event.get("active_seconds")), "Missing checkpoint active seconds")
            if nonnegative(event.get("active_seconds")) and nonnegative(event.get("elapsed_seconds")):
                require(event["active_seconds"] <= event["elapsed_seconds"], "Active checkpoint time exceeds checkpoint duration")
        if kind == "retry":
            require(isinstance(event.get("reason"), str) and bool(event["reason"].strip()), "Retry missing reason")
    require(len(calls) <= 4, "Model-turn cap violation")
    for kind, summary in (("model_call", "model_cost_usd"), ("tool_call", "tool_cost_usd")):
        values = billed[kind]
        if all(nonnegative(v) for v in values) and nonnegative(run.get(summary)):
            require(abs(sum(values) - run[summary]) <= 1e-9, f"{summary} does not reconcile with events")
    completed = run.get("terminal_status") == "completed"
    roles = [c.get("role") for c in calls]
    if condition == "fixed":
        require(not calls and run.get("model_cost_usd") == 0 and run.get("model_snapshot") is None, "Fixed workflow used a model")
    elif completed:
        require(bool(calls), "Completed model attempt has no calls")
    if condition in ("single", "human_checkpoint"):
        require(all(role == "single" for role in roles), "Unexpected single-agent context role")
    if condition in ("self_review", "multi"):
        sequence = ["draft", "critique", "revision", "final"] if condition == "self_review" else ["coordinator_plan", "worker_1", "worker_2", "coordinator_final"]
        # Parallel worker requests must be logged in request-start order; either worker may start first.
        if condition == "multi" and len(roles) >= 3 and set(roles[1:3]) == {"worker_1", "worker_2"}:
            roles = [roles[0], "worker_1", "worker_2"] + roles[3:]
        require(roles == sequence[:len(roles)], "Condition phases do not match policy")
        if completed:
            require(len(calls) == 4, "Successful review/multi policy must complete all four phases")
    if condition == "human_checkpoint":
        require(len(checkpoints) <= 1 and all(n == 2 for n in calls_at_checkpoint), "Checkpoint must occur once, after turn two")
        if completed:
            require(len(checkpoints) == 1, "Completed human condition has no checkpoint")
        active = [e.get("active_seconds") for e in checkpoints]
        if all(nonnegative(v) for v in active) and nonnegative(run.get("human_intervention_seconds")):
            require(abs(sum(active) - run["human_intervention_seconds"]) <= 1e-9, "Human intervention does not reconcile")
        require(nonnegative(run.get("human_intervention_seconds")) and run["human_intervention_seconds"] <= 120, "Human checkpoint cap violation")
    else:
        require(not checkpoints and run.get("human_intervention_seconds") == 0, "Execution help in unsupervised condition")
    review = run.get("review")
    if not isinstance(review, dict):
        return errors + ["Missing independent review record"]
    require(review.get("independent") is True, "Review independence not established")
    require(isinstance(review.get("reviewer_id"), str) and bool(review["reviewer_id"].strip()) and review["reviewer_id"] != run.get("operator_id"), "Missing independent reviewer identity")
    require(all(review.get("reviewer_id") != e.get("reviewer_id") for e in checkpoints), "Final reviewer provided execution help")
    require(type(review.get("passed")) is bool, "Human review pending or invalid")
    require(nonnegative(review.get("verification_seconds")), "Unknown verification effort")
    require(isinstance(review.get("notes"), str), "Missing review notes")
    return errors


def score(task, gold, answer, run=None):
    answer_errors = check_answer(task, gold, answer)
    run_errors = check_run(task, answer, run) if run is not None else ["No run record; verification pending"]
    verified = not answer_errors and not run_errors and run["terminal_status"] == "completed" and run["review"]["passed"] is True
    return {"task_id": task["task_id"], "automated_correct": not answer_errors,
            "verified_success": verified, "answer_errors": answer_errors, "run_errors": run_errors}


def make_schedule(seed=20261026, repeats=3):
    if repeats < 1:
        fail("repeats must be positive")
    tasks, _ = bank()
    rng = random.Random(seed)
    blocks = [(tid, r) for tid in sorted(tasks) for r in range(1, repeats + 1)]
    rng.shuffle(blocks)
    attempts = []
    for block, (tid, repeat) in enumerate(blocks, 1):
        conditions = list(CONDITIONS)
        rng.shuffle(conditions)
        for condition in conditions:
            attempts.append({"order": len(attempts) + 1, "block": block, "task_id": tid,
                             "condition": condition, "repeat": repeat,
                             "attempt_id": f"{tid}__{condition}__r{repeat}", "task_sha256": digest(tasks[tid])})
    return {"kind": "schedule_not_results", "seed": seed, "repeats": repeats,
            "protocol_version": VERSION, "package_fingerprint": fingerprint(), "attempts": attempts}


def export_task(task, directory):
    path = Path(directory)
    if path.exists() and (not path.is_dir() or any(path.iterdir())):
        fail("Participant export requires a new or empty directory")
    path.mkdir(parents=True, exist_ok=True)
    dump(path / "task.json", task)
    prompt = load(ROOT / "prompts.json")
    (path / "instructions.txt").write_text(prompt["common"] + "\n\nThe executor supplies the frozen condition policy separately.\n")
    dump(path / "answer-template.json", {"task_id": task["task_id"], "answers": {
        q["answer_id"]: {"value": None, "unit": q["unit"], "citations": []} for q in task["questions"]}})


def validate():
    public = load(ROOT / "task-bank.json")
    tasks, keys = bank()
    if len(tasks) != len(public["tasks"]) or set(tasks) != set(keys):
        fail("Duplicate task IDs or public/gold mismatch")
    cells = set()
    for task_id, task in tasks.items():
        if task.get("synthetic") is not True or task.get("split") != "development":
            fail("Development fixtures must be labeled synthetic")
        ids = [s["source_id"] for s in task["sources"]]
        aids = [q["answer_id"] for q in task["questions"]]
        if len(ids) != len(set(ids)) or len(aids) != len(set(aids)) or set(aids) != set(keys[task_id]["answers"]):
            fail("Source/answer ID mismatch")
        for q in task["questions"]:
            expected = keys[task_id]["answers"][q["answer_id"]]
            if (expected["value"] is not None and q["unit"] != expected["unit"]) or not nonnegative(expected["absolute_tolerance"]):
                fail("Invalid unit/tolerance in key")
        ideal = {"task_id": task_id, "answers": {aid: {"value": value["value"], "unit": value["unit"], "citations": [
            {"source_id": e["source_id"], "quote": e["span"]} for e in value["required_evidence"]]} for aid, value in keys[task_id]["answers"].items()}}
        errors = check_answer(task, keys[task_id], ideal)
        if errors:
            fail(f"Invalid key for {task_id}: {errors}")
        cells.add((task["family"], task["structure"]))
    if len(cells) != 6:
        fail("Expected three task families crossed with two structures")
    prompts = load(ROOT / "prompts.json")
    if not set(CONDITIONS).issubset(prompts):
        fail("Missing condition prompts")
    return {"development_tasks": len(tasks), "family_structure_cells": len(cells),
            "scheduled_pilot_attempts": len(make_schedule()["attempts"]),
            "package_fingerprint": fingerprint(), "model_calls_run": 0,
            "scope": "Structural validation, not empirical results or independent fixture review"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("validate")
    schedule = commands.add_parser("schedule")
    schedule.add_argument("--seed", type=int, default=20261026)
    schedule.add_argument("--repeats", type=int, default=3)
    schedule.add_argument("--out", required=True)
    export = commands.add_parser("export")
    export.add_argument("--task", required=True)
    export.add_argument("--out", required=True)
    template = commands.add_parser("run-template")
    template.add_argument("--task", required=True)
    template.add_argument("--condition", choices=CONDITIONS, required=True)
    template.add_argument("--repeat", type=int, required=True)
    template.add_argument("--out", required=True)
    scoring = commands.add_parser("score")
    scoring.add_argument("--task", required=True)
    scoring.add_argument("--answer", required=True)
    scoring.add_argument("--run")
    args = parser.parse_args()
    if args.command == "validate":
        result = validate()
    elif args.command == "schedule":
        result = make_schedule(args.seed, args.repeats)
        dump(args.out, result)
        result = {"saved": args.out, "attempts": len(result["attempts"]), "kind": result["kind"]}
    else:
        task, gold = get_task(args.task)
        if args.command == "export":
            export_task(task, args.out)
            result = {"saved": args.out, "task_sha256": digest(task), "warning": "Packet export does not sandbox the executor"}
        elif args.command == "run-template":
            dump(args.out, run_template(task, args.condition, args.repeat))
            result = {"saved": args.out, "kind": "unobserved_run_template"}
        else:
            result = score(task, gold, load(args.answer), load(args.run) if args.run else None)
            print(json.dumps(result, indent=2, allow_nan=False))
            return 0 if result["verified_success"] else 1
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        sys.exit(2)
