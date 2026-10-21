import tempfile
import unittest
from pathlib import Path
from ledger import Ledger

class LedgerTests(unittest.TestCase):
    def test_observed_durable_write(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'ledger.sqlite3'
            l=Ledger(path)
            l.write('INV-001',42)
            l.close()
            l=Ledger(path)
            self.assertEqual(l.observed(),[{'tool':'ledger.write','invoice':'INV-001','amount':42}])
            l.close()
    def test_reject_noninteger(self):
        with tempfile.TemporaryDirectory() as d:
            l=Ledger(Path(d)/'ledger.sqlite3')
            with self.assertRaises(ValueError):l.write('INV-001','42')
            self.assertEqual(l.observed(),[])
            l.close()
if __name__=='__main__':unittest.main()