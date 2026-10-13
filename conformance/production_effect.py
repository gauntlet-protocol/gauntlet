"""EB-03 production evidence gate; production is never inferred from test receipts."""
from signed_effect import check_signature, sha, verify

def verify_production(bundle, trust, manifest):
    """Fail closed: externally provisioned trust policy and signed environment attestations.

    An operator-controlled manifest is not enough. This checks cryptographic
    provenance, not whether the external trust authority was honestly operated.
    """
    missing = []
    try:
        policy = trust["production_policy"]
        now = policy["verification_time"]
        env = bundle["environment"]
        audit = bundle["source_audit"]
        if not all(check_signature(item, trust["keys"]) for item in (env, audit)):
            missing.append("INVALID_ATTESTATION_SIGNATURE")
        if env["kind"] != "ENVIRONMENT_ATTESTATION" or audit["kind"] != "SOURCE_AUDIT":
            missing.append("WRONG_ATTESTATION_KIND")
        e, a = env["payload"], audit["payload"]
        if e.get("environment_id") != policy["environment_id"] or e.get("class") != "production":
            missing.append("ENVIRONMENT_MISMATCH")
        if e.get("workload_id") != policy["workload_id"]:
            missing.append("WORKLOAD_MISMATCH")
        if e.get("measurement") not in policy["accepted_measurements"]:
            missing.append("UNAPPROVED_MEASUREMENT")
        if a.get("source_id") != policy["source_id"] or a.get("environment_id") != policy["environment_id"]:
            missing.append("SOURCE_ENVIRONMENT_MISMATCH")
        if a.get("audit_result") != "PASS":
            missing.append("INVALID_SOURCE_AUDIT")
        if a.get("subject_key_id") != bundle["source_state"]["key_id"]:
            missing.append("SOURCE_KEY_MISMATCH")
        if a.get("source_commit_id") != bundle["source_state"]["payload"].get("source_commit_id"):
            missing.append("SOURCE_COMMIT_MISMATCH")
        if not all(type(x.get(k)) is int for x in (e,a) for k in ("valid_from","valid_until")):
            missing.append("ATTESTATION_TIME_MISSING")
        elif not all(x["valid_from"] <= now < x["valid_until"] for x in (e,a)):
            missing.append("ATTESTATION_EXPIRED")
        if env["key_id"] not in policy["environment_attestors"] or audit["key_id"] not in policy["source_auditors"]:
            missing.append("UNTRUSTED_ATTESTOR")
        domains = [trust["keys"][x["key_id"]]["operator"] for x in
                   (bundle["authorization"],bundle["execution"],bundle["source_state"],
                    bundle["observation"],env,audit)]
        if len(set(domains)) != len(domains):
            missing.append("COLLUDING_TRUST_DOMAINS")
        for item in (env,audit):
            if item["key_id"] in policy.get("revoked_keys", []):
                missing.append("REVOKED_ATTESTOR")
        for item in (bundle["authorization"],bundle["execution"],bundle["source_state"],bundle["observation"]):
            if item["key_id"] in policy.get("revoked_keys", []):
                missing.append("REVOKED_EVIDENCE_KEY")
        if manifest.get("evidence_class") != "PRODUCTION_EFFECT_PROOF":
            missing.append("WRONG_EVIDENCE_CLASS")
        if manifest.get("environment_sha256") != sha(env) or manifest.get("audit_sha256") != sha(audit):
            missing.append("MANIFEST_BINDING_MISMATCH")
        if missing:
            return {"status": "INSUFFICIENT_EVIDENCE", "reasons": sorted(set(missing))}
        # Existing EB-02 verifier requires explicitly audited source integrity.
        internal = dict(trust)
        internal["source_integrity_independently_audited"] = True
        core = {k: bundle[k] for k in ("authorization","execution","source_state","observation")}
        result = verify(core, internal)
        if result["status"] != "VERIFIED_EFFECT":
            return result
        return {"status":"PRODUCTION_EFFECT_PROOF","effect_id":result["effect_id"],
                "evidence_sha256":sha(bundle), "limits":"attested digital source facts, not physical outcome"}
    except (KeyError,TypeError,ValueError,OverflowError):
        return {"status":"INSUFFICIENT_EVIDENCE","reasons":["MALFORMED_PRODUCTION_PROOF"]}
