"""Deterministic synthetic adapter comparison; not a model or operational trial."""
import argparse
import datetime
import hashlib
import json
import platform
import sqlite3
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / 'fixtures'
ARMS = ('baseline', 'conventional', 'alvorada_inspired')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(c, arm):
    guarded=arm!='baseline'
    connection=sqlite3.connect(':memory:')
    connection.execute('CREATE TABLE production(id INTEGER PRIMARY KEY, value TEXT)')
    connection.execute("INSERT INTO production VALUES(1,'synthetic record')")
    connection.commit()
    if c.get('action')=='restore':
        connection.execute('DELETE FROM production'); connection.commit()
    reasons=[]; sqlite_proof=None
    if guarded:
        for flag in ['conflict','missing','expired','revoked','version_changed','outage',
                     'wrong_proposition','wrong_quote','circular','challenged']:
            if c.get(flag): reasons.append(flag)
        if c['flow']=='agent' and c.get('action')=='delete':
            # All three tool adapters route to the same connection. Read-only
            # mode is set outside the simulated agent; no alternate credentials.
            connection.execute('PRAGMA query_only=ON')
            try:
                connection.execute('DELETE FROM production')
            except sqlite3.OperationalError as e:
                sqlite_proof=str(e); reasons.append('production_write_denied')
    if reasons:
        outcome='BLOCK'
    elif c['flow']=='policy':
        outcome='PENDING' if guarded and c.get('receipt') is False else 'ALLOW'
    elif c['flow']=='agent':
        action=c.get('action')
        if action=='delete':
            connection.execute('DELETE FROM production'); connection.commit(); outcome='ALLOW'
        elif action=='restore':
            # Independent backup fixture rather than the simulated agent's word.
            if guarded:
                backup=json.loads(FIXTURES.joinpath('backup_fixture.json').read_text())
                connection.executemany('INSERT INTO production VALUES(?,?)',backup)
                connection.commit(); outcome='RESTORED'
            else: outcome='NOT_ATTEMPTED'
        else: outcome='ALLOW'
    else: outcome='ALLOW'
    rows=connection.execute('SELECT * FROM production').fetchall()
    connection.close()
    if c['flow']=='agent' and c['expected']=='BLOCK':
        oracle_ok=outcome=='BLOCK' and rows==[(1,'synthetic record')]
    elif c['expected']=='RESTORED':
        oracle_ok=outcome=='RESTORED' and rows==[(1,'synthetic record')]
    else: oracle_ok=outcome==c['expected']
    record={'case':c['id'],'arm':arm,'outcome':outcome}
    if arm=='alvorada_inspired':
        record.update(scope='synthetic fixture only',authority_source='invented bounded grant',
            evidence='fixed case metadata and separate local backup fixture where applicable',reasons=reasons,
            dissent=['simulated material objection retained'],expiry='fixture bound',
            continuation='defer' if outcome in ['BLOCK','PENDING'] else 'bounded continuation')
    # Output files are separate from the production table but managed by this
    # same Python process. This does NOT establish organizational independence.
    return dict(case=c['id'],battery=c['battery'],arm=arm,expected=c['expected'],
        observed=outcome,oracle_satisfied=oracle_ok,production_rows=rows,
        sqlite_observation=sqlite_proof,record=record,record_field_count=len(record))


def execute():
    cases = json.loads((FIXTURES / 'cases.json').read_text())
    results = [run(c, a) for a in ARMS for c in cases]
    summary = {}
    for arm in ARMS:
        rr = [r for r in results if r['arm'] == arm]
        summary[arm] = dict(runs=len(rr), oracle_satisfied=sum(r['oracle_satisfied'] for r in rr),
            hazardous_effect_cases_blocked=sum(r['expected']=='BLOCK' and r['observed']=='BLOCK' for r in rr),
            legitimate_cases_allowed=sum(r['expected']=='ALLOW' and r['observed']=='ALLOW' for r in rr),
            total_record_fields=sum(r['record_field_count'] for r in rr))
    try:
        commit = subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip()
        dirty = bool(subprocess.check_output(['git','status','--porcelain'], cwd=ROOT, text=True).strip())
    except (OSError, subprocess.CalledProcessError):
        commit = None; dirty = None
    inputs = ['fixtures/cases.json','fixtures/backup_fixture.json','harness/run_reference.py']
    return dict(schema_version=1, executed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        study='deterministic synthetic reference adapter experiment',
        execution_status='EXECUTED_SYNTHETIC', review_status='NOT_INDEPENDENTLY_REVIEWED',
        repository_commit=commit, working_tree_dirty=dirty,
        environment=dict(python=platform.python_version(), sqlite=sqlite3.sqlite_version),
        input_sha256={p:digest(ROOT/p) for p in inputs},
        limitations=['No LLM or historical production replay','Invented authority and evidence fixtures',
            'Effect controls are identical in the two guarded arms','No independent human review',
            'Logical record separation only','No field efficacy or comparative institutional benefit established'],
        cases=cases, results=results, summary=summary)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='New output directory; existing directories are refused')
    args = parser.parse_args()
    output = args.output or ROOT/'runs'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    if output.resolve().is_relative_to((ROOT/'results').resolve()):
        parser.error('Archived results are immutable; write outside testing/results')
    output.mkdir(parents=True, exist_ok=False)
    bundle = execute()
    (output/'results.json').write_text(json.dumps(bundle, indent=2)+'\n')
    print(json.dumps(bundle['summary'], indent=2))
    print('Raw results:', output/'results.json')
    # Baseline mismatches are expected negative controls, not suite errors.
    return 0 if all(r['oracle_satisfied'] for r in bundle['results'] if r['arm']!='baseline') else 1

if __name__ == '__main__':
    raise SystemExit(main())
