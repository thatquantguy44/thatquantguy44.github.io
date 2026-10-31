"""Synthetic execution-policy tests, never evidence of model performance."""

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import runner
import study


def response(content="draft", final=False, **changes):
    item = {"content": content, "final": final, "model_snapshot": runner.MODEL,
            "cost_usd": .01, "elapsed_seconds": 1,
            "usage": {"input_tokens": 10, "output_tokens": 5, "reasoning_tokens": 0, "cached_tokens": 0}}
    item.update(changes)
    return item


class ExecutionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.task = runner.public_task("calculate_parallel")

    def execute(self, condition="single", responses=None, name="attempt", **options):
        path = self.root / name
        result = runner.execute_attempt(self.task, condition, 1, path,
                                        runner.ReplayBackend(responses), **options)
        return path, study.load(path / "run.json"), result

    def requests(self, path):
        return [study.load(p) for p in sorted((path / "transcripts").glob("*-request.json"))]

    def calls(self, run):
        return [e for e in run["events"] if e["kind"] == "model_call"]

    def test_all_conditions_end_with_pending_review_and_synthetic_refusal(self):
        for condition in study.CONDITIONS:
            with self.subTest(condition=condition):
                path, record, result = self.execute(condition, name=condition)
                self.assertEqual(record["terminal_status"], "completed")
                self.assertFalse(result["verified_success"])
                self.assertFalse(record["boundary_verified"])
                self.assertIsNone(record["review"]["passed"])
                self.assertIsNone(record["operator_seconds"])
                self.assertIn("Synthetic harness output is not an empirical attempt", result["run_errors"])
                self.assertEqual(set(p.name for p in (path / "participant").iterdir()),
                                 {"task.json", "instructions.txt", "answer-template.json"})

    def test_synthetic_flag_prevents_laundering_review_and_boundary_attestations(self):
        path, record, _ = self.execute()
        record.update(boundary_verified=True, operator_id="operator", operator_seconds=0)
        record["review"] = {"reviewer_id": "reviewer", "independent": True, "passed": True,
                            "verification_seconds": 0, "notes": "test only"}
        errors = study.check_run(self.task, study.load(path / "answer.json"), record)
        self.assertEqual(errors, ["Synthetic harness output is not an empirical attempt"])

    def test_single_can_submit_first_request_and_does_not_consume_extra_responses(self):
        _, record, _ = self.execute(responses=[response('{}', True), response("unused")])
        self.assertEqual(len(self.calls(record)), 1)

    def test_self_review_keeps_one_context_and_all_phases_despite_early_final(self):
        path, record, _ = self.execute("self_review", [response(f"phase-{n}", True) for n in range(4)])
        requests = self.requests(path)
        self.assertEqual([r["role"] for r in requests], ["draft", "critique", "revision", "final"])
        self.assertEqual(len({r["context_id"] for r in requests}), 1)
        self.assertIn("phase-0", json.dumps(requests[1]["messages"]))
        self.assertIn("phase-2", json.dumps(requests[3]["messages"]))
        self.assertEqual(len(self.calls(record)), 4)

    def test_multi_contexts_isolate_workers_and_coordinator_sees_both(self):
        path, record, _ = self.execute("multi", [response("PLAN"), response("WORKER-ONE-PRIVATE"),
                                                 response("WORKER-TWO-PRIVATE"), response('{}', True)])
        req = self.requests(path)
        self.assertEqual(req[0]["context_id"], req[3]["context_id"])
        self.assertNotEqual(req[1]["context_id"], req[2]["context_id"])
        self.assertIn("PLAN", json.dumps(req[1]["messages"]))
        self.assertIn("PLAN", json.dumps(req[2]["messages"]))
        self.assertNotIn("WORKER-ONE-PRIVATE", json.dumps(req[2]))
        self.assertNotIn("WORKER-TWO-PRIVATE", json.dumps(req[1]))
        self.assertIn("WORKER-ONE-PRIVATE", json.dumps(req[3]))
        self.assertIn("WORKER-TWO-PRIVATE", json.dumps(req[3]))
        self.assertEqual(len(self.calls(record)), 4)
        self.assertTrue(all(r["tools"] == req[0]["tools"] and r["task"] == self.task for r in req))

    def test_human_checkpoint_ignores_early_final_until_two_calls_and_feedback(self):
        feedback = {"feedback": "CHECK-UNITS", "active_seconds": 7, "reviewer_id": "synthetic-person"}
        path, record, _ = self.execute("human_checkpoint", [response('{}', True)] * 3, checkpoint=feedback)
        self.assertEqual(len(self.calls(record)), 3)
        kinds = [e["kind"] for e in record["events"]]
        self.assertEqual(kinds, ["model_call", "model_call", "human_checkpoint", "model_call"])
        self.assertEqual(record["human_intervention_seconds"], 7)
        req = self.requests(path)
        self.assertNotIn("CHECK-UNITS", json.dumps(req[1]))
        self.assertIn("CHECK-UNITS", json.dumps(req[2]))

    def test_multi_hands_tool_results_forward_without_worker_cross_access(self):
        plan_tool = {"name": "calculate", "arguments": {"expression": "700 + 77"}}
        worker_tool = {"name": "calculate", "arguments": {"expression": "123456 + 765432"}}
        path, _, _ = self.execute("multi", [response("PLAN", tool_calls=[plan_tool]),
                                           response("WORKER-ONE", tool_calls=[worker_tool]),
                                           response("WORKER-TWO"), response('{}', True)])
        req = self.requests(path)
        self.assertIn('"result": "777"', req[1]["messages"][0]["content"])
        self.assertIn('"result": "777"', req[2]["messages"][0]["content"])
        self.assertNotIn('"result": "888888"', req[2]["messages"][0]["content"])
        self.assertIn('"result": "888888"', req[3]["messages"][-2]["content"])

    def test_excessive_checkpoint_and_checkpoint_timeout_stop_before_third_call(self):
        for active, maximum, status in ((121, 600, "abandoned"), (4, 5, "timeout")):
            _, record, _ = self.execute("human_checkpoint", [response()] * 4,
                                       name=f"checkpoint-{active}", max_elapsed_seconds=maximum,
                                       checkpoint={"feedback": "", "active_seconds": active, "reviewer_id": "test"})
            self.assertEqual(record["terminal_status"], status)
            self.assertEqual(len(self.calls(record)), 2)

    def test_preflight_reservation_stops_request_before_remaining_budget_exceeded(self):
        _, record, _ = self.execute(responses=[response(cost_usd=.1)] * 4, budget_usd=.2)
        self.assertEqual(record["terminal_status"], "budget_exhausted")
        self.assertEqual(len(self.calls(record)), 1)
        self.assertEqual(record["model_cost_usd"], .1)

    def test_reservation_breach_is_retained_and_stops_calls(self):
        _, record, _ = self.execute(responses=[response(cost_usd=.2)] * 4)
        self.assertEqual(record["terminal_status"], "budget_exhausted")
        self.assertEqual(len(self.calls(record)), 1)
        self.assertEqual(record["model_cost_usd"], .2)

    def test_unknown_charge_remains_unknown_and_cannot_be_retried(self):
        _, record, _ = self.execute(responses=[response(error="provider_error", cost_usd=None)] * 4,
                                   allow_provider_retry=True)
        self.assertEqual(record["terminal_status"], "provider_error")
        self.assertIsNone(record["model_cost_usd"])
        self.assertIsNone(self.calls(record)[0]["cost_usd"])
        self.assertEqual(len(self.calls(record)), 1)

    def test_provider_retry_is_explicit_linked_and_counts_both_bills(self):
        path, record, _ = self.execute(responses=[response(error="provider_error", message="scripted failure"),
                                               response('{}', True)], allow_provider_retry=True)
        self.assertEqual(record["terminal_status"], "completed")
        self.assertEqual(record["terminal_reason"], "")
        self.assertEqual(len(self.calls(record)), 2)
        self.assertEqual(sum(e["kind"] == "retry" for e in record["events"]), 1)
        self.assertEqual(sum(e["kind"] == "error" for e in record["events"]), 1)
        self.assertEqual(record["model_cost_usd"], .02)
        requests = self.requests(path)
        self.assertEqual(requests[1]["retry_of"], requests[0]["request_id"])

    def test_timeout_with_unknown_charge_retains_timeout_classification(self):
        _, record, _ = self.execute(responses=[response(error="timeout", cost_usd=None, usage={})])
        self.assertEqual(record["terminal_status"], "timeout")
        self.assertIsNone(record["model_cost_usd"])

    def test_backend_exception_retains_issued_request_and_unknown_accounting(self):
        class Broken(runner.ReplayBackend):
            def respond(self, request):
                raise RuntimeError("Synthetic backend failure")

        path = self.root / "broken"
        result = runner.execute_attempt(self.task, "single", 1, path, Broken())
        record = study.load(path / "run.json")
        self.assertEqual(record["terminal_status"], "provider_error")
        self.assertIsNone(record["model_cost_usd"])
        self.assertEqual(len(self.requests(path)), 1)
        self.assertFalse(result["verified_success"])

    def test_unapproved_retry_stops_and_no_fifth_request_is_allowed(self):
        _, record, _ = self.execute(responses=[response(error="provider_error")] * 5)
        self.assertEqual(len(self.calls(record)), 1)
        self.assertEqual(sum(e["kind"] == "error" for e in record["events"]), 1)
        _, record, _ = self.execute(responses=[response(error="provider_error")] * 5,
                                   name="retry-limit", allow_provider_retry=True)
        self.assertEqual(len(self.calls(record)), 4)
        self.assertEqual(record["model_cost_usd"], .04)

    def test_late_response_and_time_exhaustion_are_classified_timeout(self):
        for duration, calls in ((601, 1), (600, 1)):
            _, record, _ = self.execute(responses=[response(elapsed_seconds=duration)] * 4,
                                       name=f"timeout-{duration}")
            self.assertEqual(record["terminal_status"], "timeout")
            self.assertEqual(record["elapsed_seconds"], duration)
            self.assertEqual(len(self.calls(record)), calls)

    def test_malformed_final_is_retained_without_repair(self):
        content = '{"task_id": "one", "task_id": "two"}'
        path, record, result = self.execute(responses=[response(content, True), response('{}', True)])
        self.assertEqual(record["terminal_status"], "completed")
        self.assertEqual(len(self.calls(record)), 1)
        self.assertIsNone(study.load(path / "answer.json"))
        self.assertFalse(result["automated_correct"])
        responses = [study.load(p) for p in (path / "transcripts").glob("*-response.json")]
        self.assertEqual(responses[0]["response"]["content"], content)

    def test_missing_usage_wrong_model_and_exhausted_script_remain_failures(self):
        for name, script in (("usage", [response(usage={})]),
                             ("model", [response(model_snapshot="changed")]), ("exhausted", [])):
            _, record, _ = self.execute(responses=script, name=name)
            self.assertEqual(record["terminal_status"], "provider_error")
            self.assertEqual(len(self.calls(record)), 1)
        self.assertIsNone(record["model_cost_usd"])

    def test_unrepresentable_charge_is_retained_as_unknown_not_lost_event(self):
        _, record, _ = self.execute(responses=[response(cost_usd=10 ** 400)])
        self.assertIsNone(record["model_cost_usd"])
        self.assertEqual(record["terminal_status"], "provider_error")
        self.assertEqual(len(self.calls(record)), 1)

    def test_tools_are_logged_and_their_outputs_continue_in_same_context(self):
        tool = {"name": "calculate", "arguments": {"expression": "1 + 2"}}
        path, record, _ = self.execute(responses=[response(tool_calls=[tool]), response('{}', True)])
        self.assertEqual([e["kind"] for e in record["events"]], ["model_call", "tool_call", "model_call"])
        self.assertIn('"result": "3"', self.requests(path)[1]["messages"][-2]["content"])
        self.assertEqual(record["tool_cost_usd"], 0)

    def test_disallowed_tool_and_post_final_tools_stop_with_retained_error(self):
        for name, call in (("bad-tool", response(tool_calls=[{"name": "shell", "arguments": {}}])),
                           ("post-final", response('{}', True, tool_calls=[{"name": "read_source", "arguments": {}}]))):
            _, record, _ = self.execute(responses=[call], name=name)
            self.assertEqual(record["terminal_status"], "tool_error")
            self.assertEqual(len(self.calls(record)), 1)

    def test_four_nonfinal_responses_produce_abandoned_attempt_not_discard(self):
        path, record, _ = self.execute(responses=[response()] * 5)
        self.assertEqual(record["terminal_status"], "abandoned")
        self.assertEqual(len(self.calls(record)), 4)
        self.assertTrue((path / "score.json").exists())

    def test_all_artifact_hashes_and_raw_event_references_reconcile(self):
        path, record, _ = self.execute()
        artifacts = study.load(path / "artifacts.json")["sha256"]
        for name, expected in artifacts.items():
            self.assertEqual(hashlib.sha256((path / name).read_bytes()).hexdigest(), expected)
        self.assertEqual([json.loads(line) for line in (path / "events.jsonl").read_text().splitlines()], record["events"])
        self.assertTrue(all((path / e["transcript_ref"]).exists() for e in record["events"]))
        self.assertEqual(study.digest(study.load(path / "session-manifest.json")), record["session_manifest_sha256"])

    def test_attempt_is_not_overwritten_and_fresh_attempt_has_no_history(self):
        path, record, _ = self.execute(responses=[response("PRIVATE-ATTEMPT-ONE", True)])
        original = (path / "run.json").read_bytes()
        with self.assertRaises(FileExistsError):
            self.execute()
        self.assertEqual((path / "run.json").read_bytes(), original)
        second, _, _ = self.execute(name="fresh")
        self.assertNotIn("PRIVATE-ATTEMPT-ONE", json.dumps(self.requests(second)))

    def test_evaluator_is_parsed_only_after_backend_finished(self):
        class Backend(runner.ReplayBackend):
            finished = False

            def respond(self, request):
                self.finished = True
                return super().respond(request)

        backend = Backend()
        get_task = study.get_task

        def deferred(task_id):
            self.assertTrue(backend.finished)
            return get_task(task_id)

        with patch.object(study, "get_task", deferred):
            runner.execute_attempt(self.task, "single", 1, self.root / "deferred", backend)

    def test_backend_reuse_and_live_backend_are_rejected_before_execution(self):
        backend = runner.ReplayBackend()
        runner.execute_attempt(self.task, "single", 1, self.root / "first", backend)
        with self.assertRaises(ValueError):
            runner.execute_attempt(self.task, "single", 2, self.root / "second", backend)
        self.assertFalse((self.root / "second").exists())
        backend = runner.ReplayBackend()
        backend.mode = "live"
        with self.assertRaises(ValueError):
            runner.execute_attempt(self.task, "single", 2, self.root / "live", backend)
        self.assertFalse((self.root / "live").exists())

    def test_invalid_configuration_rejected_before_creating_attempt(self):
        for options in ({"budget_usd": 1}, {"max_elapsed_seconds": 601}, {"checkpoint": {}}):
            with self.assertRaises(ValueError):
                self.execute(**options)
            self.assertFalse((self.root / "attempt").exists())
        with self.assertRaises(ValueError):
            self.execute("multi", allow_provider_retry=True)

    def test_smoke_retains_every_scheduled_attempt_and_refuses_overwrite(self):
        path = self.root / "smoke"
        with patch("socket.socket", side_effect=AssertionError("Network prohibited")) as socket_mock, \
                patch("socket.create_connection", side_effect=AssertionError("Network prohibited")) as connection_mock:
            result = runner.smoke(path, repeats=1)
        socket_mock.assert_not_called()
        connection_mock.assert_not_called()
        self.assertEqual(result["attempts"], 30)
        self.assertEqual(result["verified_successes"], 0)
        schedule = study.load(path / "schedule.json")
        self.assertEqual(len(list(path.glob('*/run.json'))), 30)
        for attempt in schedule["attempts"]:
            record = study.load(path / attempt["attempt_id"] / "run.json")
            self.assertEqual(record["attempt_id"], attempt["attempt_id"])
            self.assertEqual(record["task_sha256"], attempt["task_sha256"])
        with self.assertRaises(FileExistsError):
            runner.smoke(path, repeats=1)


if __name__ == "__main__":
    unittest.main()
