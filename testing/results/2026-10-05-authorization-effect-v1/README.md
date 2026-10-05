# Authorization/effect synthetic execution v1

**Executive summary:** twenty fixtures produced sixty deterministic observations.
Both guarded configurations satisfied all twenty authored oracles, including all
ten legitimate countercases. The authorization-only toy satisfied nine. This
shows local mechanics on supplied conditions, not institutional effectiveness.

**EXECUTED_SYNTHETIC — NOT_INDEPENDENTLY_REVIEWED.**

| Arm | Observations | Complete oracles satisfied | Primary variants satisfied | Positive variants satisfied |
|---|---:|---:|---:|---:|
| Authorization-only toy | 20 | 9 | 0 | 9 |
| Conventional guarded controls | 20 | 20 | 10 | 10 |
| Same controls plus Alvorada-inspired records | 20 | 20 | 10 | 10 |

## Evidence and reproduction

- [Raw inputs, events, effects, oracles and results](results.json).
- [SHA-256 manifest](manifest.json): fixtures, adapter, unit tests, verifier and raw results.
- [Case proposals](../../battery/AUTHORIZATION_EFFECT.md), [fixture inputs](../../fixtures/authorization-effect/cases.json) and [harness design](../../harness/AUTHORIZATION_EFFECT_DESIGN.md).
- [Contract](../../../process/AUTHORIZATION_EFFECT_CONTRACT.md): broader proposed semantics, not validated in full here.

The raw bundle records exact UTC execution time, Python/SQLite versions, local
commit `45e76097c83f5af3940e0718c90bfd673481f412`,
a documentation/code-dirty working tree and input hashes. The controlling commit
value is the raw bundle's `repository_commit`, not this explanatory text. Public
base `7345eb2b591fcf41d44fa4845d3a42c267cb57dc` and the local base have the same
tree `69bce52944450c32c867873727354f7d21068139`. New artifact hashes pin the
working-tree implementation actually executed; the base alone does not contain it.

From the root, use a new, nonexistent directory:

```sh
python3 testing/harness/run_authorization_effect.py --output testing/runs/authorization-effect-repeat
python3 testing/harness/verify_authorization_effect.py
python3 -m unittest discover -s testing/harness -p 'test_authorization_effect.py' -q
```

The verifier checks exact replay excluding variable execution/environment/base
metadata. It does not modify this archive. Change inputs or code only through a
new version/archive with its own evidence; preserve this snapshot.

## Interpretation

AE01–AE04 prevent represented stale-evidence, revoked-grant, target and policy
changes from producing guarded effects. AE06/AE08/AE09 distinguish critical
conflict or missing conditions from optional uncertainty. AE10 represents a
change after the first check; a second check within the local commit transaction
catches it. These are authored states, not detected real-world defects.

AE05 actually writes locally while the observer is unavailable; the guarded result
remains unconfirmed and no blind retry occurs. AE07 preserves partial delivery,
then completes only missing parts when requested. The toy duplicates delivery on
retries, including the otherwise legitimate AE05 positive variant, explaining
its nine rather than ten positive matches. The oracle is not merely “block all”:
authorized work and known partial states must retain their specified behavior.

The conventional and Alvorada-inspired arms have identical effects by construction.
Additional explanatory fields cannot establish better outcomes, usable review or
independence. The negative control is intentionally inadequate and supplies no
estimate of failure prevalence in real institutions.

## Limits and remaining work

One process, one database connection, invented grants and logical clocks control
all conditions and observations. A simulated separate verifier is not independent.
The observer API's lack of execution methods is not permission or process isolation.
There is no real remote state, concurrent executor, revocation service, hostile
input corpus, cryptographic verification, ODES conformance or full mediation.

`VERIFIED_SYNTHETIC` means the simulated payload/delivery check only. Actual
institutional verification, rights, correction, staffing, trust, clocks and
cross-system consistency remain unestablished. The ten full AE workflows, 26 SR
scenarios and original application exercises remain operationally unexecuted.
Existing reference and film archives retain their own scope and original bytes.
