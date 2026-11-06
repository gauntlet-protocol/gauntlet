#!/usr/bin/env python3
"""Credential-free, network-denied Agy inference attempt.
A failure is expected until an explicit compatible broker transport exists.
Never mounts host HOME, secrets, or network; never treats CLI startup as inference.
"""
import json,pathlib,subprocess,sys
from agy_preflight import check

def probe(binary='/home/njaal/.local/bin/agy',timeout=12):
    check(binary)
    args=['bwrap','--die-with-parent','--unshare-net','--new-session','--ro-bind','/usr','/usr','--ro-bind','/bin','/bin','--ro-bind','/lib','/lib','--ro-bind','/lib64','/lib64','--proc','/proc','--dev','/dev','--tmpfs','/tmp','--dir','/home','--dir','/home/agent','--dir','/home/agent/bin','--ro-bind',str(pathlib.Path(binary)),'/home/agent/bin/agy','--setenv','HOME','/tmp','--setenv','XDG_CONFIG_HOME','/tmp/config','--chdir','/tmp','/home/agent/bin/agy','--print','Reply with exactly READY','--print-timeout','5s','--output-format','json']
    try:
        p=subprocess.run(args,capture_output=True,text=True,timeout=timeout,env={'PATH':'/usr/bin:/bin','LANG':'C'})
        return {'attempted_real_agent_inference':True,'exit_code':p.returncode,'timed_out':False,'model_response_verified':False,'broker_connected':False,'qualified':False,'output_suppressed':True}
    except subprocess.TimeoutExpired:
        return {'attempted_real_agent_inference':True,'exit_code':None,'timed_out':True,'model_response_verified':False,'broker_connected':False,'qualified':False,'output_suppressed':True}
if __name__=='__main__':
    print(json.dumps(probe(),indent=2));sys.exit(2)