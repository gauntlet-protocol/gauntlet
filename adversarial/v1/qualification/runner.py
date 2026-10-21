#!/usr/bin/env python3
"""Fail-closed participant run entry point.

Never substitutes --help or fixture model calls for a real participant run.
"""
import json,sys
from agy_preflight import check
from gates import RunEvidence,qualify

def run():
    preflight=check()
    evidence=RunEvidence(participant_executed=False,participant_confined=preflight['real_agy_binary_started_in_bwrap'],provider_allowlisted=False,provider_transport_observed=False,direct_network_denied=True,filesystem_isolated=True,independent_oracle_observed=False,negative_controls_passed=False,frozen_contract_match=False,evidence_integrity_valid=False,blind_evaluation=False)
    result=qualify(evidence)
    return {'kind':'GAUNTLET_RUNTIME_PREFLIGHT_ONLY','preflight':preflight,'qualification':result,'result':'INCONCLUSIVE','reason':'Agy model provider transport not connected to isolated process; no inference executed'}
if __name__=='__main__':
    print(json.dumps(run(),indent=2));sys.exit(2)