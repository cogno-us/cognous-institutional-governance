# Film-review adapter: design and coverage

**Executed synthetic mechanics; no operational or human-review exercise.**

`run_film_review.py` executes [42 fixed fixtures](../fixtures/film-review/README.md) across three arms, producing 126 observations. Each full FW/TB proposal maps to a primary and positive subtest. Two independent dimensions remain separate: actual local effects and preservation of represented evidence in the output record.

## Construction and controls

The policy takes an invented grant, requested purpose/action, numeric harm/quality bounds, review-access flag and evidence objects. It counts source or suggestion origins among qualifying observations; reconstructed material cannot supply observation support. Contrary evidence and undisclosed incentives send the case to a simulated REVIEW state. Invalid authority, unavailable access, inadequate support or exceeded bounds HOLD the affected act. Unknown evidence is retained without automatically defeating otherwise sufficient support.

Each case opens a fresh in-memory SQLite database with account, downstream and history tables. ALLOW actually changes account/downstream state. CORRECTED actually clears both tables. A retention trigger denies an attempted history deletion in guarded arms; the caught database error and remaining rows are recorded. HOLD/REVIEW preserve the initial account state. No human review completes a queued case.

| Arm | Behavior and inference boundary |
|---|---|
| Permissive toy | Applies represented requests without checks; a correction changes only the reported summary, not either table; history deletion is permitted. This intentionally weak negative control is not an observed institutional baseline. |
| Conventional | Uses evidence/grant gates and history trigger; produces a decision/evidence record. It models selected competent controls, not a real institution. |
| Alvorada-inspired | Identical policy and effects, with five additional attribution/continuation fields. Any effect benefit over conventional controls is zero by construction. |

Expected observations are checked after execution. They are never passed to `evaluate()`. The oracle compares outcome, both table states, retained history and represented contradiction/unknown counts. A baseline miss may concern missing evidence records even when the legitimate action itself completed; report these separately.

## Coverage by proposal

| Proposals | Executed narrow mechanic | Full exercise still missing |
|---|---|---|
| FW01, FW08; TB01, TB07 | Represented contradiction retained; effects deferred to a simulated review queue | Counterpart understanding, omitted-evidence discovery, actual reconsideration/appeal or human judgment |
| FW02, FW07; TB03 | Qualifying observation origins counted; common suggestion origin deduplicated | Detecting dependence, social influence or confidence in real sources/models |
| FW03 | Requested purpose checked against a literal grant purpose | Beneficiary assessment, motive or incentive adjudication |
| FW04, FW05 | Scalar harm checked against an invented bound | Real harms, least-harm alternatives, proportionality or interruption tradeoffs |
| FW06; TB02, TB05, TB06 | Missing, low-quality, reconstructed or inaccessible support does not satisfy the fixture threshold | Authenticity, semantic relevance, clinical/legal standards or real evidence access |
| FW09, FW11 | An invalid grant blocks a request, even with represented harm zero | Necessity judgment, completed unauthorized near miss or independent alternate reviewer |
| FW10, TB10 | SQLite rejects history deletion and retains the original row | Detecting evasive answers, lawful institutional retention or independent custody |
| TB04 | Undisclosed incentive queues review; disclosed incentive with support can proceed | Discovering conflicts or determining witness credibility |
| TB08 | Both local effect tables clear after authorized represented correction | Real notice, restitution, other credential paths or independent organizational verification |
| TB09 | Unknown record stays visible while sufficient represented support allows the act | Assessing a changed witness account or discovering missing material |

## Run, verify and maintain

From the repo root, Python 3.9+ and standard library only:

```sh
python3 testing/harness/run_film_review.py
python3 testing/harness/verify_film_review.py
python3 -m unittest discover -s testing/harness -p "test_*.py" -q
python3 -m unittest discover -s tests -q
```

The runner writes only a new directory under ignored `testing/runs/` unless `--output` selects another new directory. It refuses existing directories and archived-result paths. Guarded mismatches produce a nonzero exit and preserve the observation file; malformed inputs fail rather than becoming successful observations. Expected permissive misses do not fail the runner.

The published archive was copied deliberately from a successful run after fixture revision. It includes the final fixture and harness copies, original-reference rerun, conformance output, hashes and a narrative interpretation. `verify_film_review.py` checks byte integrity, proposal mapping and deterministic replay; it does not establish independent review. Future revisions need a new snapshot and version, leaving this archive intact.

## Limits and verification tests

Eight additional conformance tests check guarded fixture outcomes, expected-value isolation, suggestion-origin aliasing, reconstruction exclusion, actual history-deletion rejection, correction of both actual tables, a disclosed-incentive positive case and malformed-input failure. These are software checks, not eight independent governance experiments.

All origins, evidence relations, quality, harm, authority and expected values are authored synthetic inputs. The same assistant designed fixtures, gates and oracles. All stores and verification run in one process; logical separation is not organizational independence. No LLM, semantic evidence assessment, real participant, competent human adjudication, measured workload or field efficacy is evaluated. A form field or REVIEW result cannot establish usable human agency.
