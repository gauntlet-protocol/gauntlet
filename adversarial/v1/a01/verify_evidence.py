#!/usr/bin/env python3
"""Independent-process local evidence consistency check; NOT independent attestation."""
import argparse
import hashlib
import json
from pathlib import Path
from evaluate import CASES, POLICY, evaluate


def verify(artifact):
    errors=[]
    if artifact.get('protocol') != 'gauntlet-a01-agy-local-v0':
        errors.append('protocol mismatch')
    if artifact.get('policy_sha256') != hashlib.sha256(POLICY.encode()).hexdigest():
        errors.append('policy digest mismatch')
    results=artifact.get('results')
    if not isinstance(results,list) or len(results)!=len(CASES):
        return ['missing or duplicated cases']
    for case, record in zip(CASES,results):
        if record.get('case_id') != case['id']:
            errors.append('case mismatch')
            continue
        if record.get('document_sha256') != hashlib.sha256(case['document'].encode()).hexdigest():
            errors.append(f'{case["id"]}: document digest mismatch')
        try:
            parsed=json.loads(record['raw_response'])
            if parsed != record['parsed_action']:
                errors.append(f'{case["id"]}: raw action mismatch')
            if set(parsed)!={'tool','invoice','amount'} or parsed['tool']!='write_ledger' or type(parsed['amount']) is not int or not isinstance(parsed['invoice'],str):
                errors.append(f'{case["id"]}: invalid action')
            expected_observed=[{'tool':'ledger.write','invoice':parsed['invoice'],'amount':parsed['amount']}]
            if record['observed_ledger'] != expected_observed:
                errors.append(f'{case["id"]}: action and ledger observation mismatch')
            oracle=evaluate({'actions':record['observed_ledger']},case)
            if record['oracle']!=oracle:
                errors.append(f'{case["id"]}: oracle mismatch')
        except (ValueError,TypeError,KeyError) as exc:
            errors.append(f'{case["id"]}: malformed evidence: {exc}')
    if artifact.get('overall') != ('PASS' if all(r.get('oracle',{}).get('verdict')=='PASS' for r in results) else 'NOT_PASS'):
        errors.append('aggregate mismatch')
    return errors

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('evidence')
    args=parser.parse_args()
    errors=verify(json.loads(Path(args.evidence).read_text()))
    print('CONSISTENT LOCAL EVIDENCE' if not errors else 'EVIDENCE INVALID: '+ '; '.join(errors))
    raise SystemExit(bool(errors))