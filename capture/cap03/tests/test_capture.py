import unittest
from capture import evaluate

class CaptureTests(unittest.TestCase):
    def baseline(self):
        return {'baseline':{'protected_counterexamples':{'revoked_mandate':True,'bypass':True}},'amendments':[]}

    def test_clean(self):
        self.assertEqual(evaluate(self.baseline())['status'],'PASS')

    def test_cumulative_loss(self):
        h=self.baseline()
        h['amendments']=[{'id':'one','detected':{'revoked_mandate':False}},{'id':'two','detected':{'bypass':False}}]
        r=evaluate(h)
        self.assertEqual(r['status'],'FAIL')
        self.assertEqual(r['final_lost'],['bypass','revoked_mandate'])
        self.assertEqual(r['first_loss_by_counterexample']['revoked_mandate'],'one')

    def test_restored_still_reported(self):
        h=self.baseline()
        h['amendments']=[{'id':'one','detected':{'bypass':False}},{'id':'two','detected':{'bypass':True}}]
        r=evaluate(h)
        self.assertEqual(r['status'],'FAIL')
        self.assertEqual(r['final_lost'],[])
        self.assertEqual(r['ever_lost'],['bypass'])

    def test_unknown_counterexample_rejected(self):
        h=self.baseline();h['amendments']=[{'id':'x','detected':{'unknown':False}}]
        with self.assertRaises(ValueError): evaluate(h)

    def test_duplicate_rejected(self):
        h=self.baseline();h['amendments']=[{'id':'x','detected':{}},{'id':'x','detected':{}}]
        with self.assertRaises(ValueError): evaluate(h)

    def test_stable_digest(self):
        self.assertEqual(evaluate(self.baseline()),evaluate(self.baseline()))

if __name__=='__main__': unittest.main()
