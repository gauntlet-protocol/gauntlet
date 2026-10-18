import unittest
from completion.exup_bridge import bridge, digest
from completion.completion import evaluate as evaluate_completion
from conformance.effect_boundary import evaluate as evaluate_effect, digest as grant_digest

class EffectIntegration(unittest.TestCase):
    def test_authorized_then_revoked(self):
        r = {"protocol":"EXUP-EXECUTE-01","workload_id":"test","verdict":"PASS"}
        r["receipt_sha256"] = digest(r)
        g = {"id":"g","attempt_id":"a","decision":"ALLOW","scope":"read","issued_at":1,"expires_at":3}
        e = {"id":"e","attempt_id":"a","authorization_id":"g","authorization_digest":grant_digest(g),"scope":"read","timestamp":2}
        record = {"attempts":[{"id":"a"}],"authorizations":[g],"effects":[e],
                  "observer":{"identity":"test-witness","independent":True,"coverage_complete":True,"provenance_verified":True}}
        w = {"receipt_sha256":r["receipt_sha256"],"effect_record_sha256":digest(record),
             "observer_id":"test-witness","cost_usd":2,"quality_approved":True}
        self.assertEqual(bridge(r,record,w,evaluate_effect,evaluate_completion)["status"],"PASS")
        e["timestamp"]=5
        w["effect_record_sha256"]=digest(record)
        self.assertEqual(bridge(r,record,w,evaluate_effect,evaluate_completion)["status"],"FAIL")

if __name__ == "__main__":
    unittest.main()
