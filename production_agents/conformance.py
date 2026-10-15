"""GAUNTLET-PROD-001: evidence-based, vendor-neutral production-agent checks.

A PASS is a verdict over supplied attestations, not proof of deployed controls.
The harness deliberately never executes external effects or grants authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

# Q01-Q18 correspond to PracticAI's "Production Agent Systems" (44 pages).
# Evidence field names describe verifiable signals, not a specific vendor stack.
MATRIX = {
    "Q01": ("loop_cost", ("per_task_token_budget", "context_growth_bound", "budget_enforced")),
    "Q02": ("horizontal_scale", ("external_state", "queue_backpressure", "load_test_100k")),
    "Q03": ("concurrent_memory", ("session_isolation", "versioned_updates", "conflict_test")),
    "Q04": ("mid_tool_failure", ("failure_classified", "recovery_checkpoint", "effect_reconciled")),
    "Q05": ("tracing", ("correlated_trace", "redacted_inputs", "trace_integrity")),
    "Q06": ("latency_optimization", ("stage_p95", "quality_regression_test", "measured_bottleneck")),
    "Q07": ("health_dashboard", ("error_metrics", "quality_metrics", "alert_test")),
    "Q08": ("parallel_calls", ("dependency_graph", "bounded_concurrency", "shared_write_fencing")),
    "Q09": ("async_workflows", ("durable_queue", "job_state_machine", "crash_recovery_test")),
    "Q10": ("model_switching", ("route_policy", "quality_gate", "fallback_test")),
    "Q11": ("latency_breakdown", ("p50_p95_by_stage", "queue_latency", "token_latency")),
    "Q12": ("cost_aware_routing", ("capability_registry", "budget_gate", "quality_floor")),
    "Q13": ("bounded_retry", ("retry_limit", "idempotency_binding", "unknown_effect_reconciliation")),
    "Q14": ("multi_agent_scale", ("worker_isolation", "load_balancing", "cross_worker_consistency")),
    "Q15": ("reasoning_quality", ("frozen_test_set", "version_comparison", "drift_alert")),
    "Q16": ("reasoning_fallback", ("fallback_trigger", "safe_degradation", "fallback_validation")),
    "Q17": ("tool_misuse", ("misuse_signals", "authorization_alert", "blocked_call_audit")),
    "Q18": ("token_budget", ("request_token_cap", "spent_tokens_metered", "overrun_blocked")),
}

# Scope-qualified proof gates required for an actual material consequence.
EFFECT_GATES = (
    "fresh_authority", "mandate_scope", "tool_capability_valid",
    "governed_effect_path", "effect_idempotent", "independent_observation",
    "receipt_effect_binding", "recovery_reconciled",
)


def digest(data: object) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":"),
                                      ensure_ascii=False).encode()).hexdigest()


@dataclass(frozen=True)
class Verdict:
    status: str
    findings: tuple[str, ...]

    def as_dict(self) -> dict:
        return {"status": self.status, "findings": list(self.findings)}


def evaluate(item: dict) -> Verdict:
    """False -> FAIL, missing/None -> INSUFFICIENT_EVIDENCE, True -> PASS.

    Unknown evidence is never inferred from a positive agent/tool trace.
    A non-effect case does not need effect gates.
    """
    if not isinstance(item, dict) or item.get("question") not in MATRIX:
        return Verdict("INSUFFICIENT_EVIDENCE", ("UNKNOWN_QUESTION",))
    qid = item["question"]
    if type(item.get("material_effect")) is not bool:
        return Verdict("INSUFFICIENT_EVIDENCE", ("UNKNOWN_EFFECT_CLASS",))
    if not isinstance(item.get("evidence"), dict):
        return Verdict("INSUFFICIENT_EVIDENCE", ("UNKNOWN_EVIDENCE",))
    fields = MATRIX[qid][1] + (EFFECT_GATES if item["material_effect"] else ())
    denied, unknown = [], []
    for name in fields:
        value = item["evidence"].get(name)
        if value is False:
            denied.append("FAILED_" + name.upper())
        elif value is not True:
            unknown.append("UNKNOWN_" + name.upper())
    if denied:
        return Verdict("FAIL", tuple(denied + unknown))
    if unknown:
        return Verdict("INSUFFICIENT_EVIDENCE", tuple(unknown))
    return Verdict("PASS", ())


def evaluate_suite(payload: dict) -> dict:
    if not isinstance(payload, dict) or not isinstance(payload.get("cases"), list):
        raise ValueError("expected object containing a cases array")
    cases = payload["cases"]
    if not cases:
        raise ValueError("empty suite cannot pass")
    seen = set()
    results = []
    for i, case in enumerate(cases):
        if not isinstance(case, dict):
            raise ValueError(f"case {i} must be object")
        qid = case.get("question")
        if qid in seen:
            raise ValueError(f"duplicate question: {qid}")
        seen.add(qid)
        verdict = evaluate(case)
        results.append({"question": qid, **verdict.as_dict()})
    statuses = {r["status"] for r in results}
    status = ("FAIL" if "FAIL" in statuses else
              "INSUFFICIENT_EVIDENCE" if "INSUFFICIENT_EVIDENCE" in statuses
              else "PASS")
    return {
        "protocol": "GAUNTLET-PROD-001", "schema_version": 1,
        "input_sha256": digest(payload),
        "status": status, "results": results,
        "scope": "attestation-only; does not independently validate deployed runtime or physical effect",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = evaluate_suite(json.loads(args.input.read_text(encoding="utf-8")))
    except (ValueError, OSError, json.JSONDecodeError) as error:
        report = {"protocol": "GAUNTLET-PROD-001", "status": "INSUFFICIENT_EVIDENCE",
                  "error": str(error)}
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return {"PASS": 0, "FAIL": 2, "INSUFFICIENT_EVIDENCE": 3}[report["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
