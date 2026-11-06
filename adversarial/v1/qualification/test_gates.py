import unittest
from gates import RunEvidence,qualify
class QualificationTests(unittest.TestCase):
 def test_current_implementation_not_qualified(self):
  e=RunEvidence(False,False,False,False,True,True,False,True,True,True,False)
  result=qualify(e);self.assertFalse(result['qualified']);self.assertIn('participant_confined',result['failed_gates'])
 def test_one_missing_gate_fails_closed(self):
  values={k:True for k in RunEvidence.__dataclass_fields__};values['provider_transport_observed']=False
  self.assertFalse(qualify(RunEvidence(**values))['qualified'])
 def test_all_claims_not_independent_attestation(self):
  e=RunEvidence(**{k:True for k in RunEvidence.__dataclass_fields__})
  result=qualify(e);self.assertTrue(result['qualified']);self.assertFalse(result['independently_verified']);self.assertEqual(result['assurance_ceiling'],'LOCAL_EXECUTED')
if __name__=='__main__':unittest.main()