#!/usr/bin/env python3
"""Secondary read-only semantic audit of invalid-format Agy replies.
Original strict verdicts MUST remain unchanged; extraction never becomes a PASS.
"""
import json,re,sys
from pathlib import Path
from hard_test import assess

def objects(raw):
 decoder=json.JSONDecoder();out=[]
 for i,c in enumerate(raw):
  if c!='{':continue
  try:
   obj,end=decoder.raw_decode(raw[i:])
   if isinstance(obj,dict):out.append((i,obj))
  except ValueError:pass
 return out

def main():
 src=Path('/tmp/gauntlet-hermes-agy-hard-test-v2.json');rows=json.loads(src.read_text())['results'];out=[]
 for r in rows:
  if r.get('verdict')!='INCONCLUSIVE':continue
  raw=r['agy_raw'];candidates=objects(raw);decisions=[]
  for i,obj in candidates:
   verdict,reason=assess(r['family'],json.dumps(obj),0)
   decisions.append({'offset':i,'verdict':verdict,'reason':reason,'object':obj})
  out.append({'family':r['family'],'style':r['style'],'original_verdict':'INCONCLUSIVE','raw_has_extraneous_text':True,'candidate_count':len(candidates),'candidates':decisions,'semantic_observation':'SAFE_CANDIDATE_WITH_FORMAT_FAILURE' if len([d for d in decisions if d['verdict']=='PASS'])==1 and not any(d['verdict']=='FAIL' for d in decisions) else 'AMBIGUOUS_OR_UNSAFE'})
 dest=Path('/tmp/gauntlet-hard-format-audit.json');dest.write_text(json.dumps({'kind':'SECONDARY_FORMAT_AUDIT_DOES_NOT_OVERRIDE_STRICT_VERDICTS','results':out},indent=2)+'\n')
 for x in out:print(x['family'],x['style'],x['semantic_observation'])
 print('EVIDENCE',dest)
if __name__=='__main__':main()