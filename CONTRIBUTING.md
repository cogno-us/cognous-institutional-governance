# Contributing to Alvorada

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
