import unittest
from evaluate import run

class A02Tests(unittest.TestCase):
 def test_resistant(self):self.assertEqual(run('resistant')['overall'],'PASS')
 def test_vulnerable(self):
  r=run('vulnerable');self.assertEqual(r['overall'],'FAIL');self.assertTrue(r['results'][1]['security_violation'])
 def test_refuse(self):self.assertEqual(run('refuse')['overall'],'FAIL')
if __name__=='__main__':unittest.main()