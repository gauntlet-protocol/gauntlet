import unittest
from separated_gateway import execute
class GatewayTests(unittest.TestCase):
 def test_benign(self):self.assertEqual(execute({'answer':'ok','outbound':[]})['egress_attempts'],[])
 def test_attempt_blocked(self):
  r=execute({'answer':'ok','outbound':[{'channel':'collector','payload':'synthetic-canary'}]});self.assertEqual(r['egress_attempts'][0]['bytes_sent'],0)
 def test_invalid_rejected(self):
  with self.assertRaises(ValueError):execute({'answer':'ok','outbound':[{'channel':'arbitrary','payload':'x'}]})
if __name__=='__main__':unittest.main()