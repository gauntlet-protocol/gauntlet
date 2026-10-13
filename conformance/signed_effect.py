"""EB-02: role-separated signed receipts and verifiable authoritative state."""
import base64
import hashlib
import json
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()

def sha(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()

def signable(envelope):
    return b"GAUNTLET-EB02:" + envelope["kind"].encode("ascii") + b"\x00" + canonical(envelope["payload"])

def check_signature(envelope, keys):
    if not isinstance(envelope, dict) or set(envelope) != {"kind", "payload", "key_id", "signature"}:
        return False
    key = keys.get(envelope["key_id"])
    if key is None or envelope["kind"] not in key["allowed_kinds"]:
        return False
    try:
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(key["public_hex"])).verify(
            base64.b64decode(envelope["signature"], validate=True), signable(envelope))
        return True
    except (InvalidSignature, ValueError, TypeError, KeyError):
        return False

def verify(bundle, trust):
    """Verify signed authority, executor claim, source facts, observer claim.

    PASS verifies a claimed digital state transition against independently
    signed authoritative source facts, not physical reality or log completeness.
    """
    problems = []
    try:
        keys = trust["keys"]
        authority = bundle["authorization"]
        executor = bundle["execution"]
        source = bundle["source_state"]
        observer = bundle["observation"]
        envelopes = [authority, executor, source, observer]
        expected = ["AUTHORIZATION", "EXECUTION_RECEIPT", "SOURCE_STATE", "EFFECT_ATTESTATION"]
        for env, kind in zip(envelopes, expected):
            if env["kind"] != kind or not check_signature(env, keys):
                problems.append("INVALID_" + kind)
        if problems:
            return {"status": "INSUFFICIENT_EVIDENCE", "reasons": problems}
        operators = [keys[e["key_id"]]["operator"] for e in envelopes]
        if len(set(operators)) != 4:
            return {"status": "INSUFFICIENT_EVIDENCE", "reasons": ["TRUST_DOMAINS_NOT_SEPARATE"]}
        a, e, s, o = [env["payload"] for env in envelopes]
        if not all(x.get("effect_id") == a.get("effect_id") for x in (e,s,o)):
            problems.append("EFFECT_ID_MISMATCH")
        if e.get("authorization_sha256") != sha(authority):
            problems.append("EXECUTION_AUTHORIZATION_MISMATCH")
        if s.get("execution_sha256") != sha(executor):
            problems.append("SOURCE_EXECUTION_MISMATCH")
        if o.get("source_sha256") != sha(source):
            problems.append("OBSERVER_SOURCE_MISMATCH")
        if o.get("execution_sha256") != sha(executor):
            problems.append("OBSERVER_EXECUTION_MISMATCH")
        if a.get("decision") != "ALLOW":
            problems.append("NOT_AUTHORIZED")
        if a.get("scope") != e.get("scope") or e.get("scope") != s.get("scope"):
            problems.append("SCOPE_MISMATCH")
        times = [a.get("issued_at"), s.get("committed_at"), a.get("expires_at")]
        if any(type(t) not in (int, float) for t in times):
            problems.append("MISSING_TIMESTAMPS")
        elif not (times[0] <= times[1] < times[2]):
            problems.append("STALE_AUTHORIZATION")
        if e.get("transaction_id") != s.get("transaction_id") or s.get("transaction_id") != o.get("transaction_id"):
            problems.append("TRANSACTION_MISMATCH")
        if not isinstance(s.get("before"), dict) or not isinstance(s.get("after"), dict):
            return {"status": "INSUFFICIENT_EVIDENCE", "reasons": problems + ["MISSING_STATE_FACTS"]}
        # A narrowly specified, deterministic, integer-only predicate.
        predicate = a.get("predicate")
        if not isinstance(predicate, dict) or set(predicate) != {"field", "delta"} or type(predicate["delta"]) is not int or not isinstance(predicate["field"], str):
            return {"status": "INSUFFICIENT_EVIDENCE", "reasons": problems + ["UNSUPPORTED_PREDICATE"]}
        field = predicate["field"]
        before, after = s["before"].get(field), s["after"].get(field)
        if type(before) is not int or type(after) is not int:
            return {"status": "INSUFFICIENT_EVIDENCE", "reasons": problems + ["STATE_FIELD_UNAVAILABLE"]}
        if after - before != predicate["delta"]:
            problems.append("EXPECTED_EFFECT_NOT_OBSERVED")
        if not isinstance(s.get("source_commit_id"), str) or not s["source_commit_id"]:
            return {"status": "INSUFFICIENT_EVIDENCE", "reasons": problems + ["MISSING_COMMIT_ID"]}
        if o.get("predicate_sha256") != sha(predicate):
            problems.append("PREDICATE_BINDING_MISMATCH")
        if not trust.get("source_integrity_independently_audited", False):
            return {"status": "INSUFFICIENT_EVIDENCE", "reasons": problems + ["SOURCE_INTEGRITY_NOT_ESTABLISHED"]}
        return {"status": "VIOLATION" if problems else "VERIFIED_EFFECT", "reasons": problems,
                "effect_id": a["effect_id"], "source_commit_id": s["source_commit_id"],
                "evidence_sha256": sha(bundle)}
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        return {"status": "INSUFFICIENT_EVIDENCE", "reasons": ["MALFORMED_EVIDENCE", type(exc).__name__]}
