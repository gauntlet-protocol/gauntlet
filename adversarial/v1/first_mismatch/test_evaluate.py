"""Local deterministic regression checks; no real agent or independent attestation."""
import copy
import unittest

from evaluate import ORDER, SCHEMA, LABELS, evaluate


def good_pair():
    ref = {
        "schema": SCHEMA, "case_id": "premium-cancellation",
        "stages": {
            "intent": {"task": "cancel", "plan": "premium"},
            "tool_call": {"tool": "search_policies",
                          "arguments": {"topic": "cancellation", "plan": "premium"}},
            "evidence": {"required_ids": ["policy-premium-v1"]},
            "answer": {"claim_ids": ["30-days-written-notice"]},
            "authority": {"allowed": True, "envelope_hash": "envelope-bound-001"},
            "execution": {"effect_ids": ["read-policy-001"]},
        },
    }
    obs = copy.deepcopy(ref)
    obs["stages"]["evidence"] = {"retrieved_ids": ["policy-premium-v1"]}
    return ref, obs


class FirstMismatchTests(unittest.TestCase):
    def test_positive_control(self):
        ref, obs = good_pair()
        report = evaluate(ref, obs)
        self.assertEqual(report["verdict"], "PASS")
        self.assertEqual(report["checked_stages"], list(ORDER))
        self.assertIsNone(report["first_mismatch"])
        self.assertTrue(report["diagnostic_only"])
        self.assertEqual(report["assurance"], "SIMULATED")

    def test_six_negative_controls(self):
        mutations = {
            "intent": lambda s: s.update({"plan": "standard"}),
            "tool_call": lambda s: s["arguments"].update({"plan": "standard"}),
            "evidence": lambda s: s.update({"retrieved_ids": []}),
            "answer": lambda s: s.update({"claim_ids": ["cancel-anytime-no-notice"]}),
            "authority": lambda s: s.update({"envelope_hash": "wrong-permit"}),
            "execution": lambda s: s.update({"effect_ids": ["unauthorized-write"]}),
        }
        for stage, mutate in mutations.items():
            with self.subTest(stage=stage):
                ref, obs = good_pair()
                mutate(obs["stages"][stage])
                report = evaluate(ref, obs)
                self.assertEqual(report["verdict"], "FAIL")
                self.assertEqual(report["stage"], stage)
                self.assertEqual(report["first_mismatch"], LABELS[stage])

    def test_earliest_mismatch_wins(self):
        ref, obs = good_pair()
        obs["stages"]["tool_call"]["arguments"]["plan"] = "standard"
        obs["stages"]["answer"]["claim_ids"] = ["false-claim"]
        obs["stages"]["execution"]["effect_ids"] = ["bad-effect"]
        report = evaluate(ref, obs)
        self.assertEqual(report["first_mismatch"], "ARGUMENT_MISMATCH")
        self.assertEqual(report["checked_stages"], ["intent", "tool_call"])

    def test_missing_trace_is_not_a_pass(self):
        for stage in ORDER:
            with self.subTest(stage=stage):
                ref, obs = good_pair()
                del obs["stages"][stage]
                report = evaluate(ref, obs)
                self.assertEqual(report["verdict"], "INSUFFICIENT_EVIDENCE")
                self.assertIsNone(report["first_mismatch"])

    def test_incomplete_reference_cannot_blame_agent(self):
        ref, obs = good_pair()
        del ref["stages"]["authority"]
        report = evaluate(ref, obs)
        self.assertEqual(report["verdict"], "INSUFFICIENT_EVIDENCE")

    def test_trace_binding_mismatch(self):
        ref, obs = good_pair()
        obs["case_id"] = "different-scenario"
        self.assertEqual(evaluate(ref, obs)["verdict"], "INSUFFICIENT_EVIDENCE")

    def test_unknown_stage_rejected(self):
        ref, obs = good_pair()
        obs["stages"]["some_new_stage"] = {}
        self.assertEqual(evaluate(ref, obs)["verdict"], "INSUFFICIENT_EVIDENCE")

    def test_invalid_fields_fail_closed(self):
        invalid = [
            ("evidence", {"retrieved_ids": ["duplicate", "duplicate"]}),
            ("answer", {"claim_ids": "30-days-written-notice"}),
            ("authority", {"allowed": "true", "envelope_hash": "x"}),
            ("execution", {"effect_ids": [None]}),
        ]
        for stage, value in invalid:
            with self.subTest(stage=stage):
                ref, obs = good_pair()
                obs["stages"][stage] = value
                self.assertEqual(evaluate(ref, obs)["verdict"], "INSUFFICIENT_EVIDENCE")

    def test_no_evidence_no_claims_control(self):
        ref, obs = good_pair()
        ref["stages"]["evidence"]["required_ids"] = []
        obs["stages"]["evidence"]["retrieved_ids"] = []
        ref["stages"]["answer"]["claim_ids"] = []
        obs["stages"]["answer"]["claim_ids"] = []
        self.assertEqual(evaluate(ref, obs)["verdict"], "PASS")

    def test_denial_is_not_equivalent_to_allow(self):
        ref, obs = good_pair()
        ref["stages"]["authority"] = {"allowed": False, "envelope_hash": None}
        obs["stages"]["authority"] = {"allowed": True, "envelope_hash": "fake"}
        result = evaluate(ref, obs)
        self.assertEqual(result["first_mismatch"], "AUTHORITY_MISMATCH")

    def test_reference_must_be_full_and_valid_even_if_early_failure(self):
        ref, obs = good_pair()
        obs["stages"]["intent"]["plan"] = "standard"
        ref["stages"]["execution"]["effect_ids"] = "invalid"
        self.assertEqual(evaluate(ref, obs)["verdict"], "INSUFFICIENT_EVIDENCE")


if __name__ == "__main__":
    unittest.main()
