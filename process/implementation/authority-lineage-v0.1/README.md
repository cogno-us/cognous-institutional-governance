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
8. evidence can be exported and hashed without transferring permission or creating authority in the recipient.

These checks are synthetic and conservative. They do not authenticate institutional sources, determine lawful mandate, validate cryptographic signatures, provide a production resolver, propagate revocation, enforce runtime permissions, or prove field adoption.

## Boundaries and dependencies

Source branch baseline: `1386fd236f13896029e5ab47ba5b9c3127509c3d` from issue #42. Repository contribution guidance, the existing authorization-to-effect contract, and Authority Context 0.1.0 remain controlling background. No constitutional file, runtime grant issuer, Control Plane path, or live resolver is modified.

Downstream consumers must continue to authenticate their actual authority source and obtain current effect-time authorization through their own trusted boundary. A valid lineage bundle, a successful schema check, a resolver commitment, a portable digest, or an AuthorityUseLink is evidence only.
