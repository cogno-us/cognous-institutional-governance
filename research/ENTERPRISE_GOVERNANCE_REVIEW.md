# Lessons from enterprise and agentic governance

**Executive summary:** Alvorada already addresses authority, challenge and
correction. These four readings expose a less developed connection to everyday
operations: knowing which workflows exist, who maintains them, when changes need
review and whether safeguards actually work. Add that connection without turning
every routine decision into a committee meeting.

For practice, use [operational stewardship](../process/OPERATIONAL_STEWARDSHIP.md).
For academic and source detail, [continue below](#detailed-analysis).
The additions are proposed guidance, not operating controls or field findings.

## Detailed analysis

### Review method and scope

Reviewed 2026-10-04 against repository commit
`48fd3697cfa4e4aee03745b68d2c2ef344a7a785`. Extracted text and inspected selected
rendered pages from four supplied PDFs; reviewed their orientation, relevant
operating sections and stated limitations. Compared those passages with existing
process guides, application guides, adoption/evidence documentation and evaluation
programs. This is a targeted gap review, not a line-by-line audit of every page,
legal verification, systematic literature review or reproduction of experiments.

An absence in this repository means a documentary gap, not proof that every user
lacks the practice. An absence in another framework's public account is not proof
that its organizations lack the control. New recommendations below are our
synthesis; no source endorses Alvorada or becomes a retrospective original influence.

All page references below are **PDF page positions**, starting at 1. Sun's printed
page numbers are generally one lower. The initial Kenney attachment (EG2) contained
300 pages and ended during section 20.6. That review correctly excluded unavailable
chapters. On 2026-10-04, the full 745-page attachment (EG2-F) became available;
its first 300 pages have identical extracted text to EG2. The later review extends
that baseline against repository commit `1ea31ee79f77f2e6b6c1124c93b52b55c0fbce3d`.

The full file includes all 46 chapters and appendices A–J. Text was extracted
throughout; selected relevant later passages were read and rendered pages checked.
This is **targeted review of a complete supplied file**, not verification of every
page, legal claim, template or bibliography. Its contents-page pagination does
not always match actual appendix positions; references here use actual PDF positions.

### Source register

| ID | Work and provenance | Passages used and access limits |
|---|---|---|
| EG1 | Winston Sun, *Guidelines for Implementing the Enterprise AI Governance Framework*; supplied PDF footer identifies *AI Governance Framework Implementation Guide*, ©2026, 57 pages | §§2–6, 9–10, 12–18 and Appendix E, especially PDF pp.4–9, 13–24, 25–28, 42–53. Complete-system boundaries, adoption versus governance capability, responsibility, change, evidence reconciliation and assurance. Practitioner guidance, not a comparative efficacy study. Exact public download/version not independently located; [author's related framework announcement](https://www.linkedin.com/posts/winston-sun-4666aa1b_updated-building-trustworthy-ai-ai-governance-activity-7508239833975111682-N-z2) is contextual, not verification of the attached guide. |
| EG2 | Noah M. Kenney, *The AI Governance Practitioner's Manual: Law, Privacy, Security, and Compliance for Every Role*, first edition, ©2026 Digital 520; 300 supplied pages | PDF pp.3, 5–15; chapter 2, especially pp.40–42; chapter 4 pp.62–63; chapter 5 pp.67–73; chapter 6 pp.78–86. Role-based navigation, accountable ownership, hidden AI use, staged implementation and budget/benchmark distinctions. [Author's publication page](https://noahkenney.com/books/ai-governance-practitioners-manual.html) confirms the work, not completeness or accuracy of the supplied excerpt. Later advertised chapters/appendices unavailable at the initial review (now supplemented by EG2-F); legal tables and numerical benefit claims not independently verified or imported. |
| EG2-F | Kenney, same work, full supplied manual, 745 pages | Targeted later review: chapter 23 pp.343–344,354–355 (supplier commitments); chapter 24 pp.367–370 and chapter 26 pp.392–393 (rights in operation); chapter 29 pp.421–426 (privacy design); chapter 33 pp.467–469,472–474 (fairness, explanation and scope); chapter 37 pp.520–523 (joined security/governance); chapter 39 pp.557–558 and chapter 41 pp.579–583 (assurance reporting and supplier chains); chapter 46 pp.643–648 (delegation, memory and unresolved rights questions). Appendices are present, not adopted templates. Legal interpretations, thresholds and technical assertions are not independently validated. |
| EG3 | Infocomm Media Development Authority (IMDA), *Model AI Governance Framework for Agentic AI*, v1.5, published 20 May 2026, updated 5 June 2026; supplied `GOVERNANCE_ON_AI.pdf`, 53 pages | §§2.1–2.4, especially PDF pp.15–24, 25–30, 38–47. Suitability, bounded access/actions, value-chain accountability, approval effectiveness, monitoring and user competence. Best-practice guidance; company cases are reported illustrations, not independent causal tests. [Official framework PDF](https://www.imda.gov.sg/assets/63438074-73f6-4dcc-a281-030f42642cf4.pdf) and [official announcement](https://www.imda.gov.sg/resources/press-releases-factsheets-and-speeches/press-releases/2026/new-model-ai-governance-framework-for-agentic-ai): retrieval met a verification wall; passage review used the supplied version. |
| EG4 | Kim Chin Jean Gan, Barbara Wilczek-Stronczek and Angeliki Papasava, *Governing the algorithm: a conceptual review of strategic AI oversight in global corporations*, AI & SOCIETY, 2026, 24 supplied pages; [DOI and publisher](https://doi.org/10.1007/s00146-026-03207-2), [university record](https://livrepository.liverpool.ac.uk/3199306/) | Abstract, §§2.5, 3.1–3.6, 6–8; especially PDF pp.5–8 and 16–18. Eight purposively selected firms, public disclosures, managerial/critical perspectives and strategic oversight. The review does not establish causality, internal-control effectiveness or legal compliance; public disclosure is selective and nonrepresentative. Publisher metadata checked: publication 1 July 2026. |

Attachment fingerprints identify the copies consulted, not a certification of
their authenticity or public availability:

| ID | SHA-256 |
|---|---|
| EG1 | `33aa158ed7b24dc26e1a411a52b0518cb9ee73e8d4b654afb289eda03a175442` |
| EG2 | `f384b39945d4616cba4b51d9058acda11c8e0bcc9bd4634f08e8f8158b3c0da9` |
| EG2-F | `55b76c592c13d86ea4bbc6c1198a9f3977517bb1207c328e775f5ba72a2226de` |
| EG3 | `2636e19ff1c86e862394d2fc900592e97b83c04cc35e3c8443108114b7f1dfba` |
| EG4 | `24c42a327a395fcd915aa9f14f1ea6dd03f9ce833129d69a4421438988adfa81` |

### What the readings add

**Sun: operational capability and evidentiary discipline.** EG1 treats the whole
workflow, rather than the model alone, as the boundary. Its Knowledge, Access,
Authority and Evidence approach distinguishes extent of adoption from governance
capability. The evidence discussion separates native activity records, deliberately
instrumented workflow records and derived assurance. It asks whether proposed,
approved and executed actions agree, whether outcomes are independently confirmed
and whether the recorded population omits transactions. This sharpens Alvorada's
existing remedy verification: a coherent case record can still conceal an omitted
case, unauthorized side effect or changed target.

**Kenney: responsibility must survive organizational reality.** EG2's available
sections connect governance responsibilities to actual authority, evidence and
resources. They include vendor-embedded and unofficial AI in discovery and stage
implementation rather than demand instant completeness. Its role-specific reading
paths reinforce the repository's progressive-disclosure approach. The distinction
between planning benchmarks and measured findings is useful; its stated return,
cost, staffing and timeline figures are not validated assumptions for Alvorada.

**Kenney's full manual: carry governance through the operating chain.** EG2-F
adds detail on rights requests across derived data and delegated services, the
population and conditions within which evaluation supports reliance, meaningful
explanations, assurance scope, supplier chains and coordinated incident handling.
These reinforce existing Alvorada principles rather than warrant a new constitution.
A corrected source does not ensure downstream decisions changed; a fairness score
does not establish justice; a certificate does not certify every deployment; and
a security alert does not authorize every institutional consequence. Documentary
remediation must preserve those distinctions and expose unresolved implementation.

**IMDA: human oversight itself needs review.** EG3 covers controlled permissions,
cross-organizational responsibilities, predeployment tests, continued monitoring
and user information. Approval frequency and response time can signal oversight
problems, but are not conclusive measures. It also warns that generated reasoning
may not faithfully explain an action and that human skills can erode. Alvorada
should test reviewers' practical ability to detect errors and intervene, rather
than infer oversight from a signature or an AI-generated justification.

**Gan and colleagues: public governance is not verified performance.** EG4 examines
what firms disclose and how they describe oversight. Its explicit managerial lens
and critical discussion expose a legitimacy problem: organizations may document
their own priorities while affected people lack practical influence. The useful
lesson is to inspect stakeholder concerns, board responses and control evidence
separately. Formal structures, persuasive disclosures and maturity descriptions
cannot establish equitable outcomes or effective restraint.

### Gap and remediation crosswalk

These are additions to existing guidance, not fourteen newly discovered constitutional
principles. Existing coverage is acknowledged to avoid duplicating worksheets.

| Gap | Already present | Remaining documentary weakness | Remediation / further work |
|---|---|---|---|
| OS1 workflow discovery | Domain guides and scoped decision records | No shared register of material workflows, unofficial uses and vendor features | Stewardship §1 and optional record; actual discovery and refresh still needed (EG1/EG2) |
| OS2 dependency/portfolio exposure | Independence and correlated-risk questions | No routine view of shared providers, staff, evidence routes and combined exposure | §2; contextual outage/concentration assessment pending (EG1/EG2/EG4) |
| OS3 accountable ownership | Grants, separation and adoption resources | Ongoing operation/change/stop/restart roles lack one compact handoff | §3; real mandates and alternates required (EG1/EG2/EG3) |
| OS4 supplier and obligation continuity | Rights/records/interface schedule | No explicit procurement, change-notice, export and verified retirement route | §§4–5; qualified contract/obligation review pending (EG1/EG2/EG3) |
| OS5 capability versus consequence | T0–T4 proportional governance | Adoption scale, AI capability and assurance readiness can be conflated | §6 separates axes; no equivalence with another source's numbered tiers (EG1/EG3) |
| OS6 change and lifecycle | Succession, replacement and recursive change | Need operational gates from intake to retirement and actual revalidation triggers | §5; delivery/stop/restart drills proposed (EG1/EG2/EG3) |
| OS7 approval quality and competence | Meaningful review, workload and non-AI alternatives | No compact review-effectiveness and skill-retention protocol | §7; observed competence/access/alert-load tests pending (EG2/EG3) |
| OS8 complete effect evidence | Remedy delivery, originals and outcome measures | Per-case records do not establish complete operational populations or exact approval scope | §8; missing/orphan/duplicate evidence scenarios proposed (EG1) |
| OS9 incident accountability | Exception, emergency, challenge and correction procedures | Routine containment, communication, near-miss and restart responsibilities scattered | §9; actual incident capacity/notification duties needed (EG1/EG3) |
| OS10 substantive oversight | Adoption incentives, causal evaluation and burden measures | Need operational reports of unresolved risk, affected-person concerns and action owners | §10; independent outcome comparison remains unexecuted (EG1/EG2/EG4) |
| OS11 downstream rights execution | Rights, retention and correction procedures | No compact route for requests across derived records, retrieval, recipients and delegated services | Rights procedure and stewardship §4; actual obligations, propagation and deletion limits require verification (EG2-F chs.24,26,46) |
| OS12 fitness and explanation | Subgroup harms, reviewer competence and outcome measures | Evaluation scope and explanation fidelity need explicit acceptance questions | §§7–8; local population/condition tests and intelligibility/fidelity assessment pending (EG2-F ch.33) |
| OS13 bounded assurance | Supplier duties and independence review | Certificates, reports and promises can be overgeneralized beyond entity/product/period or actual configuration | §4 and optional record; inspect scope, exclusions, chain changes and evidence independence (EG2-F chs.23,39,41) |
| OS14 joined incident handling | Incident lead, remedies and emergency separation | Security response and rights-affecting governance can lose each other's evidence or confuse mandates | §9; shared case and separated decisions need a real exercise (EG2-F ch.37) |

### Decisions made and why

1. **Add one cross-context operating guide.** Reuse existing rights, proportional
   review, adoption and recursion documents. Local units may link existing records;
   a second copied registry or mandatory report for every routine act adds burden.
2. **Preserve the broad institutional scope.** Apply stewardship to human workflows
   and ordinary software, with conditional AI considerations. A human-only process
   can fail through the same missing ownership, weak evidence or supplier dependency.
3. **Separate oversight from its implementation.** Give theory, responsibilities,
   acceptance questions and review scenarios; no runtime, telemetry code or claim
   that writing a policy enforces it. Engineering remains a separate undertaking.
4. **Keep the immutable record boundary.** No edits to Constitution v0.1, original
   decision/requirement/source-status data, harness, fixtures or frozen observations.
   Source review and new unexecuted scenarios live at their proper reading levels.
5. **Narrow the differentiation claim.** These sources also connect principles,
   authority, control and evidence. Alvorada's integration and constitutional
   lifecycle can be compared; whole-system scope or human accountability alone
   does not establish uniqueness or superiority.

### What was not imported

No source's legal deadlines, penalties, named-company performance claims, ROI
multipliers, fixed budgets or staffing ratios become repository facts or defaults.
No maturity label permits unsafe operation. No statistical outlier is presumed
to be a bad reviewer; justified dissent must remain protected. AI reasoning text
is not access to internal cognition or proof of why an action occurred. A stop
mechanism does not undo effects already delivered, and technical records do not
prove consent, fairness or an acceptable institutional purpose.

The full manual's numerical fairness, representation, drift and retention examples
are not Alvorada defaults. Select local acceptance criteria before examining results,
justify them against consequences, and disclose uncertainty and failure conditions.
Fairness metrics reflect different choices and assumptions; no metric automatically
settles a rights dispute. Agreement between explanation methods is not proof of
faithfulness. Privacy techniques have no universal ordering independent of their
assumptions and use. Certification and independent scrutiny need bounded scope;
an outside contractor is not automatically independent. Maturity and audit volume
remain distinct from substantive impact. No source's legal crosswalk, contract
notice period or unsettled claim about model erasure becomes authoritative here.

External works retain their rights. EG1 states noncommercial-use terms in Appendix
F; EG2 states all rights reserved. This repository includes original critical
analysis and guidance, not their PDFs, diagrams, checklists or copied templates,
and does not relicense those sources under CC BY 4.0. EG1's branded architecture
and EG2's five-layer model are attributed comparators, not adopted product designs.
The same reading may justify operational practice without justifying a particular
constitutional allocation. Transfer from corporate AI to other institutions is a
design inference requiring contextual review, not a finding of the sources.

### Completion boundaries

Documentary remediation is available in the [operating guide](../process/OPERATIONAL_STEWARDSHIP.md),
[optional record](../process/templates/WORKFLOW_STEWARDSHIP_RECORD.md) and
[proposed scenarios](../testing/research/OPERATIONAL_STEWARDSHIP_REVIEW.md).
Observed inventory completeness, genuine ownership, enforceable contracts,
legal applicability, independent assurance, human competence and comparative
outcome gains remain further work. The existing [evaluation program](../testing/programs/INSTITUTIONAL_ASSESSMENT.md)
supplies the route for collecting such evidence; this review produces no results.

Return to [research findings](FINDINGS.md) or [comparative work](COMPARATIVE_WORKS.md).
