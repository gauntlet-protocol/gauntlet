import os,pathlib,socket,subprocess,tempfile,threading,unittest
from transport import serve_once,client
class SecurityTests(unittest.TestCase):
 def test_socket_permissions_private(self):
  with tempfile.TemporaryDirectory() as d:
   path=pathlib.Path(d)/'broker.sock';ready=threading.Event();t=threading.Thread(target=serve_once,args=(path,ready),daemon=True);t.start();self.assertTrue(ready.wait(5));self.assertEqual(path.stat().st_mode & 0o777,0o600)
   response=client(path,{'op':'infer','model':'other','prompt':'x'});self.assertFalse(response['ok']);t.join(3)
 def test_guest_cannot_access_host_home_or_network(self):
  script='''import json,os,socket
out={'home_visible':os.path.exists('/home/njaal/.local/bin/agy'),'etc_visible':os.path.exists('/etc/passwd'),'network_denied':False}
try:socket.create_connection(('1.1.1.1',53),timeout=1)
except OSError:out['network_denied']=True
print(json.dumps(out))
'''
  import json
  p=subprocess.run(['bwrap','--die-with-parent','--unshare-net','--new-session','--ro-bind','/usr','/usr','--ro-bind','/bin','/bin','--ro-bind','/lib','/lib','--ro-bind','/lib64','/lib64','--proc','/proc','--dev','/dev','--tmpfs','/tmp','/usr/bin/python3','-c',script],capture_output=True,text=True,timeout=15)
  self.assertEqual(p.returncode,0,p.stderr);self.assertEqual(json.loads(p.stdout),{'home_visible':False,'etc_visible':False,'network_denied':True})
if __name__=='__main__':unittest.main()