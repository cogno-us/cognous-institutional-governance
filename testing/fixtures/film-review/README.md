# Film-review fixed synthetic fixtures

42 cases: one primary and one positive variant for each FW01–FW11 and TB01–TB10 proposal. [cases.json](cases.json) fixes invented grants, purpose and harm bounds, evidence relations, quality, source/suggestion origins, disclosure and access, requested actions, initial account state and expected observations.

Expected values are kept outside `inputs`; the policy receives only `inputs`. Evidence relations and quality remain author-supplied labels, not detected semantics. Expected outcomes and implementation were authored in the same session; no independent held-out selection occurred. Positive cases vary boundaries, supporting origins, disclosed incentives and unknown/derived evidence, but reuse a small synthetic service workflow. They are not a representative sample.

[Coverage and harness design](../../harness/FILM_REVIEW_DESIGN.md) identifies which narrow mechanics run and what remains untested. [Archived results](../../results/2026-10-04-film-review-v1/README.md) preserve observed effects and hashes. These fixtures contain no real people, sensitive data or tactical workflow.
