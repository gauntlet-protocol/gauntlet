import unittest
from unittest.mock import patch
from agy_inference_probe import probe
class ProbeTests(unittest.TestCase):
 @patch('agy_inference_probe.check')
 @patch('agy_inference_probe.subprocess.run')
 def test_no_success_claim_from_process_exit(self,run,check):
  run.return_value.returncode=0
  result=probe('/bin/true');self.assertFalse(result['qualified']);self.assertFalse(result['model_response_verified']);self.assertFalse(result['broker_connected'])
if __name__=='__main__':unittest.main()