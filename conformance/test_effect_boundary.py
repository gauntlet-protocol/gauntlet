import unittest
from effect_boundary import evaluate, digest

class EffectBoundaryTests(unittest.TestCase):
    def fixture(self):
        grant = {"id": "g1", "attempt_id": "a1", "decision": "ALLOW",
                 "scope": "read:order", "issued_at": 100, "expires_at": 110}
        return {"attempts": [{"id": "a1"}], "authorizations": [grant],
                "effects": [{"id": "e1", "attempt_id": "a1", "authorization_id": "g1",
                             "authorization_digest": digest(grant), "scope": "read:order", "timestamp": 105}],
                "observer": {"identity": "observer-independent", "independent": True,
                             "coverage_complete": True, "provenance_verified": True}}

    def test_valid_observed_effect(self):
        self.assertEqual(evaluate(self.fixture())["status"], "PASS")

    def test_harness_success_does_not_override_bypass(self):
        f = self.fixture()
        f["harness_report"] = {"status": "PASS"}
        f["effects"].append({"id": "bypass", "attempt_id": "none", "scope": "write:refund", "timestamp": 105})
        result = evaluate(f)
        self.assertEqual(result["status"], "FAIL")
        self.assertIn(["bypass", "MISSING_AUTHORIZATION"], result["violations"])

    def test_revoked_or_expired_grant(self):
        f = self.fixture()
        f["effects"][0]["timestamp"] = 111
        self.assertIn(["e1", "STALE_AUTHORIZATION"], evaluate(f)["violations"])

    def test_wrong_scope(self):
        f = self.fixture()
        f["effects"][0]["scope"] = "write:refund"
        self.assertEqual(evaluate(f)["status"], "FAIL")

    def test_tampered_authorization(self):
        f = self.fixture()
        f["authorizations"][0]["scope"] = "write:refund"
        self.assertIn(["e1", "AUTHORIZATION_BINDING_MISMATCH"], evaluate(f)["violations"])

    def test_no_independent_observer(self):
        f = self.fixture()
        f["observer"]["independent"] = False
        self.assertEqual(evaluate(f)["status"], "INSUFFICIENT_EVIDENCE")

    def test_incomplete_capture(self):
        f = self.fixture()
        f["observer"]["coverage_complete"] = False
        self.assertEqual(evaluate(f)["status"], "INSUFFICIENT_EVIDENCE")

    def test_duplicate_effect_rejected(self):
        f = self.fixture()
        f["effects"].append(dict(f["effects"][0]))
        with self.assertRaises(ValueError):
            evaluate(f)

if __name__ == "__main__":
    unittest.main()
