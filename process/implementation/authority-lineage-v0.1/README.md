# Authority lineage evidence profile 0.1.0

**Status:** proposed, non-authorizing evidence profile. This profile does not issue a grant, adopt institutional governance, resolve live authority, authorize an effect, or change constitutional text.

This bounded profile records how an independently established institutional authority was said to originate, delegate, mutate, succeed, be resolved at a point in time, and be referenced by a later decision/effect record. It complements the existing proposed Authority Context without changing that profile or any constitutional source.

## Record types

- **AuthorityOriginRecord** records an external mandate source, authority identity/revision, finite scope, and evidence references. The mandate remains external; the record does not create it.
- **DelegationEdge** records a parent-child relationship and the child's bounded scope. Synthetic qualification requires same institution/domain, existing parent, finite attenuation, and no cycles.
- **AuthorityMutationRecord** records amendment, suspension, reinstatement, or revocation chronology. Records are append-only evidence; later mutations do not erase earlier facts.
- **AuthoritySuccessionRecord** records predecessor/successor chronology and separately referenced successor mandate. Its fixed continuity semantics are `no_automatic_permission_transfer`.
- **AuthorityResolutionCommitment** commits to a resolver snapshot and lineage set at a stated time. It is evidence of a resolution, not a live resolver response or permission token.
- **AuthorityUseLink** links a decision/effect evidence record to the exact authority revision and resolution commitment it relied on. It never transfers permission.

The JSON Schema is `authority-lineage.schema.json` (`urn:cognous:alvorada:authority-lineage:0.1.0`). All six record types carry `non_authorizing: true`; portable bundles require `transfers_permission: false`.

## Synthetic semantics qualified

The scoped harness checks the following finite invariants:

1. a child delegation cannot add actions, targets, data scopes, amount, effect count, or a different unit beyond its parent;
2. delegation parents and referenced lineage records must exist, and delegation cycles fail closed;
3. a resolution commitment cannot claim a revision/status inconsistent with mutations effective at its resolution time;
4. a use link must reference an existing commitment for the same authority/revision and cannot rely on a commitment older than a mutation already effective when the use occurred;
5. a revoked or suspended current status cannot be represented by a later use as if active;
6. succession preserves chronology but does not copy permission; the successor needs its own independently evidenced origin/delegation lineage;
7. historical commitments remain historical evidence after later mutation, while current-use checks use the latest effective lineage known at the use time;
8. evidence can be exported and hashed without transferring permission or creating authority in the recipient;
9. validity dates are enforced for the synthetic checks: an origin's `effective_at` and each delegation's `valid_from` (inclusive) and `expires_at` (exclusive, `null` is open-ended) bound every point on the chain to an authority. A `referenced` use link, or a resolution commitment with status `active`, outside that window is refused; a `held` or `rejected` use stays representable. A delegation window must be non-empty and lie inside its parent's window.

An effective authority is derived from a single lineage, never from the union of two independent principals' scopes.

Mutation and edge checks: every mutation's amended scope must be contained in the parent's effective scope at its `effective_at` (a delegate) or in the origin's own base scope (an origin); a delegation edge is checked against the parent's effective scope and revision at `delegated_at`. A later parent narrowing is not applied retroactively, and revocation or suspension of a parent is not propagated to its children. A commitment's `lineage_record_ids` must include the origin and every edge on the chain and may add only mutations of chain members. `scope_digest`, `source_set_digest` and `source_bundle_digest` are format-checked only: no digest recipe is defined, so they are not recomputed. Replayed uses and `max_effects` counts are not checked.

Status, succession and timestamp checks (added 2026-10-22): an `amend` mutation must keep the effective status (`status_after` equal to the status before it), so a revoked or suspended authority cannot become active through an amendment; reinstatement rules are still not checked (a `reinstate` is accepted when its `status_after` is `active`). A succession is refused when predecessor and successor are the same authority, or when the successor is an ancestor or a descendant of the predecessor along delegation edges; a successor in a different delegation chain is not otherwise checked. Every `date-time` value must be a full RFC 3339 date-time with an explicit offset (`Z`, or `+hh:mm`/`-hh:mm`); the harness checks this itself because the pinned `jsonschema` does not check `format: date-time` without an extra validator package. Naive times, date-only values and a leap second (`:60`) are refused with a typed error, not a raised exception.

Known limits of the date checks: windows come from the delegation chain and the origin only. A mutation recorded after a delegation expired, and lineage-level dates on succession records, are not checked.

The harness runs semantic checks only on schema-valid bundles. It rejects non-finite (NaN or infinite) parent and child amounts, and it reports malformed input reached by the semantic pass as error strings, not exceptions.

These checks are synthetic and conservative. They do not authenticate institutional sources, determine lawful mandate, validate cryptographic signatures, provide a production resolver, propagate revocation, enforce runtime permissions, or prove field adoption.

## Boundaries and dependencies

Source branch baseline: `1386fd236f13896029e5ab47ba5b9c3127509c3d` from issue #42. Repository contribution guidance, the existing authorization-to-effect contract, and Authority Context 0.1.0 remain controlling background. No constitutional file, runtime grant issuer, Control Plane path, or live resolver is modified.

Downstream consumers must continue to authenticate their actual authority source and obtain current effect-time authorization through their own trusted boundary. A valid lineage bundle, a successful schema check, a resolver commitment, a portable digest, or an AuthorityUseLink is evidence only.
