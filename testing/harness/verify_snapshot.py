"""Check archived integrity, traceability, and deterministic replay without writes."""
import hashlib
import json
from pathlib import Path
from run_reference import execute

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / 'results/2026-10-03-reference-v1'

def main():
    manifest = json.loads((ARCHIVE/'manifest.json').read_text())
    for path, expected in manifest['sha256'].items():
        actual = hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError('Archive/input hash mismatch: '+path)
    archived = json.loads((ARCHIVE/'results.json').read_text())
    replay = json.loads(json.dumps(execute()))
    if (replay['cases'],replay['results'],replay['summary']) != (archived['cases'],archived['results'],archived['summary']):
        raise ValueError('Replay differs from archived effect observations')
    original = json.loads((ARCHIVE/'original-results.json').read_text())
    if (original['cases'],original['results'],original['summary']) != (archived['cases'],archived['results'],archived['summary']):
        raise ValueError('Integrated replay differs from original reference experiment')
    battery = json.loads((ROOT/'battery/battery.json').read_text())
    ids = [c['id'] for g in battery['groups'] for c in g['tests']] + [c['id'] for c in battery['lifecycle']]
    sources = json.loads((ROOT/'sources/incidents.json').read_text())
    source_ids = {s['id'] for s in sources}
    if len(ids)!=47 or len(set(ids))!=47:
        raise ValueError('Operational battery count or unique IDs invalid')
    if len(replay['cases'])!=24 or len(replay['results'])!=72:
        raise ValueError('Reference run count invalid')
    if not all(c['battery'] in ids for c in replay['cases']):
        raise ValueError('Unresolved battery mapping')
    for g in battery['groups']:
        if not g['sources'] or not set(g['sources']) <= source_ids:
            raise ValueError('Unresolved source mapping: '+g['id'])
        if not any(s['group']==g['id'] and s['kind']=='news_reporting' for s in sources):
            raise ValueError('Missing incident news source: '+g['id'])
        if g['status']!='PROPOSED' or any(c['status']!='PROPOSED' for c in g['tests']):
            raise ValueError('Synthetic execution incorrectly promoted operational status')
    if any(c['status']!='PROPOSED' for c in battery['lifecycle']):
        raise ValueError('Lifecycle status incorrectly promoted')
    print('PASS: hashes, original/integrated replay, 47 proposed cases, 24 fixtures, 72 observations, source mappings')

if __name__ == '__main__':
    main()
