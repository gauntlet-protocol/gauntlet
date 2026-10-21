import copy,unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from verify_bundle import create_bundle,verify
class EvidenceBundleTests(unittest.TestCase):
 def setUp(self):
  self.key=Ed25519PrivateKey.generate();self.bundle=create_bundle(b'{"synthetic":true}',self.key)
  import base64
  self.public=base64.b64decode(self.bundle['payload']['signer_public_key'])
 def test_valid(self):self.assertTrue(verify(self.bundle,self.public)['signature_valid'])
 def test_tampered_evidence(self):
  b=copy.deepcopy(self.bundle);b['payload']['evidence_base64']='e30='
  with self.assertRaises(ValueError):verify(b,self.public)
 def test_tampered_assurance(self):
  b=copy.deepcopy(self.bundle);b['payload']['assurance']='VERIFIED'
  with self.assertRaises(ValueError):verify(b,self.public)
 def test_untrusted_signer(self):
  other=Ed25519PrivateKey.generate().public_key().public_bytes_raw() if hasattr(Ed25519PrivateKey.generate().public_key(),'public_bytes_raw') else b'0'*32
  with self.assertRaises(ValueError):verify(self.bundle,other)
 def test_tampered_signature(self):
  b=copy.deepcopy(self.bundle);b['signature']='AA=='
  with self.assertRaises(ValueError):verify(b,self.public)
if __name__=='__main__':unittest.main()