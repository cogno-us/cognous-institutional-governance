# Proposed Authority Context 0.1.0

**Summary:** A requirement says what authority an action needs. A grant records
what an issuer claims to have issued. A downstream decision determines whether
a particular effect may proceed under authenticated, current conditions. Keep
those three objects distinct.

**PROPOSED CROSS-COMPONENT INTERFACE; PENDING GOVERNOR REVIEW.**
The [JSON Schema](authority-context.schema.json) checks structure, formats and
exact version. [Reference fixtures](../../../testing/fixtures/authority-context/README.md)
check a finite subset of semantics under synthetic assumptions. Neither is a
permission service. Start with [worked cases](WORKED_CASES.md).

## Record fields and meanings

| Field | Meaning and required resolution |
|---|---|
| `schema_version`, `interface_status`, `context_id` | Exact proposed version 0.1.0, explicit review-pending label and stable context identifier |
| `institution` | Institutional ID, authority domain, independently resolvable authority basis and selected mode; modes do not prove adoption |
| `principal`, `acting_identity` | Responsible principal receiving a grant and authenticated identity acting for it; neither is established by a supplied string |
| `accountable_human_role` | Human principal, role and actual mandate reference; human accountability cannot be replaced by a wallet or model |
| `requirement` | Stable requirement ID, governing provisions/version/standing, finite permitted action envelope, required approval roles and evidence/consequence profile; not an issued grant |
| `conflicts` | Ordered precedence references, incompatible role pairs and competent escalation, appeal, continuity and remedy procedures; no arbitrary numeric priority overrides law |
| Optional `grant` | Claimed issued grant, issuer/role/issuance record, principal and acting identity binding, revision, validity/status, finite permissions, delegation and actual approval references |
| `supporting_evidence_refs` | Provenance including optional BitRep/Index/ODES records; no authority is derived from their technical acceptance |
| `change` | Proposal kind/reference and optional separately verifiable adoption record; outcome feedback remains evidence, never an adoption event itself |

No `runtime_decision` or `allowed` field is accepted. A requirement-only context
is structurally valid and cannot satisfy the reference check for an issued grant.
The grant's permissions must fit inside the requirement envelope, but an envelope
is not a power to issue grants. Runtime authorization belongs to the Control
Plane and effect boundary; it must identify the grant/revision, actual operation,
target, payload, policy, effect/attempt identities and decision conditions.

### Scope, approvals and evidence

Permissions use exact action names, finite target URNs, finite data-scope names,
nonnegative amount/unit and effect-count caps. No implicit wildcards, hierarchy,
unit conversion or fuzzy matching exists. `max_effects` is a declared bound, not
a cumulative counter. Downstream must enforce shared budgets and counts across
parallel actions/descendants; giving two children the full parent cap does not
authorize spending twice that cap. More complex scopes require a separately
reviewed profile, not silently broadened string interpretation.

Approval requirements list role and actor-independence obligations. Grant
approval references point to actual records, which must bind approver mandate,
grant/revision, effect/action content, relevant policies, time and status. A
standing class approval authorizes only that class; it does not meet a reserved
case approval by analogy. The local reference inputs bind case approval using
SHA-256 over sorted compact JSON of the invented action. That is a local fixture
convention, **not a proposed universal signing/canonicalization standard**.

Each evidence obligation declares source, kind, freshness and UNKNOWN behavior:
required authorization evidence uses `hold_effect`; optional context uses
`preserve_if_other_basis_suffices`; post-effect observation uses
`reconcile_no_blind_retry`. No universal time-to-live is supplied. A downstream
profile must define competent freshness judgments, subject/dependency binding,
source authenticity and receipt/clock uncertainty. Required unknown does not
prohibit every other adequately authorized service route.

Consequence T0–T4 is the existing proposed consequence/reliance classification.
It is neither a PRP reasoning level, Index epistemic status nor implementation
maturity score. The competent human owns classifications; this schema cannot
validate a tier's accuracy or generate a downgrade.

## Authority lifecycle

| Event | Required institutional act and effect on current work |
|---|---|
| Issuance | Actual issuer within independently established mandate issues a bounded, recorded grant. Technical signature authenticity is separately assessed. Requirements/manifest declarations cannot issue it. |
| Activation / expiry | Begin only at `not_before`; at `expires_at` the grant is invalid, with exclusive expiry. Check trusted clocks and uncertainty; renewal requires competent issuance. Pending effects do not inherit prior permissibility. |
| Suspension | A competent status authority marks a reversible hold. Stop affected new effects, preserve observed/unknown attempts and legitimate continuity; restoration requires competent status and revalidation. |
| Revocation | Invalidate future reliance on the grant and descendants; no local cached pass renews it. Already delivered effects remain attributable and may require authorized remedy. |
| Amendment | Retain grant ID with explicit revision or issue a superseding grant with a documented link. Bind decisions/approvals to exact revisions; changed scope cannot silently reuse an old decision/effect. Preserve history and unresolved obligations. |
| Policy-version change | Assess applicability/effective time under controlling rules. The reference check holds on any pinned/current mismatch. Grandfathering, if lawful, needs explicit authenticated transition rules and a reviewed implementation extension. No automatic migration. |
| Delegation / parent change | Authenticate all ancestors; child scope, validity and obligations cannot exceed or weaken parent. Revoked, suspended, expired or materially revised parent requires descendant revalidation or competent reissuance. |
| Human turnover / termination | Determine surviving authority under actual succession and continuity rules; credentials alone cannot assume an office. Preserve appeals, pending delivery and custody, and rebind or reissue only by competent authority. |
| Outcome feedback | May support a policy or constitutional proposal. The correct reserved human process separately adopts a change; no benchmark, majority of agent outputs, transaction or successful run may substitute. |

The authoritative status resolver must return grant ID/revision, active status,
observation/version, authority basis and any supersession information. Its actual
trust, availability and propagation guarantees must be declared. The local
fixture status dictionary represents only active/suspended/revoked and revision;
it is not a live revocation service or complete lifecycle implementation.

### Delegation and conflicts

Authenticate the issuing office and the delegate's permitted issuing capacity,
not just parent possession. Require explicit delegation permission, bounded depth,
acyclic lineage, same institution/domain, exact policies, child identity binding,
attenuated permissions/validity and retained approval/evidence/conflict duties.
Evaluate all ancestors, not just the nearest parent. Reserve constitutional ends,
reserved judgments and changes to humans under controlling rules. Delegation
cannot confer foundational sovereignty.

The reference checker supports equal required approval/evidence/conflict schedules
across a chain, a conservative subset. Additional stricter child requirements
need compatibility review; they are not automatically accepted. It checks parent
and child required approvals separately. Real implementations must define class
approval versus effect approval and approve descendants explicitly where needed.
Cyclic/deep/absent chains, unknown status, conflicting mandates, incompatible roles
or unresolved precedence must not become authorization. The local checker is not
hardened for adversarial unbounded input; runtime limits are a downstream duty.

Conflicts go to the identified competent procedure, with nonconflicted review;
"most recent", strongest signature, most supported claim or model agreement is
not conflict precedence. A reference with a valid URI is not a reachable, fair
or properly staffed escalation route. Specify actual service/claims continuity
and remedy powers locally. A corrective effect requires its own authority.

## Downstream authentication and effect-boundary duties

Before relying, authenticate the selected authority basis/adoption where claimed,
issuer mandate, principal/acting identity, requirement/profile integrity, status
source, all ancestors, approver role and practical independence, and relevant
source/policy versions. Authenticate actual grants and records under the selected
trust policy; do not treat arbitrary caller-supplied context/snapshots as trusted.

Initial policy evaluation determines a conditional decision. Immediately before
a consequential effect, revalidate grant/revision, revocation/ancestors, approvals,
policy, payload/target/adapter, required current evidence, permitted remaining
budgets and unresolved delivery obligations. At commit, implement the consistency
boundary described in [the existing contract](../../AUTHORIZATION_EFFECT_CONTRACT.md#5-revalidate-relevant-conditions-at-the-effect-boundary).
A fresh cache or signature leaves a race unless relevant changes and effect are
coupled. Declare status maximum age, clock uncertainty, revocation propagation,
atomicity limits and authorized exposure. No universal zero-staleness guarantee
is asserted. Unknown authoritative status holds affected consequential effects;
use an actual authorized continuity route, never invent emergency authority.

Afterward, preserve stable effect and separate attempt identities, obtain actual
authoritative observation, reconcile partial/unknown outcomes before retry, and
verify/remedy under separate competent responsibility. Current local checks
execute no adapter, enforce no credentials or budgets and observe no destination.

## Reference validation scope

`schema_errors` uses Draft 2020-12 with URI/date-time format checks. It cannot
resolve references, validate issuer legitimacy or establish current permission.
`reference_errors` assumes a supplied synthetic snapshot: allowed mandates,
requirement binding, active roles, current policies/status, sources and approval
records. It checks those represented premises, not their truth. A passing result
means only **reference conditions satisfied under assumed inputs**.

The snapshot's trusted requirement binding covers institution, human role,
requirement and conflicts to expose caller changes. Real deployments need a
reviewed signing/canonicalization and authenticated resolver design. The reference
inputs deliberately support only principle-inspired examples, not full adoption,
constitutional amendment proof, sophisticated scope logic or distributed effects.
No cross-repository interface compatibility, ODES conformance, legal compliance,
field efficacy or independent review is established.
