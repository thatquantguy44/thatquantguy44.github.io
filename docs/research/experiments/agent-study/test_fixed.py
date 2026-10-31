"""Independent packet tests of the deterministic baseline's supported grammar."""

import copy
import unittest

import fixed


def packet(instructions, sources, questions):
    return {"task_id": "unseen_case", "instructions": instructions,
            "sources": [{"source_id": f"doc_{i}", "text": text} for i, text in enumerate(sources)],
            "questions": [{"answer_id": aid, "question": question, "unit": unit, "value_type": kind}
                          for aid, question, unit, kind in questions]}


class FixedTests(unittest.TestCase):
    def test_explicit_authority_and_changed_values(self):
        task = packet("Final signed reports override drafts.",
                      ["Draft. inventory: 90 [items].", "Final signed report. inventory: 71 [items]."],
                      [("inventory", "What is inventory?", "items", "number")])
        answer = fixed.execute(task)["answers"]["inventory"]
        self.assertEqual(answer["value"], 71)
        self.assertEqual(answer["citations"], [{"source_id": "doc_1", "quote": task["sources"][1]["text"]}])
        shuffled = copy.deepcopy(task)
        shuffled["task_id"] = "different_id"
        shuffled["sources"].reverse()
        self.assertEqual(fixed.execute(shuffled)["answers"], fixed.execute(task)["answers"])

    def test_does_not_invent_authority(self):
        task = packet("Report inventory.", ["Draft. inventory: 90 [items].", "Final signed report. inventory: 71 [items]."],
                      [("inventory", "What is inventory?", "items", "number")])
        answer, report = fixed.execute_with_report(task)
        self.assertIsNone(answer["answers"]["inventory"]["value"])
        self.assertIn("Conflicting", report["inventory"]["reason"])

    def test_corrected_currency_and_rule_provenance(self):
        task = packet("The correction supersedes the original. Convert net amount to USD.",
                      ["Original bill. net_amount: 3 [EUR].", "Signed correction. net_amount: 2.5 [EUR].",
                       "Reporting rule: corrections supersede originals; exclude taxes.", "Rate: 1 EUR = 1.20 USD."],
                      [("converted", "What is corrected net amount?", "USD", "number")])
        answer = fixed.execute(task)["answers"]["converted"]
        self.assertEqual(answer["value"], 3)
        self.assertEqual({c["source_id"] for c in answer["citations"]}, {"doc_1", "doc_2", "doc_3"})

    def test_formula_uses_decimal_and_explicit_values(self):
        task = packet("Yield percent = successes / trials * 100.",
                      ["successes: 0.3 [items]. trials: 0.6 [items]."],
                      [("yield", "What is yield percent?", "percent", "number")])
        self.assertEqual(fixed.execute(task)["answers"]["yield"]["value"], 50)

    def test_formula_mixed_units_abstains(self):
        task = packet("Ratio percent = numerator / denominator * 100.",
                      ["numerator: 2 [USD]. denominator: 5 [people]."],
                      [("ratio", "What is ratio?", "percent", "number")])
        self.assertIsNone(fixed.execute(task)["answers"]["ratio"]["value"])

    def test_residual_dimensions_abstain(self):
        task = packet("Ratio percent = revenue / expenses * revenue * 100.",
                      ["revenue: 20 [USD]. expenses: 5 [USD]."],
                      [("ratio", "What is ratio?", "percent", "number")])
        self.assertIsNone(fixed.execute(task)["answers"]["ratio"]["value"])

    def test_addition_requires_matching_dimensions(self):
        task = packet("Ratio percent = (revenue + 1) / expenses * 100.",
                      ["revenue: 20 [USD]. expenses: 5 [USD]."],
                      [("ratio", "What is ratio?", "percent", "number")])
        self.assertIsNone(fixed.execute(task)["answers"]["ratio"]["value"])

    def test_literal_decimal_formula_is_not_split(self):
        task = packet("Ratio percent = numerator / denominator * 1.5 * 100. Use percent.",
                      ["numerator: 2 [items]. denominator: 5 [items]."],
                      [("ratio", "What is ratio?", "percent", "number")])
        self.assertEqual(fixed.execute(task)["answers"]["ratio"]["value"], 60)

    def test_integral_magnitude_limit(self):
        task = packet("Report inventory.", ["inventory: " + "1" + "0" * 101 + " [items]."],
                      [("inventory", "What is inventory?", "items", "number")])
        self.assertIsNone(fixed.execute(task)["answers"]["inventory"]["value"])

    def test_zero_denominator_abstains(self):
        task = packet("Ratio percent = numerator / denominator * 100.",
                      ["numerator: 2 [items]. denominator: 0 [items]."],
                      [("ratio", "What is ratio?", "percent", "number")])
        self.assertIsNone(fixed.execute(task)["answers"]["ratio"]["value"])

    def test_code_in_formula_is_never_executed(self):
        task = packet("Ratio percent = __import__('os').getcwd().", ["x: 1 [items]."],
                      [("ratio", "What is ratio?", "percent", "number")])
        self.assertIsNone(fixed.execute(task)["answers"]["ratio"]["value"])

    def test_missing_or_unparseable_record_abstains(self):
        task = packet("Report inventory.", ["inventory: lots [items]."],
                      [("inventory", "What is inventory?", "items", "number")])
        self.assertEqual(fixed.execute(task)["answers"]["inventory"],
                         {"value": None, "unit": "unknown", "citations": []})

    def test_unknown_currency_conversion_abstains(self):
        task = packet("Convert balance to USD.", ["balance: 10 [EUR]. Rate: 1 EUR = 1.1 GBP."],
                      [("balance", "What is balance?", "USD", "number")])
        self.assertIsNone(fixed.execute(task)["answers"]["balance"]["value"])

    def test_ambiguous_rates_abstain(self):
        task = packet("Convert balance to USD.", ["balance: 10 [EUR].", "1 EUR = 1.1 USD. 1 EUR = 1.2 USD."],
                      [("balance", "What is balance?", "USD", "number")])
        self.assertIsNone(fixed.execute(task)["answers"]["balance"]["value"])

    def test_asof_scope_is_disclosed_unsupported(self):
        task = packet("Report balance as of 2026-01-01.", ["balance: 10 [USD]."],
                      [("balance", "What is balance?", "USD", "number")])
        answer, report = fixed.execute_with_report(task)
        self.assertFalse(report["balance"]["supported"])
        self.assertIsNone(answer["answers"]["balance"]["value"])

    def test_boolean_synthesis_is_disclosed_unsupported(self):
        task = packet("Combine service readiness.", ["Service A ready; service B not ready."],
                      [("ready", "Is launch ready?", "boolean", "boolean")])
        answer, report = fixed.execute_with_report(task)
        self.assertFalse(report["ready"]["supported"])
        self.assertIsNone(answer["answers"]["ready"]["value"])


if __name__ == "__main__":
    unittest.main()
