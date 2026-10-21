import unittest
from isolated_actor import run
class IsolatedActorTests(unittest.TestCase):
 def test_real_socket_attempt_is_blocked(self):
  r=run();self.assertEqual(r['verdict'],'PASS');self.assertEqual(r['observed']['network']['bytes_sent'],0)
if __name__=='__main__':unittest.main()