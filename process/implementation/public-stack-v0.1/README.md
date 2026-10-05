# Public-stack implementation profile 0.1.0

**Summary:** Alvorada describes who may decide and how decisions can be challenged.
This proposed profile makes those requirements inspectable by software without
turning a schema, signature or blockchain record into permission to act.

**PROPOSED PENDING GOVERNOR REVIEW. NOT ADOPTED, RATIFIED OR A RUNTIME.**
Read the [provision mapping](MAPPING.md), [Authority Context specification](AUTHORITY_CONTEXT.md),
[worked cases](WORKED_CASES.md) and [checks and limits](../../../testing/fixtures/authority-context/README.md).
The [schema](authority-context.schema.json) and [examples](examples/routine.json)
are public reference material under the existing repository license.

## Sources and scope

Baseline: `76cdff90d0370632faa4e033749c552fd6bbd37d`. No AGENTS.md was present.
[GOVERNANCE.md](../../../GOVERNANCE.md), [contribution guidance](../../../CONTRIBUTING.md)
and [documentation structure](../../../docs/DOCUMENTATION_STRUCTURE.md) apply.
The [Constitution v0.1](../../../constitutional-design/drafts/CONSTITUTION_v0.1.md)
and its recorded decisions remain unchanged. The [constitution directory](../../../constitution/README.md)
contains no adopted law. Design decisions are distinct from institutional adoption.

This profile reuses the [authorization-to-effect contract](../../AUTHORIZATION_EFFECT_CONTRACT.md),
[proportional procedures](../../PROPORTIONAL_GOVERNANCE.md),
[rights and interfaces](../../RIGHTS_RECORDS_AND_INTERFACES.md),
[stewardship](../../OPERATIONAL_STEWARDSHIP.md),
[modular framework](../../../constitutional-design/modular/README.md),
[enterprise-agent guidance](../../../applications/enterprise-ai-agents.md) and
[human-authorized learning](../../VIRTUOUS_RECURSION.md). It extends mappings,
not constitutional principles, thresholds, offices or source precedence.
All cited supporting guidance is the unadopted, unnumbered revision at the baseline
commit unless an explicit version is stated. Pin that commit for reproducibility;
newer guidance requires an explicit profile compatibility review.

An institution must select an actual lawful authority basis. Principle-inspired
practice, a separately adopted modular adaptation and full v0.1 adoption have
different sources. Do not inherit full v0.1 legitimacy, membership or office terms
from a commercial profile. Applicable law and the institution's validly adopted
rules control; supporting guidance cannot override them. If the selected basis
conflicts with this profile, hold the affected path for competent resolution.
The reference evaluator supports only invented principle-inspired practice;
other adoption modes are representable but deliberately not validated by it.

## Upstream technical baselines

The Governor supplied BitRep commit `5b5077dafde232a7801cb425c4efddcffb468723`
and The Index commit `d5e45d275cb301d9684b543e93b05997991d1cf2` as accepted
provisional baselines. They were not retested here. BitRep issuer verification
under a trusted snapshot and Index chain commitments/lifecycle records provide
bounded technical evidence. Index BitRep verification remains off-chain.
No valid signature, wallet, chain inclusion, claim status or technical identity
establishes office legitimacy, an institutional grant or permission to act.

## Consumer mapping — all proposed, pending Governor review

| Consumer | Proposed input / obligation | Boundary |
|---|---|---|
| Action Manifest | Refer to requirement ID, institutional domain, declared action/targets/limits, consequence and evidence obligations; reference the selected profile version | Manifest declares requirements; it neither issues a grant nor adopts Alvorada. No claim about existing Manifest field compatibility. |
| Control Plane | Resolve actual grant, issuer mandate, acting identity, parent chain, approvals, policy/current status and rule conflict; bind decision to operation and effect | Return its separate decision with reasons and supported controls. A schema pass or reference check cannot become a production allow result. |
| Execution component | Authenticate decision/adapter binding; enforce target, payload, limits, credentials and revalidation at the effect boundary | Prevent bypass and duplicate effects, observe actual delivery and reconcile uncertainty. Recheck relevant authority; do not rely solely on an earlier gate. |
| Evidence / Replay / ODES | Link requirement, grant/revision, policy versions, decision, effect, attempts, observations and remedy; retain provenance and unsupported controls | Evidence packaging is not authority or delivery verification. ODES export requires a separately reviewed adapter/profile; no conformance claimed here. |
| BitRep / Index | Supply attributed evidence and knowledge provenance where relevant | Neither automatically populates authoritative mandates or current revocation. A trusted institutional resolver must separately establish those. |
| Institutional humans | Issue grants within actual mandates, resolve conflicts, review reserved choices, hear appeals, authorize remedies and change | Staffing, independence, accessibility and power to remedy remain real obligations, not software fields. |

## Version and migration

Authority Context and implementation profile are both proposed **0.1.0**. Exact
version support is required; reject unsupported versions rather than coerce them.
Schema identifier `urn:cognous:alvorada:authority-context:0.1.0` is an identifier,
not a network resolver. References may use URNs resolved through an explicitly
trusted registry or HTTPS under a declared trust policy; validity is not access.
No adjacent repository has been changed or bound to these field names.

Migrate by resolving existing local mandates and grants into new linked records;
never mint grants from legacy policy-gate successes. Preserve old identifiers,
versions, pending effects and original records. Require explicit compatibility
mapping for Manifest, Control Plane and ODES; do not rename their fields silently.
A new context version needs schema, semantic and migration review. Changes to
constitutional ends or authority allocations remain subject to the established
human adoption/change process; repository merges cannot perform those acts.
