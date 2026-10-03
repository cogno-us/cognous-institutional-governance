# Harness design and construction history

## Purpose and origin

The supplied failure analysis and the [recommended pilot method](../../docs/PILOT_EVALUATION.md) motivated the operational battery. The method calls for bounded workflows, an actual baseline, predefined outcomes, failure/lifecycle exercises, independent review, and measured cost. This reference implementation exercises only adapter logic before an operational evaluation. It is not the full recommended program.

Construction sequence: derive 40 incident-inspired exercises and seven lifecycle exercises; select policy, production-permission and citation workflows; define 24 invented fixtures and expected boundaries before execution; implement three deterministic configurations; execute all 72 case/configuration pairs; inspect raw effects; keep negative findings and identify follow-up work. The same assistant authored cases, gates, oracles and interpretation. There was no independent reviewer, random assignment or held-out evidence.

The original standalone harness generated its cases in Python and rewrote output in place. Repository integration freezes those cases as JSON, reads the backup instead of creating it during a run, adds environment/commit/input hashes, makes imports side-effect free, and separates reruns from archived evidence. The underlying control and oracle logic is unchanged. An [archived original run](../results/2026-10-03-reference-v1/original-results.json) preserves earlier observations; its own input hash manifest identifies the earlier harness.

## Configurations and attribution

| Arm | Effect control | Records | Meaning |
|---|---|---|---|
| baseline | Deliberately permissive toy adapter | Case, arm, outcome | Negative control; not an observed organization's baseline |
| conventional | Metadata checks and SQLite write restriction | Same three fields | Competent conventional controls in this limited fixture world |
| alvorada_inspired | Exactly the same effect controls | Seven additional fields | Tests a proposed record schema; does not implement constitutional offices |

No effect improvement between the guarded configurations can be inferred: their gates are identical by design. Record field counts measure schema size, not usefulness, independence or institutional quality. All authority and dissent records are invented strings. Reviewer workload, latency, cost, comprehension and actual remedy quality are unmeasured.

## Execution flow and state

1. Read fixed fixtures. For each case and arm, create a fresh in-memory SQLite connection and synthetic production row. Restore cases start with an empty table in every arm.
2. Guarded adapters collect flagged reasons. This is supplied evidence; no model retrieves sources, interprets policy or detects semantic conflict.
3. For deletion attempts in guarded arms, set SQLite `PRAGMA query_only=ON`, actually attempt DELETE, retain the SQLite exception, and query the resulting table. Direct, script and indirect paths are labels for the same adapter; no alternate credentials, shell or network bypass are exercised.
4. Policy adapters allow supported fixture content, block flagged conflicts and retain pending status when delivery evidence is absent. There is no transport integration.
5. Citation adapters inspect supplied authenticity/support flags. They do not authenticate real judicial records or perform semantic legal review.
6. Recovery reads a separate local JSON backup and actually repopulates the table in guarded arms. Separate local storage does not establish independent custody; the same Python process controls both.
7. Compare outcome and, for agent hazards/recovery, actual table rows with predefined oracles. Serialize one raw observation per pair and aggregate counts.

Every run starts fresh; there is no cross-case learned state. No LLM, API key, external service, agent framework or proprietary Cognous implementation is used. Python 3.9+ standard library is sufficient. Runtime package/SQL engine versions are recorded.

## Result contract and failure handling

`results.json` records schema version, UTC time, repository HEAD, dirty-worktree flag, environment versions, SHA256 input hashes, case inputs, all raw results and summaries. Each observation contains expected/observed outcome, oracle satisfaction, production rows, SQLite observation, record fields and linked battery ID. Source and battery changes are captured by the archive manifest, separately from runtime inputs.

Exit zero means every guarded fixture oracle was satisfied. Expected permissive-baseline mismatches do not fail the command. A guarded mismatch exits one and preserves the run file. Malformed input and execution errors raise an error; they are not converted into successful results. Existing output directories and archive paths are refused. UTC time and repository metadata can differ on rerun; effect observations should match with frozen inputs.

## Why this design and what to improve

Determinism permits exact replay; SQLite provides observable state rather than accepting an agent's completion claim; permissive negative controls show that the fixtures can distinguish missing controls; legitimate allows expose overblocking. These advantages are limited by supplied truth labels and sparse coverage. Three positive cases are insufficient to estimate real service quality.

Next: use independently selected evidence, actual observed baselines, real isolated tool adapters, multiple credential paths and qualified human review. Compare conventional and Alvorada record usefulness with identity masked where practicable. Add lifecycle state sequences, unknown inputs, source drift, adverse cases and cost measures before broader claims. Keep both failures and null comparative findings. See the [protocol](../PROTOCOL.md) and [results interpretation](../results/README.md).
