import unittest
from agy_preflight import check
class AgyPreflightTests(unittest.TestCase):
 def test_missing_binary_fails_closed(self):
  with self.assertRaises(RuntimeError):check('/does/not/exist')
 def test_real_binary_starts_in_sandbox(self):
  import pathlib
  if not pathlib.Path('/home/njaal/.local/bin/agy').is_file():self.skipTest('local agy unavailable')
  result=check();self.assertTrue(result['real_agy_binary_started_in_bwrap']);self.assertFalse(result['qualified']);self.assertFalse(result['model_inference_executed'])
if __name__=='__main__':unittest.main()