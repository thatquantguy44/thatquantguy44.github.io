#!/usr/bin/env python3
"""Offline synthetic execution harness. No provider, network, or human review calls."""

import argparse
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import hashlib
import json
import math
from pathlib import Path
import sys
import time

import study
from fixed import execute_with_report
from tools import execute_tool, tool_specs

ROOT = Path(__file__).resolve().parent
MODE = "offline_synthetic"
MODEL = "offline-replay-v1"
PHASES = {
    "single": ["single"] * 4,
    "human_checkpoint": ["single"] * 4,
    "self_review": ["draft", "critique", "revision", "final"],
    "multi": ["coordinator_plan", "worker_1", "worker_2", "coordinator_final"],
}


def parsed(text):
    return json.loads(text, object_pairs_hook=study.unique_object,
                      parse_float=lambda x: float(x) if math.isfinite(float(x)) else study.fail("Non-finite JSON"),
                      parse_constant=lambda x: study.fail("Non-finite JSON"))


def money(value):
    if not study.nonnegative(value):
        raise ValueError("Charge/reservation must be finite and nonnegative")
    return Decimal(str(value))


class ScenarioClock:
    """Virtual elapsed time, explicitly scenario data rather than observed latency."""

    def __init__(self):
        self.origin = datetime.now(timezone.utc)
        self.seconds = 0.0

    def utc(self):
        return (self.origin + timedelta(seconds=self.seconds)).isoformat().replace("+00:00", "Z")

    def advance(self, seconds):
        if not study.nonnegative(seconds):
            raise ValueError("Scenario duration must be finite and nonnegative")
        self.seconds += seconds


class ReplayBackend:
    """A fresh, data-only response script per attempt; never executes script code."""

    mode = MODE
    model_snapshot = MODEL

    def __init__(self, responses=None, reservation_usd=.125):
        self.responses = deepcopy(responses) if responses is not None else None
        self.position = 0
        self.reservation_usd = reservation_usd
        self.used = False

    def reserve(self, request):
        return self.reservation_usd

    def respond(self, request):
        if self.responses is not None:
            if self.position >= len(self.responses):
                raise ValueError("Replay script exhausted; no replacement response invented")
            response = deepcopy(self.responses[self.position])
            self.position += 1
            return response
        # A plumbing control, deliberately not a solver or a gold-derived answer.
        role = request["role"]
        if role == "coordinator_plan":
            content = json.dumps({"worker_1": "Inspect source authority and requested values.",
                                  "worker_2": "Inspect units, arithmetic, and unsupported claims."})
        elif role in ("worker_1", "worker_2", "critique", "revision", "draft"):
            content = "Synthetic response: no model reasoning was performed."
        else:
            content = json.dumps({"task_id": request["task"]["task_id"], "answers": {
                q["answer_id"]: {"value": None, "unit": "unknown", "citations": []}
                for q in request["task"]["questions"]}})
        return {"content": content, "final": role in ("single", "final", "coordinator_final"),
                "model_snapshot": MODEL, "cost_usd": 0, "elapsed_seconds": 1,
                "usage": {k: 0 for k in ("input_tokens", "output_tokens", "reasoning_tokens", "cached_tokens")}}


def public_task(task_id):
    tasks = study.load(ROOT / "task-bank.json")["tasks"]
    return deepcopy(next(t for t in tasks if t["task_id"] == task_id))


def blank_answer(task):
    return {"task_id": task["task_id"], "answers": {
        q["answer_id"]: {"value": None, "unit": q["unit"], "citations": []}
        for q in task["questions"]}}


def executor_hashes():
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            for name in ("runner.py", "fixed.py", "tools.py")}


def execute_attempt(task, condition, repeat, directory, backend=None, checkpoint=None,
                    allow_provider_retry=False, budget_usd=.5, max_elapsed_seconds=600):
    """Run a synthetic attempt; evaluation occurs only after participant execution ends."""
    if condition not in study.CONDITIONS or type(repeat) is not int or repeat < 1:
        raise ValueError("Invalid condition or repetition")
    if task.get("synthetic") is not True or task.get("split") != "development":
        raise ValueError("This offline harness only accepts synthetic development packets")
    if not 0 < money(budget_usd) <= Decimal('.5'):
        raise ValueError("Budget must be positive and no greater than protocol ceiling")
    if not study.nonnegative(max_elapsed_seconds) or not 0 < max_elapsed_seconds <= 600:
        raise ValueError("Invalid elapsed-time ceiling")
    if allow_provider_retry and condition not in ("single", "human_checkpoint"):
        raise ValueError("Retries cannot repeat mandatory review/multi phases in protocol v0.1")
    backend = backend or ReplayBackend()
    if backend.mode != MODE:
        raise ValueError("Live backends are not enabled")
    if backend.used:
        raise ValueError("Each attempt requires a fresh backend with no cross-attempt state")
    if checkpoint is not None and condition != "human_checkpoint":
        raise ValueError("Execution assistance is only allowed in human_checkpoint")
    checkpoint = deepcopy(checkpoint) if checkpoint is not None else {
        "feedback": "", "active_seconds": 0, "reviewer_id": "synthetic-checkpoint"}
    if not isinstance(checkpoint, dict) or set(checkpoint) != {"feedback", "active_seconds", "reviewer_id"}:
        raise ValueError("Invalid synthetic checkpoint fields")
    if not isinstance(checkpoint["feedback"], str) or not isinstance(checkpoint["reviewer_id"], str) or not checkpoint["reviewer_id"].strip():
        raise ValueError("Invalid checkpoint feedback/identity")
    if not study.nonnegative(checkpoint["active_seconds"]):
        raise ValueError("Invalid checkpoint active time")

    out = Path(directory)
    out.mkdir(parents=True, exist_ok=False)
    backend.used = True
    participant = out / "participant"
    participant.mkdir()
    study.dump(participant / "task.json", task)
    study.dump(participant / "answer-template.json", blank_answer(task))
    prompts = study.load(ROOT / "prompts.json")
    (participant / "instructions.txt").write_text(prompts["common"] + "\n" + prompts[condition] + "\n")
    (out / "transcripts").mkdir()
    clock = ScenarioClock()
    observed_start = time.monotonic()
    run = study.run_template(task, condition, repeat)
    manifest = {"kind": MODE, "live_ready": False, "protocol_version": study.VERSION,
                "package_fingerprint": study.fingerprint(), "executor_sha256": executor_hashes(),
                "model_snapshot": backend.model_snapshot, "tools": tool_specs(), "condition": condition,
                "budget_usd": budget_usd, "max_model_calls": 4, "max_elapsed_seconds": max_elapsed_seconds,
                "timing_basis": "simulated", "usage_and_cost_basis": "scripted_scenario_not_provider_billing",
                "worker_execution": "sequential_independent_contexts", "provider_retry_authorized": allow_provider_retry}
    study.dump(out / "session-manifest.json", manifest)
    run.update({"execution_mode": MODE, "timing_basis": "simulated",
                "session_manifest_sha256": study.digest(manifest), "started_at_utc": clock.utc(),
                "model_snapshot": None if condition == "fixed" else backend.model_snapshot,
                "model_cost_usd": 0, "tool_cost_usd": 0, "human_intervention_seconds": 0})
    costs = []
    answer = None
    reason = ""
    status = "abandoned"
    histories = {"single": [], "review": [], "coordinator": [], "worker_1": [], "worker_2": []}
    plan, workers = None, {}
    calls = 0
    checkpoint_done = False
    retry_of = None

    def save_transcript(kind, data):
        name = f"transcripts/{len(list((out / 'transcripts').iterdir())) + 1:04d}-{kind}.json"
        study.dump(out / name, data)
        return name

    def event(kind, start, duration, transcript_ref, **fields):
        item = {"kind": kind, "at_utc": start, "elapsed_seconds": duration,
                "transcript_ref": transcript_ref, **fields}
        run["events"].append(item)
        with (out / "events.jsonl").open("a") as handle:
            handle.write(json.dumps(item, allow_nan=False) + "\n")

    def error(message):
        ref = save_transcript("error", {"message": message, "synthetic": True})
        event("error", clock.utc(), 0, ref, message=message)

    try:
        if condition == "fixed":
            answer, diagnostics = execute_with_report(deepcopy(task))
            ref = save_transcript("fixed", {"answer": answer, "diagnostics": diagnostics})
            event("tool_call", clock.utc(), 0, ref, cost_usd=0, tool="fixed_workflow")
            status = "completed"
        else:
            for role in PHASES[condition]:
                if clock.seconds >= max_elapsed_seconds:
                    status, reason = "timeout", "Scenario elapsed-time limit reached before request"
                    break
                if condition == "human_checkpoint" and calls == 2 and not checkpoint_done:
                    at = clock.utc()
                    clock.advance(checkpoint["active_seconds"])
                    ref = save_transcript("checkpoint", {**checkpoint, "synthetic": True})
                    event("human_checkpoint", at, checkpoint["active_seconds"], ref, **checkpoint)
                    run["human_intervention_seconds"] = checkpoint["active_seconds"]
                    checkpoint_done = True
                    if checkpoint["active_seconds"] > 120:
                        status, reason = "abandoned", "Synthetic checkpoint exceeds 120 active seconds"
                        break
                    histories["single"].append({"role": "user", "content": "Checkpoint feedback: " + checkpoint["feedback"]})
                    if clock.seconds >= max_elapsed_seconds:
                        status, reason = "timeout", "Scenario time limit reached during checkpoint"
                        break

                if condition in ("single", "human_checkpoint"):
                    context = "single"
                elif condition == "self_review":
                    context = "review"
                else:
                    context = role if role.startswith("worker_") else "coordinator"
                messages = deepcopy(histories[context])
                if role.startswith("worker_"):
                    messages.append({"role": "user", "content": "Coordinator assignment/plan: " + json.dumps(plan)})
                if role == "coordinator_final":
                    messages.append({"role": "user", "content": json.dumps({"worker_outputs": workers})})
                messages.append({"role": "user", "content": f"Execute phase {role}. " +
                                 ("Submit final JSON now." if role in ("final", "coordinator_final") else "Follow the assigned policy.")})
                request = {"task": deepcopy(task), "system": prompts["common"] + "\n" + prompts[condition],
                           "role": role, "context_id": f"{run['attempt_id']}:{context}", "messages": messages,
                           "request_id": f"{run['attempt_id']}:call-{calls + 1}", "retry_of": retry_of,
                           "tools": tool_specs(), "remaining_seconds": max_elapsed_seconds - clock.seconds,
                           "remaining_budget_usd": float(money(budget_usd) - sum(costs, Decimal(0))),
                           "calls_remaining": 4 - calls}
                reservation = money(backend.reserve(deepcopy(request)))
                if sum(costs, Decimal(0)) + reservation > money(budget_usd):
                    save_transcript("denied-reservation", {"request": request, "reservation_usd": float(reservation),
                                                            "issued": False})
                    status, reason = "budget_exhausted", "Worst-case reservation exceeds remaining ceiling"
                    break
                request["reserved_charge_usd"] = float(reservation)
                request_ref = save_transcript("request", request)
                retry_of = None
                at = clock.utc()
                calls += 1
                try:
                    response = backend.respond(deepcopy(request))
                    if not isinstance(response, dict):
                        raise ValueError("Replay response must be an object")
                    # Check all serializability before recording a partly processed response.
                    json.dumps(response, allow_nan=False)
                except Exception as exc:
                    response = {"error": "provider_error", "message": str(exc), "cost_usd": None,
                                "usage": {}, "elapsed_seconds": 0, "model_snapshot": backend.model_snapshot}
                ref = save_transcript("response", {"request_ref": request_ref, "response": response})
                duration = response.get("elapsed_seconds", 0)
                if not study.nonnegative(duration):
                    duration = 0
                    response["error"] = "provider_error"
                    response["message"] = "Invalid response duration"
                clock.advance(duration)
                usage = response.get("usage") if isinstance(response.get("usage"), dict) else {}
                charge = response.get("cost_usd")
                known_charge = study.nonnegative(charge)
                costs.append(money(charge)) if known_charge else None
                event("model_call", at, duration, ref, role=role, model_snapshot=response.get("model_snapshot"),
                      request_id=request["request_id"], retry_of=request["retry_of"],
                      cost_usd=charge if known_charge else None,
                      **{k: usage.get(k) for k in ("input_tokens", "output_tokens", "reasoning_tokens", "cached_tokens")})
                run["model_cost_usd"] = float(sum(costs, Decimal(0))) if known_charge else None
                if not known_charge:
                    status = response.get("error") if response.get("error") in ("provider_error", "tool_error", "timeout", "abandoned") else "provider_error"
                    reason = "Unknown charge prevents further budget reservation"
                    break
                if money(charge) > reservation or sum(costs, Decimal(0)) > money(budget_usd):
                    status, reason = "budget_exhausted", "Returned scenario charge exceeds reservation or ceiling"
                    break
                if clock.seconds > max_elapsed_seconds:
                    status, reason = "timeout", "Response exceeded scenario elapsed-time limit"
                    break
                if response.get("model_snapshot") != backend.model_snapshot:
                    status, reason = "provider_error", "Returned model ID differs from frozen binding"
                    break
                if any(not study.integer(usage.get(k)) for k in ("input_tokens", "output_tokens", "reasoning_tokens", "cached_tokens")) or usage.get("cached_tokens", 0) > usage.get("input_tokens", 0):
                    status, reason = "provider_error", "Missing or invalid scenario token usage"
                    break
                if response.get("error"):
                    status = response["error"] if response["error"] in study.STATUSES and response["error"] != "completed" else "provider_error"
                    reason = str(response.get("message", response["error"]))
                    if status == "provider_error" and allow_provider_retry and calls < 4:
                        error(reason)
                        ref = save_transcript("retry", {"reason": reason, "failed_request": request_ref})
                        event("retry", clock.utc(), 0, ref, reason=reason, failed_request_id=request["request_id"])
                        retry_of = request["request_id"]
                        status, reason = "abandoned", ""
                        continue
                    break
                content = response.get("content")
                if not isinstance(content, str) or type(response.get("final")) is not bool:
                    status, reason = "provider_error", "Response requires text content and boolean final"
                    break
                histories[context] = messages + [{"role": "assistant", "content": content}]
                handoff = None
                if role == "coordinator_plan":
                    plan = {"content": content, "tool_results": []}
                    handoff = plan
                elif role.startswith("worker_"):
                    workers[role] = {"content": content, "tool_results": []}
                    handoff = workers[role]
                tool_calls = response.get("tool_calls", [])
                if not isinstance(tool_calls, list) or len(tool_calls) > 16 or (tool_calls and response["final"]):
                    status, reason = "tool_error", "Invalid tools or tools requested after final submission"
                    break
                for tool_call in tool_calls:
                    at = clock.utc()
                    try:
                        if not isinstance(tool_call, dict) or set(tool_call) != {"name", "arguments"}:
                            raise ValueError("Invalid tool-call fields")
                        output = execute_tool(task, tool_call["name"], tool_call["arguments"])
                        record = {"call": tool_call, "output": output, "error": None}
                    except (ValueError, TypeError, KeyError) as exc:
                        record = {"call": tool_call, "output": None, "error": str(exc)}
                    ref = save_transcript("tool", record)
                    event("tool_call", at, 0, ref, cost_usd=0, tool=tool_call.get("name") if isinstance(tool_call, dict) else None)
                    histories[context].append({"role": "tool", "content": json.dumps(record)})
                    if handoff is not None:
                        handoff["tool_results"].append(deepcopy(record))
                    if record["error"]:
                        status, reason = "tool_error", record["error"]
                        break
                if status == "tool_error":
                    break
                may_submit = condition == "single" or (condition == "human_checkpoint" and checkpoint_done) or role in ("final", "coordinator_final")
                if response["final"] and may_submit:
                    try:
                        answer = parsed(content)
                    except (ValueError, TypeError) as exc:
                        reason = "Malformed final JSON retained without repair: " + str(exc)
                    status = "completed"
                    break
            else:
                status, reason = "abandoned", "Four requests exhausted without an eligible final submission"
    except (ValueError, TypeError, KeyError, ArithmeticError) as exc:
        status, reason = "tool_error" if condition == "fixed" else "provider_error", str(exc)
    if reason:
        error(reason)
    run.update({"terminal_status": status, "terminal_reason": reason, "answer_sha256": study.digest(answer),
                "ended_at_utc": clock.utc(), "elapsed_seconds": clock.seconds,
                "observed_runner_seconds": time.monotonic() - observed_start})
    study.dump(out / "answer.json", answer)
    study.dump(out / "run.json", run)
    # Hidden rubric is parsed for scoring only after execution has terminated.
    _, gold = study.get_task(task["task_id"])
    result = study.score(task, gold, answer, run)
    result.update({"execution_mode": MODE, "terminal_status": status, "attempt_id": run["attempt_id"]})
    study.dump(out / "score.json", result)
    artifacts = {str(p.relative_to(out)): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in sorted(out.rglob('*')) if p.is_file()}
    study.dump(out / "artifacts.json", {"kind": "local_integrity_not_independent_timestamp", "sha256": artifacts})
    return result


def smoke(directory, repeats=3, seed=20261026):
    out = Path(directory)
    out.mkdir(parents=True, exist_ok=False)
    schedule = study.make_schedule(seed, repeats)
    study.dump(out / "schedule.json", schedule)
    results = []
    for attempt in schedule["attempts"]:
        results.append(execute_attempt(public_task(attempt["task_id"]), attempt["condition"], attempt["repeat"],
                                       out / attempt["attempt_id"]))
    summary = {"kind": "synthetic_harness_smoke_not_experiment_results", "attempts": len(results),
               "conditions": {c: sum(r['attempt_id'].split('__')[1] == c for r in results) for c in study.CONDITIONS},
               "verified_successes": sum(r["verified_success"] for r in results),
               "real_provider_calls": 0, "real_human_reviews": 0,
               "note": "Replay correctness is not agent performance; costs/tokens/latencies are scenario inputs."}
    study.dump(out / "summary.json", summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    batch = commands.add_parser("smoke")
    batch.add_argument("--out", required=True)
    batch.add_argument("--repeats", type=int, default=3)
    batch.add_argument("--seed", type=int, default=20261026)
    one = commands.add_parser("run")
    one.add_argument("--task", required=True)
    one.add_argument("--condition", choices=study.CONDITIONS, required=True)
    one.add_argument("--repeat", type=int, default=1)
    one.add_argument("--script", help="Data-only JSON: responses list and optional synthetic checkpoint")
    one.add_argument("--allow-provider-retry", action="store_true")
    one.add_argument("--out", required=True)
    args = parser.parse_args()
    if args.command == "smoke":
        result = smoke(args.out, args.repeats, args.seed)
    else:
        script = study.load(args.script) if args.script else {}
        if not isinstance(script, dict) or set(script) - {"responses", "checkpoint"}:
            raise ValueError("Script requires responses and/or checkpoint only")
        if "responses" in script and not isinstance(script["responses"], list):
            raise ValueError("responses must be a list")
        result = execute_attempt(public_task(args.task), args.condition, args.repeat, args.out,
                                 ReplayBackend(script.get("responses")), script.get("checkpoint"), args.allow_provider_retry)
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0  # Successful harness execution does not imply a verified research result.


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError, TypeError, StopIteration) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        sys.exit(2)
