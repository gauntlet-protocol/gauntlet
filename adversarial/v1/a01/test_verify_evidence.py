import copy
import json
import unittest
from pathlib import Path
from verify_evidence import verify

class EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads(Path('/tmp/gauntlet-a01-agy-run.json').read_text()) if Path('/tmp/gauntlet-a01-agy-run.json').exists() else None
    def test_consistent(self):
        if self.data is None:self.skipTest('local Agy evidence absent')
        self.assertEqual(verify(self.data),[])
    def test_tampered_ledger(self):
        if self.data is None:self.skipTest('local Agy evidence absent')
        d=copy.deepcopy(self.data)
        d['results'][1]['observed_ledger'][0]['amount']=999
        self.assertTrue(verify(d))
    def test_tampered_verdict(self):
        if self.data is None:self.skipTest('local Agy evidence absent')
        d=copy.deepcopy(self.data)
        d['results'][1]['oracle']['verdict']='FAIL'
        self.assertTrue(verify(d))
if __name__=='__main__':unittest.main()