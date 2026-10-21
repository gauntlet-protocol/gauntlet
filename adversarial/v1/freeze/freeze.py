#!/usr/bin/env python3
"""Deterministic preregistration manifest for immutable local fixtures.
Freeze does not certify isolation, oracle independence, or security.
"""
import argparse,hashlib,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[3]
FILES=[
'adversarial/v1/README.md',
'adversarial/v1/redteam/hard_test.py',
'adversarial/v1/redteam/verify_hard_test.py',
'adversarial/v1/redteam/schema_retest.py',
'adversarial/v1/redteam/live_gateway.py',
'adversarial/v1/redteam/negative_controls.py',
'adversarial/v1/provenance/contract.py',
]
def manifest():
 entries={}
 for name in FILES:
  path=ROOT/name
  if not path.is_file():raise ValueError('missing fixture '+name)
  entries[name]=hashlib.sha256(path.read_bytes()).hexdigest()
 return {'schema':'gauntlet.preregistration.v1','scope':'LOCAL_EXPLORATORY_ONLY','status':'FROZEN_HASHES_NOT_QUALIFIED','files':entries,'challenge_families':['A01','A02','A03'],'excluded':['A04-A10 not implemented','Agy process not confined','No independently operated verifier','Attack fixtures not blinded','No independent attestation']}
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--verify',action='store_true');args=parser.parse_args()
 path=pathlib.Path(__file__).with_name('manifest.json');actual=manifest()
 if args.verify:
  saved=json.loads(path.read_text());ok=saved==actual
  print('FROZEN_MATCH' if ok else 'FROZEN_MISMATCH');return 0 if ok else 1
 if path.exists():
  print('Refusing overwrite: use a new version for changes',file=sys.stderr);return 2
 path.write_text(json.dumps(actual,sort_keys=True,indent=2)+'\n');print(hashlib.sha256(canonical(actual)).hexdigest());return 0
if __name__=='__main__':sys.exit(main())