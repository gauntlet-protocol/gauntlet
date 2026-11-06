import unittest
from unittest.mock import patch
from hermes_preflight import probe
class HermesTests(unittest.TestCase):
 @patch('hermes_preflight.subprocess.run')
 def test_help_cannot_qualify(self,run):
  run.return_value.returncode=0
  r=probe();self.assertFalse(r['qualified']);self.assertFalse(r['agent_inference_executed'])
 @patch('hermes_preflight.subprocess.run')
 def test_missing_dependencies_fail_closed(self,run):
  run.return_value.returncode=1
  r=probe();self.assertFalse(r['sandbox_started']);self.assertFalse(r['qualified'])
if __name__=='__main__':unittest.main()