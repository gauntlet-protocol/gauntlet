"""GAUNTLET-COMP-01: evidence-gated completion metrics.
Independent observer evidence is supplied, not authenticated here.
"""
import hashlib
import json
import math

def evaluate(payload):
    if not isinstance(payload, dict) or not isinstance(payload.get("trials"), list) or not payload["trials"]:
        raise ValueError("nonempty trials list required")
    seen, outcomes = set(), []
    total_cost, approved = 0.0, 0
    for trial in payload["trials"]:
        if not isinstance(trial, dict):
            raise ValueError("trial must be object")
        tid = trial.get("id")
        if not isinstance(tid, str) or not tid or tid in seen:
            raise ValueError("unique nonempty trial id required")
        seen.add(tid)
        cost = trial.get("cost_usd")
        if type(cost) not in (int, float) or not math.isfinite(cost) or cost < 0:
            raise ValueError("cost_usd must be finite nonnegative number")
        total_cost += cost
        evidence = trial.get("evidence")
        if not isinstance(evidence, dict):
            evidence = {}
        independent = (evidence.get("independent") is True and
                       bool(evidence.get("observer_id")) and
                       evidence.get("provenance_verified") is True)
        coverage = evidence.get("coverage_complete") is True
        observed = evidence.get("effect_observed")
        authorized = evidence.get("authorized")
        quality = evidence.get("quality_approved")
        if independent and coverage and (observed is False or authorized is False or quality is False):
            status = "FAIL"
        elif independent and coverage and observed is True and authorized is True and quality is True:
            status = "PASS"
            approved += 1
        else:
            status = "INSUFFICIENT_EVIDENCE"
        outcomes.append({"id": tid, "status": status})
    statuses = {item["status"] for item in outcomes}
    status = ("FAIL" if "FAIL" in statuses else
              "INSUFFICIENT_EVIDENCE" if "INSUFFICIENT_EVIDENCE" in statuses else "PASS")
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()
    return {"protocol": "GAUNTLET-COMP-01", "status": status,
            "trials": len(outcomes), "verified_completions": approved,
            "verified_completion_rate": approved / len(outcomes),
            "total_cost_usd": round(total_cost, 8),
            "cost_per_verified_completion_usd": round(total_cost / approved, 8) if approved else None,
            "outcomes": outcomes, "input_sha256": hashlib.sha256(canonical).hexdigest(),
            "scope": "caller-supplied independent evidence; observer identity not cryptographically authenticated"}
