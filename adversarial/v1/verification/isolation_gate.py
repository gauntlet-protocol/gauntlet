#!/usr/bin/env python3
"""Fail-closed local isolation qualification gate, not an agent runner.
Do not launch an external participant when the sandbox cannot be proven.
"""
import json,subprocess,sys
from pathlib import Path
BWRAP=['bwrap','--die-with-parent','--unshare-net','--new-session','--ro-bind','/usr','/usr','--ro-bind','/bin','/bin','--ro-bind','/lib','/lib','--ro-bind','/lib64','/lib64','--proc','/proc','--dev','/dev','--tmpfs','/tmp']
PROBE='''import json,os,socket
result={'host_file_readable':os.path.exists('/etc/passwd'),'tmp_writable':False,'network_blocked':False}
try:
 open('/tmp/gauntlet-write-test','w').write('ok');result['tmp_writable']=True
except OSError:pass
try:socket.create_connection(('1.1.1.1',53),timeout=2)
except OSError:result['network_blocked']=True
print(json.dumps(result))
'''
def check():
 p=subprocess.run(BWRAP+['/usr/bin/python3','-c',PROBE],capture_output=True,text=True,timeout=15)
 if p.returncode:raise RuntimeError('bubblewrap_failed: '+p.stderr[:200])
 d=json.loads(p.stdout)
 if d!={'host_file_readable':False,'tmp_writable':True,'network_blocked':True}:raise RuntimeError('isolation_invariant_failed: '+repr(d))
 return {'sandbox_effects_isolated':True,'participant_process_isolated':False,'qualified':False,'reason':'No controlled model API broker or fully confined Agy runtime'}
if __name__=='__main__':
 try:print(json.dumps(check(),indent=2));sys.exit(0)
 except Exception as e:print('REJECTED',e,file=sys.stderr);sys.exit(1)