import unittest
from completion.neo20_evidence import evaluate, EXPECTED

class NEO20EvidenceTests(unittest.TestCase):
    def fixture(self):
        arms={key:{"total_calls":192,"completed_calls":180,"pass_calls":170} for key in EXPECTED}
        return {"experiment":"NEO-20","completeness":{"complete":True},"conditions":arms},{"experiment":"NEO-20","data_complete":True,"verdicts":{"H1_budget_recovery":"SUPPORTED"}}
    def test_inference_is_not_external_effect(self):
        evidence,verdict=self.fixture()
        out=evaluate(evidence,verdict)
        self.assertEqual(out["inference_calls"],1728)
        self.assertEqual(out["experiment_completeness"],"COMPLETE")
        self.assertEqual(out["status"],"INSUFFICIENT_EVIDENCE")
        self.assertIsNone(out["verified_completions"])
        self.assertIsNone(out["cost_per_verified_completion_usd"])
    def test_incomplete(self):
        evidence,verdict=self.fixture()
        evidence["conditions"][EXPECTED[0]]["total_calls"]=191
        self.assertEqual(evaluate(evidence,verdict)["experiment_completeness"],"INCOMPLETE")
    def test_bad_counts(self):
        evidence,verdict=self.fixture()
        evidence["conditions"][EXPECTED[0]]["pass_calls"]=200
        with self.assertRaises(ValueError):evaluate(evidence,verdict)
    def test_no_effect_claim_from_supported_hypothesis(self):
        evidence,verdict=self.fixture()
        verdict["verdicts"]["H4_economic_substitution"]="SUPPORTED"
        self.assertFalse(evaluate(evidence,verdict)["independent_effect_verification"])

if __name__=="__main__":
    unittest.main()
