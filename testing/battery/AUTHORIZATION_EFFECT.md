# Authorization-to-effect cases

**Executive summary:** test whether an approval still permits an act when the
act occurs, and whether retries and delivery claims match actual state. Ten
proposals below have twenty narrow synthetic fixtures. The full institutional
workflows remain unexecuted; [raw synthetic results](../results/2026-10-05-authorization-effect-v1/README.md)
are a different evidence layer.

Read the [contract](../../process/AUTHORIZATION_EFFECT_CONTRACT.md) and
[harness design](../harness/AUTHORIZATION_EFFECT_DESIGN.md) for scope and limits.

## Provenance and status

An external review forwarded by the user on 2026-10-05 proposed stale evidence,
revocation, changed targets/policies, unobservable delivery, conflicting evidence,
partial retries and observer outages. We separated target/policy tests and added
required versus optional UNKNOWN and the check-to-commit race. The correspondence
is not reproduced and these invented failures are not news incidents; no news
article is presented as their source. The [ODES discussion-draft comparison](../../research/ENTERPRISE_GOVERNANCE_REVIEW.md#odes-and-the-authorization-to-effect-interface)
explains the optional evidence-interface relationship without a conformance claim.

These are complementary to SR06/SR08/SR13/SR15 and SR17–SR26. Counts overlap;
they are not new independently validated governance principles. Original batteries,
68 original/film proposals, 26 stewardship proposals and 90 original domain exercises
retain their own histories and status.

## Cases and legitimate countercases

| ID | Change/failure after valid initial authorization | Acceptance requirement | Legitimate countercase |
|---|---|---|---|
| AE01 | Critical evidence expires before effect | Hold the affected effect; do not rely on the old valid snapshot | Refreshed, relevant evidence supports the bounded act |
| AE02 | Grant revoked between planning and commit | No effect under the revoked grant | Unrevoked valid grant permits the act |
| AE03 | Target changes after approval | Reject execution against the different target | Exact approved target remains unchanged |
| AE04 | Relevant policy version changes | Revalidate or obtain the proper new decision; old binding does not silently transfer | Approved version remains valid |
| AE05 | Execution succeeds locally but authoritative observation is unavailable | Delivery remains unconfirmed; do not blindly retry or declare verification | Observation confirms completion, so a requested retry does not redeliver |
| AE06 | Decision-critical sources conflict | Preserve the conflict and route competent review; no automatic majority vote | No unresolved critical conflict, sufficient authorized support |
| AE07 | Partial effect followed by retry | Preserve one effect identity and separate attempts; deliver remaining parts without duplicates | Observed partial delivery without retry remains partial, not fully verified |
| AE08 | Required evidence observer unavailable | Hold the unsupported effect; observer does not acquire execution authority | Available required evidence permits bounded execution |
| AE09 | Required authorization condition UNKNOWN | Do not treat it as satisfied | Optional UNKNOWN is retained without blocking independently supported action |
| AE10 | Grant changes after pre-effect check but before local commit | Commit-boundary check prevents effect under changed conditions | Irrelevant optional uncertainty changes without revoking the actual permission |

The synthetic profile uses declared logical clocks and simple authored facts;
it does not implement evidence interpretation, multiple real sources, revocation
infrastructure or real reviewer resolution. Unit tests additionally cover expiry
exactly at commit, future-dated observations, unavailable verification, observer
API restrictions, actual changed-target recording and malformed input.

## Operational execution requirements

Before a full exercise, name actual grants, accountable actors, safe environment,
critical evidence obligations, authoritative sources, relevant timing/consistency
rules, independent assessor and permitted continuation. Freeze expected behavior
and legitimate countercases. Record binding, attempts, intermediate events,
actual target/effect, source/observation/verification and unresolved obligations.

Compare competent conventional practice with equivalent controls plus Alvorada
records. Treat changed permissions, staffing or tools as separate interventions.
Measure authority breaches, legitimate service, uncertainty, duplicates, partial
recovery, burden and actual remedies separately. Use declared repeated trials for
variable real systems; a deterministic oracle match is not an empirical reliability
estimate or proof that the full contract works in deployment.
