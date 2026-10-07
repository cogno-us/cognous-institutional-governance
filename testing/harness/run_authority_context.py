"""Execute proposed Authority Context schema/reference fixtures, no effects."""
import copy
import json
from pathlib import Path
from authority_context import schema_errors, reference_errors


def execute():
    cases = json.loads((Path(__file__).resolve().parents[1] / 'fixtures/authority-context/cases.json').read_text())
    bases = json.loads((Path(__file__).resolve().parents[1] / 'fixtures/authority-context/bases.json').read_text())
    results = []
    for definition in cases:
        case = copy.deepcopy(bases[definition['base']])
        for patch in definition['patches']:
            target = case
            for part in patch['path'][:-1]:
                target = target[part]
            if patch['op'] == 'delete':
                del target[patch['path'][-1]]
            else:
                target[patch['path'][-1]] = patch['value']
        case.update({k: definition[k] for k in ('id', 'schema_valid', 'expected_errors')})
        structural = schema_errors(case['context'])
        semantic = reference_errors(case['context'], case['snapshot'], case['action'], case['now']) if not structural else None
        passed = (not structural) == case['schema_valid'] and (semantic is None or semantic == sorted(case['expected_errors']))
        results.append({'id':case['id'], 'schema_valid':not structural, 'reference_errors':semantic, 'oracle_satisfied':passed})
    return {'status':'EXECUTED_LOCAL_REFERENCE_CHECKS', 'runtime_enforcement':False, 'independently_reviewed':False, 'fixture_count':len(cases), 'passed':sum(x['oracle_satisfied'] for x in results), 'results':results}


if __name__ == '__main__':
    result = execute()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['passed'] == result['fixture_count'] else 1)
