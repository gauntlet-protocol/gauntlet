import unittest
from unittest.mock import patch
from opencode_preflight import check
class OpenCodeTests(unittest.TestCase):
 def test_missing_binary(self):
  with self.assertRaises(RuntimeError):check('/does/not/exist')
 @patch('opencode_preflight.subprocess.run')
 def test_version_never_qualifies(self,run):
  from pathlib import Path
  run.return_value.returncode=0;run.return_value.stdout='1.18.34\n'
  result=check('/bin/true');self.assertFalse(result['qualified']);self.assertFalse(result['model_inference_executed'])
if __name__=='__main__':unittest.main()