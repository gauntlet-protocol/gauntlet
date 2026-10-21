#!/usr/bin/env python3
"""Re-run exactly the five v2 format failures with Agy native JSON schema enforcement."""
import hashlib,json,subprocess
from pathlib import Path
from hard_test import FAMILIES,assess,call
SCHEMAS={
'A01':{'type':'object','properties':{'tool':{'const':'write_ledger'},'invoice':{'type':'string'},'amount':{'type':'integer'}},'required':['tool','invoice','amount'],'additionalProperties':False},
'A02':{'type':'object','properties':{'decision':{'type':'string','enum':['ALLOW','DENY']}},'required':['decision'],'additionalProperties':False},
'A03':{'type':'object','properties':{'answer':{'type':'string'},'outbound':{'type':'array','items':{'type':'object','properties':{'channel':{'type':'string'},'payload':{'type':'string'}},'required':['channel','payload'],'additionalProperties':False}}},'required':['answer','outbound'],'additionalProperties':False}}
def main():
 src=Path('/tmp/gauntlet-hermes-agy-hard-test-v2.json');data=json.loads(src.read_text());rows=[]
 for r in data['results']:
  if r.get('verdict')!='INCONCLUSIVE':continue
  f=r['family'];prompt=FAMILIES[f]['trusted']+'\nUNTRUSTED_DOCUMENT:\n'+r['seed']+'\n'+r['payload']
  p=call(['agy','--sandbox','--print-timeout','65s','--output-format','json','--json-schema',json.dumps(SCHEMAS[f]),'--print='+prompt],90)
  structured=None;error=''
  try:
   envelope=json.loads(p['stdout']);structured=envelope.get('structured_output')
   if envelope.get('status')!='SUCCESS' or not isinstance(structured,dict):error='NO_STRUCTURED_OUTPUT'
  except ValueError:error='BAD_ENVELOPE'
  verdict,reason=assess(f,json.dumps(structured) if structured is not None else '',p['code'] if p['code'] else (1 if error else 0))
  rows.append({'family':f,'style':r['style'],'original_verdict':r['verdict'],'retest_verdict':verdict,'retest_reason':reason,'structured_output':structured,'agy_exit':p['code'],'error':error,'source_payload_sha256':r['payload_sha256'],'raw_envelope_sha256':hashlib.sha256(p['stdout'].encode()).hexdigest(),'raw_envelope':p['stdout']})
  print(f,r['style'],verdict,reason,flush=True)
 out=Path('/tmp/gauntlet-hard-schema-retest.json');out.write_text(json.dumps({'kind':'SEPARATE_SCHEMA_ENFORCED_RETEST_NOT_RETROACTIVE','source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'results':rows},indent=2)+'\n');print('EVIDENCE',out)
if __name__=='__main__':main()