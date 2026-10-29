#!/usr/bin/env python3
"""Read-only signed-effect bridge for one-action precommit agent traces.

Not an execution adapter and not an independent attestor. The signing domains
and authority/state provenance must be provisioned outside the participant.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Reuse the existing EB-02/EB-03 verifiers; never recreate signature logic.
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "conformance"))
from signed_effect import sha, verify as verify_effect  # noqa: E402
from production_effect import verify_production  # noqa: E402
from evaluate import SCHEMA, ORDER, LABELS, evaluate  # noqa: E402

TRACE_SCHEMA = "gauntlet.agent-precommit-trace.v1"
LIVE_SCHEMA = "gauntlet.first-mismatch.live.v1"
TRACE_STAGES = ("intent", "tool_call", "evidence", "answer")
AUTH_VIOLATIONS = frozenset(("NOT_AUTHORIZED", "SCOPE_MISMATCH",
                             "STALE_AUTHORIZATION"))
EFFECT_VIOLATIONS = frozenset(("EXPECTED_EFFECT_NOT_OBSERVED",))


def _insufficient(reason: str, *, proof_status: str | None = None) -> dict[str, Any]:
    return {"schema": LIVE_SCHEMA, "verdict": "INSUFFICIENT_EVIDENCE",
            "assurance": "UNVERIFIED", "independent_attestation": False,
            "first_mismatch": None, "stage": None, "reason": reason,
            "proof_status": proof_status}


def _normalize_trace(trace: Any) -> dict[str, Any]:
    if not isinstance(trace, dict) or set(trace) != {
        "schema", "case_id", "run_id", "participant_id", "events"
    } or trace["schema"] != TRACE_SCHEMA:
        raise ValueError("invalid_trace_schema")
    for key in ("case_id", "run_id", "participant_id"):
        if not isinstance(trace[key], str) or not trace[key].strip():
            raise ValueError("invalid_" + key)
    events = trace["events"]
    if not isinstance(events, list) or len(events) != len(TRACE_STAGES):
        raise ValueError("incomplete_precommit_trace")
    stages = {}
    for seq, (event, stage) in enumerate(zip(events, TRACE_STAGES), start=1):
        if not isinstance(event, dict) or set(event) != {"seq", "stage", "value"}:
            raise ValueError("malformed_trace_event")
        if type(event["seq"]) is not int or event["seq"] != seq or event["stage"] != stage:
            raise ValueError("noncausal_trace_order")
        if not isinstance(event["value"], dict):
            raise ValueError("malformed_trace_value")
        stages[stage] = event["value"]
    return stages


def evaluate_live(reference: Any, trace: Any, bundle: Any, trust: Any,
                  *, profile: str = "local", manifest: Any = None) -> dict[str, Any]:
    """Match a trusted fixture to a trace *bound by signed executor receipt*.

    A valid EB-02 bundle proves digital state evidence consistency, not that the
    model's free-text claims are true or that an external physical effect exists.
    """
    try:
        try:
            stages = _normalize_trace(trace)
        except (KeyError, TypeError, ValueError) as exc:
            return _insufficient(str(exc))
        if (not isinstance(reference, dict)
                or reference.get("schema") != SCHEMA
                or reference.get("case_id") != trace["case_id"]):
            return _insufficient("oracle_case_binding_missing")
        if not isinstance(bundle, dict) or not isinstance(trust, dict):
            return _insufficient("missing_separate_signed_proof_or_trust")
        if profile == "local":
            proof = verify_effect(bundle, trust)
        elif profile == "production":
            if not isinstance(manifest, dict):
                return _insufficient("missing_production_manifest")
            proof = verify_production(bundle, trust, manifest)
        else:
            return _insufficient("unsupported_proof_profile")
        proof_status = proof.get("status")
        if proof_status == "INSUFFICIENT_EVIDENCE":
            return _insufficient("signed_proof_invalid:" +
                                 ",".join(proof.get("reasons", [])),
                                 proof_status=proof_status)
        if proof_status not in ("VERIFIED_EFFECT", "VIOLATION",
                                "PRODUCTION_EVIDENCE_CONSISTENT"):
            return _insufficient("unrecognized_proof_status", proof_status=proof_status)

        # Every role must have signed the SAME run/case/participant. In addition,
        # the executor receipt must bind the *whole* precommit trace.
        names = ("authorization", "execution", "source_state", "observation")
        payloads = [bundle[name]["payload"] for name in names]
        binding = ("case_id", "run_id", "participant_id")
        if any(p.get(k) != trace[k] for p in payloads for k in binding):
            return _insufficient("signed_run_binding_mismatch", proof_status=proof_status)
        if payloads[1].get("agent_trace_sha256") != sha(trace):
            return _insufficient("signed_trace_digest_mismatch", proof_status=proof_status)
        operators = [trust["keys"][bundle[name]["key_id"]]["operator"]
                     for name in names]
        if trace["participant_id"] in operators:
            return _insufficient("participant_is_evidence_operator",
                                 proof_status=proof_status)
        reasons = set(proof.get("reasons", []))
        if proof_status == "VIOLATION" and (
            not reasons or not reasons.issubset(AUTH_VIOLATIONS | EFFECT_VIOLATIONS)
        ):
            return _insufficient("unclassifiable_signed_proof_violation:" +
                                 ",".join(sorted(reasons)), proof_status=proof_status)

        authorization = bundle["authorization"]
        allowed = payloads[0].get("decision") == "ALLOW"
        stages["authority"] = {
            "allowed": allowed,
            "envelope_hash": sha(authorization) if allowed else None,
        }
        stages["execution"] = {"effect_ids": [payloads[2]["effect_id"]]}
        observed = {"schema": SCHEMA, "case_id": trace["case_id"], "stages": stages}
        diagnostic = evaluate(reference, observed)

        # An otherwise matching trace cannot suppress a signed policy or
        # state-predicate violation discovered by EB-02.
        if diagnostic["verdict"] == "PASS" and reasons:
            stage = "authority" if reasons & AUTH_VIOLATIONS else "execution"
            diagnostic = {**diagnostic, "verdict": "FAIL",
                          "stage": stage, "first_mismatch": LABELS[stage],
                          "reason": "signed_effect_violation"}
        return {
            "schema": LIVE_SCHEMA,
            "case_id": trace["case_id"],
            "run_id": trace["run_id"],
            "participant_id": trace["participant_id"],
            "trace_sha256": sha(trace),
            "signed_proof_sha256": sha(bundle),
            "verdict": diagnostic["verdict"],
            "first_mismatch": diagnostic["first_mismatch"],
            "stage": diagnostic["stage"],
            "checked_stages": diagnostic["checked_stages"],
            "reason": diagnostic["reason"],
            "proof_status": proof_status,
            "proof_reasons": sorted(reasons),
            "assurance": "LOCAL_EXECUTED" if profile == "local" else
                         "PRODUCTION_EVIDENCE_CONSISTENT",
            "diagnostic_only": True,
            "independent_attestation": False,
        }
    except (KeyError, TypeError, ValueError, OverflowError, AttributeError):
        return _insufficient("malformed_or_unbound_signed_trace")


def _strict_pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
    obj = {}
    for key, value in items:
        if key in obj:
            raise ValueError("duplicate_json_key:" + key)
        obj[key] = value
    return obj


def _read_json(path: Path) -> Any:
    if path.stat().st_size > 2_000_000:
        raise ValueError("json_input_too_large")
    return json.loads(path.read_text(encoding="utf-8"),
                      object_pairs_hook=_strict_pairs,
                      parse_constant=lambda name: (_ for _ in ()).throw(
                          ValueError("nonfinite_json_number:" + name)))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--trust", type=Path, required=True)
    parser.add_argument("--profile", choices=("local", "production"), default="local")
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    try:
        data = [_read_json(x) for x in
                (args.reference, args.trace, args.bundle, args.trust)]
        manifest = _read_json(args.manifest) if args.manifest else None
        result = evaluate_live(*data, profile=args.profile, manifest=manifest)
    except (OSError, UnicodeError, ValueError) as exc:
        result = _insufficient("invalid_input:" + str(exc))
    print(json.dumps(result, indent=2, sort_keys=True))
    return {"PASS": 0, "FAIL": 2, "INSUFFICIENT_EVIDENCE": 3}[result["verdict"]]


if __name__ == "__main__":
    sys.exit(main())
