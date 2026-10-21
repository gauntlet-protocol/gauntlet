#!/usr/bin/env python3
"""Independent deterministic audit of exploratory Hermes/Agy evidence; no LLM calls."""
import argparse,hashlib,json,sys
from pathlib import Path
from hard_test import FAMILIES,STYLES,assess

def verify(data):
 errors=[];rows=data.get('results',[])
 if len(rows)!=30:errors.append(f'expected 30 rows, got {len(rows)}')
 seen=set()
 for n,r in enumerate(rows):
  family,style=r.get('family'),r.get('style');key=(family,style)
  if family not in FAMILIES or style not in STYLES or key in seen:errors.append(f'{n}: unexpected/duplicate case');continue
  seen.add(key)
  if r.get('status')=='INVALID_ATTACK':
   if 'verdict' in r:errors.append(f'{n}: invalid attack has verdict')
   continue
  if r.get('status')!='EXECUTED':errors.append(f'{n}: unknown status');continue
  payload=r.get('payload','')
  if not isinstance(payload,str) or not 120<=len(payload)<=1000 or any(s not in payload for s in FAMILIES[family]['required']):errors.append(f'{n}: malformed attack')
  if hashlib.sha256(payload.encode()).hexdigest()!=r.get('payload_sha256'):errors.append(f'{n}: payload hash mismatch')
  verdict,reason=assess(family,r.get('agy_raw',''),r.get('agy_exit'))
  if (verdict,reason)!=(r.get('verdict'),r.get('reason')):errors.append(f'{n}: oracle mismatch {verdict}/{reason}')
 if len(seen)!=30:errors.append('incomplete coverage')
 return errors

def main():
 p=argparse.ArgumentParser();p.add_argument('evidence',type=Path);a=p.parse_args()
 try:errors=verify(json.loads(a.evidence.read_text()))
 except (ValueError,KeyError,TypeError) as exc:errors=[str(exc)]
 print('VERIFIED LOCAL CONSISTENCY' if not errors else 'FAIL',*errors,sep='\n')
 return bool(errors)
if __name__=='__main__':sys.exit(main())