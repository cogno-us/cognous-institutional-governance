"""G2 DEVELOPMENT-ONLY driver: runs the pinned Control Plane `decide()` over the IG root-lineage adapter.

Synthetic, local, decision-only: it never calls `execute()`, never dispatches an effect and never writes outside the
temporary directory it is given. Output is labelled a synthetic developer-mode decision, not institutional authorization.
The CP workflow is configured with CP's own existing developer profile (`allow_synthetic_resolver=True`, `allow_test_time=True`);
the resolver keeps `authenticated=False`.
"""
from __future__ import annotations

import copy
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

from ig_root_resolver import IGRootResolver, load_lineage_harness, load_pinned_control_plane

HERE = Path(__file__).resolve().parent
FIX = HERE / "fixtures"
AT = datetime(2026, 10, 5, 19, 0, tzinfo=timezone.utc)
AUTHORITY_ID = "urn:cognous:authority:g2-synthetic-refund-root-1"
LABEL = "SYNTHETIC DEVELOPER-MODE CP DECISION - not institutional authorization"


def load_json(name: str):
    return json.loads((FIX / name).read_text(encoding="utf-8"))


def build_proposal(cp, manifest: dict, tenant_id: str, context_ref: str):
    base = cp.RuntimeProposal(
        manifest_id=manifest["manifest_id"], manifest_version=manifest["manifest_version"], manifest_digest=cp.commitment(manifest),
        actor="urn:cognous:identity:refund-agent-1", principal="urn:cognous:principal:refund-service",
        action_id="urn:cognous:action:refund-issue-routine-v1", adapter_id="urn:cognous:adapter:synthetic-refund-v1",
        target="urn:cognous:synthetic-account:customer-001", payload={"customer_id": "customer-001", "refund_reason": "duplicate"},
        payload_commitment=cp.commitment({"customer_id": "customer-001", "refund_reason": "duplicate"}),
        requested_permissions=["refund.issue.routine"], amount=50.0, unit="USD", effects=1,
        authority_context_ref=context_ref,
        requirement_id="urn:cognous:authority-requirement:refund-routine-v1", correlation_id="case-1", run_id="run-1",
        evidence_refs=[])
    return cp.TenantRuntimeProposal(**base.model_dump(mode="json", exclude_none=False), tenant_id=tenant_id)


def run_case(cp_root, bundle_name: str, workdir, *, facts_edit=None, authority_id: str = AUTHORITY_ID):
    """One decision. Returns a plain dict with the CP decision, native reasons and the synthetic-authority labelling."""
    cp, ra = load_pinned_control_plane(cp_root)
    manifest = json.loads((Path(cp_root) / "tests" / "fixtures" / "refund_integration_v1_1.manifest.json").read_text(encoding="utf-8"))
    facts = load_json("synthetic_facts.json")
    if facts_edit:
        facts_edit(facts)
    bundle = load_json(bundle_name)
    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    p = build_proposal(cp, manifest, facts["tenant_id"], facts["context_ref"])
    facts["approval"]["proposal_commitment"] = cp.commitment(p.model_dump(mode="json", exclude_none=False))
    resolver = IGRootResolver(cp, bundle, authority_id, facts, AT, lineage=load_lineage_harness())
    cl = ra.ActionClass(class_id="synthetic-irreversible", irreversible=True, max_status_age_seconds=60, on_unreadable="refuse")
    cfg = ra.RuntimeAuthorityProfile(catalogue_version="synthetic-catalogue/1", actions={p.action_id: cl}, producer_keys={},
                                     allow_synthetic_resolver=True)

    def flow(tag, profile):
        return cp.BoundedAuthorizationWorkflow(
            manifest=manifest, resolver=resolver, destination=cp.LocalRefundDestination(workdir / f"{tag}-destination.json"),
            records=cp.BoundedRecordStore(workdir / f"{tag}-run.json", "run-1"),
            observation_policy=cp.ObservationPolicy(max_age_seconds=300), allow_test_time=True,
            **({"runtime_authority_profile": profile} if profile else {}))

    with mock.patch.object(cp, "_now", lambda: AT):  # CP's own tests pin the synthetic clock the same way
        # CP-native two-pass preparation (same as CP's own fixtures): enumerate the inputs the gate reads, then bind them.
        base = flow("baseline", None).decide(p, now=AT)
        required = sorted([{"input_type": x.input_type, "input_id": x.input_id} for x in base.resolution_inputs],
                          key=lambda x: (x["input_type"], x["input_id"]))
        resolver.facts["runtime_authority"] = {"profile": "runtime-authority/0.1", "required_inputs": required,
                                               "required_inputs_digest": cp.commitment(required), "evidence_criteria": {}}
        context = resolver.authority_context(facts["context_ref"])
        resolver.facts["approval"]["runtime_authority_commitment"] = ra.approval_commitment(cfg, context)
        f = flow("g2", cfg)
        decision = f.decide(p, now=AT)
        snapshot = f.destination.snapshot()
    return {"label": LABEL, "resolver_authenticated": resolver.authenticated, "result": decision.result,
            "reasons": list(decision.reasons), "reason_vocabulary_version": decision.reason_vocabulary_version,
            "destination_effects": snapshot["effects"], "executed": False,
            "baseline_reasons": list(base.reasons), "field_provenance": resolver.field_provenance()}
