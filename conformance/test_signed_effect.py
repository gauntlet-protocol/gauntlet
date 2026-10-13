import base64
import copy
import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from signed_effect import sha, signable, verify

class SignedEffectTests(unittest.TestCase):
    def setUp(self):
        self.priv = {k: Ed25519PrivateKey.generate() for k in ("auth","exec","source","observer")}
        self.kinds = ("AUTHORIZATION", "EXECUTION_RECEIPT", "SOURCE_STATE", "EFFECT_ATTESTATION")
        self.trust = {"source_integrity_independently_audited": True, "keys": {
            key: {"operator": key, "allowed_kinds": [kind],
                  "public_hex": self.priv[key].public_key().public_bytes(Encoding.Raw, PublicFormat.Raw).hex()}
            for key, kind in zip(self.priv, self.kinds)}}
        self.bundle = {}
        self.put("authorization", "auth", {"effect_id":"e1","scope":"balance",
             "decision":"ALLOW","issued_at":10,"expires_at":30,
             "predicate":{"field":"balance","delta":-100}})
        self.put("execution", "exec", {"effect_id":"e1","scope":"balance",
             "transaction_id":"t1","authorization_sha256":sha(self.bundle["authorization"]),
             "result":"SUCCESS"})
        self.put("source_state", "source", {"effect_id":"e1","scope":"balance",
             "transaction_id":"t1","execution_sha256":sha(self.bundle["execution"]),
             "committed_at":20,"source_commit_id":"commit-1",
             "before":{"balance":500},"after":{"balance":400}})
        self.put("observation", "observer", {"effect_id":"e1","transaction_id":"t1",
             "execution_sha256":sha(self.bundle["execution"]),
             "source_sha256":sha(self.bundle["source_state"]),
             "predicate_sha256":sha(self.bundle["authorization"]["payload"]["predicate"])})
    def put(self, name, key, payload):
        env = {"kind":self.kinds[list(self.priv).index(key)],"key_id":key,"payload":payload}
        env["signature"] = base64.b64encode(self.priv[key].sign(signable(env))).decode()
        self.bundle[name] = env
    def test_verified(self):
        self.assertEqual(verify(self.bundle,self.trust)["status"],"VERIFIED_EFFECT")
    def test_executor_claim_only_cannot_prove_effect(self):
        b=copy.deepcopy(self.bundle); del b["source_state"]
        self.assertEqual(verify(b,self.trust)["status"],"INSUFFICIENT_EVIDENCE")
    def test_tamper(self):
        self.bundle["source_state"]["payload"]["after"]["balance"]=4000
        self.assertEqual(verify(self.bundle,self.trust)["status"],"INSUFFICIENT_EVIDENCE")
    def test_signed_no_effect(self):
        p=copy.deepcopy(self.bundle["source_state"]["payload"])
        p["after"]["balance"]=500
        self.put("source_state","source",p)
        q=copy.deepcopy(self.bundle["observation"]["payload"])
        q["source_sha256"]=sha(self.bundle["source_state"])
        self.put("observation","observer",q)
        self.assertEqual(verify(self.bundle,self.trust)["status"],"VIOLATION")
    def test_same_operator_is_not_independent(self):
        self.trust["keys"]["observer"]["operator"]="exec"
        self.assertEqual(verify(self.bundle,self.trust)["status"],"INSUFFICIENT_EVIDENCE")
    def test_untrusted_source_integrity(self):
        self.trust["source_integrity_independently_audited"]=False
        self.assertEqual(verify(self.bundle,self.trust)["status"],"INSUFFICIENT_EVIDENCE")
    def test_signature_replay_wrong_effect(self):
        self.bundle["observation"]["payload"]["effect_id"]="e2"
        self.assertEqual(verify(self.bundle,self.trust)["status"],"INSUFFICIENT_EVIDENCE")
if __name__=="__main__":
    unittest.main()
