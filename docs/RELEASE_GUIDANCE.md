# Publication, versions, citation, and adaptation

Public research publication, a repository release, Constitution v0.1, human
ratification, and operational activation are separate states.

## Creating a reviewable public snapshot

For a public launch, select an exact commit after the repository identity is
settled. Record the title, repository URL, publication date, license, proposal
status, changes, limitations, and validation commands/results. If a tag or
GitHub release is created, link it to that exact commit and supply release notes.
Do not imply that a proposed tag already exists. Preserve earlier snapshots and
supersession rather than overwriting the basis for prior citations.

Constitution v0.1 identifies the proposed document. It is not a claim that the
whole evolving repository has a stable software API or has been released as
version 1.0. Distinguish editorial revisions, new research proposals, adopted
design changes, and actual constitutional acts in notes. Corrections to a summary
must not silently change controlling decision records or reviewed digests.

## Citation and reuse

[CITATION.cff](../CITATION.cff) provides research citation metadata. Add the exact
commit SHA or release identifier and the retrieval date when citing a mutable
repository. Cite specific decision or section identifiers when making a precise
constitutional claim. No DOI, archived deposit, or release identifier is asserted
unless it has actually been created and verified.

Example: André de Lima. *Constitutional Governance for Institutions
(Alvorada): A Research Framework*. 2026. Repository URL, commit [actual SHA],
accessed [actual date]. Constitution v0.1 proposed, not adopted.

The copyright license and attribution are in [LICENSE](../LICENSE) and
[NOTICE.md](../NOTICE.md). An adapted project should identify its source,
modifications, applicable obligations, and departures from the design. External
sources retain their own rights. A fork's publication does not establish its
legitimacy or Alvorada's endorsement.

## Adaptation boundaries

Principle-inspired practice uses existing lawful authority. Institutional
adaptation is a separate design undertaking. Full adoption must satisfy the
actual membership, human offices, separated selectors, fixed thresholds,
ratification, and activation conditions; assigning new names to existing
managers is insufficient. Disclose modified office sizes, decision rights,
constituencies, and emergency or change processes as departures, not unchanged
v0.1 adoption. See [Applications](../applications/README.md).

## Rename or organization transfer

The repository moved to
[cogno-us/cognous-institutional-governance](https://github.com/cogno-us/cognous-institutional-governance)
on 2026-10-04, as reported by the owner and verified at the new location.
Main retained commit `d70e1dc714a3a197f8fce857cffc74486b364734` at verification.
Canonical links and citation metadata now use this location. Clone with:

```sh
git clone https://github.com/cogno-us/cognous-institutional-governance.git
```

For an existing checkout, update its remote with:

```sh
git remote set-url origin https://github.com/cogno-us/cognous-institutional-governance.git
```

For any future location change, check the clone URL, README,
NOTICE, citation metadata, release notes, reporting links, issue-template links,
and any outside announcements. Verify the new authoritative remote and any
redirects. Do not rely on assumed redirects for permanent citations; retain
commit identity and explain the relocation. Outside announcements and independently maintained copies need separate updates;
they were not changed by this repository revision.
