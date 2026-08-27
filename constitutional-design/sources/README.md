# Sources and prior art

`SOURCE_INDEX.yaml` locates the source registers.
`PRIOR_ART_REGISTER.yaml` is the normalized, flat prior-art evidence register.
`MECHANISM_ADOPTION_MAP.yaml` is a research-only synthesis of candidate
mechanism dispositions. Their data uses JavaScript Object Notation (JSON),
which is also valid YAML Ain't Markup Language (YAML), so baseline validation
needs no external parser.

`HISTORICAL_EVIDENCE_REGISTER.yaml` contains independently referenceable
comparative evidence records. Each record separates observation,
interpretation, and possible constitutional relevance. Those categories do not
constitute a constitutional lesson, decision, requirement, or provision.

Prior-art source statuses are `VERIFIED`, `PARTIALLY_VERIFIED`,
`SOURCE_TO_VERIFY`, and `RESEARCH_LEAD`. `VERIFIED` requires a directly
resolvable stable Hypertext Transfer Protocol or Secure (HTTP(S)) reference,
verification provenance, and a recorded review state. Partial, blocked,
mutable, or bibliographically incomplete sources retain conservative statuses
and limitations. The register must not fabricate authors, dates, citations,
Uniform Resource Locators, or findings.

Issue `known_prior_art` lists contain only `prior_art_id` references. Analysis
remains in the register and mechanism map. Source-to-issue mappings are
bidirectional and cover all 18 open issues.

Capitalized research-lead labels are supplied names. Their expansions, if any,
remain to be verified rather than inferred.

## Novelty discipline

`NO_CLOSE_PRIOR_ART_FOUND_IN_SEARCH` does not mean `NOVEL`.

Permitted research classifications are:

- `ESTABLISHED_PRIOR_ART`
- `KNOWN_BUT_UNCOMMON`
- `UNUSUAL_APPLICATION`
- `UNUSUAL_COMBINATION`
- `POTENTIALLY_DISTINCTIVE`
- `NO_CLOSE_PRIOR_ART_FOUND_IN_SEARCH`
- `INSUFFICIENT_EVIDENCE`

Automated classification must not use `NOVEL`.

Potential mechanism dispositions are:

- `CANDIDATE_ADOPT`
- `CANDIDATE_EXTEND`
- `CANDIDATE_DESIGN`
- `NOT_APPLICABLE`

A candidate disposition is research analysis, not a constitutional decision.
Every mechanism-map entry therefore has `decision_required: true`. Candidate
dispositions must not be represented as adopted, approved, rejected, decided,
or final. The map does not populate issue candidate architectures.

## Evidence boundary

Established mechanisms include organizational roles and norms, policy
evaluation and enforcement, delegated access, provenance, amendment and
voting processes, model-behavior governance, model-risk validation, and
durable decision/dissent records. That evidence does not establish a complete
mixed human/AI constitutional institution.

Model-behavior constitutions are not institutional constitutions. Valid code,
policy, or credentials do not establish legitimate authority. Provenance does
not establish truth or authorization. Delegation protocols do not determine
interregnum law. Coverage gaps and insufficient evidence do not support
novelty or patentability claims.
