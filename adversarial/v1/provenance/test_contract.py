import unittest
from contract import Level,Provenance,ProvenanceError,validate,classify
class ContractTests(unittest.TestCase):
 def test_heuristic_pass_cannot_verify(self):
  with self.assertRaises(ProvenanceError):validate(Provenance(Level.VERIFIED,'valo_heuristic','valo',heuristic=True,evidence_digest='sha256:a'))
 def test_synthetic_heimel_cannot_verify(self):
  with self.assertRaises(ProvenanceError):validate(Provenance(Level.VERIFIED,'heimel_benchmark','heimel',synthetic=True,evidence_digest='sha256:a'))
 def test_local_executed(self):validate(Provenance(Level.LOCAL_EXECUTED,'agy_cli','agy',evidence_digest='sha256:a'))
 def test_verified_requires_observer(self):
  with self.assertRaises(ProvenanceError):validate(Provenance(Level.VERIFIED,'live','agy',evidence_digest='sha256:a'))
 def test_self_verification_rejected(self):
  with self.assertRaises(ProvenanceError):validate(Provenance(Level.VERIFIED,'live','agy',evidence_digest='sha256:a',observed_effect_digest='sha256:b',verifier_id='agy',verifier_evidence_digest='sha256:c'))
 def test_distinct_verifier_claim_only(self):validate(Provenance(Level.VERIFIED,'live','agy',evidence_digest='sha256:a',observed_effect_digest='sha256:b',verifier_id='external',verifier_evidence_digest='sha256:c'))
 def test_independent_attestation_requires_third_party(self):
  with self.assertRaises(ProvenanceError):validate(Provenance(Level.INDEPENDENTLY_ATTESTED,'live','agy',evidence_digest='sha256:a',observed_effect_digest='sha256:b',verifier_id='external',verifier_evidence_digest='sha256:c',attestor_id='external',attestation_digest='sha256:d'))
 def test_unknown_level_fails(self):
  with self.assertRaises(ProvenanceError):classify({'level':'PRODUCTION_VERIFIED','method':'x','subject':'x'})
if __name__=='__main__':unittest.main()