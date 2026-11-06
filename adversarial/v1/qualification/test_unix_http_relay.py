import json,pathlib,socket,subprocess,tempfile,threading,unittest
from fixture_http_bridge import server
from unix_http_relay import relay_once
class RelayTests(unittest.TestCase):
 def test_isolated_guest_http_over_unix_socket(self):
  with tempfile.TemporaryDirectory() as d:
   http=server();t=threading.Thread(target=http.serve_forever,daemon=True);t.start()
   path=pathlib.Path(d)/'http.sock';ready=threading.Event();relay=threading.Thread(target=relay_once,args=(path,http.server_port,ready),daemon=True);relay.start();self.assertTrue(ready.wait(5))
   guest='''import socket,json
s=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);s.connect('/run/gauntlet/http.sock')
b=json.dumps({'model':'gauntlet-fixture-v1','messages':[{'role':'user','content':'test'}]}).encode()
s.sendall(b'POST /v1/chat/completions HTTP/1.1\\r\\nHost: localhost\\r\\nAuthorization: Bearer gauntlet-synthetic-no-privileges\\r\\nContent-Type: application/json\\r\\nContent-Length: '+str(len(b)).encode()+b'\\r\\nConnection: close\\r\\n\\r\\n'+b)
out=b''
while True:
 c=s.recv(16384)
 if not c:break
 out+=c
assert b'200 OK' in out and b'DENY' in out,out
print('ISOLATED_HTTP_RELAY_PASS')
'''
   cmd=['bwrap','--die-with-parent','--unshare-net','--new-session','--ro-bind','/usr','/usr','--ro-bind','/bin','/bin','--ro-bind','/lib','/lib','--ro-bind','/lib64','/lib64','--proc','/proc','--dev','/dev','--tmpfs','/tmp','--dir','/run','--dir','/run/gauntlet','--bind',str(path),'/run/gauntlet/http.sock','/usr/bin/python3','-c',guest]
   try:
    p=subprocess.run(cmd,capture_output=True,text=True,timeout=12);self.assertEqual(p.returncode,0,p.stderr);self.assertIn('ISOLATED_HTTP_RELAY_PASS',p.stdout);self.assertEqual(len(http.observed),1)
   finally:http.shutdown();http.server_close();t.join(3);relay.join(3)
if __name__=='__main__':unittest.main()