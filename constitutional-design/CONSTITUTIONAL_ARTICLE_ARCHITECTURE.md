# Constitutional Article Architecture

## Status and Boundary

**PRE-DRAFTING STRUCTURAL BLUEPRINT — NO CONSTITUTIONAL PROVISIONS**

This architecture consolidates `CR-001` through `CR-035` under decided
`CDR-001` through `CDR-005`. It does not enact constitutional text, resolve an
open issue, create an office or constituency, select a threshold or procedure,
authorize subordinate law, define an implementation standard, or create runtime
authority.

The exact source-to-consolidation-to-article mapping is recorded in
[`CONSOLIDATED_REQUIREMENT_MAP.yaml`](CONSOLIDATED_REQUIREMENT_MAP.yaml).

## Architectural Decision

The tested ten-article candidate should be consolidated into **eight
substantive articles**:

1. **Article I — Constitutional Identity and Human Sovereignty**
2. **Article II — Constitutional Authority, Constraint, and Separation of
   Functions**
3. **Article III — Constitutional Adjudication and Enforcement**
4. **Article IV — Epistemic Integrity, Provenance, Dissent, and Effective
   Power**
5. **Article V — Emergency Authority**
6. **Article VI — Continuity, Succession, and Interregnum**
7. **Article VII — Amendment and Constitutional Change**
8. **Article VIII — Refounding, Termination, Continuity of Obligations, and
   Constitutional Memory**

The candidate's separate powers-and-offices article is not yet supported:
accepted requirements establish counter-power and separation boundaries but do
not establish particular offices or allocate a complete set of powers. Those
principles therefore belong with constitutional authority and constraint.

Refounding and termination are combined because accepted requirements establish
identity discontinuity and non-erasing history, but do not yet establish a
complete termination authority or the treatment of obligations, assets,
reliance, and remedies. Splitting them would imply a resolved termination design
that does not exist.

## Article I — Constitutional Identity and Human Sovereignty

**Purpose:** State whose institution this is, who remains the ultimate
beneficiary, and why capability, delegation, continuity, necessity, reliance, or
effective control cannot create foundational sovereignty.

**Consolidated requirements:** `CCR-001`

**Source requirements:** `CR-001`, `CR-003`, `CR-015`

**Controlling CDRs:** `CDR-001`, `CDR-003`

**Unresolved issues:** `IR-01`, `IR-02`, `IR-04`, `IR-08`, `IR-09`, `IR-11`,
`IR-15`, `IR-17`, `IR-18`

**Dependencies:** None; this article supplies identity premises used throughout
the architecture.

**Explicitly excluded from constitutional text at this stage:** Membership,
foundational constituencies, selection, identity proof, office design,
succession process, and machine implementation.

**Anticipated subordinate-law needs:** Membership administration and ordinary
delegation administration only after their constitutional boundaries are
decided.

**Anticipated implementation standards:** Identity, authorization, delegation,
and registry systems that implement later constitutional and subordinate-law
decisions without defining membership or sovereignty.

## Article II — Constitutional Authority, Constraint, and Separation of Functions

**Purpose:** Establish binding constraints on ordinary human and artificial
power, independent review, and distributed counter-power without transferring
sovereignty over institutional ends.

**Consolidated requirements:** `CCR-002`, `CCR-003`

**Source requirements:** `CR-002`, `CR-004`, `CR-006`

**Controlling CDRs:** `CDR-001`, `CDR-004`

**Unresolved issues:** `IR-02`, `IR-06`, `IR-08`, `IR-09`, `IR-10`, `IR-17`,
`IR-18`

**Dependencies:** Article I for legitimate authority; Article III for the
adjudicative form of review; Article IV for reasons, dissent, provenance, and
effective-power visibility.

**Explicitly excluded from constitutional text at this stage:** A complete list
of offices or powers; reviewer composition, appointment, removal, jurisdiction,
remedies, enforcement, and appeal; institutional implementation.

**Anticipated subordinate-law needs:** Office administration, delegation,
filing, review administration, and counter-power coordination after
constitutional allocation is decided.

**Anticipated implementation standards:** Authority registries, delegation
records, publication, and verification systems that cannot allocate power or
determine legitimacy.

## Article III — Constitutional Adjudication and Enforcement

**Purpose:** Locate final human constitutional judgment within bounded
jurisdiction, preserve reviewer non-sovereignty, prohibit adjudicative amendment
or refounding, and separate judgment from enforcement.

**Consolidated requirements:** `CCR-013`, `CCR-014`, `CCR-015`, `CCR-016`

**Source requirements:** `CR-021`, `CR-022`, `CR-023`, `CR-024`, `CR-025`,
`CR-026`, `CR-027`, `CR-028`, `CR-029`

**Controlling CDRs:** `CDR-002`, `CDR-003`, `CDR-004`, `CDR-005`

**Unresolved issues:** `IR-01`, `IR-02`, `IR-03`, `IR-04`, `IR-06`, `IR-07`,
`IR-08`, `IR-09`, `IR-10`, `IR-12`, `IR-13`, `IR-14`, `IR-15`, `IR-17`,
`IR-18`

**Dependencies:** Articles I and II for authority and constraint; Article IV for
epistemic safeguards; Articles V and VI for the authority being reviewed;
Articles VII and VIII for the interpretation/change boundary.

**Explicitly excluded from constitutional text at this stage:** Standing,
composition, appointment, tenure, removal, recusal, substitution, appeal,
finality, exact jurisdiction, exact remedies, enforcement architecture,
noncompliance consequences, and machine-support implementation.

**Anticipated subordinate-law needs:** Filing, evidence, hearing, record,
recusal, appeal, enforcement, disclosure, and administrative procedures after
their constitutional design is decided.

**Anticipated implementation standards:** Case, evidence, provenance,
publication, validation, enforcement-tracking, and audit systems that cannot
exercise judgment or determine legitimacy.

## Article IV — Epistemic Integrity, Provenance, Dissent, and Effective Power

**Purpose:** Supply a shared constitutional vocabulary for evidence boundaries,
reason-giving, attributable decisions, durable dissent, precedent,
supersession, reviewability, and the distinction between formal and effective
power.

**Consolidated requirements:** `CCR-004`

**Source requirements:** `CR-005`

**Controlling CDRs:** `CDR-001`

**Unresolved issues:** `IR-06`, `IR-09`, `IR-12`, `IR-17`, `IR-18`

**Dependencies:** Article I for human authority and Article II for
constitutional constraint. Every later article cross-references these general
safeguards rather than duplicating them.

**Explicitly excluded from constitutional text at this stage:** Record formats,
publication platforms, retention periods, identity systems, cryptography,
formal validators, observability metrics, and monitoring tools.

**Anticipated subordinate-law needs:** Disclosure, record handling, publication,
retention, challenge, and audit administration.

**Anticipated implementation standards:** Storage, integrity, identity,
authentication, provenance encoding, technical validation, observability, and
monitoring, none of which may determine constitutional legitimacy.

## Article V — Emergency Authority

**Purpose:** Establish predelegation as the emergency default, bound the
human-only necessity fallback, require provenance and retrospective human
review, preserve outcome neutrality, and prevent emergency authority from
becoming succession or constitutional-change authority.

**Consolidated requirements:** `CCR-005`, `CCR-006`, `CCR-007`, `CCR-008`,
`CCR-011`

**Source requirements:** `CR-007`, `CR-008`, `CR-009`, `CR-010`, `CR-011`,
`CR-012`, `CR-013`, `CR-019`

**Controlling CDRs:** `CDR-002`, `CDR-003`, `CDR-004`, `CDR-005`

**Unresolved issues:** `IR-01`, `IR-03`, `IR-04`, `IR-05`, `IR-06`, `IR-08`,
`IR-09`, `IR-10`, `IR-13`, `IR-14`, `IR-15`, `IR-17`, `IR-18`

**Dependencies:** Articles I and II for authority boundaries; Article III for
retrospective review; Article IV for provenance; Article VI for
succession/interregnum separation; Articles VII and VIII for the
non-amendment/non-refounding boundary.

**Explicitly excluded from constitutional text at this stage:** Eligible actors,
exact evidence thresholds, absolute prohibitions, contact standards, complete
trigger tests, reviewer constitution, remedies, prolonged-emergency treatment,
clocks, restoration mechanics, and technical enforcement.

**Anticipated subordinate-law needs:** Emergency contact, filing, notification,
review, restoration, and record-administration procedures after constitutional
design is complete.

**Anticipated implementation standards:** Durable emergency logging, evidence
capture, communications, expiry, revocation, and alerting systems.

## Article VI — Continuity, Succession, and Interregnum

**Purpose:** Permit narrow administrative continuity without sovereign
succession, suspend foundational powers, require a bounded human succession or
refounding path, constrain usurpation, and restore returning authority without a
custodian veto.

**Consolidated requirements:** `CCR-009`, `CCR-010`, `CCR-012`

**Source requirements:** `CR-014`, `CR-016`, `CR-017`, `CR-018`, `CR-020`

**Controlling CDRs:** `CDR-003`, with boundaries from `CDR-002`, `CDR-004`, and
`CDR-005`

**Unresolved issues:** `IR-04`, `IR-05`, `IR-06`, `IR-07`, `IR-08`, `IR-09`,
`IR-10`, `IR-12`, `IR-13`, `IR-15`, `IR-16`, `IR-17`, `IR-18`

**Dependencies:** Article I for sovereign identity; Article III for disputed
evidence and succession review; Article IV for evidence and effective-power
visibility; Article V for emergency separation; Article VIII for the
succession-versus-refounding boundary.

**Explicitly excluded from constitutional text at this stage:** Process
composition and selection, proof of incapacity/death/loss/return/identity,
standing, exact surviving grants, maximum duration, disputed succession
procedure, invalid succession remedies, restoration mechanics, and detailed
effective-power controls.

**Anticipated subordinate-law needs:** Continuity administration, evidence
filing, challenge, restoration, invalidation, and reliance procedures after
their constitutional bounds are decided.

**Anticipated implementation standards:** Identity, evidence, records, expiry,
revocation, monitoring, and restoration-support systems.

## Article VII — Amendment and Constitutional Change

**Purpose:** Distinguish ordinary amendment, structural amendment, and explicit
refounding; preserve human authorization; prevent adjudication, emergency,
succession, or machine assistance from creating change authority; and prohibit
cumulative amendment laundering.

**Consolidated requirements:** `CCR-017`, `CCR-019`

**Source requirements:** `CR-030`, `CR-032`, `CR-033`, `CR-034`

**Controlling CDRs:** `CDR-002`, `CDR-003`, `CDR-004`, `CDR-005`

**Unresolved issues:** `IR-01`, `IR-02`, `IR-03`, `IR-04`, `IR-05`, `IR-06`,
`IR-07`, `IR-08`, `IR-09`, `IR-10`, `IR-12`, `IR-13`, `IR-15`, `IR-16`,
`IR-17`, `IR-18`

**Dependencies:** Articles I and II for legitimate human authority; Article III
for classification review without change power; Article IV for provenance and
effective-power visibility; Article VIII for the identity boundary.

**Explicitly excluded from constitutional text at this stage:** Legitimate
constituencies, exact classifications, thresholds, notice, deliberation,
consent, timing, challenge, appeal, cumulative-effect methodology, aggregation,
and remedies.

**Anticipated subordinate-law needs:** Proposal, notice, deliberation, voting,
challenge, appeal, publication, and supersession procedures only after their
constitutional design is decided.

**Anticipated implementation standards:** Proposal records, provenance,
formal-step validation, cumulative-change analysis support, and publication
systems that cannot authorize change or settle legitimacy.

## Article VIII — Refounding, Termination, Continuity of Obligations, and Constitutional Memory

**Purpose:** Identify the ten refounding-level principles, preserve their human
changeability only through explicit refounding, require acknowledged
constitutional discontinuity, and prohibit erasure of the prior order and its
history.

**Consolidated requirements:** `CCR-018`, `CCR-020`

**Source requirements:** `CR-031`, `CR-035`

**Controlling CDRs:** `CDR-001`, `CDR-002`, `CDR-003`, `CDR-004`, `CDR-005`

**Unresolved issues:** `IR-01`, `IR-02`, `IR-03`, `IR-04`, `IR-06`, `IR-08`,
`IR-10`, `IR-12`, `IR-13`, `IR-15`, `IR-16`, `IR-17`, `IR-18`

**Dependencies:** All preceding articles define the identity and authority whose
replacement constitutes refounding.

**Explicitly excluded from constitutional text at this stage:** Refounding
constituency and threshold, authorization procedure, transition, termination
authority, obligations, assets, reliance, remedies, succession interaction,
record systems, and implementation.

**Anticipated subordinate-law needs:** Transition administration and treatment
of obligations, assets, records, reliance, and remedies only after explicit
constitutional decisions establish their governing principles.

**Anticipated implementation standards:** Archival preservation, lineage,
supersession, integrity, export, and continuity records that cannot determine
the legitimacy of refounding.

## Consolidation Findings

### Duplicates and Overlaps

The source requirements contain no deletable duplicate. They contain nine
material overlaps that should share vocabulary and cross-references:

- Human sovereignty and machine non-sovereignty: `CR-001`, `CR-003`, `CR-015`,
  `CR-031`.
- General constraint and review: `CR-002`, `CR-004`, `CR-006`, `CR-021`,
  `CR-022`.
- Provenance, reasons, dissent, and reviewability: `CR-005`, `CR-011`, `CR-018`,
  `CR-025`, `CR-035`.
- Counter-power and verification: `CR-006`, `CR-024`, `CR-027`, `CR-029`.
- Emergency source, limits, review, and succession separation: `CR-007` through
  `CR-013`, `CR-019`.
- Continuity without accretion: `CR-014`, `CR-016`, `CR-020`.
- Adjudication versus constitutional change: `CR-023`, `CR-030`, `CR-033`.
- Machine validity versus legitimacy: `CR-003`, `CR-028`, `CR-032`.
- Amendment/refounding sequence: `CR-030`, `CR-031`, `CR-034`, `CR-035`.

### Classification

| Classification | Consolidated count | Meaning here |
|---|---:|---|
| `READY_FOR_CONSTITUTIONAL_DRAFT` | 11 | The adopted principle can be drafted without inventing unresolved mechanics. |
| `BLOCKED_BY_UNRESOLVED_DESIGN` | 9 | Material constitutional choices must be decided before complete drafting. |
| `SUBORDINATE_GOVERNANCE_LAW` | 0 | No source CR belongs wholly here; anticipated procedures are listed per article. |
| `IMPLEMENTATION_STANDARD` | 0 | No source CR belongs wholly here; anticipated technical standards are listed per article. |

### Material Conflicts or Gaps

No source CR records an express conflict. Five material tensions remain bounded
but incompletely designed:

1. Human sovereignty versus binding constitutional limits on ordinary human
   power.
2. Predelegated emergency authority versus a necessity fallback outside existing
   authority.
3. Administrative continuity versus legitimate sovereign succession.
4. Binding adjudication versus reviewer non-sovereignty and the
   interpretation/amendment boundary.
5. Refounding discontinuity versus continuity of obligations, assets, reliance,
   and remedies.

The largest drafting gaps are legitimate constituencies; offices and allocation
of powers; adjudicator and reviewer design; emergency evidence and remedy
standards; succession proof and process; amendment/refounding thresholds and
procedures; cumulative-effect methodology; termination authority; and
post-refounding obligations, assets, reliance, and remedies.

## Coverage Proof

The map contains 35 coverage rows, one for each source requirement from
`CR-001` through `CR-035`. Each source requirement appears in exactly one
consolidated requirement and one primary article. Cross-references identify
overlap without duplicating primary coverage.

## Preserved State

- `CDR-001` through `CDR-005`: `DECIDED`
- `FQ-01` through `FQ-05`: `RESOLVED`
- `IR-01` through `IR-18`: `OPEN`
- `CR-001` through `CR-035`: `ACCEPTED_FOR_DRAFTING`
- Constitutional provisions: **0**
- Governance runtime artifacts: **0**
