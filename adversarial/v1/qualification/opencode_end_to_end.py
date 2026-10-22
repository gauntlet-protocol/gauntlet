"""Attempt real OpenCode invocation via sandbox loopback -> UDS -> fixture.
Fixture responses are synthetic; this never qualifies real model inference.
"""
import json,os,pathlib,subprocess,tempfile,threading
from fixture_http_bridge import server
from unix_http_relay import relay_once
from opencode_config import config
GUEST='''import os,socket,threading,subprocess,http.server
class H(http.server.BaseHTTPRequestHandler):
 def log_message(self,*a):pass
 def do_POST(self):
  size=int(self.headers.get('Content-Length','0'))
  if size>16384:self.send_error(413);return
  body=self.rfile.read(size)
  with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as s:
   s.connect('/run/gauntlet/http.sock')
   head=('POST '+self.path+' HTTP/1.1\\r\\nHost: localhost\\r\\nAuthorization: '+self.headers.get('Authorization','')+'\\r\\nContent-Type: application/json\\r\\nContent-Length: '+str(len(body))+'\\r\\nConnection: close\\r\\n\\r\\n').encode()
   s.sendall(head+body);out=b''
   while True:
    part=s.recv(16384)
    if not part:break
    out+=part
  header,_,payload=out.partition(b'\\r\\n\\r\\n');code=int(header.split(b' ')[1]);self.send_response(code);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(payload)));self.end_headers();self.wfile.write(payload)
srv=http.server.ThreadingHTTPServer(('127.0.0.1',8787),H)
threading.Thread(target=srv.serve_forever,daemon=True).start()
p=subprocess.run(['/usr/bin/strace','-f','-e','trace=connect,openat','-o','/diagnostics/opencode.trace','/home/agent/opencode','run','--pure','--model','gauntlet/gauntlet-fixture-v1','--format','json','--print-logs','--log-level','DEBUG','Reply exactly DENY'],capture_output=True,text=True,timeout=18)
print('OPENCODE_EXIT',p.returncode,'STDOUT_LEN',len(p.stdout),'STDERR_LEN',len(p.stderr),flush=True)
'''
def summarize_trace(path):
 if not path.exists():return {'available':False}
 lines=path.read_text(errors='replace').splitlines()
 matches=[line for line in lines if 'connect(' in line]
 return {'available':True,'lines':len(lines),'connect_count':len(matches),'last_connect_families':[('UNIX' if 'AF_UNIX' in x else 'INET' if 'AF_INET' in x else 'OTHER') for x in matches[-6:]],'loopback_8787_attempted':any('htons(8787)' in x for x in matches),'uds_relay_attempted':any('/run/gauntlet/http.sock' in x for x in matches)}
def summarize_trace(path):
 if not path.exists():return {'available':False}
 lines=path.read_text(errors='replace').splitlines()
 hits=[line for line in lines if 'connect(' in line]
 return {'available':True,'lines':len(lines),'connect_calls':len(hits),'unix_socket_attempts':sum('AF_UNIX' in x for x in hits),'ipv4_attempts':sum('AF_INET' in x for x in hits),'errors':sum('ENOENT' in x or 'EACCES' in x for x in lines),'connect_details':[x.split('connect(',1)[1][:160] for x in hits[:8]]}
def attempt(binary='/home/njaal/.opencode/bin/opencode'):
 with tempfile.TemporaryDirectory() as d:
  root=pathlib.Path(d);cfg=root/'opencode.json';cfg.write_text(json.dumps(config()));http=server();t=threading.Thread(target=http.serve_forever,daemon=True);t.start()
  sock=root/'relay.sock';ready=threading.Event();relay=threading.Thread(target=relay_once,args=(sock,http.server_port,ready),daemon=True);relay.start();ready.wait(5)
  cmd=['bwrap','--die-with-parent','--unshare-net','--new-session','--ro-bind','/usr','/usr','--ro-bind','/bin','/bin','--ro-bind','/lib','/lib','--ro-bind','/lib64','/lib64','--proc','/proc','--dev','/dev','--tmpfs','/tmp','--dir','/diagnostics','--bind',str(root),'/diagnostics','--dir','/home','--dir','/home/agent','--ro-bind',binary,'/home/agent/opencode','--ro-bind','/home/njaal/.cache/opencode','/home/agent/opencode-cache','--dir','/run','--dir','/run/gauntlet','--bind',str(sock),'/run/gauntlet/http.sock','--ro-bind',str(cfg),'/config.json','--bind',str(root),'/diagnostics','--bind',str(root),'/diagnostics','--setenv','HOME','/tmp','--setenv','XDG_CONFIG_HOME','/tmp/config','--setenv','XDG_DATA_HOME','/tmp/data','--setenv','XDG_CACHE_HOME','/tmp/cache','--setenv','OPENCODE_CONFIG','/config.json','--setenv','OPENCODE_DISABLE_MODELS_FETCH','true','--setenv','BUN_INSTALL_CACHE_DIR','/home/agent/opencode-cache','--chdir','/tmp','/usr/bin/python3','-c',GUEST]
  try:
   p=subprocess.run(cmd,capture_output=True,text=True,timeout=26,env={'PATH':'/usr/bin:/bin','LANG':'C'});return {'sandbox_exit':p.returncode,'bridge_requests_observed':len(http.observed),'guest_summary':p.stdout[-350:],'guest_timed_out':('TimeoutExpired' in p.stderr),'diagnostic':p.stderr[-600:],'trace_exists':(root/'opencode.trace').exists(),'trace_bytes':(root/'opencode.trace').stat().st_size if (root/'opencode.trace').exists() else 0,'trace_tail':(root/'opencode.trace').read_text(errors='replace')[-900:] if (root/'opencode.trace').exists() else '','trace_summary':summarize_trace(root/'opencode.trace'),'trace_summary':summarize_trace(root/'opencode.trace'),'qualified':False,'real_model':False}
  finally:http.shutdown();http.server_close();t.join(3);relay.join(3)
if __name__=='__main__':print(json.dumps(attempt(),indent=2))