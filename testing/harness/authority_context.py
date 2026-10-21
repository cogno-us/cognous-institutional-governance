"""Local reference checks only. No credentials, network, grants or effects.

The synthetic snapshot is assumed input, never authenticated by this module.
A satisfied result is NOT a runtime authorization decision.
"""
import math
import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Proposed per-tier ceilings for consequence.delay_limit.max_pending_seconds. Owner to confirm: no value is validated or
# derived from the constitution. The same numbers appear in the tier table of process/PROPORTIONAL_GOVERNANCE.md; a test
# fails if the two drift. A context may declare a shorter limit, never a longer one.
TIER_DELAY_CEILING_SECONDS = {'T0': 4 * 3600, 'T1': 24 * 3600, 'T2': 3 * 86400, 'T3': 7 * 86400, 'T4': 30 * 86400}

PROFILE_DIR = Path(__file__).resolve().parents[2] / 'process/implementation/public-stack-v0.1'
# Head schema is 0.2.0 (consequence.delay_limit required). 0.1.0 stays available as a versioned file and has no delay limit.
SCHEMA_PATH = PROFILE_DIR / 'authority-context.schema.json'
SCHEMA_PATHS = {'0.1.0': PROFILE_DIR / 'authority-context.0.1.0.schema.json', '0.2.0': SCHEMA_PATH}


def schema_errors(context):
    """Validate against the schema generation the context names; any other or missing version is refused."""
    import jsonschema
    from jsonschema import Draft202012Validator
    version = context.get('schema_version') if isinstance(context, dict) else None
    path = SCHEMA_PATHS.get(version) if isinstance(version, str) else None
    if path is None:
        return ['unsupported or missing schema_version: expected one of ' + ', '.join(sorted(SCHEMA_PATHS))]
    schema = json.loads(path.read_text())
    Draft202012Validator.check_schema(schema)
    return sorted(error.message for error in Draft202012Validator(schema, format_checker=_format_checker(jsonschema)).iter_errors(context))


_RFC3339 = re.compile(r"([0-9]{4})-([0-9]{2})-([0-9]{2})[Tt]([0-9]{2}):([0-9]{2}):([0-9]{2})(?:\.([0-9]+))?([Zz]|[+-][0-9]{2}:[0-9]{2})", re.ASCII)
_TIMESTAMP_REFUSAL = "not an RFC 3339 date-time with an explicit offset"

def timestamp(value):
    """Strict RFC 3339 date-time: full date and time and an explicit offset are required; returns an aware datetime.
    Naive times, date-only values, other text and a leap second (:60) raise ValueError. The pinned jsonschema does not
    check `format: date-time` without rfc3339-validator, so the harness checks it itself."""
    m = _RFC3339.fullmatch(value) if isinstance(value, str) else None
    if m is None: raise ValueError(_TIMESTAMP_REFUSAL)
    y, mo, d, h, mi, s, frac, off = m.groups()
    if off in ("Z", "z"): tz = timezone.utc
    else:
        oh, om = int(off[1:3]), int(off[4:6])
        if oh > 23 or om > 59: raise ValueError(_TIMESTAMP_REFUSAL)
        tz = timezone((-1 if off[0] == "-" else 1) * timedelta(hours=oh, minutes=om))
    return datetime(int(y), int(mo), int(d), int(h), int(mi), int(s), int((frac or "0").ljust(6, "0")[:6]), tzinfo=tz)

def _format_checker(jsonschema):
    checker = jsonschema.FormatChecker()
    def date_time(instance):
        if isinstance(instance, str): timestamp(instance)
        return True
    checker.checks("date-time", raises=ValueError)(date_time)
    return checker


def binding(action):
    return hashlib.sha256(json.dumps(action, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def contained(child, parent):
    """Exact action/unit, finite target/data sets and numeric attenuation only.

    Non-finite amounts (NaN, +/-Inf) are never contained.
    """
    return all(any(c['action'] == p['action'] and c['unit'] == p['unit']
                   and math.isfinite(c['max_amount']) and math.isfinite(p['max_amount'])
                   and set(c['targets']) <= set(p['targets'])
                   and set(c['data_scopes']) <= set(p['data_scopes'])
                   and c['max_amount'] <= p['max_amount']
                   and c['max_effects'] <= p['max_effects'] for p in parent) for c in child)


def reference_errors(context, snapshot, action, now, ancestors=()):
    """Typed wrapper: a malformed or naive timestamp is the refusal code 'invalid_timestamp', never a raise."""
    try:
        return _reference_errors(context, snapshot, action, now, ancestors)
    except ValueError as exc:
        if str(exc) == _TIMESTAMP_REFUSAL: return ['invalid_timestamp']
        raise


def _reference_errors(context, snapshot, action, now, ancestors=()):
    """Reject unsupported/missing synthetic premises; never imply permission.

    Precondition: ``schema_errors(context)`` must be empty before calling, and
    snapshot, action and now must have the reference fixture shape. This
    function does not validate those shapes; malformed or unchecked input may
    raise KeyError, TypeError or ValueError instead of returning refusal codes.
    Non-finite numbers that reach canonical binding are refused as
    'non_finite_value'. Snapshot has explicit synthetic trust, policy, role,
    status, approval and evidence premises. No signature validation.
    """
    errors = []
    def check(condition, reason):
        if not condition:
            errors.append(reason)
    inst = context['institution']; req = context['requirement']; grant = context.get('grant')
    try:
        requirement_binding = binding({k: context[k] for k in ('institution', 'accountable_human_role', 'requirement', 'conflicts')})
    except ValueError:
        return errors + ['non_finite_value']
    check(snapshot['requirement_bindings'].get(req['requirement_id']) == requirement_binding, 'untrusted_requirement_binding')
    if any(type(action[k]) not in (int, float) or not math.isfinite(action[k]) or action[k] < 0 for k in ('amount', 'effects')) or type(action['effects']) is not int:
        return errors + ['invalid_action_limits']
    try:
        action_binding = binding(action)
    except ValueError:
        return errors + ['non_finite_value']
    check(inst['authority_basis_ref'] in snapshot['authority_bases'], 'missing_authority_basis')
    check(context['accountable_human_role'] in snapshot['accountable_roles'], 'unbound_accountable_role')
    check(context['conflicts']['precedence_refs'] == snapshot['precedence_refs'], 'unresolved_precedence')
    check(not snapshot['unresolved_conflict'], 'conflicting_rules')
    check(inst['authority_mode'] == 'principle_inspired', 'unsupported_adoption_mode')
    check(context['change']['adoption_record_ref'] is None or context['change']['adoption_record_ref'] in snapshot['human_adoption_records'], 'unadopted_amendment')
    check(req['consequence']['tier'] != 'T4', 'reserved_constitutional_process')
    # 0.1.0 contexts declare no delay limit: nothing to compare, and no default is invented.
    if context['schema_version'] == '0.2.0':
        check(req['consequence']['delay_limit']['max_pending_seconds'] <= TIER_DELAY_CEILING_SECONDS[req['consequence']['tier']], 'delay_limit_exceeds_tier_ceiling')
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
                    and a['binding'] == action_binding and a['policy_versions'] == grant['policy_versions']
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
