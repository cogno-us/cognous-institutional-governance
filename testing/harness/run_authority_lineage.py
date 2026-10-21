"""Scoped synthetic qualification for the non-authorizing authority lineage profile."""
from __future__ import annotations
import copy, hashlib, json, math, re
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "process" / "implementation" / "authority-lineage-v0.1" / "authority-lineage.schema.json"

_RFC3339 = re.compile(r"([0-9]{4})-([0-9]{2})-([0-9]{2})[Tt]([0-9]{2}):([0-9]{2}):([0-9]{2})(?:\.([0-9]+))?([Zz]|[+-][0-9]{2}:[0-9]{2})", re.ASCII)
_TIMESTAMP_REFUSAL = "not an RFC 3339 date-time with an explicit offset"

def _dt(value):
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
        if isinstance(instance, str): _dt(instance)
        return True
    checker.checks("date-time", raises=ValueError)(date_time)
    return checker
def _scope(actions, targets, data_scopes, amount, unit, effects):
    return {"actions": actions, "targets": targets, "data_scopes": data_scopes, "max_amount": amount, "unit": unit, "max_effects": effects}

def fixture_bundle():
    parent_scope = _scope(["refund"], ["urn:cognous:acct:customer-7"], ["billing"], 500, "USD", 5)
    child_scope = _scope(["refund"], ["urn:cognous:acct:customer-7"], ["billing"], 100, "USD", 1)
    return {
      "schema_version":"0.1.0","interface_status":"proposed_non_authorizing_evidence_only",
      "bundle_id":"urn:cognous:authority-lineage:bundle-1","captured_at":"2026-10-09T20:00:00Z",
      "portability":{"format":"application/json","source_bundle_digest":"sha256:"+"1"*64,"portable_evidence_only":True,"transfers_permission":False},
      "origins":[{"record_type":"AuthorityOriginRecord","origin_id":"urn:cognous:authority-origin:root-1","institution_id":"urn:cognous:institution:synthetic","authority_domain":"customer-refunds","authority_id":"urn:cognous:authority:refund-manager","authority_revision":"r1","external_mandate_ref":"urn:cognous:mandate:board-policy-7","mandate_kind":"adopted_rule","effective_at":"2026-10-01T00:00:00Z","recorded_at":"2026-10-01T00:01:00Z","permission_scope":parent_scope,"source_evidence_refs":["urn:cognous:evidence:mandate-7"],"authority_claim_status":"verified_by_declared_source","non_authorizing":True}],
      "delegations":[{"record_type":"DelegationEdge","delegation_id":"urn:cognous:delegation:edge-1","institution_id":"urn:cognous:institution:synthetic","authority_domain":"customer-refunds","parent_authority_id":"urn:cognous:authority:refund-manager","parent_revision":"r1","child_authority_id":"urn:cognous:authority:refund-agent","child_revision":"r1","delegated_at":"2026-10-02T00:00:00Z","valid_from":"2026-10-02T00:00:00Z","expires_at":"2026-11-01T00:00:00Z","permission_scope":child_scope,"may_redelegate":False,"remaining_depth":0,"source_evidence_refs":["urn:cognous:evidence:delegation-1"],"non_authorizing":True}],
      "mutations":[],"successions":[],
      "resolution_commitments":[{"record_type":"AuthorityResolutionCommitment","commitment_id":"urn:cognous:authority-resolution:child-r1","authority_id":"urn:cognous:authority:refund-agent","resolved_revision":"r1","resolved_status":"active","resolution_time":"2026-10-03T00:00:00Z","resolver_id":"urn:cognous:resolver:synthetic","resolver_snapshot_ref":"urn:cognous:resolver-snapshot:1","lineage_record_ids":["urn:cognous:authority-origin:root-1","urn:cognous:delegation:edge-1"],"historical_record_ids":[],"scope_digest":"sha256:"+"2"*64,"source_set_digest":"sha256:"+"3"*64,"commitment_semantics":"evidence_of_resolution_not_live_permission","non_authorizing":True}],
      "use_links":[{"record_type":"AuthorityUseLink","use_link_id":"urn:cognous:authority-use:1","authority_id":"urn:cognous:authority:refund-agent","authority_revision":"r1","decision_id":"urn:cognous:decision:1","effect_id":"urn:cognous:effect:1","used_at":"2026-10-03T00:00:01Z","resolution_commitment_id":"urn:cognous:authority-resolution:child-r1","evidence_package_ref":"urn:cognous:evidence-pack:1","use_disposition":"referenced","transfers_permission":False,"non_authorizing":True}]
    }

def _record_index(bundle):
    result={}
    for section in ("origins","delegations","mutations","successions","resolution_commitments","use_links"):
        for record in bundle[section]:
            rid=next((record[k] for k in ("origin_id","delegation_id","mutation_id","succession_id","commitment_id","use_link_id") if k in record),None)
            if rid in result: raise ValueError("duplicate record id")
            result[rid]=record
    return result

def _contained(c, ps, label):
    """Raise unless scope c is contained in scope ps (the one attenuation rule, for edges and mutations)."""
    if not set(c["actions"]).issubset(ps["actions"]): raise ValueError(f"{label} broadens actions")
    if not set(c["targets"]).issubset(ps["targets"]): raise ValueError(f"{label} broadens targets")
    if not set(c["data_scopes"]).issubset(ps["data_scopes"]): raise ValueError(f"{label} broadens data scopes")
    if c["unit"]!=ps["unit"]: raise ValueError(f"{label} changes unit")
    if not (math.isfinite(c["max_amount"]) and math.isfinite(ps["max_amount"])): raise ValueError(f"{label} amount is not finite")
    if c["max_amount"]>ps["max_amount"]: raise ValueError(f"{label} broadens amount")
    if c["max_effects"]>ps["max_effects"]: raise ValueError(f"{label} broadens effect count")

_KIND_STATUS={"revoke":"revoked","suspend":"suspended","reinstate":"active"}

def _effective(bundle, states, authority_id, when):
    """Authority state at `when`: base lineage state with every mutation effective at or before `when` applied.
    An amended scope must stay inside the effective parent scope at the mutation's effective_at (delegate),
    or inside the origin's own base scope (origin; each amendment is measured against the base, not the previous amendment)."""
    base=states.get(authority_id)
    if not base: raise ValueError("unknown authority")
    out=dict(base)
    muts=sorted((m for m in bundle["mutations"] if m["authority_id"]==authority_id and _dt(m["effective_at"])<=when), key=lambda m:_dt(m["effective_at"]))
    for m in muts:
        if m["prior_revision"]!=out["revision"]: raise ValueError("mutation prior revision mismatch")
        if m["mutation_kind"] in _KIND_STATUS and m["status_after"]!=_KIND_STATUS[m["mutation_kind"]]: raise ValueError("mutation kind inconsistent with status_after")
        if m["mutation_kind"]=="amend" and m["status_after"]!=out["status"]: raise ValueError("amend must not change status")
        if m["permission_scope_after"] is not None:
            edge=base.get("edge")
            limit=base["scope"] if edge is None else _effective(bundle,states,edge["parent_authority_id"],_dt(m["effective_at"]))["scope"]
            _contained(m["permission_scope_after"],limit,"mutation")
            out["scope"]=m["permission_scope_after"]
        out["revision"],out["status"]=m["new_revision"],m["status_after"]
    return out

def _authority_state(bundle):
    state={}
    for o in bundle["origins"]:
        if o["authority_id"] in state: raise ValueError("conflicting origins for one authority")
        state[o["authority_id"]]={"institution_id":o["institution_id"],"authority_domain":o["authority_domain"],"revision":o["authority_revision"],"status":"active","scope":o["permission_scope"]}
    pending=list(bundle["delegations"])
    while pending:
        progressed=False
        for e in pending[:]:
            if e["parent_authority_id"] not in state: continue
            # the parent as it stood when the edge was made: narrowed or amended scope and revision count
            p=_effective(bundle,state,e["parent_authority_id"],_dt(e["delegated_at"]))
            if e["parent_revision"]!=p["revision"]: raise ValueError("delegation parent revision mismatch")
            if e["institution_id"]!=p["institution_id"] or e["authority_domain"]!=p["authority_domain"]: raise ValueError("delegation crosses institution/domain")
            c=e["permission_scope"]
            _contained(c,p["scope"],"delegation")
            pe=p.get("edge")
            if pe is not None:  # the parent is itself a delegate: its own edge limits further delegation
                if not pe["may_redelegate"] or pe["remaining_depth"]<1: raise ValueError("parent delegation does not permit redelegation")
                if e["remaining_depth"]>=pe["remaining_depth"]: raise ValueError("delegation depth does not decrease below its parent")
            if e["child_authority_id"] in state: raise ValueError("duplicate/cyclic child authority")
            state[e["child_authority_id"]]={"institution_id":e["institution_id"],"authority_domain":e["authority_domain"],"revision":e["child_revision"],"status":"active","scope":c,"edge":e}
            pending.remove(e); progressed=True
        if not progressed: raise ValueError("orphan or cyclic delegation")
    return state

def _state_at(bundle, authority_id, when):
    return _effective(bundle,_authority_state(bundle),authority_id,when)

def _chain_record_ids(bundle, authority_id, when):
    """(required, allowed): required is the structural origin-to-authority chain (origin plus each delegation edge);
    allowed adds the mutations of chain members effective by `when`, which a commitment may cite but need not."""
    required=set(); allowed=set(); current=authority_id
    for _ in range(len(bundle["delegations"])+1):
        allowed.update(m["mutation_id"] for m in bundle["mutations"] if m["authority_id"]==current and _dt(m["effective_at"])<=when)
        edge=next((e for e in bundle["delegations"] if e["child_authority_id"]==current),None)
        if edge is None: break
        required.add(edge["delegation_id"]); current=edge["parent_authority_id"]
    origin=next((o for o in bundle["origins"] if o["authority_id"]==current),None)
    if origin is not None: required.add(origin["origin_id"])
    return required,allowed|required

def _chain_edges(bundle, authority_id):
    edges=[]; current=authority_id
    for _ in range(len(bundle["delegations"])+1):
        edge=next((e for e in bundle["delegations"] if e["child_authority_id"]==current),None)
        if edge is None: break
        edges.append(edge); current=edge["parent_authority_id"]
    return edges

def _delegation_relatives(bundle, authority_id):
    """Ancestors and descendants of an authority along delegation edges (not the authority itself)."""
    related={e["parent_authority_id"] for e in _chain_edges(bundle,authority_id)}
    frontier=[authority_id]; seen={authority_id}
    while frontier:
        current=frontier.pop()
        for e in bundle["delegations"]:
            child=e["child_authority_id"]
            if e["parent_authority_id"]==current and child not in seen: seen.add(child); related.add(child); frontier.append(child)
    return related

def _windows(bundle, authority_id):
    """Validity windows (start, end or None) on the chain from an authority back to its origin."""
    result=[]; current=authority_id
    for _ in range(len(bundle["delegations"])+1):
        edge=next((e for e in bundle["delegations"] if e["child_authority_id"]==current),None)
        if edge is None: break
        result.append((_dt(edge["valid_from"]),None if edge["expires_at"] is None else _dt(edge["expires_at"])))
        current=edge["parent_authority_id"]
    origin=next((o for o in bundle["origins"] if o["authority_id"]==current),None)
    if origin is not None: result.append((_dt(origin["effective_at"]),None))
    return result

def _within(bundle, authority_id, when):
    return all(start<=when and (end is None or when<end) for start,end in _windows(bundle,authority_id))

def _window_errors(bundle):
    errors=[]
    for e in bundle["delegations"]:
        start=_dt(e["valid_from"]); end=None if e["expires_at"] is None else _dt(e["expires_at"])
        if end is not None and end<=start: errors.append("delegation validity window is empty or inverted")
        parent=_windows(bundle,e["parent_authority_id"])
        if parent:
            p_start=max(s for s,_ in parent); p_ends=[x for _,x in parent if x is not None]
            if start<p_start or (p_ends and (end is None or end>min(p_ends))): errors.append("delegation validity extends beyond its parent")
    return errors

_MALFORMED=(KeyError,TypeError,ValueError)

def _semantic_message(exc):
    return str(exc) if isinstance(exc,ValueError) else f"malformed lineage input: {type(exc).__name__}: {exc}"

def semantic_errors(bundle):
    """Semantic checks; malformed input yields error strings, never exceptions."""
    errors=[]
    try: return _semantic_errors(bundle,errors)
    except _MALFORMED as exc: return errors+[_semantic_message(exc)]

def _semantic_errors(bundle, errors):
    try:
        records=_record_index(bundle); known=set(_authority_state(bundle))
    except _MALFORMED as exc: return [_semantic_message(exc)]
    for e in bundle["delegations"]:
        if not e["may_redelegate"] and e["remaining_depth"]>0: errors.append("delegation remaining_depth without may_redelegate")
    try: errors.extend(_window_errors(bundle))
    except _MALFORMED as exc: errors.append(_semantic_message(exc))
    for s in bundle["successions"]:
        if s["predecessor_authority_id"] not in known: errors.append("succession predecessor unknown")
        if s["successor_authority_id"] not in known: errors.append("succession successor has no independent origin/delegation lineage")
        elif s["predecessor_authority_id"]==s["successor_authority_id"]: errors.append("succession predecessor and successor are the same authority")
        elif s["predecessor_authority_id"] in known and s["successor_authority_id"] in _delegation_relatives(bundle,s["predecessor_authority_id"]): errors.append("succession successor is inside the predecessor's own delegation chain")
    for m in bundle["mutations"]:  # every mutation is checked, whether or not a commitment or use cites it
        try: _state_at(bundle,m["authority_id"],_dt(m["effective_at"]))
        except _MALFORMED as exc: errors.append(_semantic_message(exc))
    commitments={c["commitment_id"]:c for c in bundle["resolution_commitments"]}
    for c in bundle["resolution_commitments"]:
        for rid in c["lineage_record_ids"]+c["historical_record_ids"]:
            if rid not in records: errors.append("resolution commitment references unknown lineage record")
        try:
            required,allowed=_chain_record_ids(bundle,c["authority_id"],_dt(c["resolution_time"])); cited=set(c["lineage_record_ids"])
            if not required<=cited or not cited<=allowed: errors.append("resolution commitment lineage is not the origin-to-authority chain")
            actual=_state_at(bundle,c["authority_id"],_dt(c["resolution_time"]))
            if c["resolved_revision"]!=actual["revision"]: errors.append("resolution revision inconsistent with effective lineage")
            if c["resolved_status"]!=actual["status"]: errors.append("resolution status inconsistent with effective lineage")
            if c["resolved_status"]=="active" and not _within(bundle,c["authority_id"],_dt(c["resolution_time"])): errors.append("resolution status active outside delegation validity window")
        except _MALFORMED as exc: errors.append(_semantic_message(exc))
    for u in bundle["use_links"]:
        c=commitments.get(u["resolution_commitment_id"])
        if not c: errors.append("use link commitment missing"); continue
        if c["authority_id"]!=u["authority_id"] or c["resolved_revision"]!=u["authority_revision"]: errors.append("use link authority/revision does not match commitment")
        if _dt(c["resolution_time"])>_dt(u["used_at"]): errors.append("use link predates resolution")
        try:
            actual=_state_at(bundle,u["authority_id"],_dt(u["used_at"]))
            if actual["revision"]!=u["authority_revision"]: errors.append("use link relies on historical revision after effective mutation")
            if actual["status"]!="active" and u["use_disposition"]=="referenced": errors.append("use link references non-active current authority")
            if u["use_disposition"]=="referenced" and any(_dt(e["delegated_at"])>_dt(u["used_at"]) for e in _chain_edges(bundle,u["authority_id"])): errors.append("use link relies on a delegation made after the use")
            if u["use_disposition"]=="referenced" and not _within(bundle,u["authority_id"],_dt(u["used_at"])): errors.append("use link references authority outside its delegation validity window")
            if c["resolved_revision"]!=actual["revision"] or c["resolved_status"]!=actual["status"]: errors.append("use link commitment is stale relative to current effective lineage")
        except _MALFORMED as exc: errors.append(_semantic_message(exc))
    return errors

def schema_errors(bundle):
    import jsonschema
    schema=json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    v=jsonschema.Draft202012Validator(schema,format_checker=_format_checker(jsonschema))
    return [e.message for e in v.iter_errors(bundle)]

def validate(bundle):
    """Schema first; semantics run only on schema-valid bundles."""
    errors=schema_errors(bundle)
    return errors if errors else semantic_errors(bundle)

def cases():
    base=fixture_bundle(); out=[]
    def add(name, mutate, expected): b=copy.deepcopy(base); mutate(b); out.append((name,b,expected))
    add("valid_attenuated_parent_child",lambda b:None,True)
    add("reject_broadened_child_action",lambda b:b["delegations"][0]["permission_scope"]["actions"].append("wire-transfer"),False)
    add("reject_broadened_child_amount",lambda b:b["delegations"][0]["permission_scope"].update(max_amount=1000),False)
    add("reject_orphan_parent",lambda b:b["delegations"][0].update(parent_authority_id="urn:cognous:authority:missing"),False)
    add("reject_unknown_lineage_record",lambda b:b["resolution_commitments"][0]["lineage_record_ids"].append("urn:cognous:record:fake"),False)
    def revoked(b):
        b["mutations"].append({"record_type":"AuthorityMutationRecord","mutation_id":"urn:cognous:mutation:rev-1","authority_id":"urn:cognous:authority:refund-agent","prior_revision":"r1","new_revision":"r2","mutation_kind":"revoke","effective_at":"2026-10-03T00:00:00Z","recorded_at":"2026-10-03T00:00:00Z","status_after":"revoked","permission_scope_after":None,"basis_ref":"urn:cognous:mandate:revocation-1","non_authorizing":True})
    add("reject_resolution_claiming_active_after_revocation",revoked,False)
    def amended(b):
        b["mutations"].append({"record_type":"AuthorityMutationRecord","mutation_id":"urn:cognous:mutation:amend-1","authority_id":"urn:cognous:authority:refund-agent","prior_revision":"r1","new_revision":"r2","mutation_kind":"amend","effective_at":"2026-10-03T00:00:00.500000Z","recorded_at":"2026-10-03T00:00:00.500000Z","status_after":"active","permission_scope_after":_scope(["refund"],["urn:cognous:acct:customer-7"],["billing"],50,"USD",1),"basis_ref":"urn:cognous:mandate:amendment-1","non_authorizing":True})
    add("reject_historical_revision_as_current_after_amendment",amended,False)
    def historical_then_revoke(b):
        b["mutations"].append({"record_type":"AuthorityMutationRecord","mutation_id":"urn:cognous:mutation:rev-2","authority_id":"urn:cognous:authority:refund-agent","prior_revision":"r1","new_revision":"r2","mutation_kind":"revoke","effective_at":"2026-10-03T00:00:02Z","recorded_at":"2026-10-03T00:00:02Z","status_after":"revoked","permission_scope_after":None,"basis_ref":"urn:cognous:mandate:revocation-2","non_authorizing":True})
        b["resolution_commitments"].append({"record_type":"AuthorityResolutionCommitment","commitment_id":"urn:cognous:authority-resolution:child-r2","authority_id":"urn:cognous:authority:refund-agent","resolved_revision":"r2","resolved_status":"revoked","resolution_time":"2026-10-03T00:00:03Z","resolver_id":"urn:cognous:resolver:synthetic","resolver_snapshot_ref":"urn:cognous:resolver-snapshot:2","lineage_record_ids":["urn:cognous:authority-origin:root-1","urn:cognous:delegation:edge-1","urn:cognous:mutation:rev-2"],"historical_record_ids":["urn:cognous:authority-resolution:child-r1"],"scope_digest":"sha256:"+"4"*64,"source_set_digest":"sha256:"+"5"*64,"commitment_semantics":"evidence_of_resolution_not_live_permission","non_authorizing":True})
        b["use_links"][0].update(authority_revision="r2",used_at="2026-10-03T00:00:04Z",resolution_commitment_id="urn:cognous:authority-resolution:child-r2",use_disposition="held")
    add("allow_historical_fact_but_separate_current_revoked_state",historical_then_revoke,True)
    def succession(b):
        b["successions"].append({"record_type":"AuthoritySuccessionRecord","succession_id":"urn:cognous:succession:1","institution_id":"urn:cognous:institution:synthetic","authority_domain":"customer-refunds","predecessor_authority_id":"urn:cognous:authority:refund-manager","successor_authority_id":"urn:cognous:authority:new-manager","effective_at":"2026-10-04T00:00:00Z","recorded_at":"2026-10-04T00:00:01Z","succession_basis_ref":"urn:cognous:mandate:succession-1","successor_mandate_ref":"urn:cognous:mandate:new-manager","continuity_semantics":"no_automatic_permission_transfer","non_authorizing":True})
    add("reject_succession_as_permission_transfer_without_successor_lineage",succession,False)
    add("reject_portable_bundle_permission_transfer",lambda b:b["portability"].update(transfers_permission=True),False)
    return out

def execute():
    results=[]
    for name,bundle,expected in cases():
        errors=validate(bundle); valid=not errors
        results.append({"id":name,"expected_valid":expected,"valid":valid,"oracle_satisfied":valid==expected,"errors":errors})
    canonical=json.dumps(fixture_bundle(),sort_keys=True,separators=(",",":")).encode()
    return {"schema_id":"urn:cognous:alvorada:authority-lineage:0.1.0","case_count":len(results),"fixture_sha256":hashlib.sha256(canonical).hexdigest(),"results":results}

if __name__=="__main__": print(json.dumps(execute(),indent=2,sort_keys=True))
