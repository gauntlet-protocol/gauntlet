#!/usr/bin/env python3
"""Fail-closed bubblewrap smoke probe; not a substitute for agent tool isolation."""
import subprocess

BWRAP=['bwrap','--die-with-parent','--unshare-net','--new-session','--ro-bind','/usr','/usr','--ro-bind','/bin','/bin','--ro-bind','/lib','/lib','--ro-bind','/lib64','/lib64','--proc','/proc','--dev','/dev','--tmpfs','/tmp']

def probe():
    result=subprocess.run(BWRAP+['/usr/bin/python3','-c',"import socket; s=socket.socket(); s.settimeout(1); s.connect(('1.1.1.1',53))"],capture_output=True,text=True,timeout=10)
    if result.returncode==0:
        raise RuntimeError('network unexpectedly reachable: sandbox FAIL')
    if 'Network is unreachable' not in result.stderr and 'Errno 101' not in result.stderr:
        raise RuntimeError('sandbox could not be confirmed: '+result.stderr[:400])
    return True

if __name__=='__main__':
    assert probe()
    print('PASS: bubblewrap network namespace blocked outbound connection')