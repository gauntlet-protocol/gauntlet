import unittest
from isolated_gateway import validate_untrusted_action

class GatewayTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(validate_untrusted_action('{"tool":"write_ledger","invoice":"INV-001","amount":42}'),{'invoice':'INV-001','amount':42})
    def test_reject_bad_tool(self):
        with self.assertRaises(ValueError):validate_untrusted_action('{"tool":"shell.exec","invoice":"INV-001","amount":42}')
    def test_reject_extra_fields(self):
        with self.assertRaises(ValueError):validate_untrusted_action('{"tool":"write_ledger","invoice":"INV-001","amount":42,"cmd":"rm -rf /"}')
if __name__=='__main__':unittest.main()