<!-- cognous-banner:start -->
```text
──────────────────────────────────────────────────
   __________  _______   ______  __  _______
  / ____/ __ \/ ____/ | / / __ \/ / / / ___/
 / /   / / / / / __/  |/ / / / / / / /\__ \
/ /___/ /_/ / /_/ / /|  / /_/ / /_/ /___/ /
\____/\____/\____/_/ |_/\____/\____//____/
             INSTITUTIONAL GOVERNANCE
       g o v e r n e d   b y   d e s i g n
  github.com/cogno-us/cognous-open-control-stack
──────────────────────────────────────────────────
```
<!-- cognous-banner:end -->

# Cognous Institutional Governance

**Alvorada: authority, challenge and correction for institutions.**

## Overview

An open research framework for businesses, public bodies and communities, with or without AI. It combines proposed constitutional designs, proportional governance, domain guidance, decision templates and a public-stack implementation profile. Repository acceptance does not ratify a constitution.

**Implementation status:** this README describes merged public reference work. Component acceptance, selection in the hub and execution of a qualification are separate facts. The selected revision for this component is `fb3d97938969a89e149e8ff8db2756091d1233fc`; the [hub lock](https://github.com/cogno-us/cognous-open-control-stack/blob/5737267d94d2b445735c95e8480a31de73a2abe8/component-lock.json) is the source of that integration choice.

## Purpose and intended users

Institutions need to identify who may decide, how decisions can be challenged and who verifies correction. AI can assist evidence preparation and routine review, but it cannot create institutional authority or turn a published design into operative law.

Institutional designers, governance reviewers and teams mapping human authority into software should begin with the public research and its evidence limits.

## Key features

| Capability | Implemented or specified responsibility |
|---|---|
| **Constitutional design** | Inspect a common charter, proposed profiles and the preserved original Constitution v0.1. |
| **Proportional governance** | Match review intensity to consequences, reversibility and uncertainty. |
| **Challenge and remedy** | Make dissent, review, succession, emergencies and correction visible in institutional design. |
| **Domain guidance** | Apply the proposed framework to specific contexts while recording departures and local decisions. |
| **Authority Context profile** | Provide consumable institutional requirements for downstream software without moving runtime enforcement into this repository. |

## How it works

Choose a domain guide and a proportional review path, then follow the invented service case through decision, challenge and correction. For software integration, map independently established institutional authority into the proposed Authority Context profile. The downstream controller must still authenticate the deployment's resolver and enforce its permissions at effect time.

A valid signature, chain inclusion, message receipt, reasoning instruction or evidence-package digest does not authorize execution. Institutional authority must be supplied and evaluated through the appropriate trusted boundary.

## Getting started

Begin with [getting started](docs/GETTING_STARTED.md), the invented [service case](docs/examples/SERVICE_CASE.md) and an [application guide](applications/README.md). Python 3.10+ is required for repository validation. These commands check repository structure and synthetic invariants, not legitimacy or real-world institutional performance.

```bash
python tools/validate_bootstrap.py
python -m unittest discover -s tests -q
```

## Evidence and supported scope

The hub selects Authority Context profile 0.1.0 at `fb3d97938969a89e149e8ff8db2756091d1233fc`. Later repository guidance remains research and is not automatically selected runtime semantics. The [implementation profile](process/implementation/public-stack-v0.1/README.md) preserves lawful-source precedence, proposed consumer mappings and the distinction between software checks and actual institutional adoption.

The accepted [hub persistence-generation evidence](https://github.com/cogno-us/cognous-open-control-stack/blob/5737267d94d2b445735c95e8480a31de73a2abe8/examples/control-plane-store-adoption/qualification-summary.json) records 915 Python tests in each of two repetitions, 35 matrix entries satisfying their gates and 120 separate mocked OpenShell tests. Those are aggregate hub results, not a per-component test count or a claim of production readiness. Optional behavioral layers receive static checks only. The [support ledger](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/release-status.md) separates implementation, execution and adoption.


The [common charter and modular profiles](constitutional-design/modular/README.md), [proportional procedures](process/PROPORTIONAL_GOVERNANCE.md), [research index](research/README.md) and [original Constitution v0.1](constitutional-design/drafts/CONSTITUTION_v0.1.md) remain canonical. The [operating guide](process/OPERATIONAL_STEWARDSHIP.md) and [learning process](process/VIRTUOUS_RECURSION.md) describe owners, review and correction. Merging documentation does not adopt any of them.

## Limitations and deployment decisions

This remains proposed guidance and constitutional research, not adopted governance, operative law or demonstrated institutional superiority. Synthetic adapters did not demonstrate better institutional outcomes than conventional controls. Runtime enforcement belongs downstream; constitutional text, recorded decisions and source hierarchy remain intact.

Review original artifacts and their exact source revisions before extending a claim to a new environment. New dependencies, authority sources, destinations or enforcement mechanisms need their own compatibility and qualification. A passing reference case is not a certification of an enterprise deployment.

## Repository guide

Use these sources for details; their historical checkpoints retain the status and scope of the work they recorded:

- [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)
- [docs/EVIDENCE_STATUS.md](docs/EVIDENCE_STATUS.md)
- [process/implementation/public-stack-v0.1/README.md](process/implementation/public-stack-v0.1/README.md)
- [applications/README.md](applications/README.md)
- [testing/results/README.md](testing/results/README.md)

For a nontechnical introduction, read the [business overview](collateral/business-collateral.md) and [one-page overview](collateral/one-page-overview.md). Both describe this component's role and evidence limits, not additional runtime features.

## Contributing and attribution

[Contribution guidance](CONTRIBUTING.md) describes review and validation expectations. Keep evidence-linked claims, preserve historical records and separate proposed features from accepted implementation.

See [LICENSE](LICENSE) and [attribution](NOTICE.md) for the existing terms and third-party scope. Developed by [Cognous](https://cogno.us); no licensing change is part of this documentation update.

---

## Bibliography

Selected external sources from the October 2026 research review. These inform evaluation questions; they do not establish Cognous implementation, adoption, conformance or production qualification.

- [OECD. *Agentic AI in organisations: Early insights from practitioner interviews*. OECD Artificial Intelligence Papers, No. 65 (2026)](https://doi.org/10.1787/1257a26f-en). Qualitative practitioner research on bounded autonomy, oversight and organizational deployment.
- [John M. Willis. *Runtime Governance Body of Knowledge for Artificial Intelligence and Other Autonomous Systems — Glossary* (19 July 2026)](https://sustainablefuturetech.com/asg-wg-runtime-governance-glossary/). Discussion draft on authority, execution and evidence terminology; not an adopted standard or Cognous conformance requirement.
- [John W. Creswell and J. David Creswell. *Research Design: Qualitative, Quantitative, and Mixed Methods Approaches*, fifth edition. SAGE (2018)](https://edge.sagepub.com/creswellrd5e). Research-methods reference for explicit questions, comparison designs and interpretation limits.

See the [research bibliography](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/research-bibliography.md) for review scope and source-verification limits.

## Cognous stack components

[Stack hub](https://github.com/cogno-us/cognous-open-control-stack) · [Selected pins](https://github.com/cogno-us/cognous-open-control-stack/blob/main/component-lock.json) · [Evidence and limits](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/release-status.md)

Component links are navigation, not a requirement to install every component. The hub lock determines its supported integration.

| Component | Responsibility |
|---|---|
| [Cognous Action Manifest](https://github.com/cogno-us/cognous-action-manifest) | Declare the action before evaluating permission |
| [Cognous Control Plane](https://github.com/cogno-us/cognous-control-plane) | Evaluate proposals against authority and preserve the decision record |
| [Cognous Replay Bundle](https://github.com/cogno-us/cognous-replay-bundle) | Reconstruct what the retained records support |
| [Cognous Governance Evidence Pack](https://github.com/cogno-us/cognous-governance-evidence-pack) | Turn traceable runtime records into reviewable governance evidence |
| [Open Decision Evidence Standard](https://github.com/cogno-us/open-decision-evidence-standard) | Portable decision evidence across system and organizational boundaries |
| [Cognous Governed Exchange](https://github.com/cogno-us/cognous-governed-exchange) | Governed exchange and continuity for a bounded synthetic workflow |
| [Cognous Execution Runtime](https://github.com/cogno-us/cognous-execution-runtime) | Constrained execution beneath independent current authorization |
| [Cognous Evidence Attestation](https://github.com/cogno-us/cognous-evidence-attestation) | Verify issuer signatures under explicit trust assumptions |
| [Cognous Evidence Registry](https://github.com/cogno-us/cognous-evidence-registry) | A local blockchain reference for claims, evidence commitments and lifecycle history |
| [Portable Reasoning Protocol v1.0](https://github.com/cogno-us/portable-reasoning-protocol) | Portable instructions for evidence-bounded reasoning |
| [Research Intelligence Protocol v1.0](https://github.com/cogno-us/research-intelligence-protocol) | Disciplined discovery and cross-domain abstraction, kept separate |
| [TFA Protocol (S43)](https://github.com/cogno-us/truth-freedom-agency-protocol) | Truth · Freedom · Agency |

## Repository locations

See the [repository rename map and compatibility notes](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/repository-renames.md) for current component URLs. Existing package names, schema identifiers and retained producer identities are unchanged.
