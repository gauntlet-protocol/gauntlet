import base64
import copy
import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from completion.signed_exup_gate import evaluate, canonical_digest
from conformance.signed_effect import sha, signable

class SignedEXUPTests(unittest.TestCase):
    def setUp(self):
        kinds = {"auth":"AUTHORIZATION","exec":"EXECUTION_RECEIPT",
                 "source":"SOURCE_STATE","observer":"EFFECT_ATTESTATION",
                 "quality":"QUALITY_APPROVAL"}
        self.private={k:Ed25519PrivateKey.generate() for k in kinds}
        self.trust={"source_integrity_independently_audited":True,"keys":{
            k:{"operator":k,"allowed_kinds":[v],
               "public_hex":self.private[k].public_key().public_bytes(Encoding.Raw, PublicFormat.Raw).hex()}
            for k,v in kinds.items()}}
        self.receipt={"protocol":"EXUP-EXECUTE-01","workload_id":"fixture","verdict":"PASS"}
        self.receipt["receipt_sha256"]=canonical_digest(self.receipt)
        self.bundle={}
        self.put("authorization","auth",{"effect_id":"e1","scope":"balance","decision":"ALLOW",
                                         "issued_at":10,"expires_at":30,
                                         "predicate":{"field":"balance","delta":-1}})
        self.put("execution","exec",{"effect_id":"e1","scope":"balance","transaction_id":"t1",
                                     "authorization_sha256":sha(self.bundle["authorization"])})
        self.put("source_state","source",{"effect_id":"e1","scope":"balance","transaction_id":"t1",
                                         "execution_sha256":sha(self.bundle["execution"]),
                                         "committed_at":20,"source_commit_id":"commit-1",
                                         "before":{"balance":10},"after":{"balance":9}})
        self.put("observation","observer",{"effect_id":"e1","transaction_id":"t1",
                                           "execution_sha256":sha(self.bundle["execution"]),
                                           "source_sha256":sha(self.bundle["source_state"]),
                                           "predicate_sha256":sha(self.bundle["authorization"]["payload"]["predicate"])})
        self.binding={"receipt_sha256":self.receipt["receipt_sha256"],
                      "signed_bundle_sha256":sha(self.bundle),"effect_id":"e1"}
        self.quality={"receipt_sha256":self.receipt["receipt_sha256"],"effect_id":"e1"}
        self.sign_quality(True)

    def sign(self,key,payload):
        envelope={"kind":self.trust["keys"][key]["allowed_kinds"][0],"key_id":key,"payload":payload}
        envelope["signature"]=base64.b64encode(self.private[key].sign(signable(envelope))).decode()
        return envelope

    def put(self,name,key,payload):
        self.bundle[name]=self.sign(key,payload)

    def sign_quality(self,approved):
        self.quality["attestation"]=self.sign("quality",{"effect_id":"e1",
                      "receipt_sha256":self.receipt["receipt_sha256"],"approved":approved})

    def check(self):
        return evaluate(self.receipt,self.bundle,self.trust,self.binding,self.quality,1.25)

    def test_signed_chain_pass(self):
        r=self.check()
        self.assertEqual(r["status"],"PASS")
        self.assertEqual(r["cost_per_verified_completion_usd"],1.25)

    def test_tampered_source_fails_closed(self):
        self.bundle["source_state"]["payload"]["after"]["balance"]=99
        self.binding["signed_bundle_sha256"]=sha(self.bundle)
        self.assertEqual(self.check()["status"],"INSUFFICIENT_EVIDENCE")

    def test_untrusted_key(self):
        self.trust["keys"].pop("observer")
        self.assertEqual(self.check()["status"],"INSUFFICIENT_EVIDENCE")

    def test_unsigned_quality_rejected(self):
        self.quality.pop("attestation")
        self.assertEqual(self.check()["status"],"INSUFFICIENT_EVIDENCE")

    def test_signed_quality_denial(self):
        self.sign_quality(False)
        self.assertEqual(self.check()["status"],"INSUFFICIENT_EVIDENCE")

    def test_quality_role_collision(self):
        self.trust["keys"]["quality"]["operator"]="exec"
        self.assertEqual(self.check()["status"],"INSUFFICIENT_EVIDENCE")

    def test_binding_mismatch(self):
        self.binding["receipt_sha256"]="bad"
        self.assertEqual(self.check()["status"],"INSUFFICIENT_EVIDENCE")

    def test_untrusted_source_integrity(self):
        self.trust["source_integrity_independently_audited"]=False
        self.assertEqual(self.check()["status"],"INSUFFICIENT_EVIDENCE")

if __name__=="__main__":
    unittest.main()
