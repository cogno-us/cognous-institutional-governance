"""Stdlib-only checks that the tier table, the machine-readable ceilings and the schema agree on per-tier delay limits."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'testing/harness'))

from authority_context import SCHEMA_PATH, TIER_DELAY_CEILING_SECONDS  # noqa: E402  (jsonschema is imported lazily there)

GUIDANCE = ROOT / 'process/PROPORTIONAL_GOVERNANCE.md'


def tier_table():
    rows = [[c.strip() for c in line.strip().strip('|').split('|')] for line in GUIDANCE.read_text(encoding='utf-8').splitlines() if line.startswith('|')]
    rows = [r for r in rows if not all(set(c) <= set('-: ') for c in r)]
    start = next(i for i, r in enumerate(rows) if r[0].lower() == 'tier')
    return rows[start], [r for r in rows[start + 1:] if re.match(r'T[0-4]\b', r[0])]


class TierDelayLimitAuthorityContextTests(unittest.TestCase):
    def test_every_tier_row_declares_a_delay_limit_in_the_last_column(self):
        header, tiers = tier_table()
        self.assertEqual([r[0][:2] for r in tiers], ['T0', 'T1', 'T2', 'T3', 'T4'])
        self.assertIn('delay limit', header[-1].lower())
        for row in tiers:
            with self.subTest(tier=row[0][:2]):
                self.assertEqual(len(row), len(header))
                self.assertRegex(row[-1], r'\([0-9,]+ s\)')

    def test_table_values_equal_the_machine_readable_ceilings(self):
        _, tiers = tier_table()
        documented = {r[0][:2]: int(re.search(r'\(([0-9,]+) s\)', r[-1]).group(1).replace(',', '')) for r in tiers}
        self.assertEqual(documented, TIER_DELAY_CEILING_SECONDS)

    def test_limits_rise_with_review_burden_and_t4_is_not_a_decision_deadline(self):
        values = [TIER_DELAY_CEILING_SECONDS[t] for t in ('T0', 'T1', 'T2', 'T3', 'T4')]
        self.assertEqual(values, sorted(set(values)))
        _, tiers = tier_table()
        self.assertRegex(tiers[4][-1], r'recorded disposition into the reserved process only')

    def test_guidance_states_that_expiry_is_never_authority_and_values_need_owner_confirmation(self):
        text = ' '.join(GUIDANCE.read_text(encoding='utf-8').split())
        section = text[text.index('### Delay limits'):text.index('### Safeguards against false low-risk classification')]
        for needed in ('owner to confirm', 'Not a license', 'never approves', 'There is no automatic-approval value', 'V.2', 'Not validated'):
            with self.subTest(needed=needed):
                self.assertIn(needed, section)

    def test_schema_miss_responses_match_the_documented_responses(self):
        schema = json.loads(SCHEMA_PATH.read_text())
        limit = schema['properties']['requirement']['properties']['consequence']['properties']['delay_limit']
        self.assertEqual(limit['additionalProperties'], False)
        enum = limit['properties']['on_miss']['enum']
        text = GUIDANCE.read_text(encoding='utf-8')
        for response in enum:
            with self.subTest(on_miss=response):
                self.assertIn(response, text)
        self.assertFalse([e for e in enum if re.search(r'approv|proceed|grant|auto', e)])

    def test_mapping_and_authority_context_spec_disclose_the_delay_limit_and_its_limits(self):
        profile = ROOT / 'process/implementation/public-stack-v0.1'
        spec = (profile / 'AUTHORITY_CONTEXT.md').read_text(encoding='utf-8')
        for needed in ('delay_limit', 'delay_limit_exceeds_tier_ceiling', 'measures no elapsed time'):
            with self.subTest(spec=needed):
                self.assertIn(needed, spec)
        mapping = next(line for line in (profile / 'MAPPING.md').read_text(encoding='utf-8').splitlines() if line.startswith('| Proportional guidance'))
        self.assertRegex(mapping, r'delay-limit ceilings \(proposed, owner to confirm\)')
        self.assertRegex(mapping, r'elapsed-time measurement and delay-miss handling unimplemented')


if __name__ == '__main__':
    unittest.main()
