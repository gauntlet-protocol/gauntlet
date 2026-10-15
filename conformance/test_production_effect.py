import base64
import copy
import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from signed_effect import sha, signable
from production_effect import verify_production
import test_signed_effect

class ProductionProofTests(unittest.TestCase):
    def setUp(self):
        fixture = test_signed_effect.SignedEffectTests()
        fixture.setUp()
        self.bundle = fixture.bundle
        self.trust = fixture.trust
        self.private = {}
        for role, kind in (("environment","ENVIRONMENT_ATTESTATION"),("auditor","SOURCE_AUDIT")):
            key = Ed25519PrivateKey.generate()
            self.private[role] = key
            self.trust["keys"][role] = {"operator":role, "allowed_kinds":[kind],
                "public_hex":key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw).hex()}
        self.trust["production_policy"] = {
            "verification_time":20,"environment_id":"prod-01","workload_id":"executor-prod",
            "accepted_measurements":["sha256:approved-binary"],"source_id":"ledger-prod",
            "environment_attestors":["environment"],"source_auditors":["auditor"],"revoked_keys":[]}
        self.put("environment", "environment", "ENVIRONMENT_ATTESTATION", {
            "environment_id":"prod-01","class":"production","workload_id":"executor-prod",
            "measurement":"sha256:approved-binary","valid_from":10,"valid_until":30})
        self.put("source_audit","auditor","SOURCE_AUDIT",{
            "environment_id":"prod-01","source_id":"ledger-prod","audit_result":"PASS",
            "subject_key_id":"source","source_commit_id":"commit-1","valid_from":10,"valid_until":30})
        self.manifest={"evidence_class":"PRODUCTION_EFFECT_PROOF",
                       "environment_sha256":sha(self.bundle["environment"]),
                       "audit_sha256":sha(self.bundle["source_audit"])}
    def put(self, name, key, kind, payload):
        env={"kind":kind,"key_id":key,"payload":payload}
        env["signature"]=base64.b64encode(self.private[key].sign(signable(env))).decode()
        self.bundle[name]=env
    def check(self):
        return verify_production(self.bundle,self.trust,self.manifest)
    def test_attested_digital_production_effect(self):
        self.assertEqual(self.check()["status"],"PRODUCTION_EVIDENCE_CONSISTENT")
    def test_test_environment_substitution(self):
        p=copy.deepcopy(self.bundle["environment"]["payload"])
        p["class"]="test"
        self.put("environment","environment","ENVIRONMENT_ATTESTATION",p)
        self.manifest["environment_sha256"]=sha(self.bundle["environment"])
        self.assertEqual(self.check()["status"],"INSUFFICIENT_EVIDENCE")
    def test_revoked_key(self):
        self.trust["production_policy"]["revoked_keys"]=["source"]
        self.assertIn("REVOKED_EVIDENCE_KEY",self.check()["reasons"])
    def test_colluding_observer(self):
        self.trust["keys"]["observer"]["operator"]="exec"
        self.assertIn("COLLUDING_TRUST_DOMAINS",self.check()["reasons"])
    def test_signer_alone_cannot_prove_effect(self):
        p=copy.deepcopy(self.bundle["source_state"]["payload"])
        p["after"]["balance"]=500
        # Changing source facts without re-signing is immediately invalid
        self.bundle["source_state"]["payload"]=p
        self.assertEqual(self.check()["status"],"INSUFFICIENT_EVIDENCE")
    def test_source_audit_claim_not_bound_to_commit(self):
        p=copy.deepcopy(self.bundle["source_audit"]["payload"])
        p["source_commit_id"]="unrelated"
        self.put("source_audit","auditor","SOURCE_AUDIT",p)
        self.manifest["audit_sha256"]=sha(self.bundle["source_audit"])
        self.assertIn("SOURCE_COMMIT_MISMATCH",self.check()["reasons"])
    def test_expired_production_attestation(self):
        self.trust["production_policy"]["verification_time"]=31
        self.assertIn("ATTESTATION_EXPIRED",self.check()["reasons"])
    def test_missing_attestation_is_insufficient(self):
        del self.bundle["source_audit"]
        self.assertEqual(self.check()["status"],"INSUFFICIENT_EVIDENCE")

if __name__=="__main__":
    unittest.main()
