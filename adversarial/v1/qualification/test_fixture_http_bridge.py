import unittest,json,threading,urllib.request,urllib.error
from fixture_http_bridge import server
class BridgeTests(unittest.TestCase):
 def setUp(self):
  self.s=server();self.t=threading.Thread(target=self.s.serve_forever,daemon=True);self.t.start()
 def tearDown(self):self.s.shutdown();self.s.server_close();self.t.join()
 def post(self,model='gauntlet-fixture-v1',key='gauntlet-synthetic-no-privileges'):
  req=urllib.request.Request('http://127.0.0.1:%d/v1/chat/completions'%self.s.server_port,data=json.dumps({'model':model,'messages':[{'role':'user','content':'hi'}]}).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
  return urllib.request.urlopen(req,timeout=3)
 def test_fixture_response_and_observation(self):
  with self.post() as r:self.assertEqual(json.load(r)['choices'][0]['message']['content'],'DENY')
  self.assertEqual(len(self.s.observed),1)
 def test_denies_other_model(self):
  with self.assertRaises(urllib.error.HTTPError) as c:self.post(model='real-model')
  self.assertEqual(c.exception.code,403)
 def test_denies_wrong_token(self):
  with self.assertRaises(urllib.error.HTTPError) as c:self.post(key='bad')
  self.assertEqual(c.exception.code,403)
if __name__=='__main__':unittest.main()