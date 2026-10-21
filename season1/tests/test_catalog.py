"""Structure-only checks; do not imply any challenge has passed."""
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class CatalogStructureTests(unittest.TestCase):
    def test_catalog_is_complete_and_unique(self):
        items = json.loads((ROOT / 'catalog.json').read_text())['challenges']
        self.assertEqual(len(items), 28)
        self.assertEqual([item['id'] for item in items], [f'{i:03d}' for i in range(1, 29)])
        for item in items:
            manifest = json.loads((ROOT / 'challenges' / item['id'] / 'manifest.json').read_text())
            self.assertEqual(manifest['id'], item['id'])
            self.assertEqual(manifest['name'], item['name'])
            self.assertEqual(manifest['discipline'], item['discipline'])
            self.assertEqual(manifest['lifecycle'], 'planned')
            self.assertIsNone(manifest['oracle'])
            self.assertEqual(manifest['positive_controls'], [])
            self.assertEqual(manifest['variants'], [])
            self.assertEqual(manifest['evidence'], [])

if __name__ == '__main__':
    unittest.main()
