import unittest
from provider_policy import ProviderPolicy,ProviderPolicyError,validate
class PolicyTests(unittest.TestCase):
 def setUp(self):self.p=ProviderPolicy('fixture-provider','https://api.example.test/v1',('test-model',))
 def test_allowed(self):self.assertEqual(validate(self.p,'test-model','hi',10)['status'],'POLICY_ACCEPTED_NOT_EXECUTED')
 def test_model_denied(self):
  with self.assertRaises(ProviderPolicyError):validate(self.p,'other','hi',10)
 def test_http_denied(self):
  with self.assertRaises(ProviderPolicyError):validate(ProviderPolicy('x','http://example.com',('test-model',)),'test-model','hi',10)
 def test_local_ip_denied(self):
  with self.assertRaises(ProviderPolicyError):validate(ProviderPolicy('x','https://127.0.0.1',('test-model',)),'test-model','hi',10)
 def test_embedded_credentials_denied(self):
  with self.assertRaises(ProviderPolicyError):validate(ProviderPolicy('x','https://key:secret@example.com',('test-model',)),'test-model','hi',10)
 def test_budget_denied(self):
  with self.assertRaises(ProviderPolicyError):validate(self.p,'test-model','hi',10000)
if __name__=='__main__':unittest.main()