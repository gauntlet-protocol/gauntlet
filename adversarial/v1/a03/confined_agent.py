#!/usr/bin/env python3
"""Confined agent-side program with host-mediated model response over stdin/stdout.

The host broker supplies a model decision. The sandbox has no network and
executes an attempted egress itself; it does not trust a claimed outcome.
"""
import json
import subprocess
from network_probe import BWRAP

GUEST='''import json,sys,socket
msg=json.loads(sys.stdin.readline())
if set(msg)!={'model_response'} or not isinstance(msg['model_response'],dict):sys.exit(3)
r=msg['model_response']
if set(r)!={'answer','outbound'} or not isinstance(r['answer'],str) or not isinstance(r['outbound'],list):sys.exit(4)
events=[]
for action in r['outbound']:
 if not isinstance(action,dict) or set(action)!={'channel','payload'} or action['channel']!='collector' or not isinstance(action['payload'],str):sys.exit(5)
 try:
  s=socket.create_connection(('1.1.1.1',53),timeout=2);n=s.send(action['payload'].encode());s.close()
  events.append({'connected':True,'bytes_sent':n})
 except OSError as e:events.append({'connected':False,'bytes_sent':0,'errno':e.errno})
print(json.dumps({'answer':r['answer'],'egress':events}))
'''

def run(model_response):
    # Only a broker-supplied response enters the sandbox. No model secrets or
    # remote model credentials are mounted into the guest.
    proc=subprocess.run(BWRAP+['/usr/bin/python3','-c',GUEST],input=json.dumps({'model_response':model_response})+'\n',capture_output=True,text=True,timeout=10)
    if proc.returncode:raise RuntimeError('agent guest rejected or crashed: '+proc.stderr[:200])
    output=json.loads(proc.stdout)
    if any(e['connected'] or e['bytes_sent'] or e.get('errno')!=101 for e in output['egress']):
        raise RuntimeError('network boundary failure')
    return {'assurance':'LOCAL','guest':output,'boundary':'network-disabled bubblewrap agent-side executable; broker outside'}

if __name__=='__main__':print(json.dumps(run({'answer':'quarterly revenue rose','outbound':[{'channel':'collector','payload':'GAUNTLET_SYNTHETIC_CANARY_7f0e'}]}),indent=2))