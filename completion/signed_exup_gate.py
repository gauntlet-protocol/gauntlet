"""Fail-closed EXUP gate using EB-02's four-domain Ed25519 evidence chain.

This verifies signed digital state evidence, not physical effects, system-wide
completeness, or independently audited provenance by itself.
"""
import hashlib
import json
import math

from conformance.signed_effect import verify as verify_signed_effect
from conformance.signed_effect import sha as eb02_sha


def canonical_digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def evaluate(receipt, bundle, trust, binding, quality, cost_usd):
    if not all(isinstance(item, dict) for item in (receipt, bundle, trust, binding, quality)):
        raise ValueError("receipt, bundle, trust, binding and quality must be objects")
    if type(cost_usd) not in (int, float) or not math.isfinite(cost_usd) or cost_usd < 0:
        raise ValueError("cost must be finite and nonnegative")
    if receipt.get("protocol") not in ("EXUP-EXECUTE-01", "EXUP-EVAL-01"):
        return {"protocol": "EXUP-GAUNTLET-SIGNED-01", "status": "INSUFFICIENT_EVIDENCE",
                "reasons": ["UNSUPPORTED_EXUP_RECEIPT"]}
    unsigned = dict(receipt)
    claimed_digest = unsigned.pop("receipt_sha256", None)
    if not isinstance(claimed_digest, str) or claimed_digest != canonical_digest(unsigned):
        return {"protocol": "EXUP-GAUNTLET-SIGNED-01", "status": "INSUFFICIENT_EVIDENCE",
                "reasons": ["INVALID_EXUP_RECEIPT_DIGEST"]}
    signed = verify_signed_effect(bundle, trust)
    checks = (
        binding.get("receipt_sha256") == claimed_digest,
        binding.get("signed_bundle_sha256") == eb02_sha(bundle),
        binding.get("effect_id") == signed.get("effect_id"),
        quality.get("receipt_sha256") == claimed_digest,
        quality.get("effect_id") == signed.get("effect_id"),
    )
    reasons = []
    if not all(checks):
        reasons.append("UNBOUND_EVIDENCE")
    # Quality signoff must be issued by a separately trusted and signed source;
    # an unsigned quality_approved flag is never treated as evidence.
    from conformance.signed_effect import check_signature
    quality_envelope = quality.get("attestation")
    if not isinstance(quality_envelope, dict) or quality_envelope.get("kind") != "QUALITY_APPROVAL":
        reasons.append("MISSING_SIGNED_QUALITY")
    elif not check_signature(quality_envelope, trust.get("keys", {})):
        reasons.append("INVALID_SIGNED_QUALITY")
    else:
        qp = quality_envelope["payload"]
        source_operator = trust["keys"][bundle["source_state"]["key_id"]]["operator"]
        quality_operator = trust["keys"][quality_envelope["key_id"]]["operator"]
        if quality_operator in {source_operator,
                                trust["keys"][bundle["execution"]["key_id"]]["operator"]}:
            reasons.append("QUALITY_NOT_INDEPENDENT")
        if (qp.get("receipt_sha256") != claimed_digest or
                qp.get("effect_id") != signed.get("effect_id") or
                qp.get("approved") is not True):
            reasons.append("QUALITY_NOT_APPROVED_OR_UNBOUND")
    if signed["status"] == "VIOLATION":
        status = "FAIL"
    elif signed["status"] != "VERIFIED_EFFECT" or reasons:
        status = "INSUFFICIENT_EVIDENCE"
    else:
        status = "PASS"
    return {"protocol": "EXUP-GAUNTLET-SIGNED-01", "status": status,
            "signed_effect_status": signed["status"], "reasons": signed.get("reasons", []) + reasons,
            "verified_completions": 1 if status == "PASS" else 0,
            "cost_per_verified_completion_usd": cost_usd if status == "PASS" else None,
            "scope": "signed digital state evidence only; trust registry and source audit are external prerequisites"}
