# Getting started

You can use this repository as a reader, reviewer, researcher, or institutional
designer. Reading requires no software installation or account. The repository
contains no agent service to deploy and no adoption-by-installation mechanism.

## Choose a path

| Purpose | First steps |
|---|---|
| Understand the design | Read the [overview](../README.md), [principles](DESIGN_PRINCIPLES.md), and [architecture guide](ARCHITECTURE_GUIDE.md), then the [proposal](../constitutional-design/drafts/CONSTITUTION_v0.1.md). |
| Review a disputed choice | Use the [development index](../history/DEVELOPMENT_RECORD.md) and [decision rationale](../process/DECISIONS_AND_RATIONALE.md); identify the controlling decision and provision. |
| Explore an application | Select a [context](../applications/README.md), identify real decision rights, and use the bounded [evaluation guide](PILOT_EVALUATION.md). |
| Start a practical assessment | Use the [institutional scope guide](INSTITUTIONAL_SCOPE.md) and [prepared assessment program](../testing/programs/INSTITUTIONAL_ASSESSMENT.md); actual owners and observed evidence are still required. |
| Contribute a source or correction | Read [contribution guidance](../CONTRIBUTING.md), identify the exact claim and source, and open an issue or pull request. |
| Cite or adapt the material | Consult [citation guidance](RELEASE_GUIDANCE.md#citation-and-reuse), [CITATION.cff](../CITATION.cff), and [NOTICE.md](../NOTICE.md). |

## A worked reading example

Suppose a caseworker recommends rejecting a customer's refund request.
The same authority and review questions apply whether the work uses paper
records, ordinary software or AI assistance.

1. Identify the actual refund policy and the competent human source of its grant.
   Access to the account is not refund-decision authority.
2. Determine whether the caseworker may recommend only or execute a bounded routine
   decision under prior valid authorization. Do not infer permission from the recommendation’s
   accuracy or a policy check.
3. Preserve the evidence, uncertain facts, alternatives, customer's objection,
   chosen reason, and authorization source. See IV.1.
4. Ask whether the customer can reach an independent human reviewer and whether
   that reviewer can reconstruct the evidence without depending solely on the
   original decision-maker or contested evidence route. See IV.2.
5. Distinguish the judgment, delivery of any remedy, and verification of delivery.
   See the separation principles in II–III.
6. If the caseworker is replaced or the process changes, preserve the pending
   complaint, obligations and correction history. See the lifecycle questions in VI and VIII.

This is an illustrative application of principles under existing lawful
organizational authority. It does not appoint a Constitutional Court or adopt
v0.1. The [customer-service file](../applications/customer-service.md) provides
all principle mappings and proposed exercises.

## Check the repository locally

Use Python 3.10 or later and a local checkout. The validator and tests use the
Python standard library; no governance runtime installation is required.

```sh
python tools/validate_bootstrap.py
python -m unittest discover -s tests -q
```

Record the commit, Python version, commands, and results when reporting a defect.
The tests create a temporary workspace ignored by Git. Passing checks verifies
specified repository invariants, not sector acceptance exercises, legitimacy,
security, or operational performance. See the [FAQ](FAQ.md) for common boundaries.
