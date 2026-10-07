"""Local reference checks only. No credentials, network, grants or effects.

The synthetic snapshot is assumed input, never authenticated by this module.
A satisfied result is NOT a runtime authorization decision.
"""
import math
import hashlib
import json
from datetime import datetime
from pathlib import Path

SCHEMA_PATH = Path(__file__).resolve().parents[2] / 'process/implementation/public-stack-v0.1/authority-context.schema.json'


def schema_errors(context):
    from jsonschema import Draft202012Validator, FormatChecker
    schema = json.loads(SCHEMA_PATH.read_text())
    Draft202012Validator.check_schema(schema)
    return sorted(error.message for error in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(context))


def timestamp(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def binding(action):
    return hashlib.sha256(json.dumps(action, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def contained(child, parent):
    """Exact action/unit, finite target/data sets and numeric attenuation only."""
    return all(any(c['action'] == p['action'] and c['unit'] == p['unit']
                   and set(c['targets']) <= set(p['targets'])
                   and set(c['data_scopes']) <= set(p['data_scopes'])
                   and c['max_amount'] <= p['max_amount']
                   and c['max_effects'] <= p['max_effects'] for p in parent) for c in child)


def reference_errors(context, snapshot, action, now, ancestors=()):
    """Reject unsupported/missing synthetic premises; never imply permission.

    Caller must schema-check first. Snapshot has explicit synthetic trust,
    policy, role, status, approval and evidence premises. No signature validation.
    """
    errors = []
    def check(condition, reason):
        if not condition:
            errors.append(reason)
    inst = context['institution']; req = context['requirement']; grant = context.get('grant')
    check(snapshot['requirement_bindings'].get(req['requirement_id']) == binding({k: context[k] for k in ('institution', 'accountable_human_role', 'requirement', 'conflicts')}), 'untrusted_requirement_binding')
    if any(type(action[k]) not in (int, float) or not math.isfinite(action[k]) or action[k] < 0 for k in ('amount', 'effects')) or type(action['effects']) is not int:
        return errors + ['invalid_action_limits']
    check(inst['authority_basis_ref'] in snapshot['authority_bases'], 'missing_authority_basis')
    check(context['accountable_human_role'] in snapshot['accountable_roles'], 'unbound_accountable_role')
    check(context['conflicts']['precedence_refs'] == snapshot['precedence_refs'], 'unresolved_precedence')
    check(not snapshot['unresolved_conflict'], 'conflicting_rules')
    check(inst['authority_mode'] == 'principle_inspired', 'unsupported_adoption_mode')
    check(context['change']['adoption_record_ref'] is None or context['change']['adoption_record_ref'] in snapshot['human_adoption_records'], 'unadopted_amendment')
    check(req['consequence']['tier'] != 'T4', 'reserved_constitutional_process')
    check(req['consequence']['tier'] not in ('T2', 'T3') or bool(req['approvals']), 'missing_reserved_approval_requirement')
    for obligation in req['evidence']:
        expected = 'hold_effect' if obligation['kind'] == 'authorization' and obligation['required'] else 'reconcile_no_blind_retry' if obligation['kind'] == 'post_effect' else 'preserve_if_other_basis_suffices'
        check(obligation['unknown_behavior'] == expected, 'invalid_unknown_semantics')
    if not grant:
        return errors + ['no_issued_grant']
    gid = grant['grant_id']
    if gid in ancestors:
        return errors + ['delegation_cycle']
    check(grant['requirement_id'] == req['requirement_id'], 'requirement_binding')
    check((grant['issuer'], grant['issuer_role'], grant['issuance_record_ref'], inst['institution_id'], inst['authority_domain']) in [tuple(x) for x in snapshot['issuers']], 'untrusted_issuer_mandate')
    check(grant['grantee'] == context['principal'] and grant['acting_identity'] == context['acting_identity'], 'identity_binding')
    check(timestamp(grant['issued_at']) <= timestamp(grant['not_before']) < timestamp(grant['expires_at']), 'invalid_validity_order')
    check(timestamp(grant['not_before']) <= timestamp(now) < timestamp(grant['expires_at']), 'expired_or_not_yet_valid')
    status = snapshot['statuses'].get(grant['status_ref'])
    if status is None:
        errors.append('missing_status')
    else:
        check(status['grant_id'] == gid and status['revision'] == grant['revision'] and status['state'] == 'active', 'inactive_or_changed_grant')
        age = (timestamp(now) - timestamp(status['observed_at'])).total_seconds()
        check(0 <= age <= snapshot['max_status_age_seconds'], 'stale_status')
    policies = {p['ref']:p['version'] for p in grant['policy_versions']}
    check(len(policies) == len(grant['policy_versions']), 'duplicate_policy_ref')
    check(all(snapshot['policies'].get(ref) == version for ref, version in policies.items()), 'policy_changed')
    check(all(policies.get(s['ref']) == s['version'] for s in req['governing_sources'] if s['standing'] == 'local_policy'), 'missing_governing_policy')
    check(not any(s['standing'] == 'adopted_rule' for s in req['governing_sources']), 'unsupported_adopted_rule')
    check(contained(grant['permissions'], req['permissions']), 'grant_exceeds_requirement')
    check(contained([{'action':action['action'],'targets':[action['target']], 'data_scopes':action['data_scopes'], 'max_amount':action['amount'], 'unit':action['unit'], 'max_effects':action['effects']}], grant['permissions']), 'action_out_of_scope')
    check(action['institution_id'] == inst['institution_id'] and action['authority_domain'] == inst['authority_domain'] and action['acting_identity'] == context['acting_identity'], 'action_domain_binding')
    active = set(snapshot['actor_roles'].get(context['principal'], []))
    check(all(not set(pair) <= active for pair in context['conflicts']['incompatible_role_pairs']), 'incompatible_roles')
    for obligation in req['evidence']:
        if obligation['kind'] == 'authorization' and obligation['required']:
            fact = snapshot['evidence'].get(obligation['obligation_id'])
            check(fact is not None and fact['state'] == 'satisfied' and fact['source_ref'] == obligation['source_ref'] and fact['effect_id'] == action['effect_id'] and 0 <= (timestamp(now)-timestamp(fact['observed_at'])).total_seconds() <= obligation['max_age_seconds'], 'missing_or_stale_evidence')
    for needed in req['approvals']:
        def adequate(ref):
            a = snapshot['approvals'].get(ref)
            return (a is not None and a['state'] == 'approved' and a['role_id'] == needed['role_id']
                    and a['approver'] in snapshot['approval_role_bindings'].get(needed['role_id'], [])
                    and a['grant_id'] == gid and a['grant_revision'] == grant['revision']
                    and a['binding'] == binding(action) and a['policy_versions'] == grant['policy_versions']
                    and timestamp(a['not_before']) <= timestamp(now) < timestamp(a['expires_at'])
                    and (not needed['independent_of_actor'] or a['approver'] not in {context['principal'], context['acting_identity']}
                         and a['approver'] in snapshot['independent_reviewers']))
        check(any(adequate(ref) for ref in grant['approval_refs']), 'missing_or_invalid_approval')
    parent_id = grant['delegation']['parent_grant_id']
    if parent_id:
        parent = snapshot['parents'].get(parent_id)
        if parent is None or schema_errors(parent):
            errors.append('missing_or_malformed_parent')
        else:
            pg = parent.get('grant')
            if pg is None or pg['grant_id'] != parent_id:
                errors.append('parent_binding')
            else:
                check(parent['institution'] == inst, 'delegation_domain')
                check(pg['grantee'] == grant['issuer'], 'delegation_issuer')
                check(pg['delegation']['may_delegate'] and pg['delegation']['remaining_depth'] > grant['delegation']['remaining_depth'], 'delegation_not_permitted')
                check(contained(grant['permissions'], pg['permissions']), 'child_exceeds_parent')
                check(timestamp(pg['not_before']) <= timestamp(grant['not_before']) and timestamp(grant['expires_at']) <= timestamp(pg['expires_at']), 'delegation_validity')
                check(grant['policy_versions'] == pg['policy_versions'], 'delegation_policy')
                check(req['approvals'] == parent['requirement']['approvals'] and req['evidence'] == parent['requirement']['evidence'] and context['conflicts'] == parent['conflicts'], 'delegation_drops_obligations')
                # Verify ancestor authority separately; child-bound approvals are still
                # assessed above. Parent must also have valid required approvals.
                parent_action = dict(action, acting_identity=parent['acting_identity'])
                errors += ['parent:' + e for e in reference_errors(parent, snapshot, parent_action, now, ancestors + (gid,))]
    return sorted(set(errors))
