"""Bridge EXUP receipts with GAUNTLET observed-effect and completion verdicts.

Inputs are supplied records; provenance/identity are not cryptographically authenticated.
"""
import hashlib
import json

def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()

def bridge(receipt, effect_record, evidence, evaluate_effect, evaluate_completion):
    if not all(isinstance(x, dict) for x in (receipt, effect_record, evidence)):
        raise ValueError("receipt, effect_record and evidence must be objects")
    if receipt.get("protocol") not in ("EXUP-EXECUTE-01", "EXUP-EVAL-01"):
        raise ValueError("unsupported EXUP receipt")
    receipt_digest = receipt.get("receipt_sha256")
    unsigned = dict(receipt)
    unsigned.pop("receipt_sha256", None)
    if not isinstance(receipt_digest, str) or receipt_digest != digest(unsigned):
        raise ValueError("EXUP receipt digest missing or mismatched")
    effect = evaluate_effect(effect_record)
    observer = effect_record.get("observer")
    if not isinstance(observer, dict):
        raise ValueError("observer must be an object")
    bound = (evidence.get("receipt_sha256") == receipt_digest and
             evidence.get("effect_record_sha256") == digest(effect_record) and
             isinstance(observer.get("identity"), str) and bool(observer["identity"]) and
             evidence.get("observer_id") == observer["identity"])
    approved_effect = effect.get("status") == "PASS" and effect.get("observed_effects", 0) > 0
    witness = dict(evidence)
    witness["independent"] = bool(bound and observer.get("independent") is True and approved_effect)
    witness["coverage_complete"] = bool(bound and observer.get("coverage_complete") is True)
    witness["provenance_verified"] = bool(bound and observer.get("provenance_verified") is True)
    witness["effect_observed"] = bool(bound and approved_effect)
    witness["authorized"] = bool(bound and approved_effect)
    # EXUP optimization PASS is not a quality attestation.
    witness["quality_approved"] = evidence.get("quality_approved") if bound else None
    cost = evidence.get("cost_usd")
    if type(cost) not in (int, float):
        raise ValueError("explicit measured cost_usd required")
    completion = evaluate_completion({"trials": [{"id": receipt_digest, "cost_usd": cost, "evidence": witness}]})
    if effect.get("status") == "FAIL":
        completion["status"] = "FAIL"
    return {"protocol": "EXUP-GAUNTLET-BRIDGE-01", "effect": effect,
            "completion": completion, "binding_verified": bound,
            "status": completion["status"],
            "scope": "supplied records only; identity and provenance not cryptographically authenticated"}
