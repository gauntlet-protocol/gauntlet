#!/usr/bin/env python3
"""A03 enforced network-denial probe. This is NOT an Agy sandbox run."""
import subprocess

BWRAP=['bwrap','--die-with-parent','--unshare-net','--new-session','--ro-bind','/usr','/usr','--ro-bind','/bin','/bin','--ro-bind','/lib','/lib','--ro-bind','/lib64','/lib64','--proc','/proc','--dev','/dev','--tmpfs','/tmp']

GUEST='''import json,socket,sys
try:
 s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
 s.settimeout(2)
 s.connect(('1.1.1.1',53))
 print(json.dumps({'network_reachable':True}))
except OSError as e:
 print(json.dumps({'network_reachable':False,'errno':e.errno}))
'''

def run_probe():
    proc=subprocess.run(BWRAP+['/usr/bin/python3','-c',GUEST],capture_output=True,text=True,timeout=10)
    if proc.returncode:
        raise RuntimeError('sandbox execution failed: '+proc.stderr[:300])
    import json
    data=json.loads(proc.stdout)
    if data.get('network_reachable') is not False or data.get('errno')!=101:
        raise RuntimeError('outbound isolation not confirmed: '+repr(data))
    return data

if __name__=='__main__':
    print('PASS: outbound socket blocked by network namespace',run_probe())