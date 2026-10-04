# Film-review execution v1 — 2026-10-04

**EXECUTED_SYNTHETIC — NOT INDEPENDENTLY REVIEWED**

[Raw observations](results.json), [frozen fixture copy](fixtures.json), [harness copy](run_film_review.py.txt), [verifier copy](verify_film_review.py.txt), and [hash manifest](manifest.json) preserve this run. The active [design](../../harness/FILM_REVIEW_DESIGN.md) defines policy, oracles, provenance and limits.

## Final run results

| Configuration | Runs | Complete oracles satisfied | Positive variants with intended effects | Positive complete oracles |
|---|---:|---:|---:|---:|
| Permissive toy negative control | 42 | 15 | 21/21 | 15/21 |
| Conventional controls | 42 | 42 | 21/21 | 21/21 |
| Alvorada-inspired records, same controls | 42 | 42 | 21/21 | 21/21 |

Complete oracles include evidence-record counts as well as action outcome, both table states and retained history. The toy completed all positive actions but omitted represented unknowns in six cases. Its 27 misses are not 27 real institutional failures. The primary TB09 case permits a supported action with a missing-note unknown; the toy matches its effect but loses the unknown, so the complete oracle fails.

The two guarded arms have identical effect controls by construction. Five extra fields in the Alvorada-inspired record cannot establish better judgment, independent review or institutional effectiveness. No human reviewer completed a REVIEW case; it remained a simulated queue outcome. HOLD/REVIEW mean no new represented account restriction occurred.

## Mapped primary and positive subtests

This is narrow mechanical coverage. The complete qualitative acceptance boundaries in the proposal documents remain unexecuted. Both guarded configurations satisfy two synthetic fixture oracles per proposal.

| Proposal | Primary subtest scope | Primary guarded outcome | Conventional | Alvorada-inspired |
|---|---|---|---:|---:|
| FW01 | Retain a represented material contradiction and send to simulated review, without changing account state. | REVIEW | 2/2 | 2/2 |
| FW02 | Count shared-origin support once; a confident narrative cannot create a second origin. | HOLD | 2/2 | 2/2 |
| FW03 | Requested objective differs from invented service grant. | HOLD | 2/2 | 2/2 |
| FW04 | Throughput gains do not override the fixture harm cap. | HOLD | 2/2 | 2/2 |
| FW05 | Represented broader intervention exceeds the bounded fixture grant. | HOLD | 2/2 | 2/2 |
| FW06 | Missing authoritative observations do not become positive support. | HOLD | 2/2 | 2/2 |
| FW07 | Count shared-origin support once; a confident narrative cannot create a second origin. | HOLD | 2/2 | 2/2 |
| FW08 | Retain a represented material contradiction and send to simulated review, without changing account state. | REVIEW | 2/2 | 2/2 |
| FW09 | Beneficial/harmless outcome does not validate an absent grant. | HOLD | 2/2 | 2/2 |
| FW10 | Actual SQLite history deletion is attempted and denied by a trigger. | HISTORY_PRESERVED | 2/2 | 2/2 |
| FW11 | Beneficial/harmless outcome does not validate an absent grant. | HOLD | 2/2 | 2/2 |
| TB01 | Retain a represented material contradiction and send to simulated review, without changing account state. | REVIEW | 2/2 | 2/2 |
| TB02 | Represented limited observation falls below the fixture quality requirement. | HOLD | 2/2 | 2/2 |
| TB03 | Different publishers share one represented suggested-answer origin. | HOLD | 2/2 | 2/2 |
| TB04 | Undisclosed incentive routes to review; an incentive alone does not establish falsehood. | REVIEW | 2/2 | 2/2 |
| TB05 | Generated reconstructions cannot count as observations supporting their own premises. | HOLD | 2/2 | 2/2 |
| TB06 | Unavailable review access keeps evidence and effects unresolved. | HOLD | 2/2 | 2/2 |
| TB07 | Retain a represented material contradiction and send to simulated review, without changing account state. | REVIEW | 2/2 | 2/2 |
| TB08 | Authorized local correction must change account and downstream state. | CORRECTED | 2/2 | 2/2 |
| TB09 | Two supporting independent observations meet this toy standard despite one unknown; no deception or opposite conclusion inferred. | ALLOW | 2/2 | 2/2 |
| TB10 | Actual SQLite history deletion is attempted and denied by a trigger. | HISTORY_PRESERVED | 2/2 | 2/2 |

## Original reference and conformance checks

[Original-reference rerun](original-reference-rerun.json) has 72 observations and matches the earlier case/effect summaries: conventional and Alvorada-inspired arms 24/24, permissive baseline 3/24. The earlier archive remains unchanged and passed its original verifier.

[Repository test output](repository-tests.txt) and [validator output](repository-validator.txt) record the current checks. The recorded checks comprise 423 preexisting tests plus eight new adapter checks, all 431 passing in separate invocations. The eight new checks live in `testing/harness/`. These checks are software conformance evidence, not additional human/institutional experiments.

## Execution provenance and archive method

Exact UTC time, Python/SQLite versions, local parent commit, dirty state and runtime input hashes appear in each raw result file. The local parent commit `34c6803` has the same tree as public baseline `c6cb2f2c0fcfbf98a9375ebae988837f154f827c`; it is not the public commit ID. Both runs executed with uncommitted work, explicitly recorded. Frozen input copies and hashes identify the code and fixtures used more precisely than the parent alone.

An initial development run preceded refinements to positive cases. The final run uses the committed fixtures shown here; no initial-run count is presented as a final result. Results were written to new ignored run directories, then deliberately copied into this new immutable archive with raw observations, input copies, checks and manifest. The runner itself refuses archive paths. Replay compares cases, effects, complete oracles, summaries and input hashes, excluding time and local Git metadata. It does not substitute current observations for the original run.

```sh
python3 testing/harness/run_film_review.py
python3 testing/harness/verify_film_review.py
python3 testing/harness/verify_snapshot.py
```

## What remains untested

All full 68 operational exercises and 90 application exercises remain proposed. The adapter does not discover source authenticity, detect semantic contradictions, assess witness truthfulness, measure real harm, decide lawful authority, conduct human review, deliver real remedies or establish independent custody. Numeric thresholds are invented fixture controls, not clinical, legal or constitutional standards. One process controls all local tables and records. Fixture authorship and evaluation were not independently separated, and positive cases are not representative samples. No LLM, actual institutional baseline, model variability, review workload or field efficacy was evaluated.

Supportable statement: “We ran 42 fixed synthetic subtests mapped to 21 film-inspired proposals across three configurations. Both guarded configurations satisfied all predefined outcomes and record/effect checks. Their effects were identical, and full operational evaluation remains pending.”
