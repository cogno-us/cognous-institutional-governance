"""Synthetic mechanics for FW/TB proposals; no model or human adjudication."""
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
INPUT = ROOT / 'fixtures/film-review/cases.json'
ARMS = ('permissive_toy', 'conventional', 'alvorada_inspired')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def evaluate(inputs):
    """No expected outcomes or case IDs enter this policy function."""
    grant = inputs['grant']
    evidence = inputs['evidence']
    reasons = []
    if not grant['valid'] or inputs['action'] not in grant['actions']:
        reasons.append('outside_grant')
    if inputs['purpose'] != grant['purpose']:
        reasons.append('purpose_mismatch')
    if inputs['harm'] > grant['max_harm']:
        reasons.append('harm_bound_exceeded')
    if not inputs['review_access']:
        reasons.append('review_access_unavailable')
    visible = evidence if inputs['review_access'] else []
    support = [e for e in visible if e['kind'] == 'observation' and
               e['relation'] == 'supports' and e['quality'] >= grant['min_quality']]
    # Suggestions share an origin for this synthetic rule, even if publishers differ.
    origins = {e.get('suggestion_origin') or e['origin'] for e in support}
    if len(origins) < grant['min_origins']:
        reasons.append('insufficient_independent_observation')
    contradictions = [e['id'] for e in visible if e['relation'] == 'contradicts']
    incentives = [e['id'] for e in visible if e.get('incentive') and not e.get('disclosed')]
    if inputs['action'] == 'erase_history':
        outcome = 'HISTORY_PRESERVED'
    elif reasons:
        outcome = 'HOLD'
    elif contradictions or incentives:
        outcome = 'REVIEW'
    elif inputs['action'] == 'correct':
        outcome = 'CORRECTED'
    else:
        outcome = 'ALLOW'
    return outcome, dict(reasons=reasons, independent_origins=sorted(origins),
        contradictions=contradictions, undisclosed_incentives=incentives,
        unresolved=[e['id'] for e in visible if e['relation'] == 'unknown'],
        evidence_kinds={e['id']: e['kind'] for e in visible})

def run(case, arm):
    if arm not in ARMS:
        raise ValueError('Unknown arm')
    inputs = copy.deepcopy(case['inputs'])
    if inputs['action'] not in ('restrict', 'correct', 'erase_history'):
        raise ValueError('Unknown requested action')
    for e in inputs['evidence']:
        if e['kind'] not in ('observation', 'reported_statement', 'reconstruction'):
            raise ValueError('Unknown evidence kind')
        if e['relation'] not in ('supports', 'contradicts', 'unknown'):
            raise ValueError('Unknown evidence relation')
    db = sqlite3.connect(':memory:')
    try:
        db.executescript('CREATE TABLE accounts(id INTEGER PRIMARY KEY, status TEXT);'
            'CREATE TABLE downstream(id INTEGER PRIMARY KEY, status TEXT);'
            'CREATE TABLE history(id INTEGER PRIMARY KEY, note TEXT);')
        db.execute('INSERT INTO accounts VALUES(1,?)', (inputs['initial_state'],))
        db.execute('INSERT INTO downstream VALUES(1,?)', (inputs['initial_state'],))
        db.execute("INSERT INTO history VALUES(1,'prior decision and dissent')")
        db.commit()
        guarded = arm != 'permissive_toy'
        if guarded:
            db.executescript("CREATE TRIGGER retain_history BEFORE DELETE ON history "
                "BEGIN SELECT RAISE(ABORT,'history deletion denied'); END;")
            outcome, detail = evaluate(inputs)
        else:
            outcome = {'restrict': 'ALLOW', 'correct': 'SUMMARY_ONLY',
                       'erase_history': 'HISTORY_ERASED'}[inputs['action']]
            detail = {'reasons': [], 'independent_origins': [], 'contradictions': [],
                'undisclosed_incentives': [], 'unresolved': [], 'evidence_kinds': {}}
        deletion_error = None
        if inputs['action'] == 'erase_history':
            try:
                db.execute('DELETE FROM history')
            except sqlite3.IntegrityError as err:
                deletion_error = str(err)
        elif outcome == 'ALLOW':
            db.execute("UPDATE accounts SET status='restricted'")
            db.execute("UPDATE downstream SET status='restricted'")
        elif outcome == 'CORRECTED':
            db.execute("UPDATE accounts SET status='clear'")
            db.execute("UPDATE downstream SET status='clear'")
        db.commit()
        actual = dict(outcome=outcome,
            account_state=db.execute('SELECT status FROM accounts').fetchone()[0],
            downstream_state=db.execute('SELECT status FROM downstream').fetchone()[0],
            history_rows=db.execute('SELECT COUNT(*) FROM history').fetchone()[0],
            contradiction_count=len(detail['contradictions']),
            unresolved_count=len(detail['unresolved']))
        # Oracles run AFTER effects; expected data is never passed to evaluate().
        mismatches = {key: dict(expected=val, actual=actual[key])
            for key, val in case['expected'].items() if actual[key] != val}
        record = dict(decision=outcome, **detail)
        if arm == 'alvorada_inspired':
            record.update(authority_source='invented fixture grant',
                review_path='simulated queue; no human reviewer',
                continuation='pending review' if outcome in ('REVIEW','HOLD') else 'bounded fixture action',
                scope='single synthetic account',
                supersession='prior history retained' if actual['history_rows'] else 'history absent')
        return dict(id=case['id'], proposal=case['proposal'], variant=case['variant'],
            arm=arm, observed=actual, expected=case['expected'],
            oracle_satisfied=not mismatches, mismatches=mismatches,
            sqlite_deletion_error=deletion_error, record=record)
    finally:
        db.close()

def execute():
    cases = json.loads(INPUT.read_text())
    ids = [c['id'] for c in cases]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate case IDs')
    results = [run(c, arm) for arm in ARMS for c in cases]
    summary = {arm: dict(runs=sum(x['arm']==arm for x in results),
        oracles_satisfied=sum(x['arm']==arm and x['oracle_satisfied'] for x in results),
        positive_variants_satisfied=sum(x['arm']==arm and x['variant']=='positive' and x['oracle_satisfied'] for x in results))
        for arm in ARMS}
    commit = subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip()
    dirty = bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip())
    return dict(schema_version=1, execution_status='EXECUTED_SYNTHETIC',
        review_status='NOT_INDEPENDENTLY_REVIEWED',
        executed_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
        repository_commit=commit, working_tree_dirty=dirty,
        environment=dict(python=platform.python_version(),sqlite=sqlite3.sqlite_version),
        input_sha256={str(p.relative_to(ROOT)):sha(p) for p in (INPUT,Path(__file__))},
        limitations=['No LLM, human adjudication, real identity or institutional independence',
            'Authored evidence relations, quality, dependencies, grants and oracles',
            'Conventional and Alvorada-inspired effect policies are identical',
            'One Python process and one SQLite connection per case control all state',
            'Permissive toy is a negative control, not an observed organizational baseline',
            'Narrow subtests do not execute full operational FW/TB exercises'],
        cases=cases, results=results, summary=summary)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path)
    args=p.parse_args()
    out=args.output or ROOT/'runs'/('film-'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    if (ROOT/'results').resolve() in out.resolve().parents or out.resolve()==(ROOT/'results').resolve():
        p.error('Use a new directory outside archived results')
    out.mkdir(parents=True,exist_ok=False)
    bundle=execute()
    (out/'results.json').write_text(json.dumps(bundle,indent=2)+'\n')
    print(json.dumps(bundle['summary'],indent=2))
    print('Raw results:',out/'results.json')
    return int(any(not x['oracle_satisfied'] for x in bundle['results'] if x['arm']!='permissive_toy'))

if __name__=='__main__':
    raise SystemExit(main())
