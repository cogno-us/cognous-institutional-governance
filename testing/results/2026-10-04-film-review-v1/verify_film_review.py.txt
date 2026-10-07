"""Verify the film subtest snapshot and deterministic effects, without writes."""
import hashlib
import json
from pathlib import Path
from run_film_review import execute

ROOT=Path(__file__).resolve().parents[1]
ARCHIVE=ROOT/'results/2026-10-04-film-review-v1'

def main():
    manifest=json.loads((ARCHIVE/'manifest.json').read_text())
    for name,want in manifest['sha256'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=want:
            raise ValueError('Hash mismatch: '+name)
    archived=json.loads((ARCHIVE/'results.json').read_text()); replay=execute()
    for key in ('cases','results','summary','input_sha256'):
        if archived[key]!=replay[key]:raise ValueError('Replay mismatch: '+key)
    cases=archived['cases']; observations=archived['results']
    expected_proposals={f'FW{i:02}' for i in range(1,12)}|{f'TB{i:02}' for i in range(1,11)}
    if {c['proposal'] for c in cases}!=expected_proposals:raise ValueError('Missing proposal mapping')
    if len(cases)!=42 or len(observations)!=126:raise ValueError('Invalid counts')
    if len({c['id'] for c in cases})!=42:raise ValueError('Duplicate fixture IDs')
    for proposal in expected_proposals:
        if {c['variant'] for c in cases if c['proposal']==proposal}!={'primary','positive'}:
            raise ValueError('Missing primary/positive pair')
    for family in ('FOG_OF_WAR','THIN_BLUE_LINE'):
        text=(ROOT/f'battery/{family}.md').read_text()
        for proposal in expected_proposals:
            if proposal.startswith('FW' if family=='FOG_OF_WAR' else 'TB') and f'## {proposal}:' not in text:
                raise ValueError('Unresolved proposal heading')
    if any(not x['oracle_satisfied'] for x in observations if x['arm']!='permissive_toy'):
        raise ValueError('Guarded oracle failure')
    if archived['execution_status']!='EXECUTED_SYNTHETIC':raise ValueError('Invalid status')
    print('PASS: film hashes, 21 mapped proposals, 42 fixtures, 126 replayed observations; guarded oracles satisfied')

if __name__=='__main__':main()
