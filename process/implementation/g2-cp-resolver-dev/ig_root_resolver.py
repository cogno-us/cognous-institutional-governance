"""G2 DEVELOPMENT-ONLY, read-only adapter: Institutional Governance ROOT lineage -> Control Plane `Resolver`.

SYNTHETIC / NON-AUTHORIZING. This module issues nothing, writes nothing, dispatches no effect and never changes
the Control Plane. It reads (a) an IG authority-lineage bundle (validated with IG's own schema and semantic checks),
(b) an explicit, separately labelled block of SYNTHETIC fixture facts and (c) an explicit evaluation time, and answers
the Control Plane's existing `Resolver` protocol with the Control Plane's own pydantic records. The Control Plane
remains the only decision authority.

`authenticated` is False and is never changed: a CP "authorized" decision made through this adapter is a synthetic
developer-mode decision under CP's existing `allow_synthetic_resolver` profile, not institutional authorization. Tenant,
expiry, issuer, identity, policy, requirement, approval and role-mapping facts are NOT derived from lineage: they come only
from the fixture facts block and are listed in `field_provenance()`. Only ROOT authorities are supported; any delegation
edge in the bundle is refused.
"""
from __future__ import annotations

import copy
import importlib.util
import subprocess
import sys
import threading
from contextlib import contextmanager
from pathlib import Path

CP_PIN = "484fdbd297235dd24148ddb0703f2055a31eabff"
HARNESS = Path(__file__).resolve().parents[3] / "testing" / "harness" / "run_authority_lineage.py"


class AdapterRefusal(ValueError):
    """The bundle, facts or environment cannot be mapped; nothing is defaulted."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


def load_lineage_harness():
    """IG's own validator module (schema + semantic checks and `_state_at`), loaded by path; not copied."""
    spec = importlib.util.spec_from_file_location("ig_run_authority_lineage", HARNESS)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_pinned_control_plane(root: str | Path):
    """Verify the CP checkout is the pinned commit with an unmodified tree, then import CP's own `bounded` module."""
    root = Path(root).resolve()

    def git(*args: str) -> str:
        return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True).stdout.strip()

    if git("rev-parse", "HEAD") != CP_PIN:
        raise AdapterRefusal("control_plane_not_pinned_revision")
    if git("status", "--porcelain", "--untracked-files=all"):
        raise AdapterRefusal("control_plane_checkout_not_clean")
    loaded = sys.modules.get("agent_control_plane")
    if loaded is not None and not Path(getattr(loaded, "__file__", "") or "").resolve().is_relative_to(root):
        raise AdapterRefusal("a different agent_control_plane is already imported")
    src = str(root / "src")
    if src in sys.path:
        sys.path.remove(src)
    sys.path.insert(0, src)  # the verified checkout always wins module resolution
    import agent_control_plane.bounded as bounded  # noqa: PLC0415 - imported only after the pin is verified
    from agent_control_plane import runtime_authority  # noqa: PLC0415

    if not Path(bounded.__file__).resolve().is_relative_to(root):
        raise AdapterRefusal("control_plane_module_outside_pinned_checkout")
    return bounded, runtime_authority


_REQUIRED_FACTS = ("roles", "evaluation", "tenant_id", "expires_at", "issued_at", "context_ref", "authority_mode", "principal",
                   "acting_identity", "grantee", "accountable_human_role", "issuer", "identity", "policy", "requirement",
                   "conflicts", "approval", "role_mapping")


class IGRootResolver:
    """Implements CP's `Resolver` protocol over IG root lineage. `authenticated = False` always."""

    authenticated = False

    def __init__(self, cp, bundle: dict, authority_id: str, facts: dict, at, *, lineage=None):
        self.cp = cp
        self.lineage = lineage or load_lineage_harness()
        errors = self.lineage.validate(bundle)
        if errors:
            raise AdapterRefusal("lineage_invalid:" + errors[0])
        if bundle["delegations"]:
            raise AdapterRefusal("delegation_unsupported_root_only")
        origins = [o for o in bundle["origins"] if o["authority_id"] == authority_id]
        if len(origins) != 1:
            raise AdapterRefusal("root_origin_not_found")
        missing = [k for k in _REQUIRED_FACTS if k not in facts]
        if missing:
            raise AdapterRefusal("synthetic_fact_missing:" + ",".join(missing))
        nested = {"evaluation": ("observed_at", "status_observed_at", "status_version", "status_ref"),
                  "issuer": ("issuer", "issuer_role", "issuance_record_ref", "mandate_valid"),
                  "identity": ("authenticated", "delegation_valid", "chain"), "policy": ("ref", "version", "status"),
                  "requirement": ("requirement_id", "permissions", "approvals", "evidence", "consequence"),
                  "approval": ("approval_ref", "role_id", "approver", "proposal_commitment"), "role_mapping": ("version", "aliases")}
        absent = [f"{k}.{n}" for k, names in nested.items() for n in names
                  if not isinstance(facts[k], dict) or n not in facts[k]]
        if absent or not isinstance(facts["tenant_id"], str) or not facts["tenant_id"]:
            raise AdapterRefusal("synthetic_fact_missing_or_empty:" + ",".join(absent or ["tenant_id"]))
        try:
            expires = self.lineage._dt(facts["expires_at"])
            self.not_before = self.lineage._dt(origins[0]["effective_at"])
        except ValueError as exc:
            raise AdapterRefusal("timestamp_invalid") from exc
        if not self.not_before < expires:
            raise AdapterRefusal("expires_at_not_after_not_before")
        if at.tzinfo is None:
            raise AdapterRefusal("evaluation_time_not_aware")
        self.bundle, self.authority_id, self.origin, self.at = bundle, authority_id, origins[0], at
        self.facts = copy.deepcopy(facts)  # the driver may add CP-native derived entries (runtime_authority, approval commitment)
        self._lock = threading.RLock()

    # ------------------------------------------------------------------ IG-derived state
    def _state(self):
        """(revision, status) at the explicit evaluation time; mutations after `t` are never applied.
        Before the origin's inclusive `effective_at` there is no active status: status is `unknown`."""
        state = self.lineage._state_at(self.bundle, self.authority_id, self.at)
        if self.at < self.not_before:
            return state["revision"], "unknown"
        return state["revision"], state["status"]

    def _scope(self):
        return self.lineage._state_at(self.bundle, self.authority_id, self.at)["scope"]

    def _permissions(self):
        s = self._scope()
        return [{"action": a, "targets": list(s["targets"]), "data_scopes": list(s["data_scopes"]),
                 "max_amount": s["max_amount"], "unit": s["unit"], "max_effects": s["max_effects"]} for a in s["actions"]]

    def field_provenance(self) -> dict:
        """Which CP fields are IG-derived versus synthetic-fixture-only versus CP-native computed. Reviewer-visible."""
        ig = ["grant_id<-authority_id", "grant.revision/GrantStatus.revision<-effective authority_revision|new_revision",
              "GrantStatus.status<-effective mutations at t", "institution_id", "authority_domain",
              "authority_basis_ref<-external_mandate_ref (source reference, not authenticated mandate)",
              "grant.not_before<-origin.effective_at", "grant.permissions<-permission_scope (unchanged)"]
        synthetic = ["tenant_id", "grant.expires_at", "grant.issued_at", "GrantStatus.observed_at/version/status_ref",
                     "issuer/issuer_role/issuance_record_ref/mandate_valid", "principal/acting_identity/grantee",
                     "IdentityStatus", "accountable_human_role (incl. mandate_ref)", "authority_mode", "context_ref",
                     "supporting_evidence_refs/change (empty constants)", "policy ref/version/status", "requirement (incl. permissions, approvals, tier)",
                     "conflicts", "approval status", "role-mapping aliases/version", "delegation block (root-only constants)"]
        native = ["role-mapping digest = CP commitment({institution_id, version, aliases})",
                  "approval runtime_authority_commitment / required_inputs digest (CP native, set by the driver)"]
        return {"ig_derived": ig, "synthetic_fixture_only": synthetic, "cp_native_computed": native,
                "authenticated": False, "label": self.facts.get("label", "SYNTHETIC")}

    # ------------------------------------------------------------------ Resolver protocol
    def authority_context(self, ref: str):
        f = self.facts
        if ref != f["context_ref"]:
            return None
        revision, _ = self._state()
        o = self.origin
        ctx = {
            "schema_version": "0.1.0", "interface_status": "proposed_pending_governor_review", "context_id": f["context_ref"],
            "institution": {"institution_id": o["institution_id"], "authority_domain": o["authority_domain"],
                            "authority_basis_ref": o["external_mandate_ref"], "authority_mode": f["authority_mode"]},
            "principal": f["principal"], "acting_identity": f["acting_identity"],
            "accountable_human_role": copy.deepcopy(f["accountable_human_role"]),
            "requirement": copy.deepcopy(f["requirement"]), "conflicts": copy.deepcopy(f["conflicts"]),
            "supporting_evidence_refs": [], "change": {"kind": "none", "proposal_ref": None, "adoption_record_ref": None},
            "tenant_id": f["tenant_id"],
            "grant": {
                "grant_id": self.authority_id, "revision": revision, "requirement_id": f["requirement"]["requirement_id"],
                "issuer": f["issuer"]["issuer"], "issuer_role": f["issuer"]["issuer_role"],
                "issuance_record_ref": f["issuer"]["issuance_record_ref"], "grantee": f["grantee"],
                "acting_identity": f["acting_identity"], "issued_at": f["issued_at"],
                "not_before": self.not_before.isoformat(), "expires_at": f["expires_at"],
                "status_ref": f["evaluation"]["status_ref"],
                "policy_versions": [{"ref": f["policy"]["ref"], "version": f["policy"]["version"]}],
                "permissions": self._permissions(),
                "delegation": {"parent_grant_id": None, "may_delegate": False, "remaining_depth": 0},
                "approval_refs": [f["approval"]["approval_ref"]], "tenant_id": f["tenant_id"],
            },
        }
        if "runtime_authority" in f:
            ctx["runtime_authority"] = copy.deepcopy(f["runtime_authority"])
        return ctx

    def grant_status(self, grant_id: str):
        if grant_id != self.authority_id:
            return None
        try:
            revision, status = self._state()
        except ValueError:
            return None  # unmappable lineage -> CP-native status_unreadable
        f, o = self.facts, self.origin
        return self.cp.GrantStatus(
            grant_id=self.authority_id, revision=revision, status=status, observed_at=f["evaluation"]["status_observed_at"],
            version=f["evaluation"]["status_version"], status_ref=f["evaluation"]["status_ref"],
            authority_basis_ref=o["external_mandate_ref"], institution_id=o["institution_id"],
            authority_domain=o["authority_domain"], tenant_id=f["tenant_id"])

    def _common(self):
        return {"observed_at": self.facts["evaluation"]["observed_at"], "institution_id": self.origin["institution_id"],
                "authority_domain": self.origin["authority_domain"]}

    def identity_status(self, acting_identity: str, principal: str):
        f = self.facts
        known = acting_identity == f["acting_identity"] and principal == f["principal"]
        return self.cp.IdentityStatus(
            identity=acting_identity, principal=principal, authenticated=bool(known and f["identity"]["authenticated"]),
            delegation_valid=bool(known and f["identity"]["delegation_valid"]), chain=list(f["identity"]["chain"]) if known else [],
            **self._common())

    def issuer_mandate(self, issuer: str, issuer_role: str):
        i = self.facts["issuer"]
        known = (issuer, issuer_role) == (i["issuer"], i["issuer_role"])
        return self.cp.MandateStatus(
            issuer=issuer, issuer_role=issuer_role,
            issuance_record_ref=i["issuance_record_ref"] if known else "urn:cognous:g2-synthetic:issuance-unknown",
            mandate_valid=bool(known and i["mandate_valid"]), **self._common())

    def approval_status(self, approval_ref: str):
        a = self.facts["approval"]
        if approval_ref != a["approval_ref"]:
            return None
        revision, _ = self._state()
        return self.cp.ApprovalStatus(
            approval_ref=approval_ref, role_id=a["role_id"], approver=a["approver"], grant_id=self.authority_id,
            grant_revision=revision, proposal_commitment=a["proposal_commitment"],
            policy_versions=[{"ref": self.facts["policy"]["ref"], "version": self.facts["policy"]["version"]}],
            tenant_id=self.facts["tenant_id"], runtime_authority_commitment=a.get("runtime_authority_commitment"),
            **self._common())

    def policy_status(self, ref: str):
        p = self.facts["policy"]
        if ref != p["ref"]:
            return None
        return self.cp.PolicyStatus(ref=ref, version=p["version"], status=p["status"], tenant_id=self.facts["tenant_id"],
                                    **self._common())

    def conflict_status(self, requirement_id: str):
        if requirement_id != self.facts["requirement"]["requirement_id"]:
            return None
        return self.cp.ConflictStatus(requirement_id=requirement_id, state="clear",
                                      conflict_refs=list(self.facts["conflicts"]["precedence_refs"]), **self._common())

    def evidence_status(self, obligation_id: str):
        return None  # no evidence obligations are declared by the synthetic requirement

    def role_mapping(self, institution_id: str):
        if institution_id != self.origin["institution_id"]:
            return None
        rm = self.facts["role_mapping"]
        digest = self.cp.commitment({"institution_id": institution_id, "version": rm["version"], "aliases": rm["aliases"]})
        return self.cp.RoleMappingStatus(institution_id=institution_id, version=rm["version"], digest=digest,
                                         aliases=copy.deepcopy(rm["aliases"]))

    @contextmanager
    def authority_effect_handoff(self, ref: str):
        with self._lock:
            yield

    def authority_effect_snapshot(self, ref: str):
        ctx = self.authority_context(ref)
        if ctx is None:
            return None
        grant = ctx["grant"]
        return {"context": ctx, "grant_status": self.grant_status(grant["grant_id"]),
                "approvals": {r: self.approval_status(r) for r in grant["approval_refs"]},
                "policies": {i["ref"]: self.policy_status(i["ref"]) for i in grant["policy_versions"]}, "evidence": {}}
