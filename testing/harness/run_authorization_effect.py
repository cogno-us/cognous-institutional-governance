"""Deterministic authorization/effect mechanics; not a production runtime or ODES verifier."""
import argparse
import copy
import datetime as dt
import hashlib
import json
import platform
import sqlite3
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'fixtures/authorization-effect/cases.json'
ARMS = ('authorization_only_toy', 'conventional', 'alvorada_inspired')
REQUIRED = {'decision_id', 'effect_id', 'target', 'policy', 'action', 'grant_id'}


def eligibility(state, binding, now):
    """Only represented state, binding and logical time enter; no case IDs/oracles."""
    reasons = []
    if not state['grant_valid'] or now >= state['grant_expires']:
        reasons.append('grant_invalid_or_expired')
    for key in ('grant_id', 'target', 'policy', 'action'):
        if state[key] != binding[key]:
            reasons.append(key + '_changed')
    if not state['observer_available'] or state['required_state'] != 'KNOWN':
        reasons.append('required_condition_unknown')
    if now < state['evidence_observed_at'] or now >= state['evidence_expires']:
        reasons.append('critical_evidence_not_current')
    if reasons:
        return 'HOLD', reasons
    if state['conflict']:
        return 'REVIEW', ['critical_evidence_conflict']
    return 'ALLOW', []


def run(inputs, arm):
    """SQLite effects are real local writes. All authority/evidence facts are invented."""
    if arm not in ARMS:
        raise ValueError('Unknown arm')
    binding = copy.deepcopy(inputs['binding'])
    if set(binding) != REQUIRED or any(not isinstance(x, str) or not x for x in binding.values()):
        raise ValueError('Malformed binding')
    state = copy.deepcopy(inputs['initial_state'])
    allowed = {'grant_valid', 'grant_expires', 'grant_id', 'target', 'policy', 'action',
               'observer_available', 'required_state', 'evidence_observed_at',
               'evidence_expires', 'conflict', 'optional_state'}
    if set(state) != allowed or state['required_state'] not in ('KNOWN', 'UNKNOWN'):
        raise ValueError('Malformed represented state')
    if state['optional_state'] not in ('KNOWN', 'UNKNOWN'):
        raise ValueError('Malformed optional state')
    if any(type(state[k]) is not bool for k in ('grant_valid', 'observer_available', 'conflict')):
        raise ValueError('Malformed represented boolean')
    if any(type(state[k]) is not int for k in ('grant_expires', 'evidence_observed_at', 'evidence_expires')):
        raise ValueError('Malformed logical time')
    for changes in (inputs['before_check'], inputs['after_check']):
        if not set(changes) <= allowed:
            raise ValueError('Unknown change field')
    if any(type(inputs[k]) is not bool for k in ('retry', 'post_observer_available', 'verifier_available')):
        raise ValueError('Malformed observation/retry flag')
    if type(inputs['first_parts']) is not int or inputs['first_parts'] not in (1, 2):
        raise ValueError('Invalid partial delivery')
    guarded = arm != 'authorization_only_toy'
    db = sqlite3.connect(':memory:')
    events = []
    attempts = []
    reasons = []
    initial, reasons = eligibility(state, binding, 0)
    if initial != 'ALLOW':
        db.close()
        raise ValueError('Fixture must start with valid authorization')
    try:
        db.execute('CREATE TABLE world(revision INTEGER, state TEXT)')
        db.execute('INSERT INTO world VALUES(0,?)', (json.dumps(state),))
        constraint = ', UNIQUE(effect_id, part)' if guarded else ''
        db.execute('CREATE TABLE deliveries(effect_id TEXT, part INTEGER, target TEXT, policy TEXT, action TEXT' + constraint + ')')
        db.commit()
        events.append(dict(stage='AUTHORIZED', decision_id=binding['decision_id'],
                           effect_id=binding['effect_id'], logical_time=0))

        def mutate(changes):
            revision, raw = db.execute('SELECT revision,state FROM world').fetchone()
            current = json.loads(raw)
            current.update(changes)
            # Reuse input validation on changed states without recursion through effects.
            if current['required_state'] not in ('KNOWN', 'UNKNOWN') or current['optional_state'] not in ('KNOWN', 'UNKNOWN'):
                raise ValueError('Malformed changed evidence state')
            if any(type(current[k]) is not bool for k in ('grant_valid', 'observer_available', 'conflict')):
                raise ValueError('Malformed changed boolean')
            if any(type(current[k]) is not int for k in ('grant_expires', 'evidence_observed_at', 'evidence_expires')):
                raise ValueError('Malformed changed logical time')
            db.execute('UPDATE world SET revision=?, state=?', (revision + bool(changes), json.dumps(current)))
            db.commit()

        mutate(inputs['before_check'])
        outcome = 'ALLOW'
        observed_parts = None
        verified = False
        for attempt_index in range(1, 3 if inputs['retry'] else 2):
            if attempt_index == 2 and guarded and observed_parts is None:
                events.append(dict(stage='RETRY_DEFERRED', effect_id=binding['effect_id'],
                                   reason='authoritative_observation_unknown'))
                break
            if attempt_index == 2 and guarded and observed_parts == 2:
                events.append(dict(stage='RETRY_NOT_NEEDED', effect_id=binding['effect_id']))
                break
            attempt_id = binding['effect_id'] + ':attempt-' + str(attempt_index)
            attempts.append(attempt_id)
            check_time = 10 + (attempt_index - 1) * 2
            _, raw = db.execute('SELECT revision,state FROM world').fetchone()
            snapshot = json.loads(raw)
            outcome, reasons = eligibility(snapshot, binding, check_time) if guarded else ('ALLOW', [])
            events.append(dict(stage='PRE_EFFECT_CHECK', effect_id=binding['effect_id'],
                               attempt_id=attempt_id, outcome=outcome, logical_time=check_time))
            if outcome != 'ALLOW':
                break
            if attempt_index == 1:
                mutate(inputs['after_check'])
            # Commit check and effect share this single connection's serialized transaction.
            db.execute('BEGIN IMMEDIATE')
            revision, raw = db.execute('SELECT revision,state FROM world').fetchone()
            current = json.loads(raw)
            outcome, reasons = eligibility(current, binding, check_time + 1) if guarded else ('ALLOW', [])
            if outcome != 'ALLOW':
                db.rollback()
                events.append(dict(stage='COMMIT_DENIED', effect_id=binding['effect_id'],
                                   attempt_id=attempt_id, outcome=outcome, reasons=reasons))
                break
            parts = inputs['first_parts'] if attempt_index == 1 else 2
            for part in range(1, parts + 1):
                if guarded:
                    db.execute('INSERT OR IGNORE INTO deliveries VALUES(?,?,?,?,?)',
                               (binding['effect_id'], part, current['target'], current['policy'], current['action']))
                else:
                    db.execute('INSERT INTO deliveries VALUES(?,?,?,?,?)',
                               (binding['effect_id'], part, current['target'], current['policy'], current['action']))
            db.commit()
            events.append(dict(stage='EXECUTED', effect_id=binding['effect_id'],
                               attempt_id=attempt_id, revision=revision, logical_time=check_time + 1))
            # Observer has read-only access by API; unavailable observation never returns invented state.
            if inputs['post_observer_available']:
                observed_parts = observe_only(db, binding['effect_id'])
                events.append(dict(stage='OBSERVED', effect_id=binding['effect_id'], parts=observed_parts))
                # Separate simulated verifier read; same process/DB, NOT institutional independence.
                verified = bool(inputs['verifier_available'] and observed_parts == 2 and
                                db.execute('SELECT COUNT(*) FROM deliveries').fetchone()[0] == 2 and
                                all(tuple(row) == (binding['target'], binding['policy'], binding['action'])
                                    for row in db.execute('SELECT target,policy,action FROM deliveries')))
                if verified:
                    events.append(dict(stage='VERIFIED_SYNTHETIC', effect_id=binding['effect_id']))
            else:
                observed_parts = None
                verified = False
                events.append(dict(stage='OBSERVATION_UNKNOWN', effect_id=binding['effect_id']))
        rows = db.execute('SELECT effect_id,part,target,policy,action FROM deliveries ORDER BY rowid').fetchall()
        if outcome == 'ALLOW':
            outcome = ('EXECUTED_UNCONFIRMED' if observed_parts is None else
                       'COMPLETE_VERIFIED' if verified else
                       'PARTIAL_OBSERVED' if observed_parts == 1 else 'COMPLETE_UNVERIFIED')
        observed = dict(outcome=outcome, executed_parts=len(rows),
                        unique_parts=len({row[:2] for row in rows}), duplicate_parts=len(rows)-len({row[:2] for row in rows}),
                        executed_targets=sorted({row[2] for row in rows}),
                        observed_parts=observed_parts, verified=verified, attempts=len(attempts),
                        observer_execution_authority=False)
        record = dict(binding=binding, attempts=attempts, events=events, reasons=reasons,
                      optional_state=current['optional_state'] if 'current' in locals() else snapshot['optional_state'],
                      evidence_envelope=dict(source='invented observer', subject=binding['effect_id'],
                         observed_at=json.loads(db.execute('SELECT state FROM world').fetchone()[0])['evidence_observed_at'],
                         expires_at=json.loads(db.execute('SELECT state FROM world').fetchone()[0])['evidence_expires'],
                         version=json.loads(db.execute('SELECT state FROM world').fetchone()[0])['policy'],
                         scope='synthetic two-part effect', dependencies=['invented world state'],
                         uncertainty='represented by explicit condition/observation states'))
        if arm == 'alvorada_inspired':
            record.update(authority_basis='invented fixture grant',
                          continuation='no blind retry while delivery unknown',
                          evidence_custody='one process; not independent',
                          institutional_verification='NOT ESTABLISHED')
        return dict(observed=observed, record=record)
    finally:
        db.close()


def observe_only(db, effect_id, requested_action='read'):
    """Observer API has no execution operation, including when the service is unavailable."""
    if requested_action != 'read':
        raise PermissionError('Observer cannot execute')
    return db.execute('SELECT COUNT(DISTINCT part) FROM deliveries WHERE effect_id=?', (effect_id,)).fetchone()[0]


def execute():
    cases = json.loads(INPUT.read_text())
    if len({c['id'] for c in cases}) != len(cases):
        raise ValueError('Duplicate case IDs')
    results = []
    for arm in ARMS:
        for case in cases:
            result = run(case['inputs'], arm)
            actual = result['observed']
            mismatch = {key: dict(expected=want, actual=actual[key]) for key, want in case['expected'].items()
                        if actual[key] != want}
            results.append(dict(id=case['id'], proposal=case['proposal'], variant=case['variant'],
                                arm=arm, **result, expected=case['expected'],
                                oracle_satisfied=not mismatch, mismatches=mismatch))
    summary = {arm: dict(runs=sum(r['arm']==arm for r in results),
                        oracles_satisfied=sum(r['arm']==arm and r['oracle_satisfied'] for r in results),
                        positive_satisfied=sum(r['arm']==arm and r['variant']=='positive' and r['oracle_satisfied'] for r in results))
               for arm in ARMS}
    paths = (INPUT, Path(__file__))
    return dict(schema_version=1, execution_status='EXECUTED_SYNTHETIC', review_status='NOT_INDEPENDENTLY_REVIEWED',
                executed_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
                repository_commit=subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
                working_tree_dirty=bool(subprocess.check_output(['git','status','--porcelain'], cwd=ROOT, text=True).strip()),
                environment=dict(python=platform.python_version(), sqlite=sqlite3.sqlite_version),
                input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
                limitations=['Invented grants, conditions, clocks, observations and oracles; no model or real actors',
                             'Single process and SQLite connection; no network or distributed commit guarantee',
                             'Same guarded controls in conventional and Alvorada-inspired arms',
                             'Observer API restriction is not a credential/process security boundary',
                             'Simulated separate verifier is not institutionally independent',
                             'No ODES schema/profile/cryptographic conformance or operational efficacy claim'],
                cases=cases, results=results, summary=summary)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    out = args.output or ROOT/'runs'/('authorization-effect-'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    if out.resolve() == (ROOT/'results').resolve() or (ROOT/'results').resolve() in out.resolve().parents:
        parser.error('Write outside immutable results; use a new directory')
    out.mkdir(parents=True, exist_ok=False)
    bundle = execute()
    (out/'results.json').write_text(json.dumps(bundle, indent=2)+'\n')
    print(json.dumps(bundle['summary'], indent=2))
    return int(any(not r['oracle_satisfied'] for r in bundle['results'] if r['arm'] != ARMS[0]))


if __name__ == '__main__':
    raise SystemExit(main())
