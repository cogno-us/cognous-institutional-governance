# G2: synthetic root-lineage → Control Plane Resolver (DEVELOPMENT ONLY)

**Synthetic, non-authorizing, unqualified, builder-lineage.** Read-only adapter from IG authority-lineage `0.1.0` ROOT records to the Control Plane's existing `Resolver` protocol, plus a decision-only driver and three functional checks. Frozen contract: Hub #273 comment 6711045444 (see 'Refusal behavior' below for one correction); authorization #273 comment 6710907924. It does not change the IG lineage schema, the Control Plane, GAX or any lock, issues no grant, and dispatches no effect.

## Pins
IG `03a90c14c4a178997df2b6e527f67452b9c6bb7a`; Control Plane `484fdbd297235dd24148ddb0703f2055a31eabff` (HEAD and a clean tree are verified before CP is imported; CP is a development-only pinned checkout via `G2_CP_ROOT`, never vendored).

## What is IG-derived vs synthetic
| IG-derived (lineage) | Synthetic fixture facts only (`fixtures/synthetic_facts.json`) |
|---|---|
| `grant_id` = `authority_id`; effective revision; status at `t` (`active/suspended/revoked`, `unknown` before `effective_at`); institution; authority domain; `authority_basis_ref` ← `external_mandate_ref` (a source reference, **not** an authenticated mandate); `not_before` ← `effective_at`; permissions ← `permission_scope` unchanged | tenant, `expires_at`, `issued_at`, status observation time/version/ref, issuer (`synthetic-ocs-vnext-ig-issuer`) + role + issuance ref, identity/principal/grantee and IdentityStatus, policy, requirement, approval, conflicts, role-mapping aliases. Role-mapping digest and the runtime-authority input digest are computed with **CP's native** `commitment`, never hand-written. |
`adapter.field_provenance()` lists this split. Revoker `synthetic-ocs-vnext-ig-revoker` and policy owner `synthetic-ocs-vnext-ig-policy-owner` are labels only; IG mutations evidence no revoker identity. Only ROOT grants: any delegation edge is refused; the grant's delegation block is fixed `{null, false, 0}`.

## Refusal behavior (as implemented)
Missing/empty required synthetic facts (including nested keys and `tenant_id`), an invalid lineage bundle, a missing/invalid `expires_at`, a delegation edge anywhere in the bundle, an unknown root, or a CP checkout that is not the pinned clean commit are **explicit adapter-level refusals** (`AdapterRefusal`, raised before CP is consulted) — not CP-native HOLDs; this corrects the contract-freeze wording, which anticipated `delegation_profile_unsupported` from CP. Inside a built resolver, an unreadable status returns `None` (CP: `status_unreadable`), a pre-`effective_at` status is `unknown` (CP: `grant_unknown`), and an unknown identity/issuer is returned as unauthenticated/invalid (CP holds). None of these refusal paths is exercised by the three checks.

## Authentication boundary
The resolver is `authenticated = False` and the CP runs under its own developer profile (`allow_synthetic_resolver=True`, `allow_test_time=True`). `IdentityStatus.authenticated=True` and `mandate_valid=True` are **fixture facts** (as in CP's own fixtures), not authentication evidence. A CP `authorized` here is a *synthetic developer-mode decision*, not institutional authorization.

## Run (local; CP checkout at the pin + pydantic; IG needs jsonschema)
```bash
G2_CP_ROOT=<control-plane checkout @484fdbd2> G2_REQUIRE=1 python -m unittest tests.test_g2_cp_resolver -v
```
Three frozen checks (t = 2026-10-05T19:00:00Z): 1 valid root → `authorized`; 2 revoked root → `hold` + `grant_revoked`; 3 status observed 120 s before `t` → `hold` + `grant_status_stale_or_future`. The suspended fixture is provided but not executed.

## Not established
Authenticated grant/issuer/revoker/mandate, adopted institutional policy, real delegation (parent grants unsupported), production authorization, independent qualification, G3.

## Rollback
Delete `process/implementation/g2-cp-resolver-dev/` and `tests/test_g2_cp_resolver.py`.
