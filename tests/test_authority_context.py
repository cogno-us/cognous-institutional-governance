"""Optional third-party schema suite. Run the dedicated harness to require it."""
import importlib.util
import json
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

    def _base(self, name):
        import copy
        bases = json.loads((Path(__file__).resolve().parents[1] / 'testing/fixtures/authority-context/bases.json').read_text())
        return copy.deepcopy(bases[name])

    def test_contained_rejects_non_finite_amounts(self):
        from authority_context import contained
        def perm(amount):
            return [{'action': 'refund', 'targets': ['t'], 'data_scopes': ['d'], 'max_amount': amount, 'unit': 'USD', 'max_effects': 1}]
        for value in (float('nan'), float('inf'), float('-inf')):
            with self.subTest(value=value):
                self.assertFalse(contained(perm(10), perm(value)))
                self.assertFalse(contained(perm(value), perm(25)))
                self.assertFalse(contained(perm(value), perm(value)))
        self.assertTrue(contained(perm(10), perm(25)))

    def test_non_finite_grant_or_parent_amount_is_refused(self):
        from authority_context import reference_errors
        for value in (float('nan'), float('inf'), float('-inf')):
            with self.subTest(side='grant', value=value):
                case = self._base('routine')
                case['context']['grant']['permissions'][0]['max_amount'] = value
                errors = reference_errors(case['context'], case['snapshot'], case['action'], case['now'])
                self.assertIn('grant_exceeds_requirement', errors)
            with self.subTest(side='parent', value=value):
                case = self._base('delegation')
                parent = case['snapshot']['parents'][case['context']['grant']['delegation']['parent_grant_id']]
                parent['grant']['permissions'][0]['max_amount'] = value
                errors = reference_errors(case['context'], case['snapshot'], case['action'], case['now'])
                # -inf already fails the parent schema (minimum 0); NaN/+inf pass it.
                self.assertTrue({'child_exceeds_parent', 'missing_or_malformed_parent'} & set(errors), errors)

    def test_non_finite_requirement_amount_refused_not_raised(self):
        from authority_context import reference_errors
        for value in (float('nan'), float('inf'), float('-inf')):
            with self.subTest(value=value):
                case = self._base('routine')
                case['context']['requirement']['permissions'][0]['max_amount'] = value
                errors = reference_errors(case['context'], case['snapshot'], case['action'], case['now'])
                self.assertEqual(errors, ['non_finite_value'])
