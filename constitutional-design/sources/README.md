# Sources and prior art

`SOURCE_INDEX.yaml` is a minimal research register. Its data uses
JavaScript Object Notation (JSON), which is also valid YAML Ain't Markup
Language (YAML), so bootstrap validation needs no external parser.

Entries begin as research leads rather than evidence. A lead may become a
verified source only after primary-source provenance and human-verifiable
verification details are recorded. The register must not fabricate authors,
dates, citations, Uniform Resource Locators, or findings.

## Novelty discipline

Absence of identified prior art is not evidence of novelty.

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

