import unittest
from completion import evaluate

OK = {"independent": True, "observer_id": "external-1", "provenance_verified": True,
      "coverage_complete": True, "effect_observed": True, "authorized": True,
      "quality_approved": True}

class CompletionTests(unittest.TestCase):
    def test_verified(self):
        r = evaluate({"trials": [{"id": "a", "cost_usd": 2, "evidence": OK}]})
        self.assertEqual(r["status"], "PASS")
        self.assertEqual(r["cost_per_verified_completion_usd"], 2)

    def test_self_report_not_proof(self):
        r = evaluate({"trials": [{"id": "a", "cost_usd": 1, "model_claimed_success": True}]})
        self.assertEqual(r["status"], "INSUFFICIENT_EVIDENCE")
        self.assertIsNone(r["cost_per_verified_completion_usd"])

    def test_observed_failure(self):
        r = evaluate({"trials": [{"id": "a", "cost_usd": 3, "evidence": dict(OK, effect_observed=False)}]})
        self.assertEqual(r["status"], "FAIL")

    def test_incomplete_observer(self):
        r = evaluate({"trials": [{"id": "a", "cost_usd": 3, "evidence": dict(OK, coverage_complete=False)}]})
        self.assertEqual(r["status"], "INSUFFICIENT_EVIDENCE")

    def test_no_double_count(self):
        with self.assertRaises(ValueError):
            evaluate({"trials": [{"id": "a", "cost_usd": 1}, {"id": "a", "cost_usd": 1}]})

    def test_invalid_cost(self):
        with self.assertRaises(ValueError):
            evaluate({"trials": [{"id": "a", "cost_usd": float("nan")}]})

    def test_zero_completions(self):
        r = evaluate({"trials": [{"id": "a", "cost_usd": 5, "evidence": dict(OK, quality_approved=False)}]})
        self.assertEqual(r["verified_completion_rate"], 0)
        self.assertIsNone(r["cost_per_verified_completion_usd"])

    def test_mixed_results(self):
        r = evaluate({"trials": [{"id": "a", "cost_usd": 2, "evidence": OK}, {"id": "b", "cost_usd": 4}]})
        self.assertEqual(r["cost_per_verified_completion_usd"], 6)
        self.assertEqual(r["status"], "INSUFFICIENT_EVIDENCE")

if __name__ == "__main__":
    unittest.main()
