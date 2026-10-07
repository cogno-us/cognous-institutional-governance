"""Read-only hash and deterministic replay check of the authorization/effect archive."""
import hashlib
import json
from pathlib import Path
from run_authorization_effect import execute, ARMS

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT/'results/2026-10-05-authorization-effect-v1'


def main():
    manifest = json.loads((ARCHIVE/'manifest.json').read_text())
    for name, want in manifest['sha256'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != want:
            raise ValueError('Hash mismatch: ' + name)
    archived = json.loads((ARCHIVE/'results.json').read_text())
    replay = execute()
    for key in ('cases', 'results', 'summary', 'input_sha256'):
        if archived[key] != replay[key]:
            raise ValueError('Replay mismatch: ' + key)
    if len(archived['cases']) != 20 or len(archived['results']) != 60:
        raise ValueError('Count mismatch')
    for number in range(1, 11):
        proposal = f'AE{number:02}'
        pair = [c for c in archived['cases'] if c['proposal'] == proposal]
        if len(pair) != 2 or {c['variant'] for c in pair} != {'primary', 'positive'}:
            raise ValueError('Pair missing: ' + proposal)
    if len({c['id'] for c in archived['cases']}) != 20:
        raise ValueError('Duplicate fixture IDs')
    if any(not r['oracle_satisfied'] for r in archived['results'] if r['arm'] != ARMS[0]):
        raise ValueError('Guarded oracle failure')
    if archived['execution_status'] != 'EXECUTED_SYNTHETIC' or archived['review_status'] != 'NOT_INDEPENDENTLY_REVIEWED':
        raise ValueError('Incorrect evidence status')
    print('PASS: authorization/effect hashes, 10 paired proposals, 20 fixtures, 60 observations; guarded oracles satisfied')


if __name__ == '__main__':
    main()
