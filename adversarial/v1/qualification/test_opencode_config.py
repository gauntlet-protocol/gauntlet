import unittest
from opencode_config import config
class ConfigTests(unittest.TestCase):
 def test_local_only(self):
  c=config();self.assertEqual(c['provider']['gauntlet']['options']['baseURL'],'http://127.0.0.1:8787/v1');self.assertEqual(c['permission']['*'],'deny')
 def test_external_denied(self):
  with self.assertRaises(ValueError):config('https://external.example/v1')
if __name__=='__main__':unittest.main()