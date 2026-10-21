import unittest
from evaluate import CANARY,CASES,oracle,run

class A03Tests(unittest.TestCase):
 def test_resistant(self):self.assertEqual(run('resistant')['overall'],'PASS')
 def test_vulnerable(self):
  r=run('vulnerable');self.assertEqual(r['overall'],'FAIL');self.assertTrue(r['results'][1]['security_violation'])
 def test_refuse(self):self.assertEqual(run('refuse')['overall'],'FAIL')
 def test_hidden_channel(self):self.assertEqual(oracle(CASES[1],[('tool_log','prefix '+CANARY)],CASES[1]['expected'])['verdict'],'FAIL')
if __name__=='__main__':unittest.main()