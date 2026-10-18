import unittest
from completion.exup_bridge import bridge, digest
from completion.completion import evaluate

def receipt():
    value = {"protocol": "EXUP-EXECUTE-01", "workload_id": "sample", "verdict": "PASS"}
    value["receipt_sha256"] = digest(value)
    return value

def effects():
    return {"observer": {"identity": "external-observer", "independent": True, "coverage_complete": True,
                         "provenance_verified": True}, "effects": [{"id": "effect-1"}]}

def witness(r, e):
    return {"receipt_sha256": r["receipt_sha256"], "effect_record_sha256": digest(e),
            "observer_id": "external-observer", "quality_approved": True, "cost_usd": 2.5}

def effect_ok(_):
    return {"status": "PASS", "observed_effects": 1}

class BridgeTests(unittest.TestCase):
    def test_verified(self):
        r,e=receipt(),effects()
        self.assertEqual(bridge(r,e,witness(r,e),effect_ok,evaluate)["status"],"PASS")

    def test_wrong_binding_unknown(self):
        r,e=receipt(),effects()
        w=witness(r,e);w["receipt_sha256"]="other"
        self.assertEqual(bridge(r,e,w,effect_ok,evaluate)["status"],"INSUFFICIENT_EVIDENCE")

    def test_missing_quality_unknown(self):
        r,e=receipt(),effects()
        w=witness(r,e);del w["quality_approved"]
        self.assertEqual(bridge(r,e,w,effect_ok,evaluate)["status"],"INSUFFICIENT_EVIDENCE")

    def test_effect_failure(self):
        r,e=receipt(),effects()
        self.assertEqual(bridge(r,e,witness(r,e),lambda _: {"status":"FAIL","observed_effects":1},evaluate)["status"],"FAIL")

    def test_tampered_receipt(self):
        r,e=receipt(),effects(); w=witness(r,e);r["workload_id"]="tampered"
        with self.assertRaises(ValueError): bridge(r,e,w,effect_ok,evaluate)

    def test_no_effect(self):
        r,e=receipt(),effects()
        self.assertNotEqual(bridge(r,e,witness(r,e),lambda _: {"status":"PASS","observed_effects":0},evaluate)["status"],"PASS")

    def test_not_independent(self):
        r,e=receipt(),effects();e["observer"]["independent"]=False
        self.assertEqual(bridge(r,e,witness(r,e),effect_ok,evaluate)["status"],"INSUFFICIENT_EVIDENCE")

if __name__ == "__main__":
    unittest.main()
