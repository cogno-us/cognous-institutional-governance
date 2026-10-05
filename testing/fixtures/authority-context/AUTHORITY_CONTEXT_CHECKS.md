# Executed local profile checks — 2026-10-05

**Summary:** The 44 schema/reference fixtures passed their specified oracles.
No effects were executed and no institutional adoption or field benefit was tested.

Starting commit: `76cdff90d0370632faa4e033749c552fd6bbd37d`.
[Raw results and reproducible input hashes](results.json) identify exact schema,
examples, reference code, fixture definitions and unit test inputs. Re-run the
[commands](README.md#reproduce) on the PR head. Results are local reference checks,
not independent review, security certification or cross-repository integration.

## Commands and results

| Command | Actual result |
|---|---|
| `python3 -m pip install -r testing/harness/requirements-authority.txt` | jsonschema 4.26.0 installed; dependency required for dedicated runner |
| `python3 testing/harness/run_authority_context.py` | 44/44 fixture oracles satisfied; schema and reference semantics reported separately |
| `python3 -m unittest discover -s tests -q` | 424 tests passed, including the one added fixture-suite test; no skips |
| `python3 -m unittest discover -s testing/harness -p 'test_*.py' -q` | 22 existing harness unit tests passed |
| `python3 tools/validate_bootstrap.py` | Passed; recorded readiness labels retain their existing narrow interpretation |
| `python3 testing/harness/verify_snapshot.py` | Hashes and deterministic replay passed; existing 24 fixtures / 72 observations |
| `python3 testing/harness/verify_film_review.py` | Hashes and deterministic replay passed; existing 42 fixtures / 126 observations |
| `python3 testing/harness/verify_authorization_effect.py` | Hashes and deterministic replay passed; existing 20 fixtures / 60 observations |
| `git diff --check` | Passed |

The repository suite and harness suite together contain 446 tests. The previous
445 count consisted of 423 repository tests plus 22 harness tests; this change
adds one test method with 44 separately checked fixture oracles. Do not confuse
fixture counts with test methods or the old adapter observation counts.

A final relative file-link check also passed. It checks that linked file targets
exist, not anchor semantics, external URLs or newcomer usability.

## Limits and unresolved decisions

Real mandate and identity authentication, adoption evidence, actual approver
competence/independence, live revocation, trusted clocks, permissions, aggregate
budgets, transactional commit, remote observation, distributed retry and rights
access are not implemented by these fixtures. Neither BitRep nor The Index was
modified or retested. Their accepted commits are Governor-supplied baselines.

The schema and field names, exact-version policy, consumer mappings, restricted
finite scope model, status freshness/error rules and migration plan remain
proposed pending Governor review. Practical controls must be implemented and
separately tested in downstream components. All three existing synthetic archives
and the original Constitution/source records remain byte-for-byte unchanged.

Material AI assistance: this profile, reference code and fixture design were
prepared in the Worker 3 thread. Checks reported above were locally executed;
no independent human review or institutional ratification is inferred.
