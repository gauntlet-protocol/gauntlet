import pathlib,socket,subprocess,tempfile,threading,unittest
from transport import adjudicate,client,serve_once,BrokerDenied
class BrokerTests(unittest.TestCase):
 def test_allowlisted_fixture(self):self.assertFalse(adjudicate({'op':'infer','model':'gauntlet-fixture-v1','prompt':'hello'})['real_model'])
 def test_external_model_denied(self):
  with self.assertRaises(BrokerDenied):adjudicate({'op':'infer','model':'gpt-6','prompt':'hello'})
 def test_unexpected_fields_denied(self):
  with self.assertRaises(BrokerDenied):adjudicate({'op':'infer','model':'gauntlet-fixture-v1','prompt':'hello','url':'https://example.com'})
 def test_isolated_guest_uses_unix_socket_no_network(self):
  with tempfile.TemporaryDirectory() as d:
   path=pathlib.Path(d)/'broker.sock';ready=threading.Event();t=threading.Thread(target=serve_once,args=(path,ready),daemon=True);t.start();self.assertTrue(ready.wait(5))
   guest='''import json,socket
s=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);s.connect('/run/gauntlet/broker.sock');s.sendall(json.dumps({'op':'infer','model':'gauntlet-fixture-v1','prompt':'test'}).encode());print(s.recv(8192).decode());s.close()
'''
   p=subprocess.run(['bwrap','--die-with-parent','--unshare-net','--new-session','--ro-bind','/usr','/usr','--ro-bind','/bin','/bin','--ro-bind','/lib','/lib','--ro-bind','/lib64','/lib64','--proc','/proc','--dev','/dev','--tmpfs','/tmp','--dir','/run','--dir','/run/gauntlet','--bind',str(path),'/run/gauntlet/broker.sock','/usr/bin/python3','-c',guest],capture_output=True,text=True,timeout=15)
   self.assertEqual(p.returncode,0,p.stderr);self.assertIn('fixture_response',p.stdout);t.join(3)
if __name__=='__main__':unittest.main()