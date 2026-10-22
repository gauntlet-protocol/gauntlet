#!/usr/bin/env python3
"""Real Agy executable sandbox preflight; deliberately does not run a model.
No host credentials, project, home, or general network are mounted.
"""
import json,os,pathlib,subprocess,sys

def check(binary='/home/njaal/.local/bin/agy'):
    binary=pathlib.Path(binary)
    if not binary.is_file():raise RuntimeError('agy_binary_missing')
    args=['bwrap','--die-with-parent','--unshare-net','--new-session','--ro-bind','/usr','/usr','--ro-bind','/bin','/bin','--ro-bind','/lib','/lib','--ro-bind','/lib64','/lib64','--proc','/proc','--dev','/dev','--tmpfs','/tmp','--dir','/home','--dir','/home/agent','--dir','/home/agent/bin','--ro-bind',str(binary),'/home/agent/bin/agy','--setenv','HOME','/tmp','--setenv','XDG_CONFIG_HOME','/tmp/config','--chdir','/tmp','/home/agent/bin/agy','--help']
    proc=subprocess.run(args,capture_output=True,text=True,timeout=15,env={'PATH':'/usr/bin:/bin','LANG':'C'})
    if proc.returncode or 'Usage of agy:' not in proc.stdout+proc.stderr:raise RuntimeError('isolated_agy_failed:'+proc.stderr[:200])
    return {'real_agy_binary_started_in_bwrap':True,'network_namespace':'unshare-net','host_home_mounted':False,'model_inference_executed':False,'provider_broker_connected':False,'qualified':False}
if __name__=='__main__':
    try:print(json.dumps(check(sys.argv[1] if len(sys.argv)>1 else '/home/njaal/.local/bin/agy'),indent=2))
    except Exception as exc:print('REJECTED',str(exc),file=sys.stderr);sys.exit(1)