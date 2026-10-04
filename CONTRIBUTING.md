# Contributing to Constitutional Governance for Institutions

Alvorada is the project name of this research framework.

Contributions should improve constitutional analysis, source quality,
comprehensibility, adversarial review, and the distinction between lawful
authority and effective power.

## Public contribution boundary

Submit material you have authority to share under the repository's CC BY 4.0
license. Identify third-party material and its applicable rights. Do not submit
confidential documents, private product designs, unpublished patent material,
customer information, secrets, or implementation details from proprietary
systems. Public institutional requirements can be discussed without disclosing
an underlying product's mechanisms.

For changes, identify the affected files and provisions, source and rationale,
material alternatives, dissent, uncertainty, and any constitutional-change
implications. Distinguish proposals from adopted human design decisions and
operative law. A maintainer merging a contribution does not ratify the
Constitution or exercise constitutional jurisdiction.

## Submission and review

Use issues for questions, constitutional critique, source corrections, and
reproducible defects. Use pull requests for concrete changes. Templates help
identify the commit, affected record, primary evidence, alternatives, dissent,
conflicts, authority implications, and actual verification results. Do not
paste unverified model output as a verified source or a human decision.

For AI-assisted contributions, identify material assistance and what the
contributor actually checked. The contributor remains responsible for source
accuracy, sharing rights, and claims of execution. Do not infer an author's
private motives or consent from generated text.

Follow [repository governance](GOVERNANCE.md), [community conduct](CODE_OF_CONDUCT.md),
and [sensitive-reporting guidance](SECURITY.md). For readability, define terms
on first use, use descriptive headings, provide meaningful link text, avoid
color-only distinctions, and supply text alternatives for diagrams. Preserve
non-English source context and translation uncertainty when relevant.

Use [progressive disclosure](docs/DOCUMENTATION_STRUCTURE.md): a short, plain-language
summary first, descriptive links next, detailed analysis and source limits deeper.
Keep research, history and films in the unified research section, and experimental
claims in testing. Maintain one canonical analysis rather than parallel copies.

There is no guaranteed response or merge deadline. Substantive objections should
remain traceable even when a proposal is declined. See [release guidance](docs/RELEASE_GUIDANCE.md)
for version, citation, and adaptation boundaries.

## Verification

Run from the repository root with Python 3.10 or later:

```sh
python tools/validate_bootstrap.py
python -m unittest discover -s tests -q
```

The validator checks repository structure and specified research invariants.
Reviewed artifacts are compared against pinned digests with LF/CRLF portability;
other content changes remain significant. Passing checks cannot establish
legitimacy, legal clearance, or real-world institutional performance.

Machine-capture scenarios in the Phase H catalogue remain proposed human-review
cases, not automatically passed tests. Runtime engineering remains deferred.
