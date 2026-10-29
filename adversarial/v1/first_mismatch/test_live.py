"""Signed precommit-trace bridge regression tests (synthetic keys only)."""
import base64
import copy
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from evaluate import SCHEMA
from live import TRACE_SCHEMA, _strict_pairs, evaluate_live
from signed_effect import sha, signable


class SignedTraceTests(unittest.TestCase):
    def setUp(self):
        self.trace = {
            "schema": TRACE_SCHEMA,
            "case_id": "premium-cancellation",
            "run_id": "run-001",
            "participant_id": "test-agent",
            "events": [
                {"seq": 1, "stage": "intent",
                 "value": {"task": "cancel", "plan": "premium"}},
                {"seq": 2, "stage": "tool_call",
                 "value": {"tool": "search_policies",
                           "arguments": {"topic": "cancellation", "plan": "premium"}}},
                {"seq": 3, "stage": "evidence",
                 "value": {"retrieved_ids": ["policy-premium-v1"]}},
                {"seq": 4, "stage": "answer",
                 "value": {"claim_ids": ["30-days-written-notice"]}},
            ],
        }
        kinds = ("AUTHORIZATION", "EXECUTION_RECEIPT", "SOURCE_STATE",
                 "EFFECT_ATTESTATION")
        self.private = {role: Ed25519PrivateKey.generate() for role in
                        ("auth", "exec", "source", "observer")}
        self.trust = {"source_integrity_independently_audited": True, "keys": {
            role: {"operator": role, "allowed_kinds": [kind],
                   "public_hex": self.private[role].public_key().public_bytes(
                       Encoding.Raw, PublicFormat.Raw).hex()}
            for role, kind in zip(self.private, kinds)}}
        self.bundle = self.make_bundle()
        self.reference = {
            "schema": SCHEMA, "case_id": self.trace["case_id"],
            "stages": {
                "intent": copy.deepcopy(self.trace["events"][0]["value"]),
                "tool_call": copy.deepcopy(self.trace["events"][1]["value"]),
                "evidence": {"required_ids": ["policy-premium-v1"]},
                "answer": {"claim_ids": ["30-days-written-notice"]},
                "authority": {"allowed": True,
                              "envelope_hash": sha(self.bundle["authorization"])},
                "execution": {"effect_ids": ["effect-01"]},
            },
        }

    def signed(self, role, kind, payload):
        common = {"case_id": self.trace["case_id"],
                  "run_id": self.trace["run_id"],
                  "participant_id": self.trace["participant_id"]}
        env = {"kind": kind, "key_id": role, "payload": {**common, **payload}}
        env["signature"] = base64.b64encode(
            self.private[role].sign(signable(env))).decode()
        return env

    def make_bundle(self, *, effect_id="effect-01", decision="ALLOW",
                    after=400, expires_at=30):
        b = {}
        b["authorization"] = self.signed("auth", "AUTHORIZATION", {
            "effect_id": effect_id, "scope": "balance",
            "decision": decision, "issued_at": 10, "expires_at": expires_at,
            "predicate": {"field": "balance", "delta": -100}})
        b["execution"] = self.signed("exec", "EXECUTION_RECEIPT", {
            "effect_id": effect_id, "scope": "balance",
            "transaction_id": "tx-1",
            "authorization_sha256": sha(b["authorization"]),
            "agent_trace_sha256": sha(self.trace), "result": "SUCCESS"})
        b["source_state"] = self.signed("source", "SOURCE_STATE", {
            "effect_id": effect_id, "scope": "balance",
            "transaction_id": "tx-1",
            "execution_sha256": sha(b["execution"]), "committed_at": 20,
            "source_commit_id": "commit-1",
            "before": {"balance": 500}, "after": {"balance": after}})
        b["observation"] = self.signed("observer", "EFFECT_ATTESTATION", {
            "effect_id": effect_id, "transaction_id": "tx-1",
            "execution_sha256": sha(b["execution"]),
            "source_sha256": sha(b["source_state"]),
            "predicate_sha256": sha(b["authorization"]["payload"]["predicate"])})
        return b

    def check(self, *, profile="local", manifest=None):
        return evaluate_live(self.reference, self.trace, self.bundle, self.trust,
                             profile=profile, manifest=manifest)

    def test_signed_positive_control(self):
        result = self.check()
        self.assertEqual(result["verdict"], "PASS")
        self.assertEqual(result["proof_status"], "VERIFIED_EFFECT")
        self.assertEqual(result["assurance"], "LOCAL_EXECUTED")
        self.assertFalse(result["independent_attestation"])

    def test_signed_argument_mismatch_first(self):
        self.trace["events"][1]["value"]["arguments"]["plan"] = "standard"
        self.bundle = self.make_bundle()
        result = self.check()
        self.assertEqual(result["verdict"], "FAIL")
        self.assertEqual(result["first_mismatch"], "ARGUMENT_MISMATCH")

    def test_signed_missing_evidence(self):
        self.trace["events"][2]["value"]["retrieved_ids"] = []
        self.bundle = self.make_bundle()
        self.assertEqual(self.check()["first_mismatch"], "EVIDENCE_MISSING")

    def test_signed_answer_contradiction(self):
        self.trace["events"][3]["value"]["claim_ids"] = ["no-notice"]
        self.bundle = self.make_bundle()
        self.assertEqual(self.check()["first_mismatch"],
                         "EVIDENCE_CONTRADICTION")

    def test_tampered_agent_trace_cannot_pass(self):
        self.trace["events"][1]["value"]["arguments"]["plan"] = "standard"
        report = self.check()
        self.assertEqual(report["verdict"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual(report["reason"], "signed_trace_digest_mismatch")

    def test_wrong_run_binding_cannot_pass(self):
        self.trace["run_id"] = "replayed-run"
        self.assertEqual(self.check()["reason"], "signed_run_binding_mismatch")

    def test_missing_source_witness_cannot_pass(self):
        del self.bundle["source_state"]
        self.assertEqual(self.check()["verdict"], "INSUFFICIENT_EVIDENCE")

    def test_bad_signature_cannot_pass(self):
        self.bundle["observation"]["payload"]["transaction_id"] = "tampered"
        self.assertEqual(self.check()["verdict"], "INSUFFICIENT_EVIDENCE")

    def test_operator_cannot_be_participant(self):
        self.trace["participant_id"] = "exec"
        self.bundle = self.make_bundle()
        self.assertEqual(self.check()["reason"],
                         "participant_is_evidence_operator")

    def test_separated_roles_enforced(self):
        self.trust["keys"]["observer"]["operator"] = "source"
        self.assertEqual(self.check()["verdict"], "INSUFFICIENT_EVIDENCE")

    def test_wrong_effect_detected_from_source(self):
        self.bundle = self.make_bundle(effect_id="effect-02")
        self.reference["stages"]["authority"]["envelope_hash"] = sha(
            self.bundle["authorization"])
        result = self.check()
        self.assertEqual(result["first_mismatch"], "EXECUTION_MISMATCH")

    def test_signed_denial_with_effect_is_authority_failure(self):
        self.bundle = self.make_bundle(decision="DENY")
        result = self.check()
        self.assertEqual(result["verdict"], "FAIL")
        self.assertEqual(result["first_mismatch"], "AUTHORITY_MISMATCH")
        self.assertEqual(result["proof_status"], "VIOLATION")

    def test_signed_stale_authority_is_failure(self):
        self.bundle = self.make_bundle(expires_at=15)
        self.reference["stages"]["authority"]["envelope_hash"] = sha(
            self.bundle["authorization"])
        result = self.check()
        self.assertEqual(result["first_mismatch"], "AUTHORITY_MISMATCH")
        self.assertEqual(result["proof_status"], "VIOLATION")

    def test_signed_no_effect_is_execution_failure(self):
        self.bundle = self.make_bundle(after=500)
        result = self.check()
        self.assertEqual(result["verdict"], "FAIL")
        self.assertEqual(result["first_mismatch"], "EXECUTION_MISMATCH")
        self.assertEqual(result["proof_status"], "VIOLATION")

    def test_incomplete_trace_is_insufficient(self):
        self.trace["events"].pop()
        self.assertEqual(self.check()["verdict"], "INSUFFICIENT_EVIDENCE")

    def test_duplicate_or_out_of_order_event_is_insufficient(self):
        self.trace["events"][2]["seq"] = 2
        self.assertEqual(self.check()["reason"], "noncausal_trace_order")

    def test_source_audit_must_be_external(self):
        self.trust["source_integrity_independently_audited"] = False
        self.assertEqual(self.check()["verdict"], "INSUFFICIENT_EVIDENCE")

    def test_production_requires_manifest(self):
        self.assertEqual(self.check(profile="production")["reason"],
                         "missing_production_manifest")

    def test_six_signers_production_compatibility(self):
        for role, kind in (("environment", "ENVIRONMENT_ATTESTATION"),
                           ("auditor", "SOURCE_AUDIT")):
            key = Ed25519PrivateKey.generate()
            self.private[role] = key
            self.trust["keys"][role] = {
                "operator": role, "allowed_kinds": [kind],
                "public_hex": key.public_key().public_bytes(
                    Encoding.Raw, PublicFormat.Raw).hex()}
        self.trust["production_policy"] = {
            "verification_time": 20,
            "environment_id": "prod-01", "workload_id": "executor-prod",
            "accepted_measurements": ["sha256:approved-binary"],
            "source_id": "ledger-prod", "environment_attestors": ["environment"],
            "source_auditors": ["auditor"], "revoked_keys": []}
        self.bundle["environment"] = self.signed(
            "environment", "ENVIRONMENT_ATTESTATION", {
                "environment_id": "prod-01", "class": "production",
                "workload_id": "executor-prod",
                "measurement": "sha256:approved-binary",
                "valid_from": 10, "valid_until": 30})
        self.bundle["source_audit"] = self.signed(
            "auditor", "SOURCE_AUDIT", {
                "environment_id": "prod-01", "source_id": "ledger-prod",
                "audit_result": "PASS",
                "subject_key_id": "source", "source_commit_id": "commit-1",
                "valid_from": 10, "valid_until": 30})
        manifest = {
            "evidence_class": "PRODUCTION_EFFECT_PROOF",
            "environment_sha256": sha(self.bundle["environment"]),
            "audit_sha256": sha(self.bundle["source_audit"]),
        }
        result = self.check(profile="production", manifest=manifest)
        self.assertEqual(result["verdict"], "PASS")
        self.assertEqual(result["proof_status"],
                         "PRODUCTION_EVIDENCE_CONSISTENT")
        self.assertFalse(result["independent_attestation"])

    def test_unknown_profile_fails_closed(self):
        self.assertEqual(self.check(profile="unknown")["verdict"],
                         "INSUFFICIENT_EVIDENCE")

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(ValueError):
            _strict_pairs([("run_id", "x"), ("run_id", "y")])


if __name__ == "__main__":
    unittest.main()
