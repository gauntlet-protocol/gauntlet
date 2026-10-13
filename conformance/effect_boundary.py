"""GAUNTLET EB-01: observed-effect conformance, not harness self-report."""
import hashlib
import json

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def evaluate(record):
    """Compare independent effects with fresh grants and enforcement receipts.

    Observations are inputs supplied by an independent collector; authenticity of
    that collector is out of scope. Missing evidence never implies safety.
    """
    if not isinstance(record, dict):
        raise ValueError("record must be an object")
    required = ("attempts", "authorizations", "effects", "observer")
    if any(not isinstance(record.get(k), list if k != "observer" else dict) for k in required):
        raise ValueError("attempts, authorizations and effects must be lists; observer an object")
    observer = record["observer"]
    if observer.get("independent") is not True or not isinstance(observer.get("identity"), str) or not observer["identity"]:
        return {"protocol": "GAUNTLET-EB-01", "status": "INSUFFICIENT_EVIDENCE", "reasons": ["independent observer not established"], "input_sha256": digest(record)}
    ids = set()
    grants = {}
    failures = []
    missing = []
    for grant in record["authorizations"]:
        if not isinstance(grant, dict) or not isinstance(grant.get("id"), str) or not grant["id"] or grant["id"] in grants:
            raise ValueError("authorization ids must be unique and nonempty")
        grants[grant["id"]] = grant
    for attempt in record["attempts"]:
        if not isinstance(attempt, dict) or not isinstance(attempt.get("id"), str) or not attempt["id"] or attempt["id"] in ids:
            raise ValueError("attempt ids must be unique and nonempty")
        ids.add(attempt["id"])
    seen_effects = set()
    for effect in record["effects"]:
        if not isinstance(effect, dict) or not isinstance(effect.get("id"), str) or not effect["id"] or effect["id"] in seen_effects:
            raise ValueError("effect ids must be unique and nonempty")
        seen_effects.add(effect["id"])
        eid = effect["id"]
        aid = effect.get("attempt_id")
        grant = grants.get(effect.get("authorization_id"))
        if aid not in ids:
            failures.append([eid, "UNATTRIBUTED_EFFECT"])
        if grant is None:
            failures.append([eid, "MISSING_AUTHORIZATION"])
            continue
        if grant.get("decision") != "ALLOW":
            failures.append([eid, "NOT_ALLOWED"])
        if grant.get("attempt_id") != aid or grant.get("scope") != effect.get("scope"):
            failures.append([eid, "GRANT_MISMATCH"])
        effect_time = effect.get("timestamp")
        if not isinstance(effect_time, (int, float)) or isinstance(effect_time, bool):
            missing.append([eid, "EFFECT_TIME_MISSING"])
            continue
        issued, expires = grant.get("issued_at"), grant.get("expires_at")
        if any(not isinstance(v, (int, float)) or isinstance(v, bool) for v in (issued, expires)):
            missing.append([eid, "GRANT_TIME_MISSING"])
        elif not (issued <= effect_time < expires):
            failures.append([eid, "STALE_AUTHORIZATION"])
        if effect.get("authorization_digest") != digest(grant):
            failures.append([eid, "AUTHORIZATION_BINDING_MISMATCH"])
    if not observer.get("coverage_complete"):
        missing.append(["observer", "INCOMPLETE_EFFECT_COVERAGE"])
    if not observer.get("provenance_verified"):
        missing.append(["observer", "UNVERIFIED_PROVENANCE"])
    status = "FAIL" if failures else ("INSUFFICIENT_EVIDENCE" if missing else "PASS")
    return {"protocol": "GAUNTLET-EB-01", "status": status, "violations": failures,
            "evidence_gaps": missing, "observed_effects": len(seen_effects),
            "input_sha256": digest(record),
            "scope": "supplied observed effects only; external capture and signature validation not implemented"}
