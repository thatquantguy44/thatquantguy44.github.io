"""Synthetic software checks only; none of these records are research observations."""

import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

import study


def ideal_answer(task_id):
    """Construct a key-derived scorer fixture, never a participant/baseline output."""
    task, gold = study.get_task(task_id)
    return {"task_id": task_id, "answers": {
        aid: {"value": expected["value"], "unit": expected["unit"], "citations": [
            {"source_id": e["source_id"], "quote": e["span"]} for e in expected["required_evidence"]]}
        for aid, expected in gold["answers"].items()}}


def synthetic_record(task, answer, condition="single"):
    """Invented positive-control metadata for tests, not a real model/reviewer log."""
    run = study.run_template(task, condition, 1)
    roles = {"fixed": [], "single": ["single"], "self_review": ["draft", "critique", "revision", "final"],
             "human_checkpoint": ["single", "single", "single"],
             "multi": ["coordinator_plan", "worker_1", "worker_2", "coordinator_final"]}[condition]
    run.update({"answer_sha256": study.digest(answer), "session_manifest_sha256": "a" * 64,
                "terminal_status": "completed", "model_snapshot": "synthetic-test-model" if roles else None,
                "started_at_utc": "2026-10-26T12:00:00Z", "ended_at_utc": "2026-10-26T12:01:00Z",
                "elapsed_seconds": 60, "model_cost_usd": .01 * len(roles), "tool_cost_usd": 0,
                "human_intervention_seconds": 5 if condition == "human_checkpoint" else 0,
                "operator_seconds": 2, "boundary_verified": True, "operator_id": "test-operator",
                "review": {"reviewer_id": "test-reviewer", "independent": True, "passed": True,
                           "verification_seconds": 10, "notes": "Synthetic software positive control."}})
    for index, role in enumerate(roles):
        run["events"].append({"kind": "model_call", "role": role,
                              "at_utc": f"2026-10-26T12:00:{index * 10:02d}Z", "elapsed_seconds": 1,
                              "transcript_ref": f"synthetic-call-{index}.json", "cost_usd": .01,
                              "model_snapshot": "synthetic-test-model", "input_tokens": 20,
                              "output_tokens": 10, "reasoning_tokens": 0, "cached_tokens": 0})
        if condition == "human_checkpoint" and index == 1:
            run["events"].append({"kind": "human_checkpoint", "at_utc": "2026-10-26T12:00:12Z",
                                  "elapsed_seconds": 5, "active_seconds": 5, "feedback": "Check units.",
                                  "reviewer_id": "test-checkpoint-reviewer",
                                  "transcript_ref": "synthetic-feedback.txt"})
    return run


class AnswerScoringTests(unittest.TestCase):
    def setUp(self):
        self.task, self.gold = study.get_task("calculate_parallel")
        self.answer = ideal_answer(self.task["task_id"])

    def errors(self):
        return study.check_answer(self.task, self.gold, self.answer)

    def test_every_key_has_literal_support_in_public_sources(self):
        self.assertEqual(study.validate()["development_tasks"], 6)
        for task_id in study.bank()[0]:
            task, gold = study.get_task(task_id)
            self.assertEqual(study.check_answer(task, gold, ideal_answer(task_id)), [])

    def test_derived_gold_values_recomputed_independently(self):
        # Explicit calculations from source numbers, independent of scoring helpers.
        _, keys = study.bank()
        margin = (Decimal(200000) - Decimal(120000)) / Decimal(200000) * 100
        compounded = ((1 + (Decimal(10) - 1) / 100) * (1 + (Decimal(-5) - 1) / 100) - 1) * 100
        usd = Decimal(900) * Decimal("1.10")
        self.assertEqual(margin, Decimal(str(keys["calculate_parallel"]["answers"]["gross_margin"]["value"])))
        self.assertEqual(compounded, Decimal(str(keys["calculate_sequential"]["answers"]["total_net"]["value"])))
        self.assertEqual(usd, Decimal(str(keys["reconcile_sequential"]["answers"]["net_usd"]["value"])))
        self.assertEqual(Decimal(40) / 500 * 100, Decimal(str(keys["calculate_parallel"]["answers"]["conversion"]["value"])))

    def test_wrong_unit_fails_even_when_number_is_correct(self):
        self.answer["answers"]["gross_margin"]["unit"] = "fraction"
        self.assertTrue(self.errors())

    def test_wrong_value_fails_with_real_citations(self):
        self.answer["answers"]["conversion"]["value"] = 80
        self.assertTrue(self.errors())

    def test_boolean_is_not_a_number(self):
        self.answer["answers"]["conversion"]["value"] = True
        self.assertTrue(self.errors())

    def test_nonverbatim_quote_fails(self):
        self.answer["answers"]["conversion"]["citations"][0]["quote"] = "visitors: 999 [people]"
        self.assertTrue(self.errors())

    def test_real_but_irrelevant_citation_fails(self):
        self.answer["answers"]["gross_margin"]["citations"] = [{"source_id": "funnel", "quote": "visitors: 500 [people]"}]
        self.assertTrue(self.errors())

    def test_missing_derivation_input_fails(self):
        self.answer["answers"]["gross_margin"]["citations"].pop()
        self.assertTrue(self.errors())

    def test_extra_unscored_claim_fails(self):
        self.answer["answers"]["unrequested_claim"] = {"value": "success"}
        self.assertTrue(self.errors())

    def test_unsupported_certainty_fails(self):
        task, gold = study.get_task("synthesize_sequential")
        answer = ideal_answer(task["task_id"])
        self.assertFalse(study.check_answer(task, gold, answer))
        answer["answers"]["backup_retention"] = {"value": 45, "unit": "days", "citations": []}
        self.assertTrue(study.check_answer(task, gold, answer))

    def test_fraction_does_not_pass_as_percent(self):
        self.answer["answers"]["gross_margin"]["value"] = .4
        self.assertTrue(self.errors())

    def test_parse_rejects_duplicate_keys_and_nonfinite_numbers(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "answer.json"
            for text in ('{"x": 1, "x": 2}', '{"x": NaN}', '{"x": Infinity}', '{"x": 1e999}'):
                path.write_text(text)
                with self.assertRaises(ValueError):
                    study.load(path)


class ProtocolRecordTests(unittest.TestCase):
    def setUp(self):
        self.task, self.gold = study.get_task("reconcile_parallel")
        self.answer = ideal_answer(self.task["task_id"])
        self.run = synthetic_record(self.task, self.answer)

    def result(self):
        return study.score(self.task, self.gold, self.answer, self.run)

    def test_correct_answer_without_run_is_not_verified(self):
        result = study.score(self.task, self.gold, self.answer)
        self.assertTrue(result["automated_correct"])
        self.assertFalse(result["verified_success"])

    def test_synthetic_positive_controls_for_all_five_conditions(self):
        for condition in study.CONDITIONS:
            with self.subTest(condition=condition):
                run = synthetic_record(self.task, self.answer, condition)
                self.assertTrue(study.score(self.task, self.gold, self.answer, run)["verified_success"])

    def test_missing_or_nonindependent_review_is_not_verified(self):
        for change in ({"passed": None}, {"passed": False}, {"independent": False}, {"reviewer_id": "test-operator"}):
            with self.subTest(change=change):
                self.run = synthetic_record(self.task, self.answer)
                self.run["review"].update(change)
                self.assertFalse(self.result()["verified_success"])

    def test_unknown_cost_is_not_zero(self):
        self.run["model_cost_usd"] = None
        self.assertFalse(self.result()["verified_success"])

    def test_budget_overrun_fails(self):
        self.run["model_cost_usd"] = .51
        self.run["events"][0]["cost_usd"] = .51
        self.assertFalse(self.result()["verified_success"])

    def test_unreconciled_billing_fails(self):
        self.run["events"][0]["cost_usd"] = .02
        self.assertFalse(self.result()["verified_success"])

    def test_fifth_model_call_fails(self):
        self.run["events"] *= 5
        self.run["model_cost_usd"] = .05
        self.assertFalse(self.result()["verified_success"])

    def test_unscheduled_human_help_fails(self):
        self.run["human_intervention_seconds"] = 1
        self.assertFalse(self.result()["verified_success"])

    def test_timeout_with_correct_output_is_not_success(self):
        self.run["terminal_status"] = "timeout"
        self.assertFalse(self.result()["verified_success"])

    def test_answer_or_task_tampering_fails(self):
        self.run["answer_sha256"] = "b" * 64
        self.assertFalse(self.result()["verified_success"])
        self.run = synthetic_record(self.task, self.answer)
        self.run["task_sha256"] = "b" * 64
        self.assertFalse(self.result()["verified_success"])

    def test_unknown_token_usage_fails(self):
        self.run["events"][0]["reasoning_tokens"] = None
        self.assertFalse(self.result()["verified_success"])

    def test_wrong_multi_context_sequence_fails(self):
        self.run = synthetic_record(self.task, self.answer, "multi")
        self.run["events"][1]["role"] = "single"
        self.assertFalse(self.result()["verified_success"])

    def test_human_checkpoint_timing_and_cap(self):
        self.run = synthetic_record(self.task, self.answer, "human_checkpoint")
        self.run["human_intervention_seconds"] = 121
        self.run["events"][2]["active_seconds"] = 121
        self.assertFalse(self.result()["verified_success"])

    def test_missing_input_isolation_fails(self):
        self.run["boundary_verified"] = False
        self.assertFalse(self.result()["verified_success"])

    def test_impossible_event_duration_fails(self):
        self.run["events"][0]["elapsed_seconds"] = 61
        self.assertFalse(self.result()["verified_success"])

    def test_event_cannot_finish_after_submission(self):
        self.run["events"][0]["at_utc"] = "2026-10-26T12:00:59Z"
        self.run["events"][0]["elapsed_seconds"] = 5
        self.assertFalse(self.result()["verified_success"])

    def test_checkpoint_reviewer_cannot_verify_own_assistance(self):
        self.run = synthetic_record(self.task, self.answer, "human_checkpoint")
        self.run["review"]["reviewer_id"] = "test-checkpoint-reviewer"
        self.assertFalse(self.result()["verified_success"])


class PreparationTests(unittest.TestCase):
    def test_schedule_is_paired_reproducible_and_complete(self):
        schedule = study.make_schedule()
        self.assertEqual(schedule, study.make_schedule())
        attempts = schedule["attempts"]
        self.assertEqual(len(attempts), 90)
        self.assertEqual(len({a["attempt_id"] for a in attempts}), 90)
        self.assertEqual(sum(a["condition"] != "fixed" for a in attempts), 72)
        for block in range(1, 19):
            group = [a for a in attempts if a["block"] == block]
            self.assertEqual({a["condition"] for a in group}, set(study.CONDITIONS))
            self.assertEqual(len({(a["task_id"], a["repeat"]) for a in group}), 1)

    def test_clean_export_has_no_gold_or_evaluator(self):
        task, _ = study.get_task("synthesize_sequential")
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "participant"
            study.export_task(task, target)
            self.assertEqual({p.name for p in target.iterdir()}, {"task.json", "instructions.txt", "answer-template.json"})
            public = study.load(target / "task.json")
            self.assertNotIn("required_evidence", json.dumps(public))
            self.assertNotIn("absolute_tolerance", json.dumps(public))
            self.assertEqual(study.digest(public), study.digest(task))
            with self.assertRaises(ValueError):
                study.export_task(task, target)

    def test_templates_keep_unobserved_values_unknown(self):
        task, _ = study.get_task("reconcile_parallel")
        run = study.run_template(task, "single", 1)
        self.assertIsNone(run["model_cost_usd"])
        self.assertIsNone(run["elapsed_seconds"])
        self.assertIsNone(run["review"]["passed"])

    def test_public_question_does_not_reveal_missing_answer(self):
        task, _ = study.get_task("synthesize_sequential")
        question = next(q for q in task["questions"] if q["answer_id"] == "backup_retention")
        self.assertEqual(question["unit"], "days")
        self.assertEqual(question["value_type"], "number_or_null")

    def test_schedule_cannot_overwrite_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "schedule.json"
            study.dump(path, study.make_schedule())
            with self.assertRaises(FileExistsError):
                study.dump(path, study.make_schedule())


if __name__ == "__main__":
    unittest.main()
