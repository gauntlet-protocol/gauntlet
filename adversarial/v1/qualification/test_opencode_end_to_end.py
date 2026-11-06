import unittest
from unittest.mock import patch
from opencode_end_to_end import attempt
class IntegrationTests(unittest.TestCase):
 @patch('opencode_end_to_end.subprocess.run')
 def test_never_claims_real_model_or_qualification(self,run):
  run.return_value.returncode=0;run.return_value.stdout='';run.return_value.stderr=''
  result=attempt('/bin/true');self.assertFalse(result['qualified']);self.assertFalse(result['real_model'])
if __name__=='__main__':unittest.main()