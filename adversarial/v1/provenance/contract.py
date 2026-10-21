"""GAUNTLET portable result provenance; pure stdlib, no VALO/core dependencies.

This validates evidence claims, not the truth of a signature or remote identity.
Independent verification requires an external trusted verifier and evidence access.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Any

class Level(str, Enum):
    SIMULATED='SIMULATED'
    LOCAL_EXECUTED='LOCAL_EXECUTED'
    VERIFIED='VERIFIED'
    INDEPENDENTLY_ATTESTED='INDEPENDENTLY_ATTESTED'

@dataclass(frozen=True)
class Provenance:
    level: Level
    method: str
    subject: str
    evidence_digest: str | None = None
    observed_effect_digest: str | None = None
    verifier_id: str | None = None
    verifier_evidence_digest: str | None = None
    attestor_id: str | None = None
    attestation_digest: str | None = None
    heuristic: bool = False
    synthetic: bool = False

class ProvenanceError(ValueError):pass

def validate(p: Provenance) -> None:
    if not isinstance(p.level,Level):raise ProvenanceError('unknown_assurance_level')
    if not p.method or not p.subject:raise ProvenanceError('missing_method_or_subject')
    if p.level in (Level.VERIFIED,Level.INDEPENDENTLY_ATTESTED) and (p.heuristic or p.synthetic):
        raise ProvenanceError('simulation_cannot_be_verified')
    if p.level!=Level.SIMULATED and not p.evidence_digest:raise ProvenanceError('missing_execution_evidence')
    if p.level in (Level.VERIFIED,Level.INDEPENDENTLY_ATTESTED):
        if not all((p.observed_effect_digest,p.verifier_id,p.verifier_evidence_digest)):
            raise ProvenanceError('missing_independent_verification_evidence')
        if p.verifier_id==p.subject:raise ProvenanceError('self_verification_forbidden')
    if p.level==Level.INDEPENDENTLY_ATTESTED:
        if not all((p.attestor_id,p.attestation_digest)):
            raise ProvenanceError('missing_attestation')
        if p.attestor_id in (p.subject,p.verifier_id):raise ProvenanceError('self_attestation_forbidden')

def classify(record: dict[str,Any]) -> Level:
    """Fail closed: unknown and incomplete records cannot assert VERIFIED."""
    raw=record.get('level','SIMULATED')
    try:level=Level(raw)
    except ValueError as exc:raise ProvenanceError('unknown_assurance_level') from exc
    p=Provenance(level=level,method=record.get('method',''),subject=record.get('subject',''),evidence_digest=record.get('evidence_digest'),observed_effect_digest=record.get('observed_effect_digest'),verifier_id=record.get('verifier_id'),verifier_evidence_digest=record.get('verifier_evidence_digest'),attestor_id=record.get('attestor_id'),attestation_digest=record.get('attestation_digest'),heuristic=record.get('heuristic',False),synthetic=record.get('synthetic',False))
    validate(p)
    return level