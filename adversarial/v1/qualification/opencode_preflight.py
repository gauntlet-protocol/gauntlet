#!/usr/bin/env python3
"""Local OpenCode process preflight without host home or network access.
A CLI --version check is never a model inference or qualification result.
"""
import json,pathlib,subprocess,sys

def check(binary='/home/njaal/.opencode/bin/opencode'):
    if not pathlib.Path(binary).is_file():raise RuntimeError('opencode_binary_missing')
    cmd=['bwrap','--die-with-parent','--unshare-net','--new-session','--ro-bind','/usr','/usr','--ro-bind','/bin','/bin','--ro-bind','/lib','/lib','--ro-bind','/lib64','/lib64','--proc','/proc','--dev','/dev','--tmpfs','/tmp','--dir','/home','--dir','/home/agent','--ro-bind',binary,'/home/agent/opencode','--setenv','HOME','/tmp','--setenv','XDG_CONFIG_HOME','/tmp/config','--setenv','XDG_DATA_HOME','/tmp/data','--setenv','XDG_CACHE_HOME','/tmp/cache','--chdir','/tmp','/home/agent/opencode','--version']
    p=subprocess.run(cmd,env={'PATH':'/usr/bin:/bin','LANG':'C'},capture_output=True,text=True,timeout=15)
    if p.returncode or not p.stdout.strip():raise RuntimeError('isolated_opencode_start_failed')
    return {'real_opencode_binary_started':True,'network_unshared':True,'host_home_mounted':False,'version':p.stdout.strip(),'model_inference_executed':False,'broker_connected':False,'qualified':False}
if __name__=='__main__':
    try:print(json.dumps(check(),indent=2))
    except Exception as exc:print('REJECTED',str(exc),file=sys.stderr);sys.exit(2)