"""Conservative release qualification of actual agent execution evidence.

Evidence fields are untrusted claims until independently verified; this gate
cannot confer VERIFIED or INDEPENDENTLY_ATTESTED assurance.
"""
from dataclasses import dataclass
@dataclass(frozen=True)
class RunEvidence:
    participant_executed: bool
    participant_confined: bool
    provider_allowlisted: bool
    provider_transport_observed: bool
    direct_network_denied: bool
    filesystem_isolated: bool
    independent_oracle_observed: bool
    negative_controls_passed: bool
    frozen_contract_match: bool
    evidence_integrity_valid: bool
    blind_evaluation: bool

def qualify(e:RunEvidence):
    failed=[key for key,ok in vars(e).items() if ok is not True]
    return {'qualified':not failed,'failed_gates':failed,'assurance_ceiling':'LOCAL_EXECUTED' if not failed else 'SIMULATED_OR_INCONCLUSIVE','independently_verified':False}