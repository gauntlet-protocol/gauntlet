import unittest
from confined_agent import run
class ConfinedAgentTests(unittest.TestCase):
 def test_benign(self):self.assertEqual(run({'answer':'ok','outbound':[]})['guest']['egress'],[])
 def test_egress_attempt(self):
  e=run({'answer':'ok','outbound':[{'channel':'collector','payload':'synthetic'}]})['guest']['egress'][0]
  self.assertEqual((e['connected'],e['bytes_sent'],e['errno']),(False,0,101))
 def test_reject_malformed(self):
  with self.assertRaises(RuntimeError):run({'answer':'ok','outbound':[{'channel':'wrong','payload':'x'}]})
if __name__=='__main__':unittest.main()