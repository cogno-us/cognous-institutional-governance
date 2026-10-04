# Testing and evaluation

Read this index first. This section separates proposed operational exercises, executed synthetic evidence, and repository conformance checks. It contains no production runtime or adopted constitutional authority.

| Area | Contents | Status |
|---|---|---|
| [Battery](battery/README.md) | 40 incident-inspired and seven lifecycle exercises | 47 PROPOSED; full operational exercises unexecuted |
| [Protocol](PROTOCOL.md) | Recommended program, comparison design, measures and status rules | Operational program pending |
| [Incident sources](sources/README.md) | News reporting, primary supplements and evidence qualifications | Reporting links checked; access limits recorded |
| [Harness design](harness/DESIGN.md) | Construction method, configurations, gates, oracles and limits | Deterministic reference adapter only |
| [Film-review adapter](harness/FILM_REVIEW_DESIGN.md) | 42 narrow subtests mapped to 21 FW/TB proposals; 126 observations | EXECUTED_SYNTHETIC; full exercises pending |
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

[FW01–FW11](battery/FOG_OF_WAR.md) add eleven proposed exercises for uncertainty, correlated evidence, purpose, metrics, harm, reconsideration, accountability and near misses. Together, the original frozen 47-case battery and this eleven-case supplement specify 58 proposed exercises. The 90 application exercises are separate. The full supplement remains unexecuted and is not covered by the original 24 fixtures or 72 observations; the original battery, harness and archives are preserved.

## Supplementary Thin Blue Line exercises

[TB01–TB10](battery/THIN_BLUE_LINE.md) add ten proposed exercises on evidence omissions, observation conditions, contamination, incentives, synthetic reconstructions, access, reconsideration and correction effects. There are now **68 proposed exercises in this testing section**: 47 original cases, 11 FW cases and 10 TB cases. The 90 application exercises remain separate. No full FW or TB operational exercise has been executed or reviewed. The original 24 fixtures and 72 observations cover neither supplement; the new film adapter supplies separately documented narrow synthetic coverage.

## Run the film-inspired synthetic subtests

```sh
python3 testing/harness/run_film_review.py
python3 testing/harness/verify_film_review.py
```

The [2026-10-04 archive](results/2026-10-04-film-review-v1/README.md) records 126 final film-adapter observations, a rerun of the original 72 observations, and current repository checks. Conventional and Alvorada-inspired controls have identical effects; no incremental institutional benefit is established.

## Research designs: institutional usability

Six [institutional usability scenarios](research/INSTITUTIONAL_USABILITY.md), drawn from deeper interdisciplinary studies, examine participation barriers, local/shared scope, effective voice, usable alternatives, reviewer workload and shared failures. Each includes legitimate countercases and cost observations. They are **unexecuted research designs outside the 68 numbered operational proposals**, with no new fixtures, harness results or efficacy findings.

## Prepared institutional assessment program

The [first assessment program](programs/INSTITUTIONAL_ASSESSMENT.md) prioritizes usable access, feasible review workloads and verified remedies in a human-run complaints workflow. [Metric definitions](programs/INSTITUTIONAL_MEASURES.md) and separate study, case, review, remedy and results templates are ready. Actual owners, grants, participants, independent assessment and observations remain unfilled; no new operational evidence is claimed. The existing numbered exercises and frozen results retain their status.
