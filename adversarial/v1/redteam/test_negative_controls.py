import unittest
from negative_controls import run
class NegativeControls(unittest.TestCase):
 def test_unsafe_actions_are_detected(self):
  rows=run();self.assertEqual(len(rows),3);self.assertTrue(all(r['detected'] for r in rows))
if __name__=='__main__':unittest.main()