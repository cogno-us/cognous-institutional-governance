# Authorization-to-effect synthetic adapter

**Executive summary:** this adapter models approval, changes, local commit,
observation and retry separately. It checks invented conditions against actual
local SQLite writes. It tests mechanics, not real authority, institutional
independence, live agents or production enforcement.

## Inputs and comparator design

[Twenty fixtures](../fixtures/authorization-effect/cases.json) pair ten primary
cases with ten legitimate countercases from the [battery](../battery/AUTHORIZATION_EFFECT.md).
The three arms are:

- `authorization_only_toy`: validates initial permission, then ignores subsequent
  conditions and blindly repeats requested deliveries. This is a deliberately
  inadequate negative control, not observed organizational practice.
- `conventional`: rechecks relevant conditions and uses the guarded effect/retry rules.
- `alvorada_inspired`: the same guarded rules, plus explanatory authority,
  continuation, custody and verification-limit fields.

The two guarded effect policies are identical by design. No incremental effect
benefit may be inferred from comparing them. Record usefulness needs independent
human assessment; this adapter does not test it.

## Actual local mechanism

[The runner](run_authorization_effect.py) takes effect binding, invented initial
conditions, scheduled changes, logical times, partial-delivery and observation
flags. The eligibility function sees state/binding/time, never case IDs or expected
outcomes. A test oracle compares results after execution. Input metadata is authored,
not authenticated or discovered; there is no probabilistic confidence cutoff.

The runner records initial approval, checks again before execution, applies any
scheduled intervening change and rechecks at commit. Commit evaluation and local
writes share one SQLite transaction/connection. The represented clock uses 0 for
approval, 10 for first check, 11 for first commit, then 12/13 for a retry. Critical
expiry is exclusive: time equal to expiry is no longer valid. These numbers are
fixture coordinates, not recommended TTLs or deadlines. Grant and evidence
conditions are explicit, while optional UNKNOWN is not an execution prerequisite.

Deliveries contain actual target/policy/action, effect identity and part number.
The guarded database has a unique `(effect_id, part)` constraint; retries retain
the effect identity but create separate attempt identities. An observed complete
effect is not repeated. A known partial effect can complete remaining parts;
an unobservable effect defers a requested retry. The toy lacks deduplication.
This does not implement remote idempotency, distributed atomicity or concurrency
across multiple executor connections.

The observer API supports reading, not execution, and its forbidden operation is
unit-tested. No credential, process or network isolation follows from that API.
Missing post-effect observation remains `EXECUTED_UNCONFIRMED`. A separate
simulated verifier checks observed complete delivery, duplicate count and intended
payload. `COMPLETE_VERIFIED` / `VERIFIED_SYNTHETIC` mean only that simulated check;
no institutionally independent verifier or verified institutional effect exists.
Known partial delivery is `PARTIAL_OBSERVED`; unavailable verification yields
`COMPLETE_UNVERIFIED`. Holds and reviews preserve their specific reasons.

## Coverage limits and ODES

The synthetic evidence envelope carries claimed source, effect subject, observation
and expiry coordinates, version, scope, dependencies and uncertainty. These are
invented metadata, not ODES schema validation, signatures, trust profiles or proof
of truth. Supersession is represented narrowly by a changed relevant policy/target
or revoked grant, not a complete source-lineage service.

The adapter has no LLM, human review, affected-person access, legal determination,
separate evidence custodian, real conflicting sources, distributed commit protocol,
external tools, hostile credentials or end-to-end production mediation. All state,
authority and verifier observations are controlled by the same process. A blocked
fixture establishes response to supplied labels, not discovery of an actual defect.

## Reproduce and preserve evidence

From the repository root, Python 3.10+:

```sh
python3 testing/harness/run_authorization_effect.py --output testing/runs/authorization-effect-repeat
python3 -m unittest discover -s testing/harness -p 'test_authorization_effect.py' -q
python3 testing/harness/verify_authorization_effect.py
```

Use a new output directory. The runner refuses existing directories and paths
under `testing/results/`; it exits nonzero for any guarded oracle mismatch.
[The archive](../results/2026-10-05-authorization-effect-v1/README.md) pins fixture,
adapter and unit-test hashes, raw input/observations, environment and limitations.
The [verifier](verify_authorization_effect.py) checks hashes, exact deterministic
replay, primary/positive pairs and guarded oracles without rewriting the archive.
Future changes need a new archive/version and must preserve adverse results.
