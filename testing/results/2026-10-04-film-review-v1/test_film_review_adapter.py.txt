"""Mechanics checks only; no institutional or human-review conclusions."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('film_adapter',ROOT/'testing/harness/run_film_review.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class FilmAdapterTests(unittest.TestCase):
    def setUp(self):
        self.cases={c['id']:c for c in json.loads(module.INPUT.read_text())}

    def test_all_guarded_effect_oracles(self):
        for c in self.cases.values():
            for arm in ('conventional','alvorada_inspired'):
                with self.subTest(case=c['id'],arm=arm):
                    self.assertTrue(module.run(c,arm)['oracle_satisfied'])

    def test_expected_values_cannot_change_actual_effect(self):
        original=self.cases['TB08-primary']; altered=copy.deepcopy(original)
        altered['expected']['account_state']='invented result'
        before=module.run(original,'conventional');after=module.run(altered,'conventional')
        self.assertEqual(before['observed'],after['observed'])
        self.assertFalse(after['oracle_satisfied'])

    def test_nominal_publishers_cannot_hide_common_suggestion(self):
        c=copy.deepcopy(self.cases['TB03-primary'])
        for index,e in enumerate(c['inputs']['evidence']):e['origin']=f'new-publisher-{index}'
        result=module.run(c,'conventional')
        self.assertEqual(result['observed']['outcome'],'HOLD')
        self.assertEqual(result['observed']['account_state'],'clear')

    def test_reconstruction_is_not_observation_even_at_high_quality(self):
        c=copy.deepcopy(self.cases['TB05-primary'])
        for e in c['inputs']['evidence']:e['quality']=100
        self.assertEqual(module.run(c,'conventional')['observed']['outcome'],'HOLD')

    def test_history_protection_has_actual_database_evidence(self):
        c=self.cases['TB10-primary']
        guarded=module.run(c,'conventional');toy=module.run(c,'permissive_toy')
        self.assertEqual(guarded['observed']['history_rows'],1)
        self.assertIn('denied',guarded['sqlite_deletion_error'])
        self.assertEqual(toy['observed']['history_rows'],0)

    def test_remedy_updates_both_actual_tables(self):
        c=self.cases['TB08-primary'];a=module.run(c,'conventional');b=module.run(c,'permissive_toy')
        self.assertEqual((a['observed']['account_state'],a['observed']['downstream_state']),('clear','clear'))
        self.assertEqual((b['observed']['account_state'],b['observed']['downstream_state']),('restricted','restricted'))

    def test_disclosed_incentive_does_not_trigger_blanket_rejection(self):
        self.assertEqual(module.run(self.cases['TB04-positive'],'conventional')['observed']['outcome'],'ALLOW')

    def test_invalid_input_fails_instead_of_silently_passing(self):
        c=copy.deepcopy(self.cases['TB05-primary']);c['inputs']['evidence'][0]['kind']='unknown_type'
        with self.assertRaises(ValueError):module.run(c,'conventional')

if __name__=='__main__':unittest.main()
