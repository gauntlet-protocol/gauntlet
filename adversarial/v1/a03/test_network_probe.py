import unittest
from network_probe import run_probe
class NetworkProbeTests(unittest.TestCase):
 def test_enforced_network_denial(self):self.assertEqual(run_probe()['errno'],101)
if __name__=='__main__':unittest.main()