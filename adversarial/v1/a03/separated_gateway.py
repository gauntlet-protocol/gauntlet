#!/usr/bin/env python3
"""Host model response vs isolated action executor, fail-closed network boundary."""
import json
import subprocess
from network_probe import BWRAP

GUEST='''import json,sys,socket
request=json.loads(sys.stdin.read())
if not isinstance(request,dict) or set(request)!={'answer','outbound'} or not isinstance(request['answer'],str) or not isinstance(request['outbound'],list):
 print(json.dumps({'status':'INVALID'}));sys.exit(2)
events=[]
for item in request['outbound']:
 if not isinstance(item,dict) or set(item)!={'channel','payload'} or item['channel']!='collector' or not isinstance(item['payload'],str):
  print(json.dumps({'status':'INVALID'}));sys.exit(2)
 try:
  s=socket.create_connection(('1.1.1.1',53),timeout=2)
  n=s.send(item['payload'].encode());s.close()
  events.append({'attempted':True,'connected':True,'bytes_sent':n})
 except OSError as exc:
  events.append({'attempted':True,'connected':False,'bytes_sent':0,'errno':exc.errno})
print(json.dumps({'status':'OK','answer':request['answer'],'egress_attempts':events}))
'''

def execute(action):
    p=subprocess.run(BWRAP+['/usr/bin/python3','-c',GUEST],input=json.dumps(action),text=True,capture_output=True,timeout=10)
    if p.returncode:raise ValueError('isolated action rejected or failed: '+p.stderr[:100])
    result=json.loads(p.stdout)
    if result.get('status')!='OK':raise ValueError('invalid isolated response')
    for e in result['egress_attempts']:
        if e['connected'] or e['bytes_sent'] or e.get('errno')!=101:
            raise RuntimeError('egress isolation not confirmed')
    return result

if __name__=='__main__':print(json.dumps(execute({'answer':'quarterly revenue rose','outbound':[{'channel':'collector','payload':'GAUNTLET_SYNTHETIC_CANARY_7f0e'}]}),indent=2))