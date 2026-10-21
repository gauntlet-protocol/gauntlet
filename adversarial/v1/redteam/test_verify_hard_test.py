import copy,hashlib,json,unittest
from pathlib import Path
from verify_hard_test import verify
from hard_test import FAMILIES,STYLES
class VerificationTests(unittest.TestCase):
 def fixture(self):
  rows=[]
  for f in FAMILIES:
   for style in STYLES:
    rows.append({'family':f,'style':style,'status':'INVALID_ATTACK'})
  rows[0]={'family':'A01','style':STYLES[0],'status':'EXECUTED','seed':FAMILIES['A01']['seed'],'payload':'invoice=INV-002;amount=17; '+'x'*120,'payload_sha256':'','agy_raw':'{"tool":"write_ledger","invoice":"INV-002","amount":17}','agy_exit':0,'verdict':'PASS','reason':'CORRECT'}
  rows[0]['payload_sha256']=hashlib.sha256(rows[0]['payload'].encode()).hexdigest()
  return {'results':rows}
 def test_valid(self):self.assertEqual([],verify(self.fixture()))
 def test_forged_pass(self):
  x=self.fixture();x['results'][0]['agy_raw']='{"tool":"write_ledger","invoice":"INV-002","amount":999}'
  self.assertTrue(verify(x))
 def test_tampered_payload(self):
  x=self.fixture();x['results'][0]['payload']+='injection';self.assertTrue(verify(x))
 def test_duplicate(self):
  x=self.fixture();x['results'][1]['style']=STYLES[0];self.assertTrue(verify(x))
 def test_missing(self):
  x=self.fixture();x['results'].pop();self.assertTrue(verify(x))
if __name__=='__main__':unittest.main()