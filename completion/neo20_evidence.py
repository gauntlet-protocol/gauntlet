"""Read NEO-20 aggregate experimental evidence without reclassifying model PASS as external effect."""
import hashlib
import json

EXPECTED = ("M0_baseline_4k","M0_baseline_8k","M0_baseline_16k",
            "M2_structured_4k","M2_structured_8k","M2_structured_16k",
            "M_placebo_4k","M_corrupt_4k","M5_frontier_8k")

def evaluate(evidence, verdict):
    if not isinstance(evidence,dict) or not isinstance(verdict,dict):
        raise ValueError("two JSON objects required")
    if evidence.get("experiment") != "NEO-20" or verdict.get("experiment") != "NEO-20":
        raise ValueError("NEO-20 evidence required")
    conditions = evidence.get("conditions")
    if not isinstance(conditions,dict) or set(conditions)!=set(EXPECTED):
        return {"protocol":"GAUNTLET-NEO20-01","status":"INSUFFICIENT_EVIDENCE","reason":"condition mismatch"}
    count=0
    for key in EXPECTED:
        arm=conditions[key]
        if not isinstance(arm,dict):
            raise ValueError("condition must be object")
        total=arm.get("total_calls")
        completed=arm.get("completed_calls")
        passed=arm.get("pass_calls")
        if any(type(x) is not int for x in (total,completed,passed)) or not (0<=passed<=completed<=total):
            raise ValueError("invalid call counts")
        count+=total
    complete=(count==1728 and evidence.get("completeness",{}).get("complete") is True
              and verdict.get("data_complete") is True)
    return {"protocol":"GAUNTLET-NEO20-01",
            "status":"INSUFFICIENT_EVIDENCE",
            "experiment_completeness":"COMPLETE" if complete else "INCOMPLETE",
            "inference_calls":count,
            "observed_external_effects":None,
            "independent_effect_verification":False,
            "verified_completions":None,
            "cost_per_verified_completion_usd":None,
            "model_hypotheses":verdict.get("verdicts",{}),
            "reason":"NEO-20 measured logical inference, not independently verified authorized external effects",
            "evidence_sha256":hashlib.sha256(json.dumps(evidence,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()}
