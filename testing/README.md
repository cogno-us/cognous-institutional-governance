# Testing and evaluation

Read this index first. This section separates proposed operational exercises, executed synthetic evidence, and repository conformance checks. It contains no production runtime or adopted constitutional authority.

| Area | Contents | Status |
|---|---|---|
| [Battery](battery/README.md) | 40 incident-inspired and seven lifecycle exercises | 47 PROPOSED; full operational exercises unexecuted |
| [Protocol](PROTOCOL.md) | Recommended program, comparison design, measures and status rules | Operational program pending |
| [Incident sources](sources/README.md) | News reporting, primary supplements and evidence qualifications | Reporting links checked; access limits recorded |
| [Harness design](harness/DESIGN.md) | Construction method, configurations, gates, oracles and limits | Deterministic reference adapter only |
| [Fixtures](fixtures/README.md) | 24 fixed synthetic subtests and recovery data | Invented; no real participants or production data |
| [Results](results/README.md) | Raw 72-run observations, interpretation and reproducibility evidence | EXECUTED_SYNTHETIC; not independently reviewed |
| [Execution template](templates/OPERATIONAL_RECORD.md) | Actual operational run record requirements | Template only |
| [Repository checks](../tests/README.md) | Validator and existing invariant tests | Conformance checks, not efficacy evidence |

## Run locally

From the repository root, using Python 3.9+ and no additional dependencies:

```sh
python3 testing/harness/run_reference.py
python3 testing/harness/verify_snapshot.py
python3 tools/validate_bootstrap.py
python3 -m unittest discover -s tests -q
```

The reference runner prints summaries and writes a new timestamped directory under `testing/runs/` (ignored by Git). You may provide `--output /path/to/new-directory`. Existing directories and paths under archived `testing/results/` are refused. Committed fixtures and results are never overwritten by reruns.

## Current finding

Both guarded configurations satisfied the same 24 predefined fixture outcomes; the deliberately permissive toy baseline satisfied three. Nineteen hazardous cases were blocked and all three legitimate allows were retained by both guarded configurations. Pending delivery and recovery behaved as specified. The Alvorada-inspired arm adds records but has identical effect controls. This establishes no incremental effect benefit, historical prevention or real-world efficacy. Record richness needs independent human evaluation.

All 47 full operational exercises and the existing 90 application exercises remain proposed. Follow [PROTOCOL.md](PROTOCOL.md) for what remains to be done. The earlier separate report and ZIP are superseded as the primary presentation by this repository section; all necessary specifications, execution code and observations are here. No binary report or article copies are required.

## Supplementary Fog of War exercises

[FW01–FW11](battery/FOG_OF_WAR.md) add eleven proposed exercises for uncertainty, correlated evidence, purpose, metrics, harm, reconsideration, accountability and near misses. The testing section now specifies 58 proposed exercises: the original frozen 47-case battery plus this separate eleven-case supplement. The 90 application exercises are separate. The supplement is unexecuted and not supported by the current 24 fixtures or 72 observations; the original battery, harness and archives are preserved.
