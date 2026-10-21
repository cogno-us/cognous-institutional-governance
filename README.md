<!-- cognous-banner:start -->
```text
──────────────────────────────────────────────────
   __________  _______   ______  __  _______
  / ____/ __ \/ ____/ | / / __ \/ / / / ___/
 / /   / / / / / __/  |/ / / / / / / /\__ \
/ /___/ /_/ / /_/ / /|  / /_/ / /_/ /___/ /
\____/\____/\____/_/ |_/\____/\____//____/
         COGNOUS INSTITUTIONAL GOVERNANCE
       g o v e r n e d   b y   d e s i g n
  github.com/cogno-us/cognous-open-control-stack
──────────────────────────────────────────────────
```
<!-- cognous-banner:end -->

# Cognous Institutional Governance

**Authority, challenge and correction for institutions.** Display alias: Alvorada (the older name; the repository and the component are called Institutional Governance, and the former alvorada repository is now the [governed exchange](https://github.com/cogno-us/cognous-governed-exchange); see the hub [naming table](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/naming.md)).

**Status:** group 02 · Institutional Governance; lock status **selected** (Authority Context 0.1.0 at the revision named in the [revision table](#revisions-and-selection)); constitutional designs, the delay limit and the 0.2.0 schema generation are **proposed**; proposed authority is not operative authority. Nothing here is a release. Cognous operational environment trust remains [not established](https://github.com/cogno-us/cognous-stack-orchestrator/issues/30).

## What it is

An open research framework for businesses, public bodies and communities, with or without AI. It combines proposed constitutional designs, proportional governance, domain guidance, decision templates and a public-stack implementation profile (the Authority Context) with a small reference checker. Repository acceptance does not ratify a constitution.

**Who it is for.** Institutional designers, governance reviewers and teams mapping human authority into software. Institutions need to identify who may decide, how decisions can be challenged and who verifies correction. AI can assist evidence preparation and routine review, but it cannot create institutional authority or turn a published design into operative law.

**What it does not do.** This remains proposed guidance and constitutional research, not adopted governance, operative law or demonstrated institutional superiority. Synthetic adapters did not demonstrate better institutional outcomes than conventional controls. Runtime enforcement belongs downstream (Control Plane and Execution Runtime); constitutional text, recorded decisions and source hierarchy remain intact. See [limits](#limits).

**Example.** A caseworker's refund recommendation may cite a proposed review rule; that citation is not a grant. Before software attempts an effect, the relevant real institution must establish decision rights, authenticate the authority source and provide any required approval through its own process. A synthetic Authority Context fixture can test schema and downstream refusal logic, but cannot attest that an actual institution adopted the proposed constitution, mandate or policy. A successful attestation of bytes likewise establishes no grant. A valid signature, chain inclusion, message receipt, reasoning instruction or evidence-package digest does not authorize execution; institutional authority must be supplied and evaluated through the appropriate trusted boundary.

## Where it fits

<a id="cognous-stack-components"></a>

<!-- stack-map:start -->
<!-- Canonical block: identical text in every component README. Source: docs/stack-map.md in the hub. Refresh at the pin round. -->
The Open Control Stack groups its repositories by responsibility. The groups are a navigation map, not an execution sequence and not a requirement to install every component. The hub [component lock](https://github.com/cogno-us/cognous-open-control-stack/blob/main/component-lock.json) is the only source of selected revisions; [release status](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/release-status.md) states their evidence and limits. Last checked against `component-lock.json` at hub commit `dcc9bd7533ef`.

| Group | Members |
| --- | --- |
| **01 Knowledge & Provenance** | [Evidence Registry (The Index)](https://github.com/cogno-us/cognous-evidence-registry) · [Evidence Attestation (BitRep)](https://github.com/cogno-us/cognous-evidence-attestation) |
| **02 Institutional Governance** | [Institutional Governance (Alvorada)](https://github.com/cogno-us/cognous-institutional-governance) |
| **03 Declaration & Policy Control** | [Action Manifest](https://github.com/cogno-us/cognous-action-manifest) · [Control Plane](https://github.com/cogno-us/cognous-control-plane) |
| **04 Constrained Execution** | [Execution Runtime](https://github.com/cogno-us/cognous-execution-runtime) |
| **05 Replay & Evidence** | [Replay Bundle](https://github.com/cogno-us/cognous-replay-bundle) · [Governance Evidence Pack](https://github.com/cogno-us/cognous-governance-evidence-pack) · [ODES](https://github.com/cogno-us/open-decision-evidence-standard) |
| **Cross-cutting exchange** | [Governed Exchange (GAX/IMX)](https://github.com/cogno-us/cognous-governed-exchange) |
| **Tooling and qualification** (side group) | [Ergonomics (`cognous-ocs`)](https://github.com/cogno-us/cognous-open-control-stack-ergonomics) · [Verifier](https://github.com/cogno-us/cognous-open-control-stack-verifier) · [Orchestrator](https://github.com/cogno-us/cognous-stack-orchestrator) · [Qualification](https://github.com/cogno-us/cognous-stack-qualification) |

Status labels used in this README: **merged** (reviewed and merged in the owning repository; not by itself selected), **selected** (pinned in the hub lock), **known limit** (a limitation that is stated and kept visible) and **proposed** (draft or planned work, not a supported interface). Full map, names and commands: [stack map](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/stack-map.md), [naming](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/naming.md), [profiles and tools](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/profiles-and-tools.md). A signature, registry entry, message receipt or evidence summary does not grant execution authority.
<!-- stack-map:end -->

This component sits in group 02. Its Authority Context is consumed downstream by [Action Manifest](https://github.com/cogno-us/cognous-action-manifest) (declares requirements), [Control Plane](https://github.com/cogno-us/cognous-control-plane) (resolves actual authority and decides) and [Execution Runtime](https://github.com/cogno-us/cognous-execution-runtime) (enforces at the effect boundary); evidence about it can travel through [Replay Bundle](https://github.com/cogno-us/cognous-replay-bundle) and [ODES](https://github.com/cogno-us/open-decision-evidence-standard). The downstream controller must still authenticate the deployment's resolver and enforce its permissions at effect time. Test results, run commentary and historical qualification records are in the [central test hub](https://github.com/cogno-us/cognous-stack-qualification/blob/main/results/readme-commentary/index.md); read them against their recorded source revisions.

## Quick start

Prerequisites: Linux, Python 3.10 or newer (the commands below were run on 3.13), nothing else for the first step. These commands check repository structure and synthetic invariants, not legitimacy or real-world institutional performance.

**1. Check the repository (about a second).** `validate_bootstrap.py` reads the constitutional-design records and prints its counts:

```bash
python tools/validate_bootstrap.py
```

Expected: exit code 0 and, among about 130 lines of counts, `VALIDATION_RESULT: PASS`, `ISSUE_COUNT: 18` and `CONSTITUTIONAL_PROVISION_COUNT: 0` (no adopted provision exists).

**2. Install the one optional dependency (about ten seconds).** The Authority Context and lineage checks need `jsonschema`; without it those tests skip silently and the suite still reports OK:

```bash
python -m pip install -r testing/harness/requirements-authority.txt
```

**3. Run the Authority Context reference checks (a few seconds):**

```bash
python testing/harness/run_authority_context.py
```

Expected: a JSON report that starts with `"status": "EXECUTED_LOCAL_REFERENCE_CHECKS"`, `"runtime_enforcement": false`, `"fixture_count": 54` and `"passed": 54`. Every fixture carries its own expected outcome (accepted or refused); the report counts how many matched.

**4. Run the full test suite (about three minutes; five or more on a loaded machine).** It includes tests that build and verify temporary copies of the repository:

```bash
python -m unittest discover -s tests -q
```

Expected: `Ran 469 tests ... OK` with no skips once `jsonschema` is installed (31 tests skip without it).

The result of any of these is a statement about encoded invariants and synthetic fixtures. A pass is not a legitimacy, compliance or production conclusion.

**Read first.** For one route through the material rather than a repository tour, use the [guides index](docs/README.md), [Getting started](docs/GETTING_STARTED.md) and the invented [service case](docs/examples/SERVICE_CASE.md). Constitutional designs, historical research, proposed workflows and actual institutional adoption are different categories; the [evidence status guide](docs/EVIDENCE_STATUS.md) records those distinctions.

## What is in this repository

Labels: **proposed** (a design or profile that is not adopted), **research** (analysis and sources), **canonical** (text that is the maintained record and is not edited casually), **historical** (a preserved record), **synthetic** (invented fixtures and reference checks).

| Area | What it holds | Label |
| --- | --- | --- |
| [constitution/](constitution/README.md) | Reserved for adopted constitutional law. It contains no adopted provisions. | canonical (empty by design) |
| [constitutional-design/](constitutional-design/README.md) | The proposed Constitution v0.1, the [modular framework](constitutional-design/modular/README.md) (shared charter and four profiles), the human design decisions, requirements and reviews behind them. Proposed for human ratification, not adopted. | proposed; canonical text |
| [process/](process/README.md) | How the principles were developed; [proportional governance](process/PROPORTIONAL_GOVERNANCE.md), [operational stewardship](process/OPERATIONAL_STEWARDSHIP.md), the [authorization-to-effect contract](process/AUTHORIZATION_EFFECT_CONTRACT.md) and the two implementation profiles below. | proposed |
| [process/implementation/public-stack-v0.1/](process/implementation/public-stack-v0.1/README.md) | Authority Context profile 0.1.0: [specification](process/implementation/public-stack-v0.1/AUTHORITY_CONTEXT.md), provision mapping, worked cases, schemas for generations 0.1.0 and 0.2.0, examples. | proposed profile; schema 0.1.0 selected by the lock |
| [process/implementation/authority-lineage-v0.1/](process/implementation/authority-lineage-v0.1/README.md) | Authority lineage evidence profile 0.1.0: origin, delegation, mutation, succession, resolution and use records, with a schema. Non-authorizing. | proposed; synthetic checks |
| [applications/](applications/README.md) | Eighteen illustrative context guides (customer service, finance, health administration, government, AI agents and others). No constitutional effect. | proposed; illustrative |
| [governance-engineering/](governance-engineering/README.md) | Deferred implementation: no production governance runtime exists. | proposed (deferred) |
| [research/](research/README.md) | Research, history and film studies, comparative works, limitations and evaluation. | research |
| [history/](history/README.md) | A relocation notice that preserves older links; the maintained history is under research. | historical |
| [testing/](testing/README.md) | Proposed operational exercises, synthetic fixtures, reference harnesses and recorded results. Results commentary lives in the central test hub. | proposed; synthetic; historical results |
| [tests/](tests/README.md) | Repository conformance tests (469): bootstrap, Authority Context, schema generations, lineage, delay limits, reviewed-artifact digest. | synthetic |
| [tools/](tools/validate_bootstrap.py) | `validate_bootstrap.py`, the structure and traceability validator. | synthetic |
| [docs/](docs/README.md) | The guides index and reference pages: getting started, evidence status, FAQ, glossary, architecture guide, assessments and reviews. | proposed; reviews are historical |
| [collateral/](collateral/business-collateral.md) | A [business overview](collateral/business-collateral.md) and a [one-page overview](collateral/one-page-overview.md). Both describe this component's role and evidence limits, not additional runtime features. | non-technical |

Single-file items: [CONTRIBUTING.md](CONTRIBUTING.md), [GOVERNANCE.md](GOVERNANCE.md), [SECURITY.md](SECURITY.md), [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md), [CHANGELOG.md](CHANGELOG.md), [CITATION.cff](CITATION.cff), [LICENSE](LICENSE), [NOTICE.md](NOTICE.md).

The Authority Context has two schema generations: 0.1.0 (no delay limit) and 0.2.0 (`requirement.consequence.delay_limit` required, declaration only). A context is validated against the schema its own `schema_version` names; a missing, unsupported or non-string version is refused and nothing is coerced between generations. The reference checker also enforces validity windows for the lineage profile: an origin's `effective_at` and each delegation's `valid_from` (inclusive) and `expires_at` (exclusive) bound every point of a chain. Details and their own limits are on the [Authority Context](process/implementation/public-stack-v0.1/AUTHORITY_CONTEXT.md#schema-generations) and [lineage](process/implementation/authority-lineage-v0.1/README.md) pages.

## Revisions and selection

The [current hub component lock](https://github.com/cogno-us/cognous-open-control-stack/blob/main/component-lock.json) selects Authority Context revision `d4462697197d6eb4e76bbfc3d712c8c1dab27884`, which carries Authority Context 0.2.0 and the lineage validator fixes of #60. Earlier revisions `0124adcdceb8`, `fb3d97938969` and `89e4722b0b7b` are superseded and kept as provenance. The V1 profile (revisions r4 to r8) pins this repository at `cbc39e79`; the hub lock does not select that revision. Later source acceptance does not create adoption or automatically update runtime selection.

| Revision | Role | Note |
| --- | --- | --- |
| [`d4462697197d`](https://github.com/cogno-us/cognous-institutional-governance/commit/d4462697197d6eb4e76bbfc3d712c8c1dab27884) | selected | What the hub lock selects: Authority Context 0.1.0 and 0.2.0 as separate generations, lineage validity dates enforced, redelegation limits and one origin per authority enforced by the synthetic lineage validator. |
| [`0124adcdceb8`](https://github.com/cogno-us/cognous-institutional-governance/commit/0124adcdceb8cee973f0631adb2639f14472df63) | superseded | Previously selected. Kept as provenance. |
| [`fb3d97938969`](https://github.com/cogno-us/cognous-institutional-governance/commit/fb3d97938969a89e149e8ff8db2756091d1233fc) | superseded | Previously selected: Authority Context 0.1.0 only. Kept as provenance. |
| [`89e4722b0b7b`](https://github.com/cogno-us/cognous-institutional-governance/commit/89e4722b0b7b9337d47f36afd28a28b076b128fd) | superseded | An earlier accepted main source (the authority-lineage profile acceptance). Kept as provenance. |
| `412fbbdcd57d` | licensing head | Recorded in the lock as `licensing_head` (the Apache 2.0 adoption commit); it does not select a version. |
| [`cbc39e79`](https://github.com/cogno-us/cognous-institutional-governance/commit/cbc39e7) | V1 profile pin | Pinned by V1 profile revisions r4 to r8. Adds the proposed delay limit per consequence tier; the 0.1.0 schema was edited in place there. |
| [`d40522af`](https://github.com/cogno-us/cognous-institutional-governance/commit/d40522a) | earlier main | First Authority Context 0.2.0: generations 0.1.0 and 0.2.0 separated, lineage validity dates enforced. |
| `5737267d94d2` | historical hub link | An older hub revision linked from the [business overview](collateral/business-collateral.md). It is not a substitute for the current lock. |

The pinned version of this table is a reading aid; the lock is the only source of selection. The [implementation profile](process/implementation/public-stack-v0.1/README.md) preserves lawful-source precedence, proposed consumer mappings and the distinction between software checks and actual institutional adoption. The [common charter and modular profiles](constitutional-design/modular/README.md), [proportional procedures](process/PROPORTIONAL_GOVERNANCE.md), [research index](research/README.md) and [original Constitution v0.1](constitutional-design/drafts/CONSTITUTION_v0.1.md) remain canonical. The [operating guide](process/OPERATIONAL_STEWARDSHIP.md) and [learning process](process/VIRTUOUS_RECURSION.md) describe owners, review and correction. Merging documentation does not adopt any of them.

## Documentation

The [guides index](docs/README.md) is the documentation index; it lists the guides by question. Start with [getting started](docs/GETTING_STARTED.md), the invented [service case](docs/examples/SERVICE_CASE.md) and an [application guide](applications/README.md). Other entry points: [evidence status](docs/EVIDENCE_STATUS.md), [implementation profile](process/implementation/public-stack-v0.1/README.md), [testing index](testing/README.md) and [recorded results](testing/results/README.md).

## Limits

- **Proposed, not adopted.** Constitution v0.1 is proposed for human ratification. The constitution directory holds no adopted law.
- **Authority is external.** A schema pass or reference check cannot become a production allow result. Mapping institutional authority into the Authority Context needs a trusted institutional resolver; BitRep or Index records do not populate mandates or revocation.
- **The delay limit is a declaration.** `requirement.consequence.delay_limit` (0.2.0) is declared, not enforced by this repository, and no default delay exists for a 0.1.0 context. The five tier ceilings and the rule that both generations stay accepted are marked for the project owner to confirm.
- **One label, more than one content.** The Authority Context 0.1.0 schema at `cbc39e79` differs from the one at `fb3d9793`; generations are separated from `d40522af`, which the selected revision includes. A 0.1.0 context needs its own trusted binding, because the requirement is part of the compared binding.
- **Date checks cover the chain only.** Lineage windows come from the origin and the delegation chain. A mutation recorded after a delegation expired, and dates on succession records, are not checked.
- **Synthetic evidence.** The checks cover invented fixtures. Review original artifacts and their exact source revisions before extending a claim to a new environment. New dependencies, authority sources, destinations or enforcement mechanisms need their own compatibility and qualification. A passing reference case is not a certification of an enterprise deployment.

## Contributing and attribution

[Contribution guidance](CONTRIBUTING.md) describes review and validation expectations. Keep evidence-linked claims, preserve historical records and separate proposed features from accepted implementation.

See [LICENSE](LICENSE) and [attribution](NOTICE.md) for the existing terms and third-party scope. Developed by [Cognous](https://cogno.us); no licensing change is part of this documentation update. Repository renames: see the [rename map](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/repository-renames.md); package names, schema identifiers and retained producer identities are unchanged.

---

## Bibliography

Selected external sources from the October 2026 research review. These inform evaluation questions; they do not establish Cognous implementation, adoption, conformance or production qualification.

- [OECD. *Agentic AI in organisations: Early insights from practitioner interviews*. OECD Artificial Intelligence Papers, No. 65 (2026)](https://doi.org/10.1787/1257a26f-en). Qualitative practitioner research on bounded autonomy, oversight and organizational deployment.
- [John M. Willis. *Runtime Governance Body of Knowledge for Artificial Intelligence and Other Autonomous Systems — Glossary* (19 July 2026)](https://sustainablefuturetech.com/asg-wg-runtime-governance-glossary/). Discussion draft on authority, execution and evidence terminology; not an adopted standard or Cognous conformance requirement.
- [John W. Creswell and J. David Creswell. *Research Design: Qualitative, Quantitative, and Mixed Methods Approaches*, fifth edition. SAGE (2018)](https://edge.sagepub.com/creswellrd5e). Research-methods reference for explicit questions, comparison designs and interpretation limits.

See the [research bibliography](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/research-bibliography.md) for review scope and source-verification limits.

<!-- Retained anchors for existing documentation links. -->
<a id="evidence-and-supported-scope"></a>
