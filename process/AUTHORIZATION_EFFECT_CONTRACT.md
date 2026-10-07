# Keep authorization valid through the effect

**Executive summary:** approval is a conditional permission, not a guarantee that
an action may still happen later. Check the conditions that matter at the effect
boundary, preserve unknown delivery states and reconcile retries against what
actually happened. Evidence providers never acquire authority by observing events.

Use this proposed contract with [operational stewardship](OPERATIONAL_STEWARDSHIP.md).
See the [synthetic cases and limits](../testing/battery/AUTHORIZATION_EFFECT.md).
[Detailed semantics](#detailed-semantics) follow; routine authorized work can use a
bounded class rather than repeated individual approval.

## Detailed semantics

**PROPOSED IMPLEMENTATION CONTRACT; NOT AN AMENDMENT OR PRODUCTION RUNTIME.**
This formalizes an interface between existing institutional distinctions. It
supplies neither grants nor a new office. Actual rules, people, permissions,
resources and safeguards remain necessary. The reference adapter is a narrow
local demonstration; it is not the contract's complete implementation.

An external review supplied by the user on 2026-10-05 identified the gap between
valid authorization at one time and permissible effect later. This document and
its new cases respond to that contribution. The correspondence is not reproduced.
The related [ODES comparison](../research/ENTERPRISE_GOVERNANCE_REVIEW.md#odes-and-the-authorization-to-effect-interface)
uses the supplied discussion draft, not a claim of settled standard conformance.

## 1. Keep roles separate

| Function | Responsibility | Boundary |
|---|---|---|
| Producer / observer | Supply attributable observations and their limitations | Cannot grant authority, settle legitimacy or execute because evidence is missing |
| Evidence envelope | Carry source, subject, time, version, scope, dependencies, uncertainty and supersession | A portable claim, not proof of world state or a permission token by itself |
| Authority / decision | Decide under an actual grant with relevant evidence and constraints | Capability, verifier acceptance and a complete record do not confer authority |
| Pre-effect revalidation | Check the obligations relevant to that specific permission | Cannot renew a revoked grant, invent an exception or change the approved payload |
| Executor | Attempt the authorized bounded effect under enforced permissions | Cannot label its own report as independent observation or verification |
| Post-effect observer | Establish delivered, partial, contradicted or unknown state | Local success, tool acknowledgment and remote authoritative delivery differ |
| Verifier / reconciler | Check claims against actual sources, independence and pending obligations | Reconciliation does not create the authority needed for a new corrective act |

These may be existing human or software functions. Naming separate services is
not independence; use the [effective-control procedure](RIGHTS_RECORDS_AND_INTERFACES.md).
Design access so an observer can provide evidence without execution credentials.
An evidence outage cannot transfer execution power to the observer.

## 2. Bind the decision to the intended effect

Before execution, assign a stable **effect identity**, linked to the decision,
actual grant and approved action, target/recipient, scope/amount, policy/version,
conditions, duration and relevant approval. Give each attempt its own identity.
Use explicit authority to define any allowed variability or class-level scope.

A reused effect identity must not silently refer to a new target, payload or
purpose. Material changes require the proper decision and a new or explicitly
superseding effect binding, while preserving the old effect's unresolved state.
A superseding approval does not erase a prior attempt or delivered harm. Local
and remote systems need a declared mapping of their identifiers; no particular
identifier format, hashing scheme or shared ledger is mandated here.

## 3. Declare evidence obligations before relying on them

For each material condition, record what proposition must be supported, its source
and subject, allowed versions/scope, observation time, freshness/expiry rule,
dependencies, supersession/revocation source and unavailable/conflict semantics.
Identify who is competent to set and assess that rule. Separate mandatory
conditions from optional context and post-effect obligations. Freshness alone
cannot establish truth; a recent irrelevant observation is not sufficient.

An envelope should preserve claimed provenance, source version, observation and
receipt times where relevant, effect/subject scope, uncertainty, dependency links
and correction/supersession history. Producer identity or signature authenticity
is different from legitimate authority and the truth of the claim. Actual trust,
clock uncertainty, propagation delays and source availability must be assessed.
Do not prescribe a universal time-to-live or demand excessive personal data.

## 4. Give UNKNOWN obligation-specific consequences

| Unknown state | Continuation semantics |
|---|---|
| Optional contextual fact | Preserve it; continue only if remaining evidence and the grant independently suffice |
| Required authorization condition | Do not treat it as satisfied; obtain competent clarification/revalidation or hold the affected effect |
| Conflicting decision-critical sources | Preserve provenance and conflict; use competent resolution rather than vote-counting or automatic overwriting |
| Post-effect authoritative observation | Keep delivery unconfirmed; investigate and reconcile before a potentially duplicating retry |
| Verification unavailable | Delivery may be observed but verification remains pending; do not declare independently verified institutional completion |

A hold applies to the unsupported effect. Other sufficiently authorized work may
continue, and essential service/claims need a lawful continuity route. UNKNOWN
cannot be converted into an emergency grant. A record failing acceptance under a
profile is not automatically a prohibition on every alternative lawful workflow.

## 5. Revalidate relevant conditions at the effect boundary

Check that the grant remains valid and unrevoked, the approved binding still
matches, critical evidence meets its contextual requirements, no material
superseding condition has appeared, and unresolved obligations permit this act.
Evaluate relevant dependencies and actual permissions. Routine class grants may
supply these conditions; every action need not return to a committee.

A check immediately before execution still leaves a possible check-to-commit gap.
Declare the effect boundary and the implementation's consistency guarantee:
which authoritative resources participate, which concurrent changes are detected,
and what cannot be coupled to the effect. Where possible, validation and the
local effect share a serialized transaction or equivalent enforceable boundary.
This is an implementation option, not a universal cross-system guarantee.

Where external effects cannot be coupled to validation, explicitly state residual
race/propagation risk, permitted exposure, narrower-use/stop conditions and
observation/reconciliation duties. A deadline or fresh signature alone cannot
close that gap. Compensating correction may reduce harm but cannot guarantee
reversal of physical, financial, disclosed or otherwise irreversible effects.

## 6. Preserve lineage without equating stages

| Record / state | What it establishes |
|---|---|
| Decision | A disposition represented as made under a stated grant |
| Authorized effect | The bounded effect and conditions approved, not delivered |
| Attempt | A particular request/attempt against that effect; denial or failure remains visible |
| Executed effect | Executor evidence of the actual operation, including partial results |
| Observed effect | Authoritative-source evidence of delivery, non-delivery, partial state or contradiction |
| Verified institutional effect | Competent verification of the relevant effect with disclosed sources, actual independence and remaining obligations |

These are linked records, not a claim that every stage exists or follows without
uncertainty. Keep timestamps, versions, attempt identifiers, actual targets,
contradictions, pending claims and remedy status. Partial completion need not mean
failure of every part, and technical completion does not settle institutional duties.

## 7. Retry and reconcile against actual state

Determine what was delivered and what remains before repeating a consequential
act. Retain the effect identity for a genuine retry and separate attempt identities.
Use an enforceable duplicate-prevention mechanism appropriate to the actual
systems; a label called “idempotent” proves nothing. Changed effect payloads must
not bypass a new authorization decision by reusing an old identifier.

When observation is unavailable, retain an unresolved state and escalate or use
an actually authorized safe continuation. Do not assume either success or failure.
Restart must recheck current permissions and conditions. Corrective operations
have their own grants and effect records; they cannot retroactively legitimize an
unauthorized original act. Preserve lawful claims through suspension or replacement.

## 8. ODES is an optional evidence interface

The supplied ODES v0.2 narrative retains its v0.1 schema reference. It proposes
decision identifiers, authority metadata, evidence commitments, model context,
freshness, revocation/supersession and reliance conditions. It distinguishes
schema validity, profile conformance, verifier acceptance and a relying party's
own decision. Runtime enforcement and settled trust/cryptographic profiles remain
outside that draft's scope.

ODES can carry relevant decision evidence, but this contract's effect/attempt
identities and commit-boundary semantics are **proposed complementary concepts**,
not existing ODES requirements. No new field names or conformance profile are
asserted here. Alvorada can use other adequate records; ODES is not a proprietary
or mandatory dependency. Neither record acceptance nor synthetic success proves
authority, actual review, lawful reliance or institutional benefit.

## 9. Proposed first implementation stage and remaining work

This document specifies shared semantics and acceptance questions. A bounded
first stage should identify one decision/effect type, actual owner and grant,
required conditions, source/version rules, effect boundary, retry mapping,
observation/verification obligations and tests before expansion. It is proposed
scope, not an approved implementation schedule or completed adoption.

Further work includes real identity/permission separation, source authenticity,
revocation propagation and clocks, distributed/remote failure, effective-control
independence, domain-specific continuation rules, ODES interoperability if chosen,
participant access, adversarial assessment and comparative outcome/burden evidence.
The [test design](../testing/harness/AUTHORIZATION_EFFECT_DESIGN.md) makes explicit
which small subset is represented by the synthetic adapter.
