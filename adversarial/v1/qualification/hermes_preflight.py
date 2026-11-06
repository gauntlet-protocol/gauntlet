#!/usr/bin/env python3
"""Hermes sandbox compatibility probe: no HOME, secrets, or outbound network.
Never equate executable discovery or --help with successful agent inference.
"""
import json,subprocess,sys

def probe(hermes_root='/home/njaal/.hermes'):
    cmd=['bwrap','--die-with-parent','--unshare-net','--new-session','--ro-bind','/usr','/usr','--ro-bind','/bin','/bin','--ro-bind','/lib','/lib','--ro-bind','/lib64','/lib64','--proc','/proc','--dev','/dev','--tmpfs','/tmp','--dir','/home','--dir','/home/njaal','--ro-bind',hermes_root,hermes_root,'--setenv','HOME','/tmp','--chdir','/tmp',hermes_root+'/hermes-agent/.hermes/bin/hermes','--help']
    p=subprocess.run(cmd,env={'PATH':'/usr/bin:/bin','LANG':'C'},capture_output=True,text=True,timeout=15)
    return {'sandbox_started':p.returncode==0,'sandbox_exit_code':p.returncode,'agent_inference_executed':False,'broker_connected':False,'qualified':False,'reason':'HELP_ONLY' if p.returncode==0 else 'HERMES_INSTALL_DEPENDENCIES_UNAVAILABLE_IN_SANDBOX'}
if __name__=='__main__':
    result=probe();print(json.dumps(result,indent=2));sys.exit(0 if result['sandbox_started'] else 2)