"""Schema generations of the proposed Authority Context: 0.1.0 (no delay limit) and 0.2.0 (delay limit required).

Each generation is validated against its own versioned schema file. Unsupported or missing versions are refused.
"""
import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'testing/harness'))
PROFILE = ROOT / 'process/implementation/public-stack-v0.1'
BASES = json.loads((ROOT / 'testing/fixtures/authority-context/bases.json').read_text())


def base(name):
    return copy.deepcopy(BASES[name])


def as_0_1_0(case):
    """The same context as a 0.1.0 declaration: no delay limit. The requirement digest changes with it, so the
    synthetic trusted binding is recomputed for the 0.1.0 form."""
    from authority_context import binding
    context = case['context']
    context['schema_version'] = '0.1.0'
    del context['requirement']['consequence']['delay_limit']
    case['snapshot']['requirement_bindings'][context['requirement']['requirement_id']] = binding(
        {k: context[k] for k in ('institution', 'accountable_human_role', 'requirement', 'conflicts')})
    return case


@unittest.skipUnless(importlib.util.find_spec('jsonschema'), 'install testing/harness/requirements-authority.txt')
class AuthorityContextVersionTests(unittest.TestCase):
    def test_both_schema_generations_exist_as_versioned_files(self):
        old = json.loads((PROFILE / 'authority-context.0.1.0.schema.json').read_text())
        new = json.loads((PROFILE / 'authority-context.schema.json').read_text())
        self.assertEqual(old['$id'], 'urn:cognous:alvorada:authority-context:0.1.0')
        self.assertEqual(new['$id'], 'urn:cognous:alvorada:authority-context:0.2.0')
        self.assertEqual(old['properties']['schema_version'], {'const': '0.1.0'})
        self.assertEqual(new['properties']['schema_version'], {'const': '0.2.0'})
        old_consequence = old['properties']['requirement']['properties']['consequence']
        new_consequence = new['properties']['requirement']['properties']['consequence']
        self.assertNotIn('delay_limit', old_consequence['properties'])
        self.assertNotIn('delay_limit', old_consequence['required'])
        self.assertIn('delay_limit', new_consequence['required'])

    def test_each_generation_accepts_its_own_valid_context(self):
        from authority_context import schema_errors
        for name in ('routine', 'higher-consequence', 'delegation'):
            with self.subTest(base=name, version='0.2.0'):
                self.assertEqual(schema_errors(base(name)['context']), [])
            with self.subTest(base=name, version='0.1.0'):
                self.assertEqual(schema_errors(as_0_1_0(base(name))['context']), [])

    def test_generations_do_not_cross(self):
        from authority_context import schema_errors
        undeclared = base('routine')
        del undeclared['context']['requirement']['consequence']['delay_limit']
        self.assertTrue(schema_errors(undeclared['context']), 'a 0.2.0 context without a delay limit must be refused')
        declared = as_0_1_0(base('routine'))
        declared['context']['requirement']['consequence']['delay_limit'] = {'max_pending_seconds': 3600, 'on_miss': 'defer_with_reason'}
        self.assertTrue(schema_errors(declared['context']), 'a 0.1.0 context cannot carry a member its schema does not define')

    def test_unsupported_or_missing_versions_are_refused_not_raised(self):
        from authority_context import schema_errors
        for value in ('0.3.0', '0.1', '', None, 1, ['0.2.0']):
            with self.subTest(version=value):
                case = base('routine')
                case['context']['schema_version'] = value
                errors = schema_errors(case['context'])
                self.assertTrue(errors)
                self.assertTrue(all(isinstance(e, str) for e in errors))
        missing = base('routine')
        del missing['context']['schema_version']
        self.assertTrue(schema_errors(missing['context']))
        self.assertTrue(schema_errors([]))

    def test_reference_check_handles_a_0_1_0_context_without_a_delay_limit(self):
        from authority_context import reference_errors, schema_errors
        for name in ('routine', 'higher-consequence'):
            case = as_0_1_0(base(name))
            self.assertEqual(schema_errors(case['context']), [])
            errors = reference_errors(case['context'], case['snapshot'], case['action'], case['now'])
            with self.subTest(base=name):
                self.assertNotIn('delay_limit_exceeds_tier_ceiling', errors)
            reference = reference_errors(base(name)['context'], base(name)['snapshot'], base(name)['action'], base(name)['now'])
            self.assertEqual(errors, reference)

    def test_a_0_1_0_context_is_not_trusted_under_the_0_2_0_binding(self):
        from authority_context import reference_errors
        case = base('routine')
        stale = as_0_1_0(copy.deepcopy(case))
        stale['snapshot'] = case['snapshot']
        errors = reference_errors(stale['context'], stale['snapshot'], stale['action'], stale['now'])
        self.assertIn('untrusted_requirement_binding', errors)

    def test_delay_limit_ceiling_still_applies_to_0_2_0(self):
        from authority_context import TIER_DELAY_CEILING_SECONDS, reference_errors
        case = base('routine')
        tier = case['context']['requirement']['consequence']['tier']
        case['context']['requirement']['consequence']['delay_limit']['max_pending_seconds'] = TIER_DELAY_CEILING_SECONDS[tier] + 1
        self.assertIn('delay_limit_exceeds_tier_ceiling', reference_errors(case['context'], case['snapshot'], case['action'], case['now']))

    def test_delegation_parent_of_either_generation_is_checked_against_its_own_schema(self):
        from authority_context import reference_errors
        case = base('delegation')
        parent = case['snapshot']['parents'][case['context']['grant']['delegation']['parent_grant_id']]
        self.assertEqual(parent['schema_version'], '0.2.0')
        parent['schema_version'] = '0.1.0'
        del parent['requirement']['consequence']['delay_limit']
        errors = reference_errors(case['context'], case['snapshot'], case['action'], case['now'])
        self.assertNotIn('missing_or_malformed_parent', errors)
        parent['schema_version'] = '0.9.9'
        errors = reference_errors(case['context'], case['snapshot'], case['action'], case['now'])
        self.assertIn('missing_or_malformed_parent', errors)

    def test_review_marker_and_declaration_only_note_are_present(self):
        spec = ' '.join((PROFILE / 'AUTHORITY_CONTEXT.md').read_text(encoding='utf-8').split())
        for needed in ('REVIEW (owner):', '0.2.0', 'declaration only', 'no default delay'):
            with self.subTest(needed=needed):
                self.assertIn(needed, spec)


if __name__ == '__main__':
    unittest.main()
