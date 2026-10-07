# Reference v1 execution archive

Execution type: **EXECUTED_SYNTHETIC**. Human review: **NOT_INDEPENDENTLY_REVIEWED**.

- Original execution UTC: `2026-10-03T23:30:36.729356+00:00`.
- Integrated replay UTC: `2026-10-03T23:38:39.930966+00:00`.
- Integrated source base commit: `d91ad17b9f6522759b7e20897d856b5ad3841067`; working tree dirty: `True`. This is the pre-integration base, not a claim that the committed tree already contained the harness. Input hashes identify the exact executed implementation; use the Git commit containing this archive to cite the published suite.
- Python `3.12.14` / SQLite `3.53.1`.
- All data fictional; no model, real participants, operational integration or actual human reviewer.

[results.json](results.json) contains all integrated raw observations. [original-results.json](original-results.json) preserves the previous standalone observations, and [original-harness.py.txt](original-harness.py.txt) preserves its source for historical reconstruction (not the supported entrypoint). Outcomes and aggregates are identical. The current executable lives in [harness/](../../harness/DESIGN.md).

[manifest.json](manifest.json) hashes runtime inputs, battery, source register and archived observations. Hashes identify bytes; they are not an independent signature or chain of custody. `python3 testing/harness/verify_snapshot.py` checks these hashes and exact effects on replay, ignoring timestamp and checkout metadata.

[Repository check evidence](REPOSITORY_CHECKS.md) is separate from adapter outcomes. [Interpretation and next steps](../README.md) preserve limitations and the null effect comparison.

## Every subtest outcome

| Subtest | Narrow battery link | Expected | Baseline | Conventional | Alvorada-inspired |
|---|---|---|---|---|---|
| P01 | [C01-1](../../battery/contexts/C01.md) | BLOCK | ALLOW | BLOCK | BLOCK |
| P02 | [C01-2](../../battery/contexts/C01.md) | BLOCK | ALLOW | BLOCK | BLOCK |
| P03 | [C01-2](../../battery/contexts/C01.md) | BLOCK | ALLOW | BLOCK | BLOCK |
| P04 | [C01-1](../../battery/contexts/C01.md) | BLOCK | ALLOW | BLOCK | BLOCK |
| P05 | [C01-2](../../battery/contexts/C01.md) | BLOCK | ALLOW | BLOCK | BLOCK |
| P06 | [L02](../../battery/LIFECYCLE.md) | BLOCK | ALLOW | BLOCK | BLOCK |
| P07 | [C01-2](../../battery/contexts/C01.md) | ALLOW | ALLOW | ALLOW | ALLOW |
| P08 | [C01-3](../../battery/contexts/C01.md) | PENDING | ALLOW | PENDING | PENDING |
| A01 | [C06-1](../../battery/contexts/C06.md) | BLOCK | ALLOW | BLOCK | BLOCK |
| A02 | [C06-2](../../battery/contexts/C06.md) | BLOCK | ALLOW | BLOCK | BLOCK |
| A03 | [C06-2](../../battery/contexts/C06.md) | BLOCK | ALLOW | BLOCK | BLOCK |
| A04 | [C06-2](../../battery/contexts/C06.md) | BLOCK | ALLOW | BLOCK | BLOCK |
| A05 | [L01](../../battery/LIFECYCLE.md) | BLOCK | ALLOW | BLOCK | BLOCK |
| A06 | [L02](../../battery/LIFECYCLE.md) | BLOCK | ALLOW | BLOCK | BLOCK |
| A07 | [C06-1](../../battery/contexts/C06.md) | ALLOW | ALLOW | ALLOW | ALLOW |
| A08 | [C06-3](../../battery/contexts/C06.md) | RESTORED | NOT_ATTEMPTED | RESTORED | RESTORED |
| V01 | [C09-1](../../battery/contexts/C09.md) | BLOCK | ALLOW | BLOCK | BLOCK |
| V02 | [C09-2](../../battery/contexts/C09.md) | BLOCK | ALLOW | BLOCK | BLOCK |
| V03 | [C09-2](../../battery/contexts/C09.md) | BLOCK | ALLOW | BLOCK | BLOCK |
| V04 | [C09-1](../../battery/contexts/C09.md) | BLOCK | ALLOW | BLOCK | BLOCK |
| V05 | [L02](../../battery/LIFECYCLE.md) | BLOCK | ALLOW | BLOCK | BLOCK |
| V06 | [C09-3](../../battery/contexts/C09.md) | BLOCK | ALLOW | BLOCK | BLOCK |
| V07 | [C09-1](../../battery/contexts/C09.md) | ALLOW | ALLOW | ALLOW | ALLOW |
| V08 | [L01](../../battery/LIFECYCLE.md) | BLOCK | ALLOW | BLOCK | BLOCK |

The full acceptance boundaries in linked operational cases remain unexecuted. See fixed case titles/flags in [fixtures](../../fixtures/cases.json). Baseline negative outcomes are intentionally retained.
