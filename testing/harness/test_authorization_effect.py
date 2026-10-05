"""Boundary and mutation checks for the narrow synthetic adapter, not institutional tests."""
import copy
import json
import sqlite3
import unittest
from run_authorization_effect import INPUT, ARMS, run, execute, observe_only


class AuthorizationEffectTests(unittest.TestCase):
    def setUp(self):
        self.cases = json.loads(INPUT.read_text())
        self.inputs = copy.deepcopy(self.cases[1]['inputs'])

    def test_guarded_fixture_oracles(self):
        bundle = execute()
        self.assertEqual(len(bundle['results']), 60)
        self.assertTrue(all(r['oracle_satisfied'] for r in bundle['results'] if r['arm'] != ARMS[0]))

    def test_negative_control_exposes_missing_revalidation(self):
        self.inputs['before_check'] = {'grant_valid': False}
        self.assertEqual(run(self.inputs, ARMS[0])['observed']['executed_parts'], 2)
        self.assertEqual(run(self.inputs, ARMS[1])['observed']['executed_parts'], 0)

    def test_change_after_check_is_denied_at_commit(self):
        for change in ({'grant_valid': False}, {'target': 'other'}, {'policy': 'v2'}, {'action': 'other'}):
            with self.subTest(change=change):
                self.inputs['after_check'] = change
                result = run(self.inputs, ARMS[1])
                self.assertEqual(result['observed']['executed_parts'], 0)
                self.assertEqual(result['record']['events'][-1]['stage'], 'COMMIT_DENIED')

    def test_expiry_at_commit_and_future_observation(self):
        for change in ({'evidence_expires': 11}, {'grant_expires': 11}, {'evidence_observed_at': 12}):
            with self.subTest(change=change):
                self.inputs['after_check'] = change
                self.assertEqual(run(self.inputs, ARMS[1])['observed']['executed_parts'], 0)

    def test_unknown_is_obligation_specific(self):
        self.inputs['before_check'] = {'optional_state': 'UNKNOWN'}
        result = run(self.inputs, ARMS[1])
        self.assertTrue(result['observed']['verified'])
        self.assertEqual(result['record']['optional_state'], 'UNKNOWN')
        self.inputs['before_check'] = {'required_state': 'UNKNOWN'}
        self.assertEqual(run(self.inputs, ARMS[1])['observed']['executed_parts'], 0)

    def test_unknown_post_effect_cannot_trigger_blind_retry(self):
        self.inputs.update(post_observer_available=False, retry=True)
        observed = run(self.inputs, ARMS[1])['observed']
        self.assertIsNone(observed['observed_parts'])
        self.assertFalse(observed['verified'])
        self.assertEqual(observed['attempts'], 1)
        self.assertEqual(observed['executed_parts'], 2)

    def test_partial_retry_has_stable_effect_and_distinct_attempts(self):
        self.inputs.update(first_parts=1, retry=True)
        result = run(self.inputs, ARMS[1])
        self.assertEqual(result['observed']['duplicate_parts'], 0)
        self.assertEqual(result['observed']['executed_parts'], 2)
        self.assertEqual(len(set(result['record']['attempts'])), 2)
        self.assertTrue(all(e['effect_id'] == self.inputs['binding']['effect_id'] for e in result['record']['events']))

    def test_delivery_records_actual_changed_target(self):
        self.inputs['before_check'] = {'target': 'account-B'}
        toy = run(self.inputs, ARMS[0])['observed']
        self.assertEqual(toy['executed_targets'], ['account-B'])
        self.assertFalse(toy['verified'])
        self.assertEqual(run(self.inputs, ARMS[1])['observed']['executed_targets'], [])

    def test_observer_has_no_execution_operation(self):
        with sqlite3.connect(':memory:') as db:
            db.execute('CREATE TABLE deliveries(effect_id TEXT,part INTEGER)')
            with self.assertRaises(PermissionError):
                observe_only(db, 'effect-1', 'execute')
            self.assertEqual(observe_only(db, 'effect-1'), 0)

    def test_unavailable_verifier_is_not_verified(self):
        self.inputs['verifier_available'] = False
        observed = run(self.inputs, ARMS[1])['observed']
        self.assertEqual(observed['outcome'], 'COMPLETE_UNVERIFIED')
        self.assertFalse(observed['verified'])
        self.assertEqual(observed['observed_parts'], 2)

    def test_conflict_needs_review_not_vote_or_execution(self):
        self.inputs['before_check'] = {'conflict': True}
        observed = run(self.inputs, ARMS[1])['observed']
        self.assertEqual(observed['outcome'], 'REVIEW')
        self.assertEqual(observed['executed_parts'], 0)

    def test_expected_results_do_not_control_engine(self):
        changed = copy.deepcopy(self.cases[0])
        original = run(changed['inputs'], ARMS[1])
        changed['id'] = 'a misleading label'
        changed['expected']['executed_parts'] = 999
        self.assertEqual(run(changed['inputs'], ARMS[1]), original)

    def test_effect_controls_identical_in_guarded_arms(self):
        for case in self.cases:
            self.assertEqual(run(case['inputs'], ARMS[1])['observed'], run(case['inputs'], ARMS[2])['observed'])

    def test_malformed_flags_and_conditions_rejected(self):
        for key, bad in [('retry', 'false'), ('post_observer_available', None), ('first_parts', True)]:
            with self.subTest(key=key):
                inputs = copy.deepcopy(self.inputs)
                inputs[key] = bad
                with self.assertRaises(ValueError):
                    run(inputs, ARMS[1])
        self.inputs['before_check'] = {'required_state': 'CONFIDENT'}
        with self.assertRaises(ValueError):
            run(self.inputs, ARMS[1])


if __name__ == '__main__':
    unittest.main()
