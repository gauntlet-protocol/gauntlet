import unittest
from unittest.mock import patch
from runner import run
class RunnerTests(unittest.TestCase):
 def test_preflight_does_not_count_as_agent_execution(self):
  with patch('runner.check',return_value={'real_agy_binary_started_in_bwrap':True}):
   r=run();self.assertEqual(r['result'],'INCONCLUSIVE');self.assertFalse(r['qualification']['qualified']);self.assertIn('participant_executed',r['qualification']['failed_gates']);self.assertIn('provider_transport_observed',r['qualification']['failed_gates'])
if __name__=='__main__':unittest.main()