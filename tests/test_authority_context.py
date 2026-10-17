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
        self.assertEqual(result['fixture_count'], 51)
        self.assertEqual(len({row['id'] for row in result['results']}), 51)
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

    def test_delay_limit_is_required_and_has_no_approving_miss_response(self):
        from authority_context import TIER_DELAY_CEILING_SECONDS, schema_errors, SCHEMA_PATH
        schema = json.loads(SCHEMA_PATH.read_text())
        consequence = schema['properties']['requirement']['properties']['consequence']
        self.assertIn('delay_limit', consequence['required'])
        misses = set(consequence['properties']['delay_limit']['properties']['on_miss']['enum'])
        self.assertEqual(misses, {'escalate_to_alternate_reviewer', 'defer_with_reason', 'narrower_authorized_action'})
        for tier in TIER_DELAY_CEILING_SECONDS:
            base = self._base('routine')
            base['context']['requirement']['consequence']['tier'] = tier
            with self.subTest(tier=tier, case='declared'):
                self.assertEqual(schema_errors(base['context']), [])
            del base['context']['requirement']['consequence']['delay_limit']
            with self.subTest(tier=tier, case='undeclared'):
                self.assertTrue(any('delay_limit' in e for e in schema_errors(base['context'])))
        for miss in ('approve', 'auto_approve', 'proceed', 'default_to_act', 'ignore', None):
            base = self._base('routine')
            base['context']['requirement']['consequence']['delay_limit']['on_miss'] = miss
            with self.subTest(on_miss=miss):
                self.assertTrue(schema_errors(base['context']))
        for bad in (0, -1, 1.5, '3600', True):
            base = self._base('routine')
            base['context']['requirement']['consequence']['delay_limit']['max_pending_seconds'] = bad
            with self.subTest(max_pending_seconds=bad):
                self.assertTrue(schema_errors(base['context']))

    def test_delay_limit_ceiling_is_enforced_for_every_tier_boundary(self):
        from authority_context import TIER_DELAY_CEILING_SECONDS, reference_errors
        for tier, ceiling in TIER_DELAY_CEILING_SECONDS.items():
            for seconds, flagged in ((1, False), (ceiling - 1, False), (ceiling, False), (ceiling + 1, True)):
                case = self._base('routine')
                case['context']['requirement']['consequence'].update(tier=tier)
                case['context']['requirement']['consequence']['delay_limit']['max_pending_seconds'] = seconds
                with self.subTest(tier=tier, seconds=seconds):
                    errors = reference_errors(case['context'], case['snapshot'], case['action'], case['now'])
                    self.assertEqual('delay_limit_exceeds_tier_ceiling' in errors, flagged, errors)

    def test_a_delay_limit_never_authorizes_the_act(self):
        """Declaring or tightening a limit cannot repair a failing context, and the check has no time-based approval path."""
        from authority_context import reference_errors
        case = self._base('higher-consequence')
        case['context']['grant']['approval_refs'] = []
        case['context']['requirement']['consequence']['delay_limit']['max_pending_seconds'] = 1
        errors = reference_errors(case['context'], case['snapshot'], case['action'], case['now'])
        self.assertIn('missing_or_invalid_approval', errors)
        self.assertNotIn('delay_limit_exceeds_tier_ceiling', errors)

    def test_shipped_examples_declare_a_valid_delay_limit_within_their_tier(self):
        from authority_context import TIER_DELAY_CEILING_SECONDS, schema_errors
        examples = Path(__file__).resolve().parents[1] / 'process/implementation/public-stack-v0.1/examples'
        for name in ('routine', 'higher-consequence', 'requirement-only'):
            context = json.loads((examples / f'{name}.json').read_text())
            consequence = context['requirement']['consequence']
            with self.subTest(example=name):
                self.assertEqual(schema_errors(context), [])
                self.assertLessEqual(consequence['delay_limit']['max_pending_seconds'], TIER_DELAY_CEILING_SECONDS[consequence['tier']])
