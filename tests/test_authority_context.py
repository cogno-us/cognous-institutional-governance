"""Optional third-party schema suite. Run the dedicated harness to require it."""
import importlib.util
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'testing/harness'))


@unittest.skipUnless(importlib.util.find_spec('jsonschema'), 'Install testing/harness/requirements-authority.txt and run dedicated harness')
class AuthorityContextTests(unittest.TestCase):
    def test_schema_and_semantic_fixture_oracles(self):
        from run_authority_context import execute
        result = execute()
        self.assertEqual(result['fixture_count'], 44)
        self.assertEqual(len({row['id'] for row in result['results']}), 44)
        for row in result['results']:
            with self.subTest(fixture=row['id']):
                self.assertTrue(row['oracle_satisfied'], row)
