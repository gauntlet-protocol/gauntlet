import copy
import unittest
from validate import validate, reject_duplicates, KINDS

S = dict(product_id='agent-x', product_version='1.0', environment_id='local-a')

def sample():
    return dict(format='gauntlet-claim-chain-v0.1', subject=S, records=[dict(id=f'id-{i}', kind=k, subject=S.copy(), scope='policy-a', version='1', source_ref='sha256:example', upstream_id=f'id-{i-1}' if i else None) for i, k in enumerate(KINDS)])

class ChainTests(unittest.TestCase):
    def test_valid_is_not_verification(self):
        self.assertEqual(validate(sample()), 'STRUCTURALLY_VALID_UNVERIFIED')
    def test_duplicate_ids(self):
        d=sample(); d['records'][1]['id']='id-0'
        with self.assertRaises(ValueError): validate(d)
    def test_wrong_product_version(self):
        d=sample(); d['records'][2]['subject']['product_version']='2.0'
        with self.assertRaises(ValueError): validate(d)
    def test_missing_upstream(self):
        d=sample(); d['records'][3]['upstream_id']='absent'
        with self.assertRaises(ValueError): validate(d)
    def test_skipped_stage(self):
        d=sample(); d['records'][5]['upstream_id']='id-2'
        with self.assertRaises(ValueError): validate(d)
    def test_scope_drift(self):
        d=sample(); d['records'][4]['scope']='other'
        with self.assertRaises(ValueError): validate(d)
    def test_duplicate_json_key(self):
        with self.assertRaises(ValueError): reject_duplicates([('a',1),('a',2)])
    def test_unknown_field(self):
        d=sample(); d['records'][0]['asserted_pass']=True
        with self.assertRaises(ValueError): validate(d)

if __name__ == '__main__': unittest.main()
