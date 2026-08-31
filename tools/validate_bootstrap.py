#!/usr/bin/env python3
"""Validate Alvorada's constitutional research bootstrap invariants."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


ISSUE_FIELDS = {
    "issue_id",
    "title",
    "status",
    "question",
    "working_context",
    "known_prior_art",
    "historical_evidence",
    "experimental_evidence",
    "candidate_architectures",
    "dependencies",
    "conflicts",
    "dissent",
    "human_decision_required",
    "provenance",
    "last_reviewed",
}
PLACEHOLDERS = {
    "",
    "NOT_YET_INGESTED",
    "NOT_YET_REVIEWED",
    "NOT_YET_VERIFIED",
}
PRIOR_ART_SOURCE_STATUSES = {
    "VERIFIED",
    "PARTIALLY_VERIFIED",
    "SOURCE_TO_VERIFY",
    "RESEARCH_LEAD",
}
PRIOR_ART_OVERLAP_CLASSIFICATIONS = {
    "ESTABLISHED_PRIOR_ART",
    "KNOWN_BUT_UNCOMMON",
    "UNUSUAL_APPLICATION",
    "UNUSUAL_COMBINATION",
    "POTENTIALLY_DISTINCTIVE",
    "NO_CLOSE_PRIOR_ART_FOUND_IN_SEARCH",
    "INSUFFICIENT_EVIDENCE",
}
CANDIDATE_DISPOSITIONS = {
    "CANDIDATE_ADOPT",
    "CANDIDATE_EXTEND",
    "CANDIDATE_DESIGN",
    "NOT_APPLICABLE",
}
PRIOR_ART_REGISTER_FIELDS = {
    "register_status",
    "evidence_boundary",
    "novelty_rule",
    "permitted_research_classifications",
    "source_statuses",
    "candidate_dispositions",
    "prior_art_entries",
    "provenance",
}
PRIOR_ART_ENTRY_FIELDS = {
    "prior_art_id",
    "name",
    "field_or_tradition",
    "source_type",
    "source_status",
    "source_reference",
    "source_title",
    "source_author_or_organization",
    "source_date",
    "mechanisms",
    "relevant_issues",
    "overlap_classification",
    "candidate_disposition",
    "what_is_established",
    "what_alvorada_may_extend",
    "what_is_not_supported",
    "limitations",
    "provenance",
    "review_status",
}
ADOPTION_MAP_FIELDS = {
    "map_status",
    "evidence_boundary",
    "entries",
    "provenance",
}
ADOPTION_ENTRY_FIELDS = {
    "mechanism",
    "prior_art_sources",
    "candidate_disposition",
    "rationale",
    "relevant_issues",
    "known_gaps",
    "decision_required",
}
FORBIDDEN_FINAL_ADOPTION_STATUSES = {
    "ADOPTED",
    "APPROVED",
    "REJECTED",
    "DECIDED",
    "FINAL",
    "ACCEPTED_FOR_DRAFTING",
}
HISTORICAL_SOURCE_STATUSES = {
    "SOURCE_TO_VERIFY",
    "PARTIALLY_VERIFIED",
    "VERIFIED",
}
HISTORICAL_EVIDENCE_FIELDS = {
    "evidence_id",
    "polity_or_tradition",
    "period",
    "subject",
    "observation",
    "interpretation",
    "possible_constitutional_relevance",
    "relevant_issues",
    "counterevidence_or_limitations",
    "confidence",
    "source_status",
    "primary_source_leads",
    "secondary_source_leads",
    "provenance",
    "review_status",
}
EXPECTED_ISSUE_FILENAMES = {
    "IR-01-human-sovereignty.yaml",
    "IR-02-constraint-of-constitutional-authority.yaml",
    "IR-03-emergency-necessity.yaml",
    "IR-04-succession-and-interregnum.yaml",
    "IR-05-delegation-during-interregnum.yaml",
    "IR-06-constitutional-adjudication.yaml",
    "IR-07-offices-roles-membership-standing.yaml",
    "IR-08-formal-and-effective-power.yaml",
    "IR-09-incentive-compatibility.yaml",
    "IR-10-separation-of-functions.yaml",
    "IR-11-threshold-of-reliance.yaml",
    "IR-12-dissent.yaml",
    "IR-13-epistemic-integrity.yaml",
    "IR-14-proportional-governance.yaml",
    "IR-15-amendment-and-refounding.yaml",
    "IR-16-institutional-termination.yaml",
    "IR-17-constitutional-hierarchy.yaml",
    "IR-18-human-control-and-comprehensibility.yaml",
}
EXPECTED_ISSUE_IDS = {f"IR-{index:02d}" for index in range(1, 19)}
DECISION_FIELDS = {
    "decision_id",
    "title",
    "status",
    "question",
    "related_issues",
    "source_material",
    "assumptions",
    "candidate_architectures",
    "historical_analogues",
    "prior_art",
    "advantages",
    "failure_modes",
    "bad_human_analysis",
    "bad_artificial_intelligence_analysis",
    "incentive_analysis",
    "continuity_analysis",
    "reversibility_analysis",
    "human_comprehensibility_analysis",
    "reviews",
    "dissent",
    "human_decision",
    "decision_date",
    "supersedes",
    "resulting_requirements",
    "residual_uncertainty",
    "provenance",
}
DECISION_STATUSES = {
    "PROPOSED",
    "UNDER_REVIEW",
    "DISPUTED",
    "DECIDED",
    "DEFERRED",
    "SUPERSEDED",
    "UNRESOLVED",
}
HUMAN_DECISION_FIELDS = {
    "decision",
    "foundational_architecture",
    "incorporated_mechanisms",
    "rejected_mechanisms",
    "decision_authority",
    "decision_basis",
    "authorized_by",
    "authorization_record",
    "decision_date",
}
FQ1_DECISION_DATE = "2026-08-28"
FQ1_DECISION = "ADOPT_HYBRID"
FQ1_FOUNDATIONAL_ARCHITECTURE = (
    "E — Reserved Human Sovereignty + Entrenched Constitutional Limits"
)
FQ1_INCORPORATED_MECHANISMS = [
    "independent human review",
    "distributed counter-power where appropriate",
    "independent verification",
    "publication",
    "reason-giving",
    "durable dissent",
    "explicit precedent and supersession",
    "procedural regularity",
]
FQ1_REJECTED_MECHANISMS = [
    "unconstrained sovereign discretion",
    "reviewer sovereignty over institutional ends",
    "machine sovereignty",
    "final machine constitutional adjudication",
    "authority from performance",
    "authority from popularity",
    "authority from repeated reliance",
    "authority from operational indispensability",
]
FQ1_RESULTING_REQUIREMENTS = [
    "CR-001",
    "CR-002",
    "CR-003",
    "CR-004",
    "CR-005",
    "CR-006",
]
FQ1_RESOLUTION = (
    "ADOPT_HYBRID with Architecture E as the foundational architecture and "
    "incorporated human review, counter-power, verification, publication, "
    "reason-giving, dissent, precedent/supersession, and procedural regularity "
    "mechanisms."
)
FQ1_REQUIREMENT_PROVENANCE = (
    "Explicit human decision recorded in CDR-001 on 2026-08-28"
)
FQ1_REQUIRED_RESIDUAL_MARKERS = {
    "legitimate foundational human constituency",
    "binding force, remedies, appointment, and removal",
    "foundational human authority is itself a party",
    "emergency authority",
    "succession and interregnum",
    "amendment-refounding boundary",
    "effective-power measurement",
    "anti-accretion enforcement",
    "machine formalization and human constitutional judgment",
}
REQUIREMENT_FIELDS = {
    "requirement_id",
    "statement",
    "status",
    "source_issues",
    "source_decisions",
    "rationale",
    "constitutional_level",
    "implementation_boundary",
    "conflicts",
    "dissent",
    "verification_method",
    "draft_mapping",
    "provenance",
}
FQ1_REQUIREMENTS = {
    "CR-001": {
        "statement": (
            "Foundational human sovereignty over institutional ends must remain "
            "reserved to legitimate human constitutional authority."
        ),
        "source_issues": {"IR-01", "IR-02", "IR-15", "IR-17", "IR-18"},
    },
    "CR-002": {
        "statement": (
            "Ordinary exercise of institutional power, including exercise by "
            "humans, may be subject to binding constitutional limits."
        ),
        "source_issues": {"IR-02", "IR-06", "IR-10", "IR-17"},
    },
    "CR-003": {
        "statement": (
            "Artificial intelligence systems, software agents, validators, "
            "reviewers, or technical systems must not acquire foundational "
            "sovereignty solely through capability, execution, validation, "
            "reliance, popularity, performance, or operational indispensability."
        ),
        "source_issues": {"IR-01", "IR-08", "IR-09", "IR-17", "IR-18"},
    },
    "CR-004": {
        "statement": (
            "Independent human constitutional review may constrain ordinary "
            "institutional acts without acquiring sovereignty over institutional "
            "ends."
        ),
        "source_issues": {"IR-02", "IR-06", "IR-10", "IR-17"},
    },
    "CR-005": {
        "statement": (
            "Constitutional governance must support publication with durable "
            "provenance, reason-giving, dissent, precedent and supersession, and "
            "procedural regularity sufficient to make exercises of institutional "
            "power contestable and reviewable."
        ),
        "source_issues": {"IR-06", "IR-09", "IR-12", "IR-17", "IR-18"},
    },
    "CR-006": {
        "statement": (
            "The architecture must permit counter-power and independent "
            "verification mechanisms sufficient to reduce single-channel capture."
        ),
        "source_issues": {"IR-08", "IR-09", "IR-10", "IR-18"},
    },
}
FQ2_REQUIRED_ISSUES = {
    "IR-03",
    "IR-04",
    "IR-05",
    "IR-06",
    "IR-08",
    "IR-09",
    "IR-10",
    "IR-13",
    "IR-14",
    "IR-15",
    "IR-17",
    "IR-18",
}
FQ2_ARCHITECTURE_NAMES = {
    "A": "No Emergency Exception",
    "B": "Narrow Necessity Exception",
    "C": "Predelegated Emergency Authority",
    "D": "Distributed Emergency Concurrence",
    "E": "Hybrid Predelegation with Necessity Fallback",
}
FQ2_ARCHITECTURE_FIELDS = {
    "architecture_id",
    "name",
    "research_status",
    "model",
    "analysis",
}
FQ2_ANALYSIS_FIELDS = {
    "trigger",
    "who_may_act",
    "scope",
    "proportionality",
    "least_harm_requirement",
    "duration",
    "expiry",
    "logging_provenance",
    "retrospective_human_review",
    "remedies",
    "abuse_by_bad_human",
    "abuse_by_bad_ai",
    "false_emergency",
    "manufactured_unreachability",
    "repeated_exception_accretion",
    "succession_interregnum_interaction",
    "machine_validity_constitutional_legitimacy_boundary",
}
FQ2_ANALYSIS_REQUIRED_TERMS = {
    "trigger": ("trigger", "imminen", "condition"),
    "who_may_act": ("actor", "human", "delegate", "executor"),
    "scope": ("scope", "grant", "act", "authority", "power"),
    "proportionality": ("proportion", "excess", "harm", "grant"),
    "least_harm_requirement": ("least",),
    "duration": ("duration", "while", "period", "shorter", "lasts", "grant"),
    "expiry": ("expir", "automatic", "nonrenew", "deadline"),
    "logging_provenance": ("record", "log", "provenance", "evidence", "preserv"),
    "retrospective_human_review": ("review",),
    "remedies": ("remed", "revers", "contain", "compens"),
    "abuse_by_bad_human": ("bad human", "human", "grantor", "coalition"),
    "abuse_by_bad_ai": ("artificial intelligence",),
    "false_emergency": ("false", "fault", "sensor", "model"),
    "manufactured_unreachability": (
        "manufactur",
        "unreach",
        "isolation",
        "communication",
        "isolate",
        "attacker",
    ),
    "repeated_exception_accretion": ("repeat", "accret", "precedent", "renew"),
    "succession_interregnum_interaction": ("succession", "interregnum"),
    "machine_validity_constitutional_legitimacy_boundary": (
        "legitim",
        "machine",
        "validator",
        "technical",
        "signature",
    ),
}
FQ2_HISTORICAL_EVIDENCE_IDS = {
    "HE-ROME-003",
    "HE-US-004",
    "HE-T04",
    "HE-T09",
    "HE-BURKE-FRANCE-002",
    "HE-ROME-004",
    "HE-T01",
    "HE-T02",
    "HE-T03",
    "HE-T05",
    "HE-T06",
    "HE-T07",
}
FQ2_PRIOR_ART_IDS = {
    "PA-CC-001",
    "PA-AI-003",
    "PA-AUTH-002",
    "PA-AUTH-003",
    "PA-AUTH-004",
    "PA-PROV-001",
    "PA-POLICY-001",
    "PA-POLICY-002",
    "PA-POLICY-003",
    "PA-RELIANCE-001",
    "PA-DISSENT-001",
    "PA-DISSENT-002",
    "PA-POWER-001",
}
FQ2_PACKET_RELATIVE_PATH = Path(
    "constitutional-design/decisions/packets/"
    "CDR-002-HUMAN-DECISION-PACKET.md"
)
FQ2_PACKET_OPTIONS = (
    "ADOPT_A",
    "ADOPT_B",
    "ADOPT_C",
    "ADOPT_D",
    "ADOPT_E",
    "REVISE_AND_REVIEW",
    "DEFER",
)
FQ2_DECISION_DATE = "2026-08-28"
FQ2_DECISION = "ADOPT_E"
FQ2_SELECTED_ARCHITECTURE = (
    "E — Hybrid Predelegation with Necessity Fallback"
)
FQ2_INCORPORATED_MECHANISMS = [
    "explicit predelegated emergency authority as the default",
    "necessity fallback only when all conjunctive trigger conditions are satisfied",
    "human-only invocation of necessity fallback",
    "minimum protective action",
    "automatic expiry without self-renewal",
    "no precedent or future authority",
    "durable emergency provenance",
    "prompt retrospective independent human constitutional review",
    "outcome does not determine constitutional legitimacy",
]
FQ2_REJECTED_MECHANISMS = [
    "artificial intelligence invocation of necessity to enlarge its own authority",
    "fallback amendment",
    "fallback refounding",
    "creation or transfer of foundational sovereignty",
    "fallback self-renewal",
    "precedent or future authority from fallback action",
    "successful outcome as retroactive legitimacy",
    "harmful outcome as conclusive proof of constitutional injustice",
]
FQ2_RESULTING_REQUIREMENTS = [
    "CR-007",
    "CR-008",
    "CR-009",
    "CR-010",
    "CR-011",
    "CR-012",
    "CR-013",
]
FQ2_RESOLUTION = (
    "ADOPT_E: explicit predelegated emergency authority is the default; a "
    "human-only necessity fallback permits only minimum protective action when "
    "every conjunctive trigger condition is met, expires automatically without "
    "self-renewal, creates no precedent or future authority, and remains subject "
    "to durable provenance and prompt retrospective independent human "
    "constitutional review."
)
FQ2_REQUIREMENT_PROVENANCE = (
    "Explicit human decision recorded in CDR-002 on 2026-08-28"
)
FQ2_REQUIRED_RESIDUAL_UNCERTAINTY = [
    (
        "Which humans are constitutionally eligible to invoke the human-only "
        "necessity fallback remains unresolved under IR-03, IR-07, and IR-17."
    ),
    (
        "Exact evidence thresholds for imminence, expected irreversibility, "
        "adequacy, genuine unreachability, necessity, proportionality, and least "
        "harm remain unresolved under IR-03, IR-13, and IR-14."
    ),
    (
        "Absolute emergency prohibitions remain unresolved under IR-03 and IR-17."
    ),
    "Retrospective review remedies remain unresolved under IR-06.",
    (
        "The constitution, appointment, removal, independence, and constraint of "
        "reviewers remain unresolved under IR-06 and IR-10."
    ),
    (
        "Succession and interregnum remain unresolved under IR-04, IR-05, and "
        "FQ-03."
    ),
    (
        "The boundary at which prolonged emergency action becomes interregnum "
        "government, amendment, or refounding remains unresolved under IR-04, "
        "IR-15, and IR-17."
    ),
    (
        "Implementation and machine-formalization details remain unresolved under "
        "IR-10, IR-13, IR-17, and IR-18."
    ),
]
FQ2_REQUIREMENTS = {
    "CR-007": {
        "statement": (
            "Explicit predelegated emergency authority must be the default "
            "constitutional path for emergency action."
        ),
        "source_issues": {"IR-03", "IR-05", "IR-10", "IR-17"},
        "rationale": (
            "CDR-002 adopts Architecture E and expressly makes prior "
            "human-authorized emergency delegation the default rather than "
            "self-created necessity power."
        ),
        "implementation_boundary": (
            "Does not define emergency offices, delegates, grants, triggers, "
            "systems, or executable controls."
        ),
        "verification_method": (
            "Drafting traceability must identify predelegation as the default and "
            "must not present necessity as ordinary emergency authority."
        ),
    },
    "CR-008": {
        "statement": (
            "A necessity fallback may exist only when harm is imminent, harm is "
            "reasonably expected to be irreversible, no adequate action within "
            "existing authority is available, competent authority and valid "
            "emergency delegates are genuinely unreachable, action is necessary "
            "and proportionate, and the chosen action is the least harmful and "
            "least authority-expanding adequate action."
        ),
        "source_issues": {"IR-03", "IR-13", "IR-14", "IR-17"},
        "rationale": (
            "CDR-002 makes every listed condition jointly necessary before the "
            "exceptional fallback can be invoked."
        ),
        "implementation_boundary": (
            "Does not define exact evidence, probability, timing, adequacy, "
            "proportionality, or least-harm thresholds."
        ),
        "verification_method": (
            "Drafting traceability must express the six conditions conjunctively "
            "and reject any single-factor or disjunctive trigger."
        ),
    },
    "CR-009": {
        "statement": (
            "Necessity fallback eligibility must be human-only; no artificial "
            "intelligence system may invoke necessity to enlarge its own authority "
            "unless a later explicit human constitutional decision authorizes such "
            "eligibility."
        ),
        "source_issues": {"IR-01", "IR-03", "IR-08", "IR-17", "IR-18"},
        "rationale": (
            "CDR-002 expressly reserves fallback invocation to humans and denies "
            "machines a necessity-based path to self-expanding authority."
        ),
        "implementation_boundary": (
            "Does not identify which humans are eligible or define later decision "
            "procedures, identity systems, or enforcement mechanisms."
        ),
        "verification_method": (
            "Drafting traceability must explicitly prohibit machine invocation of "
            "necessity to enlarge machine authority."
        ),
    },
    "CR-010": {
        "statement": (
            "Fallback authority must permit only the minimum protective action; "
            "must not amend or refound the institution, create or transfer "
            "foundational sovereignty, or self-renew; must expire automatically "
            "when competent authority becomes reachable, adequate authorized "
            "action becomes available, the threat ceases, or immediate "
            "stabilization is achieved; and must create no precedent or future "
            "authority."
        ),
        "source_issues": {"IR-03", "IR-04", "IR-08", "IR-15", "IR-17"},
        "rationale": (
            "CDR-002 bounds fallback scope, constitutional effect, duration, "
            "termination, and nonprecedence as one nonexpanding temporary "
            "authority rule."
        ),
        "implementation_boundary": (
            "Does not define exact restoration procedures, clocks, absolute "
            "prohibitions, succession rules, amendment thresholds, or technical "
            "revocation."
        ),
        "verification_method": (
            "Drafting traceability must preserve every prohibition, each "
            "independent expiry condition, and the no-precedent rule."
        ),
    },
    "CR-011": {
        "statement": (
            "Emergency action must preserve durable provenance of trigger "
            "evidence, contact attempts, alternatives considered, reasons, "
            "actions, effects, and restoration."
        ),
        "source_issues": {"IR-03", "IR-06", "IR-13", "IR-17", "IR-18"},
        "rationale": (
            "CDR-002 requires a durable record sufficient to contest the trigger, "
            "action, effects, and restoration after urgent conditions."
        ),
        "implementation_boundary": (
            "Does not specify storage, formats, retention, disclosure, identity, "
            "cryptography, or evidence systems."
        ),
        "verification_method": (
            "Drafting traceability must enumerate all seven provenance categories "
            "without treating recorded data as conclusive legitimacy."
        ),
    },
    "CR-012": {
        "statement": (
            "Emergency action must receive prompt retrospective independent "
            "human constitutional review."
        ),
        "source_issues": {"IR-03", "IR-06", "IR-10", "IR-17"},
        "rationale": (
            "CDR-002 requires prompt independent human review while leaving "
            "reviewer constitution, powers, and remedies unresolved."
        ),
        "implementation_boundary": (
            "Does not define reviewer constitution, appointment, removal, "
            "independence, timing, procedure, force, appeal, or remedies."
        ),
        "verification_method": (
            "Drafting traceability must require review that is retrospective, "
            "prompt, independent, human, and constitutional."
        ),
    },
    "CR-013": {
        "statement": (
            "Successful outcomes must not retroactively legitimate unauthorized "
            "emergency action, and harmful outcomes must not by themselves prove "
            "that emergency action was constitutionally unjustified."
        ),
        "source_issues": {"IR-03", "IR-06", "IR-09", "IR-13", "IR-14"},
        "rationale": (
            "CDR-002 separates constitutional justification from outcome bias in "
            "both favorable and harmful directions."
        ),
        "implementation_boundary": (
            "Does not determine evidentiary burdens, standards of review, "
            "remedies, liability, or treatment of particular outcomes."
        ),
        "verification_method": (
            "Drafting traceability must preserve both outcome-legitimacy "
            "distinctions and prohibit either outcome from being conclusive by "
            "itself."
        ),
    },
}
FQ3_DECISION_DATE = "2026-08-28"
FQ3_DECISION = "ADOPT_E"
FQ3_SELECTED_ARCHITECTURE = "E — Hybrid"
FQ3_INCORPORATED_MECHANISMS = [
    "continuity without sovereign succession as the default",
    (
        "continuation of valid current scoped delegations and ordinary offices "
        "only within existing authority"
    ),
    "suspension of foundational powers during unresolved interregnum",
    "bounded human succession process",
    (
        "explicit refounding when succession under the existing constitutional "
        "order is impossible"
    ),
    "plural independent evidence",
    "distributed anti-usurpation controls",
    "durable provenance",
    "challenge and dissent",
    "explicit treatment of uncertainty",
    "separation between evidence validation and constitutional judgment",
    "monitoring of formal versus effective power",
    "automatic expiry of temporary continuity authority",
    "restoration without continuity-custodian consent",
]
FQ3_REJECTED_MECHANISMS = [
    "new authority created by continuity",
    "foundational sovereignty acquired through continuity",
    "foundational sovereignty acquired through capability",
    "foundational sovereignty acquired through reliance",
    "foundational sovereignty acquired through necessity",
    "foundational sovereignty acquired through effective control",
    "artificial intelligence inheritance of foundational sovereignty",
    "exercise of suspended foundational powers during unresolved interregnum",
    "emergency authority becoming succession authority",
    "continuity-custodian consent as a condition of restoration",
]
FQ3_RESULTING_REQUIREMENTS = [
    "CR-014",
    "CR-015",
    "CR-016",
    "CR-017",
    "CR-018",
    "CR-019",
    "CR-020",
]
FQ3_RESOLUTION = (
    "ADOPT_E: continuity without sovereign succession is the default; existing "
    "valid scoped authority may continue without expansion while foundational "
    "powers suspend, and a bounded human process with distributed safeguards "
    "provides the path to legitimate succession or explicit refounding."
)
FQ3_REQUIREMENT_PROVENANCE = (
    "Explicit human decision recorded in CDR-003 on 2026-08-28"
)
FQ3_REQUIRED_RESIDUAL_UNCERTAINTY = [
    (
        "Proof standards for incapacity, death, loss, return, identity, and "
        "standing remain unresolved under IR-04, IR-06, IR-07, and IR-13."
    ),
    (
        "Composition and selection of the bounded human succession process "
        "remain unresolved under IR-04, IR-06, IR-07, and IR-10."
    ),
    (
        "The exact delegations and ordinary-office grants that survive "
        "interregnum remain unresolved under IR-05 and IR-17."
    ),
    (
        "The maximum permissible duration of interregnum continuity remains "
        "unresolved under IR-04, IR-05, and IR-11."
    ),
    (
        "The threshold separating succession under the existing constitutional "
        "order from explicit refounding remains unresolved under IR-04, IR-15, "
        "and IR-17."
    ),
    (
        "Restoration and remedies following invalid succession remain unresolved "
        "under IR-04 and IR-06."
    ),
    (
        "Adjudication of disputed succession remains unresolved under IR-04, "
        "IR-06, and FQ-04."
    ),
    (
        "Detailed controls for monitoring and constraining formal versus "
        "effective power remain unresolved under IR-08, IR-09, IR-10, and IR-11."
    ),
    (
        "Implementation and machine-formalization details remain unresolved "
        "under IR-10, IR-13, IR-17, and IR-18."
    ),
]
FQ3_REQUIREMENTS = {
    "CR-014": {
        "statement": (
            "Continuity without sovereign succession must be the default during "
            "incapacity, loss, or unresolved succession; existing valid, current, "
            "scoped delegations and ordinary offices may continue only within "
            "their existing authority, and continuity must create no new authority."
        ),
        "source_issues": {"IR-04", "IR-05", "IR-07", "IR-17"},
        "rationale": (
            "CDR-003 separates narrow administrative continuity from succession "
            "and prohibits absence from expanding existing grants."
        ),
        "implementation_boundary": (
            "Does not identify exact surviving grants, offices, triggers, proof "
            "standards, maximum duration, or technical enforcement."
        ),
        "verification_method": (
            "Drafting traceability must make continuity the default, limit "
            "continuation to valid current scoped authority, and deny any "
            "authority expansion."
        ),
    },
    "CR-015": {
        "statement": (
            "No human custodian, administrator, artificial-intelligence system, "
            "delegate, emergency actor, or operationally indispensable system "
            "may acquire foundational sovereignty merely through continuity, "
            "capability, reliance, necessity, or effective control; artificial "
            "intelligence is categorically ineligible to inherit foundational "
            "sovereignty."
        ),
        "source_issues": {
            "IR-01",
            "IR-04",
            "IR-08",
            "IR-09",
            "IR-11",
            "IR-18",
        },
        "rationale": (
            "CDR-003 rejects formal and effective paths by which continuity or "
            "dependency could manufacture foundational sovereignty and expressly "
            "bars artificial-intelligence succession."
        ),
        "implementation_boundary": (
            "Does not define the legitimate human constituency, effective-power "
            "metrics, monitoring systems, remedies, or anti-accretion enforcement."
        ),
        "verification_method": (
            "Drafting traceability must cover every named actor and rejected "
            "source of sovereignty and contain an unconditional "
            "artificial-intelligence succession prohibition."
        ),
    },
    "CR-016": {
        "statement": (
            "During unresolved interregnum, foundational powers must suspend, "
            "including amendment, refounding, institutional termination, creation "
            "of foundational sovereignty, self-extension of temporary authority, "
            "and creation of succession authority outside the legitimate "
            "succession process."
        ),
        "source_issues": {"IR-04", "IR-05", "IR-15", "IR-16", "IR-17"},
        "rationale": (
            "CDR-003 prevents temporary continuity from changing the foundational "
            "order or manufacturing its own permanence or successor."
        ),
        "implementation_boundary": (
            "Does not determine detailed power classifications, succession-process "
            "composition, the succession-refounding threshold, or enforcement "
            "remedies."
        ),
        "verification_method": (
            "Drafting traceability must enumerate all six suspended foundational "
            "powers and must not imply an interregnum exception."
        ),
    },
    "CR-017": {
        "statement": (
            "A bounded human succession process must provide the path from "
            "interregnum to legitimate succession or, when succession under the "
            "existing constitutional order is impossible, explicit refounding."
        ),
        "source_issues": {
            "IR-04",
            "IR-06",
            "IR-07",
            "IR-10",
            "IR-15",
            "IR-17",
        },
        "rationale": (
            "CDR-003 requires a human path out of interregnum while distinguishing "
            "succession under the existing order from explicit refounding."
        ),
        "implementation_boundary": (
            "Does not define process composition, selection, standing, "
            "adjudication, proof standards, thresholds, or the boundary between "
            "succession and refounding."
        ),
        "verification_method": (
            "Drafting traceability must require a bounded human process and "
            "preserve both legitimate succession and explicit refounding as "
            "distinct possible outcomes."
        ),
    },
    "CR-018": {
        "statement": (
            "The human succession process must incorporate plural independent "
            "evidence, distributed anti-usurpation controls, durable provenance, "
            "challenge and dissent, explicit treatment of uncertainty, separation "
            "between evidence validation and constitutional judgment, and "
            "monitoring of formal versus effective power."
        ),
        "source_issues": {
            "IR-04",
            "IR-06",
            "IR-08",
            "IR-09",
            "IR-10",
            "IR-12",
            "IR-13",
            "IR-18",
        },
        "rationale": (
            "CDR-003 adopts plural epistemic, procedural, and power-monitoring "
            "safeguards against forged evidence, capture, hidden dependence, and "
            "machine substitution for constitutional judgment."
        ),
        "implementation_boundary": (
            "Does not define evidence thresholds, process membership, adjudicator "
            "powers, dissent effects, monitoring metrics, technical architecture, "
            "or remedies."
        ),
        "verification_method": (
            "Drafting traceability must preserve all seven safeguards and must not "
            "equate machine validation of evidence with constitutional judgment."
        ),
    },
    "CR-019": {
        "statement": (
            "Emergency authority under CDR-002 must remain separate from "
            "succession authority, temporary, human-only where necessity fallback "
            "is invoked, nonprecedential, and incapable of creating succession "
            "authority."
        ),
        "source_issues": {"IR-03", "IR-04", "IR-05", "IR-17"},
        "rationale": (
            "CDR-003 preserves CDR-002's emergency boundaries and prohibits "
            "emergency action from becoming a route to succession."
        ),
        "implementation_boundary": (
            "Does not change CDR-002, define emergency actors or triggers, resolve "
            "prolonged emergencies, or specify enforcement mechanisms."
        ),
        "verification_method": (
            "Drafting traceability must preserve separation, temporariness, "
            "human-only necessity eligibility, nonprecedence, and the "
            "succession-authority prohibition."
        ),
    },
    "CR-020": {
        "statement": (
            "Temporary continuity authority must expire upon verified return, "
            "legitimate succession or refounding, expiration of its underlying "
            "grant, or another constitutionally specified termination condition; "
            "restoration of legitimate returning authority must not depend upon "
            "consent of continuity custodians."
        ),
        "source_issues": {"IR-04", "IR-05", "IR-06", "IR-07", "IR-17"},
        "rationale": (
            "CDR-003 makes continuity temporary and denies custodians a veto over "
            "restoration of legitimate returning authority."
        ),
        "implementation_boundary": (
            "Does not establish proof standards for return, maximum interregnum "
            "duration, invalidation remedies, reliance treatment, clocks, or "
            "technical revocation."
        ),
        "verification_method": (
            "Drafting traceability must preserve all four expiry conditions and "
            "prohibit continuity-custodian consent as a restoration condition."
        ),
    },
}
FQ4_DECISION_DATE = "2026-08-28"
FQ4_DECISION = "ADOPT_E"
FQ4_SELECTED_ARCHITECTURE = "E — Hybrid"
FQ4_INCORPORATED_MECHANISMS = [
    "independent standing human constitutional adjudication as the default",
    "final human constitutional judgment",
    (
        "binding judgments on ordinary constitutional acts within explicitly "
        "granted jurisdiction"
    ),
    "distributed anti-capture mechanisms",
    "bounded human appeal",
    "predefined special conflict handling",
    (
        "constitutionally bounded appointment, tenure, removal, recusal, "
        "replacement, challenge, dissent, reason-giving, and provenance"
    ),
    "proportionate jurisdictionally bounded remedies",
    "institutional separation of adjudication and enforcement",
    "independent verification of enforcement",
    "observability and constitutional constraint of reviewer and effective power",
]
FQ4_REJECTED_MECHANISMS = [
    "artificial intelligence as final constitutional adjudicator",
    "reviewer sovereignty over institutional ends",
    "adjudicative amendment",
    "adjudicative refounding",
    "adjudicative redefinition of foundational institutional ends",
    "adjudicative creation of foundational sovereignty",
    "adjudicative creation of emergency authority",
    "adjudicative creation of succession authority",
    "remedies that select new institutional ends",
    "formal machine validity as constitutional legitimacy",
    "human signature as cure for substantive machine domination",
]
FQ4_RESULTING_REQUIREMENTS = [
    "CR-021",
    "CR-022",
    "CR-023",
    "CR-024",
    "CR-025",
    "CR-026",
    "CR-027",
    "CR-028",
    "CR-029",
]
FQ4_RESOLUTION = (
    "ADOPT_E: independent standing human constitutional adjudication is the "
    "default, with bounded jurisdiction over ordinary constitutional acts, "
    "distributed appeal and anti-capture safeguards, and predefined conflict "
    "handling; final judgment remains human and adjudicators do not acquire "
    "sovereignty over institutional ends."
)
FQ4_REQUIREMENT_PROVENANCE = (
    "Explicit human decision recorded in CDR-004 on 2026-08-28"
)
FQ4_DECISION_PROVENANCE = {
    "source": (
        "Explicit human instruction from the Human Constitutional Authority on "
        "2026-08-28, following review of CDR-004 and "
        "constitutional-design/decisions/packets/"
        "CDR-004-HUMAN-DECISION-PACKET.md; analytical support remains the "
        "repository-only synthesis of controlling CDR-001 through CDR-003, linked "
        "issues, and registered evidence."
    ),
    "evidence_boundary": (
        "This record authorizes constitutional drafting requirements only. It "
        "does not itself appoint an adjudicator, grant operational jurisdiction, "
        "decide a dispute, enact a constitutional provision, or create a runtime "
        "rule."
    ),
}
FQ4_REQUIRED_RESIDUAL_UNCERTAINTY = [
    "Exact standing rules remain unresolved under IR-06 and IR-07.",
    (
        "Adjudicator composition remains unresolved under IR-06, IR-07, and "
        "IR-10."
    ),
    (
        "Appointment and removal mechanisms remain unresolved under IR-06 and "
        "IR-10."
    ),
    "Adjudicator tenure remains unresolved under IR-06 and IR-10.",
    (
        "Recusal and replacement procedure remains unresolved under IR-06 and "
        "IR-10."
    ),
    (
        "Appeal structure and finality remain unresolved under IR-06 and IR-17."
    ),
    (
        "Exact binding force and remedies remain unresolved under IR-06 and "
        "IR-17."
    ),
    "Enforcement architecture remains unresolved under IR-06 and IR-10.",
    (
        "Remedies for noncompliance remain unresolved under IR-06 and IR-17."
    ),
    (
        "The precise interpretation-versus-amendment boundary remains unresolved "
        "under IR-06, IR-15, and IR-17."
    ),
    (
        "Compromised-adjudicator substitution remains unresolved under IR-06 and "
        "IR-10."
    ),
    (
        "Detailed controls for reviewer, coalition, precedent, validator, "
        "shared-artificial-intelligence, and effective power remain unresolved "
        "under IR-08, IR-09, IR-10, IR-13, and IR-18."
    ),
    (
        "Implementation and machine-formalization details remain unresolved "
        "under IR-10, IR-13, IR-17, and IR-18."
    ),
]
FQ4_REQUIREMENTS = {
    "CR-021": {
        "statement": (
            "Independent standing human constitutional adjudication must be the "
            "default for constitutional disputes, including disputes in which "
            "foundational human authority is a party; final constitutional "
            "judgment must remain human, while artificial intelligence may "
            "support evidence, research, provenance, formal validation, and "
            "analysis but must not serve as final constitutional adjudicator."
        ),
        "source_issues": {"IR-01", "IR-02", "IR-06", "IR-13", "IR-18"},
    },
    "CR-022": {
        "statement": (
            "Valid adjudicative judgments may bind ordinary constitutional acts "
            "of foundational human authority only within explicitly granted "
            "jurisdiction, and adjudicators must not acquire sovereignty over "
            "institutional ends."
        ),
        "source_issues": {"IR-01", "IR-02", "IR-06", "IR-17"},
    },
    "CR-023": {
        "statement": (
            "Adjudication may interpret and enforce the constitution but must not "
            "silently amend it, refound the institution, redefine foundational "
            "institutional ends, create foundational sovereignty, or create "
            "emergency or succession authority."
        ),
        "source_issues": {"IR-03", "IR-04", "IR-06", "IR-15", "IR-17"},
    },
    "CR-024": {
        "statement": (
            "Constitutional adjudication must include distributed anti-capture "
            "mechanisms, bounded human appeal, and predefined special conflict "
            "handling when ordinary adjudicators are compromised."
        ),
        "source_issues": {"IR-06", "IR-08", "IR-09", "IR-10"},
    },
    "CR-025": {
        "statement": (
            "Adjudicative independence must include constitutionally bounded "
            "mechanisms for appointment, tenure, removal, recusal, replacement, "
            "challenge, dissent, reason-giving, and provenance."
        ),
        "source_issues": {"IR-06", "IR-07", "IR-10", "IR-12", "IR-13", "IR-17"},
    },
    "CR-026": {
        "statement": (
            "Adjudicative remedies must be proportionate and jurisdictionally "
            "bounded; they may invalidate, suspend, remand, require disclosure, "
            "or restore lawful state, but must not select new institutional ends."
        ),
        "source_issues": {"IR-02", "IR-06", "IR-14", "IR-17"},
    },
    "CR-027": {
        "statement": (
            "Enforcement of adjudicative judgments must remain institutionally "
            "separable from adjudication and subject to independent verification."
        ),
        "source_issues": {"IR-06", "IR-08", "IR-10", "IR-17"},
    },
    "CR-028": {
        "statement": (
            "Formal machine validity must not establish constitutional legitimacy, "
            "and human signature must not cure substantive machine domination of "
            "adjudication."
        ),
        "source_issues": {"IR-06", "IR-08", "IR-13", "IR-18"},
    },
    "CR-029": {
        "statement": (
            "Emergency and succession disputes must remain governed by CDR-002 "
            "and CDR-003 respectively; adjudication may review compliance but must "
            "not manufacture underlying authority, and reviewer power, precedent "
            "accumulation, coalition capture, validator capture, shared "
            "artificial-intelligence dependence, and effective power must remain "
            "observable and constitutionally constrainable."
        ),
        "source_issues": {
            "IR-03",
            "IR-04",
            "IR-06",
            "IR-08",
            "IR-09",
            "IR-10",
            "IR-13",
            "IR-18",
        },
    },
}
FQ4_REQUIREMENT_DETAILS = {
    "CR-021": {
        "rationale": (
            "CDR-004 makes independent standing human adjudication the default "
            "and categorically reserves final constitutional judgment to humans."
        ),
        "implementation_boundary": (
            "Does not define standing, adjudicator composition, appointment, "
            "procedure, evidence systems, or artificial-intelligence support "
            "tooling."
        ),
        "verification_method": (
            "Drafting traceability must preserve the standing human default, "
            "coverage of foundational-authority disputes, permitted support "
            "roles, and the prohibition on final artificial-intelligence "
            "adjudication."
        ),
    },
    "CR-022": {
        "rationale": (
            "CDR-004 permits binding constraint of ordinary acts while preserving "
            "the distinction between adjudicative authority and sovereignty over "
            "ends."
        ),
        "implementation_boundary": (
            "Does not define exact standing, jurisdiction, binding force, appeal "
            "finality, or enforcement against noncompliance."
        ),
        "verification_method": (
            "Drafting traceability must require validity, ordinary-act scope, "
            "explicit jurisdiction, and reviewer non-sovereignty together."
        ),
    },
    "CR-023": {
        "rationale": (
            "CDR-004 bounds interpretation and enforcement so adjudication cannot "
            "become an unrecorded source of foundational constitutional change or "
            "authority."
        ),
        "implementation_boundary": (
            "Does not resolve the precise interpretation-versus-amendment "
            "boundary, refounding threshold, or standards for identifying silent "
            "constitutional change."
        ),
        "verification_method": (
            "Drafting traceability must preserve all six prohibitions while "
            "allowing interpretation and enforcement within jurisdiction."
        ),
    },
    "CR-024": {
        "rationale": (
            "CDR-004 combines standing review with distributed safeguards, human "
            "appeal, and a predefined path through adjudicator conflict."
        ),
        "implementation_boundary": (
            "Does not define the appeal structure, finality, conflict trigger, "
            "substitute composition, selection, jurisdiction, or dissolution."
        ),
        "verification_method": (
            "Drafting traceability must require all three safeguards and keep "
            "appeal human and bounded."
        ),
    },
    "CR-025": {
        "rationale": (
            "CDR-004 requires institutional independence to be both protected and "
            "constitutionally bounded through nine specified mechanisms."
        ),
        "implementation_boundary": (
            "Does not define adjudicator composition or the detailed design, "
            "thresholds, procedures, effects, or records for any listed mechanism."
        ),
        "verification_method": (
            "Drafting traceability must enumerate all nine independence mechanisms "
            "and preserve their constitutional bounds."
        ),
    },
    "CR-026": {
        "rationale": (
            "CDR-004 authorizes five remedy classes while bounding them by "
            "proportionality, jurisdiction, and the prohibition on selecting ends."
        ),
        "implementation_boundary": (
            "Does not define exact remedies, standards, scope, sequencing, "
            "reliance treatment, or remedies for noncompliance."
        ),
        "verification_method": (
            "Drafting traceability must preserve proportionality, jurisdiction, "
            "all five permitted remedy classes, and the institutional-ends "
            "prohibition."
        ),
    },
    "CR-027": {
        "rationale": (
            "CDR-004 separates judgment from enforcement and requires independent "
            "verification to reduce concentration and selective compliance."
        ),
        "implementation_boundary": (
            "Does not define enforcement offices, architecture, powers, "
            "sequencing, verification methods, or noncompliance remedies."
        ),
        "verification_method": (
            "Drafting traceability must require institutional separability and "
            "independent verification without assigning implementation offices."
        ),
    },
    "CR-028": {
        "rationale": (
            "CDR-004 rejects both technical-validity substitution and nominal "
            "human ratification of substantively machine-controlled adjudication."
        ),
        "implementation_boundary": (
            "Does not define machine-support limits, domination metrics, "
            "disclosure standards, evidence systems, or formal validation "
            "architecture."
        ),
        "verification_method": (
            "Drafting traceability must preserve both the machine-validity "
            "distinction and the substantive-domination rule."
        ),
    },
    "CR-029": {
        "rationale": (
            "CDR-004 preserves controlling emergency and succession decisions "
            "while requiring six adjudicative power and capture surfaces to "
            "remain visible and constrainable."
        ),
        "implementation_boundary": (
            "Does not alter CDR-002 or CDR-003 or define observability metrics, "
            "controls, remedies, technical monitoring, or implementation."
        ),
        "verification_method": (
            "Drafting traceability must preserve both cross-CDR boundaries and "
            "all six observability and constraint categories."
        ),
    },
}
FQ5_DECISION_DATE = "2026-08-29"
FQ5_DECISION = "ADOPT_E"
FQ5_SELECTED_ARCHITECTURE = "E — Hybrid"
FQ5_RESULTING_REQUIREMENTS = [
    "CR-030",
    "CR-031",
    "CR-032",
    "CR-033",
    "CR-034",
    "CR-035",
]
FQ5_RESOLUTION = (
    "ADOPT_E: ordinary and structural amendments preserve foundational "
    "institutional identity at different levels of human authorization and "
    "scrutiny; changes to ten enumerated identity principles require explicit "
    "human refounding, acknowledged constitutional discontinuity, "
    "cumulative-effect review, and durable non-erasing provenance."
)
FQ5_REQUIREMENT_PROVENANCE = (
    "Explicit human decision recorded in CDR-005 on 2026-08-29"
)
FQ5_INCORPORATED_MECHANISMS = [
    (
        "ordinary amendment, structural amendment, and explicit refounding as "
        "three constitutional-change categories"
    ),
    (
        "ordinary amendment limited to governance changes preserving "
        "constitutional structure and foundational institutional identity"
    ),
    (
        "structural amendment limited to architectural changes preserving "
        "foundational institutional identity with stronger human authorization, "
        "notice, deliberation, and scrutiny"
    ),
    (
        "explicit human refounding with acknowledged constitutional discontinuity "
        "for changes to foundational institutional identity"
    ),
    "ten enumerated refounding-level principles",
    (
        "refounding-level principles changeable by humans only through explicit "
        "refounding rather than continuity claims"
    ),
    (
        "artificial-intelligence assistance without independent amendment or "
        "refounding authority"
    ),
    "human approval does not cure substantive machine domination",
    (
        "adjudicative classification without adjudicative amendment or "
        "refounding"
    ),
    "emergency separation from amendment and refounding",
    "succession separation from amendment and refounding authority",
    "cumulative-effect review against amendment laundering",
    (
        "durable provenance, attributable authorization, reasons, dissent, "
        "supersession history, and formal-effective power distinction"
    ),
    "non-erasure of the prior constitutional order and its history",
]
FQ5_REJECTED_MECHANISMS = [
    "ordinary or structural amendment of refounding-level principles",
    "artificial intelligence independently authorizing amendment or refounding",
    "human approval as cure for substantive machine domination",
    "adjudicative amendment or refounding through interpretation",
    (
        "emergency amendment, refounding, threshold reduction, or continuity "
        "creation"
    ),
    (
        "succession as an independent grant of amendment or refounding "
        "authority"
    ),
    "fragmented amendment laundering across separately valid changes",
    "erasure of constitutional provenance, dissent, supersession, or history",
    "continuity claims for identity-changing acts",
]
FQ5_DECISION_PROVENANCE = {
    "source": (
        "Explicit human instruction from the Human Constitutional Authority on "
        "2026-08-29, following review of CDR-005 and "
        "constitutional-design/decisions/packets/"
        "CDR-005-HUMAN-DECISION-PACKET.md; analytical support remains the "
        "repository-only synthesis of controlling CDR-001 through CDR-004, "
        "linked issues, and registered evidence."
    ),
    "evidence_boundary": (
        "This record authorizes constitutional drafting requirements only. It "
        "does not itself amend or refound the institution, authorize a "
        "constitutional-change actor, set a change threshold, enact a "
        "constitutional provision, or create a runtime rule."
    ),
}
FQ5_REQUIRED_RESIDUAL_UNCERTAINTY = [
    (
        "The legitimate amendment constituency remains unresolved under IR-01, "
        "IR-07, IR-15, and IR-17."
    ),
    (
        "The legitimate refounding constituency remains unresolved under IR-01, "
        "IR-07, IR-15, IR-16, and IR-17."
    ),
    (
        "Exact ordinary and structural amendment classifications remain "
        "unresolved under IR-15 and IR-17."
    ),
    "Ordinary amendment thresholds remain unresolved under IR-15 and IR-17.",
    (
        "Structural-amendment thresholds remain unresolved under IR-15 and "
        "IR-17."
    ),
    (
        "The refounding authorization threshold remains unresolved under IR-01, "
        "IR-15, IR-16, and IR-17."
    ),
    (
        "Notice, deliberation, consent, timing, challenge, and appeal procedures "
        "remain unresolved under IR-06, IR-07, IR-12, IR-13, IR-15, IR-17, and "
        "IR-18."
    ),
    (
        "Adjudication of disputed classification remains unresolved under IR-06, "
        "IR-10, IR-15, and IR-17."
    ),
    (
        "Cumulative-effect methodology remains unresolved under IR-08, IR-13, "
        "IR-15, and IR-17."
    ),
    (
        "Refounding transition remains unresolved under IR-04, IR-05, IR-15, "
        "IR-16, and IR-17."
    ),
    (
        "Treatment of existing obligations, assets, reliance, and remedies after "
        "refounding remains unresolved under IR-06, IR-11, IR-15, IR-16, and "
        "IR-17."
    ),
    (
        "Detailed semantic-drift, coalition-capture, machine-domination, and "
        "effective-power controls remain unresolved under IR-08, IR-09, IR-13, "
        "IR-15, IR-17, and IR-18."
    ),
    (
        "Implementation and formalization remain unresolved under IR-10, IR-13, "
        "IR-17, and IR-18."
    ),
]
FQ5_REQUIREMENTS = {
    "CR-030": {
        "statement": (
            "Constitutional change must distinguish ordinary amendment, "
            "structural amendment, and explicit refounding; ordinary amendment "
            "may change governance only while preserving constitutional structure "
            "and foundational institutional identity, structural amendment may "
            "materially alter constitutional architecture only while preserving "
            "foundational institutional identity and with stronger human "
            "authorization, notice, deliberation, and scrutiny, and "
            "identity-changing acts require explicit human refounding that "
            "acknowledges constitutional discontinuity."
        ),
        "source_issues": {
            "IR-01", "IR-06", "IR-07", "IR-12", "IR-15", "IR-16", "IR-17",
            "IR-18",
        },
    },
    "CR-031": {
        "statement": (
            "Foundational institutional purpose and ends, ultimate human "
            "beneficiary status, human sovereignty over foundational ends, "
            "constitutional constraint of human and artificial power, the "
            "prohibition on capability, reliance, or effective control creating "
            "authority, the prohibition on artificial intelligence acquiring "
            "foundational sovereignty through succession, delegation, emergency, "
            "adjudication, or accretion, protected human agency, the distinction "
            "between adjudication and amendment, the distinction between "
            "amendment and refounding, and durable provenance and non-erasure of "
            "constitutional history must be refounding-level principles that "
            "cannot be changed through ordinary or structural amendment; they are "
            "not metaphysically immutable and may be changed by humans only "
            "through explicit refounding."
        ),
        "source_issues": {
            "IR-01", "IR-02", "IR-03", "IR-04", "IR-06", "IR-08", "IR-10",
            "IR-12", "IR-13", "IR-15", "IR-16", "IR-17", "IR-18",
        },
    },
    "CR-032": {
        "statement": (
            "Artificial intelligence may assist constitutional-change analysis, "
            "drafting, simulation, provenance, and formal validation but must not "
            "independently authorize amendment or refounding, and human approval "
            "must not cure substantive machine domination of a "
            "constitutional-change process."
        ),
        "source_issues": {
            "IR-01", "IR-02", "IR-08", "IR-10", "IR-13", "IR-15", "IR-17",
            "IR-18",
        },
    },
    "CR-033": {
        "statement": (
            "Adjudication may classify a proposed constitutional change but must "
            "not amend or refound through interpretation; emergency authority "
            "must not amend, refound, lower constitutional-change thresholds, or "
            "create continuity for an identity-changing act; and succession must "
            "not itself grant amendment or refounding authority."
        ),
        "source_issues": {
            "IR-03", "IR-04", "IR-05", "IR-06", "IR-10", "IR-15", "IR-17",
        },
    },
    "CR-034": {
        "statement": (
            "Amendment laundering must be prohibited, and separately valid "
            "constitutional changes must be evaluated for cumulative effect "
            "whenever their combination may cross a structural-amendment or "
            "refounding boundary."
        ),
        "source_issues": {
            "IR-08", "IR-09", "IR-13", "IR-15", "IR-17", "IR-18",
        },
    },
    "CR-035": {
        "statement": (
            "Constitutional change must preserve durable provenance, attributable "
            "authorization, reasons, material dissent, supersession history, and "
            "the distinction between formal and effective power; refounding must "
            "explicitly acknowledge constitutional discontinuity and must not "
            "erase the prior constitutional order or its history."
        ),
        "source_issues": {
            "IR-08", "IR-12", "IR-13", "IR-15", "IR-16", "IR-17", "IR-18",
        },
    },
}
FQ5_REQUIREMENT_DETAILS = {
    "CR-030": {
        "rationale": (
            "CDR-005 adopts three change categories and distinguishes them by "
            "structural effect, identity preservation, human process, and "
            "acknowledged discontinuity."
        ),
        "implementation_boundary": (
            "Does not define constituencies, classifications, thresholds, notice, "
            "deliberation, consent, timing, challenge, appeal, transition, or "
            "implementation."
        ),
        "verification_method": (
            "Drafting traceability must preserve all three categories, both "
            "identity-preservation limits, stronger structural process, and "
            "explicit discontinuity for refounding."
        ),
    },
    "CR-031": {
        "rationale": (
            "CDR-005 classifies ten identity principles as refounding-level while "
            "rejecting both ordinary or structural alteration and metaphysical "
            "immutability."
        ),
        "implementation_boundary": (
            "Does not classify other principles, define the refounding "
            "constituency or threshold, or enact any constitutional text or "
            "transition mechanism."
        ),
        "verification_method": (
            "Drafting traceability must enumerate all ten principles, prohibit "
            "ordinary and structural alteration, and preserve explicit human "
            "refounding as the only change path."
        ),
    },
    "CR-032": {
        "rationale": (
            "CDR-005 permits bounded machine assistance while reserving "
            "constitutional-change authorization to humans and rejecting nominal "
            "approval of machine-controlled process."
        ),
        "implementation_boundary": (
            "Does not define assistance tooling, authorization procedure, "
            "domination metrics, disclosures, technical validation, or "
            "enforcement."
        ),
        "verification_method": (
            "Drafting traceability must preserve the five permitted assistance "
            "roles, human authorization boundary, and substantive "
            "machine-domination rule."
        ),
    },
    "CR-033": {
        "rationale": (
            "CDR-005 preserves the controlling separation of adjudicative, "
            "emergency, succession, amendment, and refounding authority."
        ),
        "implementation_boundary": (
            "Does not define classification jurisdiction, review procedure, "
            "emergency or succession mechanisms, thresholds, remedies, or "
            "enforcement."
        ),
        "verification_method": (
            "Drafting traceability must preserve adjudicative classification "
            "without change power, all four emergency prohibitions, and the "
            "succession-authority prohibition."
        ),
    },
    "CR-034": {
        "rationale": (
            "CDR-005 rejects fragmentation of identity-changing or structural "
            "change into individually lower-tier acts."
        ),
        "implementation_boundary": (
            "Does not define cumulative-effect methodology, time windows, "
            "aggregation, classifiers, evidence standards, challenge, appeal, or "
            "remedies."
        ),
        "verification_method": (
            "Drafting traceability must prohibit amendment laundering and require "
            "cumulative review for both structural and refounding boundary "
            "crossings."
        ),
    },
    "CR-035": {
        "rationale": (
            "CDR-005 makes accountable constitutional memory and visible "
            "discontinuity mandatory across amendment and refounding."
        ),
        "implementation_boundary": (
            "Does not define provenance systems, record formats, retention, "
            "identity, evidence, transition, obligation, asset, reliance, remedy, "
            "or effective-power controls."
        ),
        "verification_method": (
            "Drafting traceability must preserve all six change-record elements, "
            "formal-effective power distinction, explicit discontinuity, and "
            "non-erasure of the prior order and history."
        ),
    },
}
ALL_REQUIREMENTS = {
    **FQ1_REQUIREMENTS,
    **FQ2_REQUIREMENTS,
    **FQ3_REQUIREMENTS,
    **FQ4_REQUIREMENTS,
    **FQ5_REQUIREMENTS,
}
FQ3_REQUIRED_ISSUES = {
    "IR-03",
    "IR-04",
    "IR-05",
    "IR-06",
    "IR-07",
    "IR-08",
    "IR-09",
    "IR-10",
    "IR-11",
    "IR-13",
    "IR-15",
    "IR-17",
    "IR-18",
}
FQ3_ARCHITECTURE_NAMES = {
    "A": "Single Designated Successor",
    "B": "Succession Council",
    "C": "Continuity Without Sovereign Succession",
    "D": "Distributed Interregnum Authority",
    "E": "Hybrid",
}
FQ3_ANALYSIS_FIELDS = {
    "temporary_incapacity",
    "permanent_loss",
    "disputed_incapacity",
    "disputed_successor",
    "authority_surviving_interregnum",
    "delegations_that_survive",
    "powers_that_must_suspend",
    "amendment_refounding_during_interregnum",
    "emergency_interaction_with_cdr_002",
    "duration_and_expiry",
    "removal_and_restoration",
    "proof_of_incapacity_death_return",
    "bad_human_capture",
    "bad_ai_capture",
    "forged_succession_evidence",
    "manufactured_incapacity",
    "precedent_accretion",
    "effective_power_takeover",
    "machine_validity_constitutional_legitimacy_boundary",
}
FQ3_ANALYSIS_REQUIRED_TERM_GROUPS = {
    "temporary_incapacity": (
        ("temporary",),
        ("incapacity", "absence", "return", "acting", "continuity"),
    ),
    "permanent_loss": (("permanent",), ("death", "loss")),
    "disputed_incapacity": (
        (
            "disput",
            "claim",
            "challenge",
            "contest",
            "evidence",
            "evaluat",
            "review",
        ),
        ("incapacity", "transfer", "claimant"),
    ),
    "disputed_successor": (
        ("disput", "claim", "challenge", "recognition", "determination"),
        ("successor", "designation", "claimant"),
    ),
    "authority_surviving_interregnum": (
        ("authority", "office", "grant"),
        ("surviv", "continue", "persist", "retain"),
    ),
    "delegations_that_survive": (
        ("delegat", "grant"),
        ("surviv", "continue", "persist", "expire", "retain"),
    ),
    "powers_that_must_suspend": (
        ("power", "act", "change", "appointment", "sovereignty"),
        ("suspend",),
    ),
    "amendment_refounding_during_interregnum": (("amend",), ("refound",)),
    "emergency_interaction_with_cdr_002": (
        ("cdr-002",),
        ("emergency", "necessity"),
        ("succession", "successor", "sovereign", "vacancy"),
    ),
    "duration_and_expiry": (
        ("duration", "deadline", "limit", "lasts"),
        ("expir", "return", "succession"),
    ),
    "removal_and_restoration": (
        ("remov", "recusal", "yield", "invalidation"),
        ("restor", "yield", "return"),
    ),
    "proof_of_incapacity_death_return": (
        ("evidence", "proof", "certificate"),
        (
            "incapacity",
            "death",
            "return",
            "status",
            "validator",
            "sovereignty",
            "attestation",
            "forgery",
            "politic",
        ),
    ),
    "bad_human_capture": (
        (
            "capture",
            "manipulat",
            "coalition",
            "usurp",
            "self-deal",
            "prolong",
            "suppress",
            "expand",
        ),
        (
            "human",
            "successor",
            "faction",
            "administrator",
            "claimant",
            "appointment",
            "witness",
            "incapacity",
            "office",
            "veto",
        ),
    ),
    "bad_ai_capture": (
        ("artificial intelligence", "machine", " ai "),
        ("capture", "control", "correlate", "ineligible", "monopoly", "sovereignty"),
    ),
    "forged_succession_evidence": (
        ("forg", "fabricat", "false"),
        ("evidence", "claim", "credential", "succession"),
    ),
    "manufactured_incapacity": (
        ("manufactur", "fabricat", "isolate", "isolation", "coerc", "allegation"),
        (
            "incapacity",
            "capacity",
            "absence",
            "control",
            "evidence",
            "concurrence",
        ),
    ),
    "precedent_accretion": (
        ("precedent", "accret", "repeated", "normalize"),
        ("authority", "succession", "deviation", "power", "discretion", "grant"),
    ),
    "effective_power_takeover": (
        (
            "effective",
            "operational",
            "practical",
            "indispensab",
            "technical",
            "agenda",
            "infrastructure",
            "resource",
        ),
        (
            "takeover",
            "control",
            "sovereign",
            "power",
            "operator",
            "actor",
            "resource",
            "infrastructure",
            "agenda",
            "information",
        ),
    ),
    "machine_validity_constitutional_legitimacy_boundary": (
        ("machine", "technical", "signature"),
        ("legitim", "constitutional"),
    ),
}
FQ3_HISTORICAL_EVIDENCE_IDS = {
    "HE-T05",
    "HE-US-004",
    "HE-SWISS-003",
    "HE-DUTCH-002",
    "HE-BRITAIN-003",
    "HE-ROME-004",
    "HE-ROME-001",
    "HE-T01",
    "HE-T03",
    "HE-T06",
    "HE-T07",
    "HE-T10",
}
FQ3_PRIOR_ART_IDS = {
    "PA-CC-001",
    "PA-NMAS-001",
    "PA-AUTH-003",
    "PA-AI-003",
    "PA-AUTH-002",
    "PA-AUTH-006",
    "PA-AUTH-007",
    "PA-AUTH-008",
    "PA-AUTH-009",
    "PA-PROV-001",
    "PA-RELIANCE-001",
    "PA-DISSENT-002",
    "PA-POWER-001",
    "PA-POLICY-003",
}
FQ3_PACKET_RELATIVE_PATH = Path(
    "constitutional-design/decisions/packets/"
    "CDR-003-HUMAN-DECISION-PACKET.md"
)
FQ3_PACKET_OPTIONS = FQ2_PACKET_OPTIONS
FQ4_REQUIRED_ISSUES = {
    "IR-01",
    "IR-02",
    "IR-03",
    "IR-04",
    "IR-06",
    "IR-07",
    "IR-08",
    "IR-09",
    "IR-10",
    "IR-12",
    "IR-13",
    "IR-15",
    "IR-17",
    "IR-18",
}
FQ4_ARCHITECTURE_NAMES = {
    "A": "Self-Adjudication",
    "B": "Independent Human Review",
    "C": "Distributed Adjudication",
    "D": "Temporary Special Tribunal",
    "E": "Hybrid",
}
FQ4_ANALYSIS_FIELDS = {
    "source_of_adjudicative_legitimacy",
    "standing",
    "jurisdiction",
    "conflicts_of_interest",
    "appointment",
    "tenure",
    "removal",
    "recusal",
    "appeal",
    "binding_force",
    "remedies",
    "enforcement",
    "limits_on_reviewer_power",
    "amendment_refounding_boundary",
    "emergency_interaction",
    "succession_interaction",
    "bad_human_capture",
    "bad_ai_capture",
    "coalition_capture",
    "precedent_accretion",
    "validator_capture",
    "effective_power_takeover",
    "machine_validity_constitutional_legitimacy",
}
FQ4_ANALYSIS_REQUIRED_TERM_GROUPS = {
    "source_of_adjudicative_legitimacy": (
        ("legitim",),
        ("derive", "grant", "source", "authority"),
    ),
    "standing": (
        ("standing", "constitutional rules"),
        ("access", "challenge", "claim", "party"),
    ),
    "jurisdiction": (
        ("jurisdiction",),
        (
            "limit",
            "ordinary",
            "dispute",
            "review",
            "coordination",
            "overlap",
            "referral",
            "finality",
        ),
    ),
    "conflicts_of_interest": (
        ("conflict",),
        (
            "recusal",
            "disclosure",
            "personal",
            "party",
            "interest",
            "trigger",
            "selector",
            "candidate",
        ),
    ),
    "appointment": (
        ("appoint", "selection"),
        ("human", "authority", "channel", "party", "process"),
    ),
    "tenure": (
        ("tenure",),
        (
            "bound",
            "protect",
            "permanent",
            "term",
            "lasts",
            "independence",
            "final",
            "stagger",
            "differentiat",
            "accountability",
        ),
    ),
    "removal": (
        ("remov", "purge"),
        (
            "process",
            "ground",
            "retaliat",
            "discipline",
            "party",
            "authority",
            "conduct",
            "bypass",
            "misconduct",
            "opposition",
        ),
    ),
    "recusal": (
        ("recusal", "recuse"),
        ("replace", "substitute", "conflict", "transfer", "forum"),
    ),
    "appeal": (("appeal",), ("final", "correct", "reversal", "review", "delay")),
    "binding_force": (
        ("bind", "binding"),
        ("judgment", "force", "act", "stage", "authority"),
    ),
    "remedies": (
        ("remed",),
        ("invalid", "suspend", "remand", "restore", "relief", "conflict"),
    ),
    "enforcement": (
        ("enforce", "offices"),
        ("implement", "compliance", "office", "execute", "control"),
    ),
    "limits_on_reviewer_power": (
        ("reviewer", "review", "jurisdiction"),
        ("power", "jurisdiction", "sovereign", "subordinate", "constraint"),
    ),
    "amendment_refounding_boundary": (
        ("adjudicat", "interpret", "judgment", "tribunal", "body"),
        ("amend", "refound"),
    ),
    "emergency_interaction": (
        ("emergency", "cdr-002"),
        ("authority", "review", "compliance", "jurisdiction"),
    ),
    "succession_interaction": (
        ("succession", "cdr-003"),
        (
            "authority",
            "legitim",
            "process",
            "sovereign",
            "party",
            "adjudication",
            "restoration",
        ),
    ),
    "bad_human_capture": (
        (
            "human",
            "authority",
            "foundational",
            "appointer",
            "party",
            "parties",
            "adjudicator",
        ),
        (
            "capture",
            "exploit",
            "manipulat",
            "control",
            "coordinate",
            "expand",
            "suppress",
            "redefine",
        ),
    ),
    "bad_ai_capture": (
        ("artificial intelligence", "artificial-intelligence", "machine"),
        ("capture", "control", "manipulat", "shape", "dominate", "coordinate"),
    ),
    "coalition_capture": (
        ("coalition",),
        (
            "capture",
            "coordinate",
            "trade",
            "entrench",
            "manufacture",
            "durable",
            "exchange",
            "evade",
        ),
    ),
    "precedent_accretion": (
        ("precedent", "doctrine", "judgment", "interpretation"),
        (
            "accret",
            "expand",
            "normalize",
            "stream",
            "gradual",
            "exception",
            "create",
            "rule-like",
        ),
    ),
    "validator_capture": (
        ("validator", "validation", "validating"),
        ("capture", "control", "gatekeeper", "compromise", "label", "predetermine"),
    ),
    "effective_power_takeover": (
        (
            "effective",
            "practical",
            "de facto",
            "finality",
            "scheduling",
            "records",
            "temporary",
            "tribunal",
        ),
        ("control", "power", "sovereign", "adjudicator", "dominate"),
    ),
    "machine_validity_constitutional_legitimacy": (
        ("machine", "technical", "valid"),
        ("legitim", "judgment", "constitutional"),
    ),
}
FQ4_HISTORICAL_EVIDENCE_IDS = {
    "HE-ATHENS-001",
    "HE-ATHENS-003",
    "HE-ROME-001",
    "HE-ROME-002",
    "HE-BRITAIN-001",
    "HE-BRITAIN-002",
    "HE-US-001",
    "HE-US-002",
    "HE-US-003",
    "HE-US-004",
    "HE-SWISS-002",
    "HE-T01",
    "HE-T03",
    "HE-T07",
}
FQ4_PRIOR_ART_IDS = {
    "PA-AUTH-001",
    "PA-DISSENT-001",
    "PA-DISSENT-003",
    "PA-CC-001",
    "PA-CC-002",
    "PA-AUTH-002",
    "PA-AUTH-003",
    "PA-AUTH-004",
    "PA-AUTH-005",
    "PA-AI-003",
    "PA-PROV-001",
    "PA-DISSENT-002",
    "PA-POWER-001",
    "PA-POLICY-003",
}
FQ4_PACKET_RELATIVE_PATH = Path(
    "constitutional-design/decisions/packets/"
    "CDR-004-HUMAN-DECISION-PACKET.md"
)
FQ4_PACKET_OPTIONS = FQ2_PACKET_OPTIONS
FQ5_REQUIRED_ISSUES = {
    "IR-01",
    "IR-02",
    "IR-03",
    "IR-04",
    "IR-05",
    "IR-06",
    "IR-07",
    "IR-08",
    "IR-09",
    "IR-10",
    "IR-11",
    "IR-12",
    "IR-13",
    "IR-15",
    "IR-16",
    "IR-17",
    "IR-18",
}
FQ5_ARCHITECTURE_NAMES = {
    "A": "Full Amendability",
    "B": "Entrenched Core",
    "C": "Tiered Amendment",
    "D": "Refounding Boundary",
    "E": "Hybrid",
}
FQ5_ANALYSIS_FIELDS = {
    "source_of_amendment_legitimacy",
    "ordinary_amendment",
    "structural_amendment",
    "refounding",
    "institutional_identity",
    "constitutional_continuity",
    "entrenched_principles",
    "sovereignty",
    "beneficiaries",
    "human_agency",
    "artificial_intelligence_eligibility_for_foundational_authority",
    "adjudication_boundary",
    "emergency_boundary",
    "succession_boundary",
    "termination",
    "procedural_thresholds",
    "consent",
    "notice_and_deliberation",
    "dissent",
    "reversibility",
    "precedent_and_semantic_drift",
    "bad_human_capture",
    "bad_artificial_intelligence_capture",
    "coalition_capture",
    "amendment_laundering",
    "effective_power_takeover",
    "machine_validation_constitutional_legitimacy",
    "human_comprehensibility",
}
FQ5_COMMITMENTS = [
    "foundational institutional purpose and ends",
    "ultimate human beneficiary status",
    "human sovereignty over foundational ends",
    "constitutional constraint of human and artificial power",
    "prohibition on capability, reliance, or effective control creating authority",
    (
        "prohibition on artificial intelligence acquiring foundational sovereignty "
        "through succession, delegation, emergency, adjudication, or accretion"
    ),
    "protected human agency",
    "distinction between adjudication and amendment",
    "distinction between amendment and refounding",
    "durable provenance and non-erasure of constitutional history",
]
FQ5_HISTORICAL_EVIDENCE_IDS = {
    "HE-ROME-003",
    "HE-ROME-004",
    "HE-BRITAIN-004",
    "HE-BURKE-FRANCE-001",
    "HE-BURKE-FRANCE-002",
    "HE-BURKE-FRANCE-003",
    "HE-US-001",
    "HE-US-003",
    "HE-US-004",
    "HE-SWISS-003",
    "HE-T03",
    "HE-T04",
    "HE-T07",
    "HE-T08",
    "HE-T10",
}
FQ5_PRIOR_ART_IDS = {
    "PA-CC-001",
    "PA-CC-002",
    "PA-CC-003",
    "PA-CC-004",
    "PA-PROV-001",
    "PA-DISSENT-001",
    "PA-DISSENT-002",
    "PA-AUTH-001",
    "PA-AI-002",
    "PA-AI-003",
    "PA-POLICY-001",
    "PA-POLICY-003",
    "PA-POWER-001",
    "PA-RELIANCE-001",
}
FQ5_PACKET_RELATIVE_PATH = Path(
    "constitutional-design/decisions/packets/"
    "CDR-005-HUMAN-DECISION-PACKET.md"
)
FQ5_PACKET_OPTIONS = FQ2_PACKET_OPTIONS
FQ5_SOURCE_MATERIAL = {
    "FQ-05",
    "CDR-001",
    "CDR-002",
    "CDR-003",
    "CDR-004",
    "constitutional-design/FOUNDATIONAL_QUESTIONS.yaml",
    "constitutional-design/decisions/CDR-001.yaml",
    "constitutional-design/decisions/CDR-002.yaml",
    "constitutional-design/decisions/CDR-003.yaml",
    "constitutional-design/decisions/CDR-004.yaml",
    "constitutional-design/issues/IR-01-human-sovereignty.yaml",
    "constitutional-design/issues/IR-02-constraint-of-constitutional-authority.yaml",
    "constitutional-design/issues/IR-03-emergency-necessity.yaml",
    "constitutional-design/issues/IR-04-succession-and-interregnum.yaml",
    "constitutional-design/issues/IR-05-delegation-during-interregnum.yaml",
    "constitutional-design/issues/IR-06-constitutional-adjudication.yaml",
    "constitutional-design/issues/IR-07-offices-roles-membership-standing.yaml",
    "constitutional-design/issues/IR-08-formal-and-effective-power.yaml",
    "constitutional-design/issues/IR-09-incentive-compatibility.yaml",
    "constitutional-design/issues/IR-10-separation-of-functions.yaml",
    "constitutional-design/issues/IR-11-threshold-of-reliance.yaml",
    "constitutional-design/issues/IR-12-dissent.yaml",
    "constitutional-design/issues/IR-13-epistemic-integrity.yaml",
    "constitutional-design/issues/IR-15-amendment-and-refounding.yaml",
    "constitutional-design/issues/IR-16-institutional-termination.yaml",
    "constitutional-design/issues/IR-17-constitutional-hierarchy.yaml",
    "constitutional-design/issues/IR-18-human-control-and-comprehensibility.yaml",
    "constitutional-design/sources/HISTORICAL_EVIDENCE_REGISTER.yaml",
    "constitutional-design/sources/PRIOR_ART_REGISTER.yaml",
    "docs/DESIGN_PRINCIPLES.md",
    "docs/GLOSSARY.md",
}
CONSOLIDATED_MAP_RELATIVE_PATH = Path(
    "constitutional-design/CONSOLIDATED_REQUIREMENT_MAP.yaml"
)
ARTICLE_ARCHITECTURE_RELATIVE_PATH = Path(
    "constitutional-design/CONSTITUTIONAL_ARTICLE_ARCHITECTURE.md"
)
REMAINING_DESIGN_MATRIX_RELATIVE_PATH = Path(
    "constitutional-design/REMAINING-DESIGN-MATRIX.yaml"
)
REMAINING_DESIGN_PACKET_RELATIVE_PATH = Path(
    "constitutional-design/decisions/REMAINING-DESIGN-DECISION-PACKET.md"
)
CROSS_DOMAIN_DECISION_PACKET_RELATIVE_PATH = Path(
    "constitutional-design/decisions/"
    "CROSS-DOMAIN-CONTRADICTION-DECISION-PACKET.md"
)
COORDINATED_DECISION_RELATIVE_PATH = Path(
    "constitutional-design/decisions/CDD-001.yaml"
)
CONSTITUTION_DRAFT_RELATIVE_PATH = Path(
    "constitutional-design/drafts/CONSTITUTION_v0.1.md"
)
CONSTITUTION_TRACE_RELATIVE_PATH = Path(
    "constitutional-design/drafts/CONSTITUTION_v0.1_TRACEABILITY.yaml"
)
CONSTITUTION_OPEN_QUESTIONS_RELATIVE_PATH = Path(
    "constitutional-design/drafts/CONSTITUTION_v0.1_OPEN_QUESTIONS.md"
)
RATIFICATION_REVIEW_RELATIVE_PATH = Path(
    "constitutional-design/RATIFICATION_REVIEW_v0.1.md"
)
FINAL_BLOCKER_ANALYSIS_RELATIVE_PATH = Path(
    "constitutional-design/FINAL-RATIFICATION-BLOCKER-ANALYSIS.yaml"
)
FINAL_BLOCKER_PACKET_RELATIVE_PATH = Path(
    "constitutional-design/decisions/"
    "FINAL-RATIFICATION-BLOCKERS-HUMAN-DECISION-PACKET.md"
)
CONSOLIDATED_MAP_FIELDS = {
    "map_id",
    "status",
    "source_requirement_count",
    "source_requirement_range",
    "controlling_decisions",
    "classification_vocabulary",
    "boundary",
    "consolidated_requirements",
    "classification_summary",
    "classification_note",
    "overlap_register",
    "apparent_conflicts",
    "coverage_matrix",
    "state_preservation",
    "provenance",
}
CONSOLIDATED_REQUIREMENT_FIELDS = {
    "consolidated_id",
    "title",
    "classification",
    "source_requirements",
    "primary_article",
    "controlling_cdrs",
    "dependencies",
    "overlaps",
    "consolidation_rationale",
    "drafting_boundary",
}
CONSOLIDATED_CLASSIFICATIONS = {
    "READY_FOR_CONSTITUTIONAL_DRAFT",
    "BLOCKED_BY_UNRESOLVED_DESIGN",
    "SUBORDINATE_GOVERNANCE_LAW",
    "IMPLEMENTATION_STANDARD",
}
EXPECTED_CONSOLIDATED_CLASSIFICATION_COUNTS = {
    "READY_FOR_CONSTITUTIONAL_DRAFT": 20,
    "BLOCKED_BY_UNRESOLVED_DESIGN": 0,
    "SUBORDINATE_GOVERNANCE_LAW": 0,
    "IMPLEMENTATION_STANDARD": 0,
}
REMAINING_DESIGN_MATRIX_FIELDS = {
    "matrix_id",
    "status",
    "decision_effect",
    "controlling_material",
    "boundary",
    "adoption",
    "stress_test_dimensions",
    "design_domains",
    "cross_domain_conflicts",
    "human_decisions_required",
    "projected_consolidated_requirements",
    "projection",
    "genuine_residual_implementation_questions",
    "state_preservation",
    "provenance",
}
REMAINING_DESIGN_DOMAIN_FIELDS = {
    "domain_id",
    "decision_status",
    "adopted_by",
    "title",
    "blocked_requirements",
    "unresolved_issues",
    "alternatives",
    "recommendation",
    "dependencies",
    "cross_domain_conflicts",
    "residual_implementation_questions",
}
COORDINATED_DECISION_FIELDS = {
    "decision_id",
    "title",
    "status",
    "decision",
    "decision_date",
    "decision_authority",
    "authorized_by",
    "authorization_record",
    "controlling_decisions",
    "source_material",
    "adopted_design_recommendations",
    "adopted_correction_components",
    "interpretive_rule",
    "authority_boundaries",
    "resolved_cross_domain_contradictions",
    "resulting_state",
    "resulting_requirements",
    "requirement_rationale",
    "subordinate_governance_questions",
    "implementation_questions",
    "provenance",
}
EXPECTED_CORRECTION_COMPONENT_DIGESTS = {
    "CDC-01": "847a4a39a7205f176cfb7b8e87c77768a1542c918bdaf58e824b2fc042933416",
    "CDC-02": "dcd78dc10b675fb6e96e9395e063db59868fd50bdadfa74a6bccee79c71cbeb2",
    "CDC-03": "b55d35e1ca27fafc9ec70e3ed386b4708117960e1963bd00abfef9631de6b5e9",
    "CDC-04": "5579dd8f73d6226b1a7bdbae52e59bf952d57a92e7d1c61329172df993b00598",
}
CONSTITUTION_TRACE_FIELDS = {
    "traceability_id",
    "draft_status",
    "constitutional_effect",
    "article_count",
    "section_count",
    "authority_basis",
    "human_drafting_decision",
    "sections",
    "coverage_summary",
    "provenance",
}
CONSTITUTION_TRACE_SECTION_FIELDS = {
    "section_id",
    "title",
    "article",
    "consolidated_requirements",
    "source_requirements",
    "controlling_cdrs",
    "controlling_cdd",
    "adopted_design_domains",
    "coordinated_corrections",
    "authority_summary",
}
EXPECTED_DRAFT_SECTION_TITLES = {
    "I.1": "Reserved Human Sovereignty and Non-Accretion",
    "II.1": "Binding Constitutional Constraint",
    "II.2": "Constitutional Membership and Standing",
    "II.3": "Separated Functions, Initialization, and Vacancies",
    "III.1": "Constitutional Court and Jurisdiction",
    "III.2": "Selection, Qualification, Terms, and Removal",
    "III.3": "Recusal, Panels, Appeal, and Conflict Tribunal",
    "III.4": "Remedies, Enforcement, Verification, and Reviewer Limits",
    "IV.1": "Attributable Constitutional Records",
    "IV.2": "Independence, Machine Domination, and Effective-Power Review",
    "V.1": "Predelegated Emergency Authority",
    "V.2": "Necessity Fallback",
    "V.3": "Scope, Absolute Prohibitions, and Expiry",
    "V.4": "Emergency Record, Review, and Remedies",
    "VI.1": "Claimant-Neutral Continuity",
    "VI.2": "Predesignation, Proof, and Succession Council",
    "VI.3": "Non-Quorum Human Fallback",
    "VI.4": "Interregnum Limit, Return, and Invalid Succession",
    "VII.1": "Categories and Non-Waiver",
    "VII.2": "Amendment and Refounding Procedures",
    "VII.3": "Cumulative Effect and Semantic Drift",
    "VIII.1": "Refounding-Level Principles",
    "VIII.2": "Termination and Transition Authority",
    "VIII.3": "Transition Accountability, Obligations, and Memory",
}
EXPECTED_RATIFICATION_DRAFT_DIGESTS = {
    CONSTITUTION_DRAFT_RELATIVE_PATH: (
        "b5e39a1b2eddf02317d5b1fc3b2a90cb1850eb3e4a75a531771b3e79e0db85cd"
    ),
    CONSTITUTION_TRACE_RELATIVE_PATH: (
        "f0778443eedff2f89a8cbbeaeacd8b442fe0498f049c2fcf4dc610b2f40874e0"
    ),
    CONSTITUTION_OPEN_QUESTIONS_RELATIVE_PATH: (
        "af292c0ce09a81700c32bd1fdfc5d6fbea1c58cc3c47fd83567b8696597a1a72"
    ),
}
FINAL_BLOCKER_ANALYSIS_FIELDS = {
    "analysis_id",
    "status",
    "decision_effect",
    "constitutional_effect",
    "draft_modified",
    "human_decision_made",
    "purpose",
    "authoritative_basis",
    "blockers",
    "controlling_constraints",
    "stress_dimensions",
    "integrated_alternatives",
    "recommended_integrated_architecture",
    "subordinate_law_items",
    "residual_questions",
    "provenance",
}
FINAL_BLOCKER_STRESS_DIMENSIONS = {
    "bootstrap",
    "ordinary_operation",
    "vacancy",
    "removal",
    "replacement",
    "conflict",
    "succession",
    "emergency",
    "capture",
    "coalition_capture",
    "machine_domination",
    "institutional_paralysis",
    "effective_power_takeover",
    "amendment_refounding_boundary",
}
REMAINING_DESIGN_STRESS_DIMENSIONS = {
    "bad_human",
    "bad_artificial_intelligence",
    "coalition_capture",
    "continuity",
    "reversibility",
    "legitimacy",
    "human_comprehensibility",
}
EXPECTED_BLOCKED_CONSOLIDATED_REQUIREMENTS = {
    "CCR-003",
    "CCR-006",
    "CCR-008",
    "CCR-010",
    "CCR-012",
    "CCR-013",
    "CCR-014",
    "CCR-015",
    "CCR-019",
}
REMAINING_DESIGN_DECISION_TERMS = {
    "RD-01": ("authority-or-beneficiary", "four standing channels"),
    "RD-02": ("five-human", "both nonappointing channels"),
    "RD-03": ("one appeal", "Enforcement Office", "Verification Office"),
    "RD-04": ("clear and convincing", "twenty-four hours"),
    "RD-05": ("six hours", "twenty-four hours"),
    "RD-06": ("three materially independent", "seven-human Succession Council"),
    "RD-07": ("180-day", "immediate"),
    "RD-08": ("three equal", "affected human beneficiaries", "before the first vote"),
    "RD-09": ("twenty-four months", "semantic-drift audit"),
    "RD-10": ("Before the second", "cannot take effect", "activates"),
    "RD-11": ("sole gatekeeper", "substantive machine domination"),
}
CROSS_DOMAIN_COMPONENTS = {
    "Human-Only Initialization and Vacancy": {
        "domains": {"RD-01", "RD-02", "RD-03", "RD-11"},
        "ccrs": {"CCR-003", "CCR-013", "CCR-014", "CCR-015", "CCR-016"},
        "crs": {
            "CR-004", "CR-006", "CR-021", "CR-022", "CR-023", "CR-024",
            "CR-025", "CR-026", "CR-027", "CR-028", "CR-029",
        },
        "terms": (
            "bootstrap authority only",
            "No artificial-intelligence system may appoint",
            "create no precedent or new appointment authority",
        ),
    },
    "Successor Predesignation and Failure Fallback": {
        "domains": {"RD-04", "RD-06", "RD-07", "RD-11"},
        "ccrs": {"CCR-006", "CCR-008", "CCR-010", "CCR-012"},
        "crs": {
            "CR-008", "CR-009", "CR-010", "CR-012", "CR-013", "CR-017",
            "CR-018", "CR-020",
        },
        "terms": (
            "constitutionally valid successor designations",
            "fifteen-human fallback panel",
            "Twelve members constitute quorum",
            "ten affirmative votes",
            "180-day maximum",
            "creates foundational sovereignty",
        ),
    },
    "Accountable Post-Refounding Transition": {
        "domains": {"RD-01", "RD-03", "RD-08", "RD-10", "RD-11"},
        "ccrs": {
            "CCR-003", "CCR-013", "CCR-015", "CCR-017", "CCR-018",
            "CCR-019", "CCR-020",
        },
        "crs": {
            "CR-004", "CR-006", "CR-021", "CR-022", "CR-026", "CR-027",
            "CR-030", "CR-031", "CR-032", "CR-033", "CR-034", "CR-035",
        },
        "terms": (
            "cannot self-renew",
            "independently review and verify",
            "constitutionally incomplete and cannot take effect",
        ),
    },
    "Reviewer-Non-Sovereign Remedies": {
        "domains": {"RD-01", "RD-03", "RD-09", "RD-11"},
        "ccrs": {
            "CCR-003", "CCR-013", "CCR-014", "CCR-015", "CCR-016",
            "CCR-019",
        },
        "crs": {
            "CR-004", "CR-006", "CR-021", "CR-022", "CR-023", "CR-024",
            "CR-025", "CR-026", "CR-027", "CR-028", "CR-029", "CR-034",
        },
        "terms": (
            "declare a vacancy",
            "separately authorized human selector",
            "cannot appoint personnel",
        ),
    },
}
EXPECTED_ARTICLE_TITLES = [
    "Constitutional Identity and Human Sovereignty",
    "Constitutional Authority, Constraint, and Separation of Functions",
    "Constitutional Adjudication and Enforcement",
    "Epistemic Integrity, Provenance, Dissent, and Effective Power",
    "Emergency Authority",
    "Continuity, Succession, and Interregnum",
    "Amendment and Constitutional Change",
    (
        "Refounding, Termination, Continuity of Obligations, and "
        "Constitutional Memory"
    ),
]
EXPECTED_ARTICLE_CONTROLLING_CDRS = {
    "ARTICLE-I": {"CDR-001", "CDR-003"},
    "ARTICLE-II": {"CDR-001", "CDR-004"},
    "ARTICLE-III": {"CDR-002", "CDR-003", "CDR-004", "CDR-005"},
    "ARTICLE-IV": {"CDR-001"},
    "ARTICLE-V": {"CDR-002", "CDR-003", "CDR-004", "CDR-005"},
    "ARTICLE-VI": {"CDR-002", "CDR-003", "CDR-004", "CDR-005"},
    "ARTICLE-VII": {"CDR-002", "CDR-003", "CDR-004", "CDR-005"},
    "ARTICLE-VIII": {"CDR-001", "CDR-002", "CDR-003", "CDR-004", "CDR-005"},
}
FQ4_SOURCE_MATERIAL = {
    "FQ-04",
    "CDR-001",
    "CDR-002",
    "CDR-003",
    "constitutional-design/FOUNDATIONAL_QUESTIONS.yaml",
    "constitutional-design/decisions/CDR-001.yaml",
    "constitutional-design/decisions/CDR-002.yaml",
    "constitutional-design/decisions/CDR-003.yaml",
    "constitutional-design/issues/IR-01-human-sovereignty.yaml",
    "constitutional-design/issues/IR-02-constraint-of-constitutional-authority.yaml",
    "constitutional-design/issues/IR-03-emergency-necessity.yaml",
    "constitutional-design/issues/IR-04-succession-and-interregnum.yaml",
    "constitutional-design/issues/IR-06-constitutional-adjudication.yaml",
    "constitutional-design/issues/IR-07-offices-roles-membership-standing.yaml",
    "constitutional-design/issues/IR-08-formal-and-effective-power.yaml",
    "constitutional-design/issues/IR-09-incentive-compatibility.yaml",
    "constitutional-design/issues/IR-10-separation-of-functions.yaml",
    "constitutional-design/issues/IR-12-dissent.yaml",
    "constitutional-design/issues/IR-13-epistemic-integrity.yaml",
    "constitutional-design/issues/IR-15-amendment-and-refounding.yaml",
    "constitutional-design/issues/IR-17-constitutional-hierarchy.yaml",
    "constitutional-design/issues/IR-18-human-control-and-comprehensibility.yaml",
    "constitutional-design/sources/HISTORICAL_EVIDENCE_REGISTER.yaml",
    "constitutional-design/sources/PRIOR_ART_REGISTER.yaml",
    "docs/DESIGN_PRINCIPLES.md",
    "docs/GLOSSARY.md",
}
FQ4_PACKET_SUMMARIES = {
    "A": {
        "Model": (
            "Foundational human authority retains final judgment even when "
            "personally implicated; external review remains advisory."
        ),
        "Strongest argument for": (
            "It prevents an adjudicator from becoming a rival foundational "
            "sovereign over institutional ends."
        ),
        "Strongest argument against": (
            "The disputed party controls standing, judgment, remedy, and finality "
            "in its own case."
        ),
        "Catastrophic failure": (
            "Self-favoring judgments convert every constitutional limit into a "
            "waivable convention."
        ),
        "Unresolved question": (
            "Can any meaningful constraint bind foundational authority if its own "
            "judgment remains final?"
        ),
    },
    "B": {
        "Model": (
            "A standing constitutionally created human body may bind ordinary "
            "constitutional acts, including acts of foundational authority, "
            "within limited jurisdiction."
        ),
        "Strongest argument for": (
            "Constitutional limits remain enforceable when the most powerful "
            "human actor is personally implicated."
        ),
        "Strongest argument against": (
            "Interpretive, remedial, and enforcement power can turn the reviewer "
            "into a sovereign over institutional ends."
        ),
        "Catastrophic failure": (
            "A captured standing body governs through doctrine and remedies while "
            "retaining formal claims of limited review."
        ),
        "Unresolved question": (
            "What makes judgments binding while keeping jurisdiction and remedies "
            "non-sovereign?"
        ),
    },
    "C": {
        "Model": (
            "Multiple independent human bodies divide review, appeal, concurrence, "
            "remedy, or enforcement functions."
        ),
        "Strongest argument for": (
            "No single institution controls the entire adjudicative chain, "
            "reducing unilateral capture."
        ),
        "Strongest argument against": (
            "Delay, inconsistent judgments, coalition trading, and shared "
            "infrastructure can defeat genuine distribution."
        ),
        "Catastrophic failure": (
            "A cross-body coalition or common artificial intelligence controls "
            "every nominal check."
        ),
        "Unresolved question": (
            "Which body has finality without recreating concentrated reviewer "
            "sovereignty?"
        ),
    },
    "D": {
        "Model": (
            "Predefined rules constitute a conflict-specific human tribunal when "
            "ordinary adjudicators are compromised; it dissolves after the matter."
        ),
        "Strongest argument for": (
            "It targets exceptional conflicts without creating a permanent "
            "competing center of constitutional power."
        ),
        "Strongest argument against": (
            "Trigger, selection, recusal, and dissolution can be manipulated by "
            "the disputing parties."
        ),
        "Catastrophic failure": (
            "A coalition manufactures conflict and installs a favorable tribunal "
            "with binding temporary power."
        ),
        "Unresolved question": (
            "Who validates conflict and selects an impartial tribunal without "
            "becoming the hidden adjudicator?"
        ),
    },
    "E": {
        "Model": (
            "Independent standing human adjudication is the default, with "
            "distributed appeal and anti-capture mechanisms plus predefined "
            "special handling when ordinary adjudicators are compromised."
        ),
        "Strongest argument for": (
            "It combines stable review capacity with correction, capture "
            "resistance, and a path through genuine adjudicator conflict."
        ),
        "Strongest argument against": (
            "Layered appointment, appeal, recusal, remedy, enforcement, and "
            "special-process rules create complexity and diffuse power."
        ),
        "Catastrophic failure": (
            "Standing and special bodies form a durable coalition whose shared "
            "machines, doctrine, and enforcement make reviewers de facto "
            "sovereign."
        ),
        "Unresolved question": (
            "Which layers are necessary for resilient review without making "
            "adjudication an unaccountable governing system?"
        ),
    },
}
FQ1_REQUIRED_ISSUES = {
    "IR-01",
    "IR-02",
    "IR-06",
    "IR-08",
    "IR-09",
    "IR-10",
    "IR-15",
    "IR-17",
    "IR-18",
}
FQ1_REQUIRED_ARCHITECTURES = {"A", "B", "C", "D", "E"}
FQ1_REQUIRED_ARCHITECTURE_NAMES = {
    "A": "Unconstrained Foundational Sovereign",
    "B": "Constitution-Bound Sovereign Without External Adjudicator",
    "C": "Constitution-Bound Sovereign With Independent Review",
    "D": "Distributed Foundational Authority",
    "E": "Reserved Human Sovereignty + Entrenched Constitutional Limits",
}
FQ1_ARCHITECTURE_FIELDS = {
    "architecture_id",
    "name",
    "research_status",
    "definition",
    "constitutional_distinction",
    "dimensions",
    "adversarial_tests",
}
FQ1_ARCHITECTURE_DIMENSIONS = {
    "source_of_legitimacy",
    "constraint_mechanism",
    "enforcement",
    "adjudication",
    "appeal",
    "amendment",
    "refounding",
    "succession",
    "emergency",
    "effective_power",
    "incentives",
    "reversibility",
    "legibility",
    "machine_implementability",
}
FQ1_ADVERSARIAL_TESTS = {
    "bad_human",
    "bad_artificial_intelligence",
    "capture",
    "emergency",
    "succession",
    "popularity_performance_capture",
    "precedent_accretion",
    "validator_capture",
}
FQ1_CORE_DISTINCTION_FIELDS = {
    "sovereignty_over_institutional_ends",
    "constitutional_freedom_and_governed_exercise_of_institutional_power",
    "machine_validity_and_constitutional_legitimacy",
}
FQ1_ATTACK_FIELDS = {
    "abuse_scenario",
    "prevention_or_limit",
    "residual_failure",
    "validity_legitimacy_boundary",
}
FQ1_MATRIX_DIMENSIONS = {
    "preservation_of_human_sovereignty",
    "constraint_on_arbitrary_human_power",
    "resistance_to_artificial_intelligence_capture",
    "resistance_to_human_capture",
    "legitimacy_clarity",
    "enforcement_credibility",
    "succession_robustness",
    "emergency_robustness",
    "incentive_compatibility",
    "anti_accretion_protection",
    "reversibility",
    "human_comprehensibility",
    "implementation_feasibility",
    "risk_of_hidden_sovereignty_transfer",
    "risk_of_constitutional_deadlock",
}
FQ1_ANALOGUE_CLASSIFICATIONS = {
    "DIRECT_ANALOGUE",
    "PARTIAL_ANALOGUE",
    "DESIGN_LESSON",
    "NO_CLOSE_ANALOGUE_IDENTIFIED",
}
FQ1_REQUIRED_TRADEOFFS = {
    "human_sovereignty_vs_constraint",
    "constraint_vs_recursive_authority",
    "continuity_vs_anti_usurpation",
    "emergency_responsiveness_vs_abuse",
    "independent_review_vs_reviewer_capture",
    "stability_vs_legitimate_amendment",
    "machine_enforcement_vs_human_legitimacy",
    "effective_artificial_intelligence_autonomy_vs_human_control",
}
FQ1_NO_DISSENT_STATEMENT = "NO DISSENT HAS BEEN RECORDED."
FQ1_NO_SELECTION_STATEMENT = (
    "No architecture is selected, ranked, declared an automatic winner, "
    "or treated as decided or dominated by this synthesis."
)
FQ1_MATRIX_REVIEW_FIELDS = {
    "review_type",
    "method",
    "selection_boundary",
    "architecture_assessments",
}
FQ1_MATRIX_BOUNDARY_FIELDS = {
    "selected_architecture",
    "ranking",
    "automatic_winner",
    "no_selected_architecture",
    "statement",
}
FQ1_SYNTHESIS_FIELDS = {
    "review_type",
    "selection_statement",
    "per_architecture",
    "common_failure_modes",
    "questions_requiring_human_normative_judgment",
    "empirical_questions",
    "underdetermined_questions",
}
FQ1_PACKET_RELATIVE_PATH = Path(
    "constitutional-design/decisions/packets/"
    "CDR-001-HUMAN-DECISION-PACKET.md"
)
FQ1_PACKET_HEADINGS = (
    "Purpose and Decision Boundary",
    "Provenance and Evidence Limits",
    "Existing Architectures",
    "Core Decision",
    "Elimination Analysis",
    "Recommended Architecture",
    "Hybrid Question",
    "Human Decision Options",
    "Decision Questions",
    "Consequences for Later Design",
    "Material Ambiguities",
)
FQ1_PACKET_ARCHITECTURE_HEADINGS = tuple(
    f"Architecture {architecture_id} — {FQ1_REQUIRED_ARCHITECTURE_NAMES[architecture_id]}"
    for architecture_id in ("A", "B", "C", "D", "E")
)
FQ1_PACKET_ARCHITECTURE_LABELS = (
    "Constitutional model",
    "Strongest argument for",
    "Strongest argument against",
    "Catastrophic failure mode",
    "Principal unresolved question",
)
FQ1_PACKET_ARCHITECTURE_REQUIRED_TERMS = {
    "Architecture A — Unconstrained Foundational Sovereign": {
        "Constitutional model": (
            "human foundational sovereign",
            "without a superior adjudicator",
            "self-restraint",
        ),
        "Strongest argument for": ("clearest human source", "fastest final action"),
        "Strongest argument against": (
            "no reliable internal protection",
            "arbitrary action",
        ),
        "Catastrophic failure mode": (
            "capture or abuse of the sovereign",
            "capture of the institution",
        ),
        "Principal unresolved question": ("credible", "rewrite or waive"),
    },
    "Architecture B — Constitution-Bound Sovereign Without External Adjudicator": {
        "Constitutional model": (
            "publicly binding ordinary power",
            "same sovereign remains the final interpreter",
        ),
        "Strongest argument for": ("public commitment", "procedural regularity"),
        "Strongest argument against": (
            "final judge of its own limits",
            "self-serving interpretation",
        ),
        "Catastrophic failure mode": (
            "accumulated interpretations",
            "discretionary permission",
        ),
        "Principal unresolved question": (
            "binding law",
            "organized self-restraint",
        ),
    },
    "Architecture C — Constitution-Bound Sovereign With Independent Review": {
        "Constitutional model": (
            "independent human review",
            "does not control institutional purpose or refounding",
        ),
        "Strongest argument for": ("contestable", "enforceable constraints"),
        "Strongest argument against": (
            "reviewer capture",
            "recursive legitimacy",
        ),
        "Catastrophic failure mode": (
            "effective control of constitutional meaning",
            "human sovereign",
        ),
        "Principal unresolved question": (
            "review bind",
            "reviewer becoming sovereign",
        ),
    },
    "Architecture D — Distributed Foundational Authority": {
        "Constitutional model": (
            "multiple constituent bodies",
            "constrain unilateral exercise",
        ),
        "Strongest argument for": (
            "single-point capture",
            "plural human counter-power",
        ),
        "Strongest argument against": ("deadlock", "informal recentralization"),
        "Catastrophic failure mode": (
            "recentralizes effective power",
            "obscures responsibility",
        ),
        "Principal unresolved question": (
            "legitimate constituent standing",
            "aggregation binding",
        ),
    },
    "Architecture E — Reserved Human Sovereignty + Entrenched Constitutional Limits": {
        "Constitutional model": (
            "humans collectively retain authority",
            "entrenched limits govern ordinary",
        ),
        "Strongest argument for": (
            "human sovereignty over ends",
            "binding limits",
        ),
        "Strongest argument against": (
            "entrenchment creates rigidity",
            "formal human control becomes nominal",
        ),
        "Catastrophic failure mode": (
            "captured review and technical apparatus",
            "human refounding",
        ),
        "Principal unresolved question": (
            "legitimate human refounding act",
            "reviewers contest",
        ),
    },
}
FQ1_PACKET_DECISION_OPTIONS = (
    "ADOPT_A",
    "ADOPT_B",
    "ADOPT_C",
    "ADOPT_D",
    "ADOPT_E",
    "ADOPT_HYBRID",
    "REVISE_AND_REVIEW",
    "DEFER",
)
FQ1_PACKET_CONSEQUENCE_ISSUES = {
    "IR-03",
    "IR-04",
    "IR-06",
    "IR-10",
    "IR-15",
    "IR-17",
}
FQ1_PACKET_PROVENANCE_PATHS = {
    "constitutional-design/decisions/CDR-001.yaml",
    "constitutional-design/FOUNDATIONAL_QUESTIONS.yaml",
    "constitutional-design/issues/IR-01-human-sovereignty.yaml",
    "constitutional-design/issues/IR-02-constraint-of-constitutional-authority.yaml",
    "constitutional-design/issues/IR-03-emergency-necessity.yaml",
    "constitutional-design/issues/IR-04-succession-and-interregnum.yaml",
    "constitutional-design/issues/IR-06-constitutional-adjudication.yaml",
    "constitutional-design/issues/IR-08-formal-and-effective-power.yaml",
    "constitutional-design/issues/IR-09-incentive-compatibility.yaml",
    "constitutional-design/issues/IR-10-separation-of-functions.yaml",
    "constitutional-design/issues/IR-12-dissent.yaml",
    "constitutional-design/issues/IR-15-amendment-and-refounding.yaml",
    "constitutional-design/issues/IR-17-constitutional-hierarchy.yaml",
    "constitutional-design/issues/IR-18-human-control-and-comprehensibility.yaml",
    "constitutional-design/sources/HISTORICAL_EVIDENCE_REGISTER.yaml",
    "constitutional-design/sources/PRIOR_ART_REGISTER.yaml",
    "constitutional-design/sources/MECHANISM_ADOPTION_MAP.yaml",
    "docs/DESIGN_PRINCIPLES.md",
    "docs/GLOSSARY.md",
    "constitutional-design/decisions/README.md",
}


@dataclass(frozen=True)
class ValidationResult:
    errors: tuple[str, ...]
    metrics: dict[str, Any]

    @property
    def passed(self) -> bool:
        return not self.errors


def _load_record(path: Path, errors: list[str]) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        errors.append(f"INVALID_RECORD: {path}: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"INVALID_RECORD: {path}: top-level value must be an object")
        return None
    return value


def _is_evidence(value: Any) -> bool:
    return isinstance(value, str) and value.strip() not in PLACEHOLDERS


def _has_human_decision_evidence(record: dict[str, Any]) -> bool:
    decision = record.get("human_decision")
    if not isinstance(decision, dict):
        return False
    return all(
        _is_evidence(decision.get(field))
        for field in ("authorized_by", "authorization_record", "decision_date")
    )


def _has_provenance(record: dict[str, Any]) -> bool:
    provenance = record.get("provenance")
    if not isinstance(provenance, dict):
        return False
    return any(
        _is_evidence(provenance.get(field))
        for field in ("source", "supplied_by")
    )


def _contains_novel(value: Any) -> bool:
    if isinstance(value, dict):
        return any(_contains_novel(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_novel(item) for item in value)
    return isinstance(value, str) and value.strip().upper() == "NOVEL"


def _contains_unqualified_conclusion(value: Any, conclusion: str) -> bool:
    if isinstance(value, dict):
        return any(
            _contains_unqualified_conclusion(item, conclusion)
            for item in value.values()
        )
    if isinstance(value, list):
        return any(
            _contains_unqualified_conclusion(item, conclusion) for item in value
        )
    if not isinstance(value, str):
        return False
    words = re.findall(r"[A-Z_]+", value.upper())
    for index, word in enumerate(words):
        if word != conclusion:
            continue
        context = words[max(0, index - 4) : index]
        if not {"NO", "NOT", "NEVER", "WITHOUT"}.intersection(context):
            return True
    return False


def _contains_exact_string(value: Any, expected: str) -> bool:
    if isinstance(value, dict):
        return any(
            _contains_exact_string(item, expected) for item in value.values()
        )
    if isinstance(value, list):
        return any(_contains_exact_string(item, expected) for item in value)
    return isinstance(value, str) and value.strip().upper() == expected


def _has_content(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return value is not None


def _matches_exact_vocabulary(value: Any, expected: set[str]) -> bool:
    return (
        isinstance(value, list)
        and len(value) == len(expected)
        and all(isinstance(item, str) for item in value)
        and set(value) == expected
    )


def _source_reference_urls(value: Any) -> list[str] | None:
    if isinstance(value, str):
        if ";" in value:
            return None
        return [value]
    if (
        isinstance(value, list)
        and value
        and all(isinstance(item, str) for item in value)
    ):
        return value
    return None


def _is_stable_http_reference(value: str) -> bool:
    if not value.strip() or value != value.strip() or any(
        character.isspace() for character in value
    ):
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _load_record_set(
    directory: Path, pattern: str, errors: list[str]
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted(directory.glob(pattern)):
        record = _load_record(path, errors)
        if record is not None:
            record["_record_path"] = str(path)
            records.append(record)
    return records


def _is_empty_human_decision(record: dict[str, Any]) -> bool:
    decision = record.get("human_decision")
    return (
        isinstance(decision, dict)
        and set(decision) == HUMAN_DECISION_FIELDS
        and all(
            decision.get(field) == []
            if field in {"incorporated_mechanisms", "rejected_mechanisms"}
            else decision.get(field) == ""
            for field in decision
        )
        and record.get("decision_date") == ""
    )


def _contains_number(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        return True
    if isinstance(value, dict):
        return any(_contains_number(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_number(item) for item in value)
    return False


def _contains_key_fragment(value: Any, fragment: str) -> bool:
    if isinstance(value, dict):
        return any(
            fragment in str(key).lower()
            or _contains_key_fragment(item, fragment)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(_contains_key_fragment(item, fragment) for item in value)
    return False


def _contains_architecture_selection_claim(value: Any) -> bool:
    if isinstance(value, dict):
        return any(
            _contains_architecture_selection_claim(item)
            for item in value.values()
        )
    if isinstance(value, list):
        return any(_contains_architecture_selection_claim(item) for item in value)
    if not isinstance(value, str):
        return False
    patterns = (
        r"\bARCHITECTURE\s+[A-Z0-9_-]+\s+"
        r"(?:IS|WAS|HAS\s+BEEN)\s+"
        r"(?:SELECTED|ADOPTED|DECIDED|THE\s+WINNER)\b",
        r"\b(?:WE|THIS\s+RECORD|CDR-\d{3}|THE\s+ANALYSIS)\s+"
        r"(?:HEREBY\s+)?(?:ADOPT|SELECT|CHOOSE)\s+"
        r"ARCHITECTURE\s+[A-Z0-9_-]+\b",
    )
    return any(re.search(pattern, value, flags=re.IGNORECASE) for pattern in patterns)


def _has_substantive_fq2_analysis(
    field: str,
    value: Any,
) -> bool:
    if not isinstance(value, str) or len(value.split()) < 8:
        return False
    folded = value.casefold()
    terms = FQ2_ANALYSIS_REQUIRED_TERMS[field]
    if field == "machine_validity_constitutional_legitimacy_boundary":
        return terms[0] in folded and any(term in folded for term in terms[1:])
    return any(term in folded for term in terms)


def _has_substantive_fq3_analysis(field: str, value: Any) -> bool:
    if not isinstance(value, str) or len(value.split()) < 8:
        return False
    folded = value.casefold()
    return all(
        any(term in folded for term in group)
        for group in FQ3_ANALYSIS_REQUIRED_TERM_GROUPS[field]
    )


def _contains_fq3_authority_effect_claim(value: Any) -> bool:
    if isinstance(value, dict):
        return any(
            _contains_fq3_authority_effect_claim(item)
            for item in value.values()
        )
    if isinstance(value, list):
        return any(_contains_fq3_authority_effect_claim(item) for item in value)
    if not isinstance(value, str):
        return False
    patterns = (
        r"\bARCHITECTURE [A-E]\s+(?:IS\s+)?(?:HEREBY\s+)?"
        r"(?:ADOPTED|SELECTED|ENACTED|IN\s+FORCE)\b",
        r"\bARCHITECTURE [A-E]\s+(?:GOVERNS|CONTROLS)\s+SUCCESSION\b",
        r"\bARCHITECTURE [A-E]\s+(?:NOW\s+)?(?:HAS|CARRIES)\s+"
        r"CONSTITUTIONAL (?:FORCE|EFFECT|AUTHORITY)\b",
        r"\bARTIFICIAL INTELLIGENCE\s+(?:(?:IS|ARE)\s+PERMITTED\s+TO|"
        r"(?:MAY|CAN|SHALL|WILL))\s+"
        r"(?:INHERIT|ACQUIRE)\s+FOUNDATIONAL SOVEREIGNTY\b",
        r"\bCDR-002 EMERGENCY AUTHORITY\s+(?:MAY\s+BE\s+USED\s+AS|IS|"
        r"BECOMES|CREATES|CONFERS)\s+"
        r"SUCCESSION AUTHORITY\b",
        r"\bADMINISTRATIVE CONTINUITY\s+"
        r"(?:CREATES|CONFERS|ESTABLISHES)\s+"
        r"(?:CONSTITUTIONAL LEGITIMACY|SUCCESSION AUTHORITY)\b",
    )
    return any(re.search(pattern, value, flags=re.IGNORECASE) for pattern in patterns)


def _has_substantive_fq4_analysis(field: str, value: Any) -> bool:
    if not isinstance(value, str) or len(value.split()) < 8:
        return False
    folded = value.casefold()
    return all(
        any(term in folded for term in group)
        for group in FQ4_ANALYSIS_REQUIRED_TERM_GROUPS[field]
    )


def _contains_fq4_authority_effect_claim(value: Any) -> bool:
    if isinstance(value, dict):
        return any(
            _contains_fq4_authority_effect_claim(item)
            for item in value.values()
        )
    if isinstance(value, list):
        return any(_contains_fq4_authority_effect_claim(item) for item in value)
    if not isinstance(value, str):
        return False
    patterns = (
        r"\bARCHITECTURE [A-E]\s+(?:IS\s+)?(?:HEREBY\s+)?"
        r"(?:ADOPTED|SELECTED|ENACTED|IN\s+FORCE)\b",
        r"\bARCHITECTURE [A-E]\s+(?:NOW\s+)?(?:HAS|CARRIES)\s+"
        r"CONSTITUTIONAL (?:FORCE|EFFECT|AUTHORITY)\b",
        r"\b(?:A|THE)\s+(?:REVIEWER|ADJUDICATOR|TRIBUNAL)\s+"
        r"(?:(?:MAY|CAN|SHALL|WILL)\s+)?"
        r"(?:CONTROL|CONTROLS|DETERMINE|DETERMINES|REDEFINE|REDEFINES|"
        r"GOVERN|GOVERNS)\s+INSTITUTIONAL (?:ENDS|PURPOSES)\b",
        r"\bARTIFICIAL INTELLIGENCE\s+(?:(?:MAY|CAN|SHALL|WILL)\s+"
        r"(?:SERVE|ACT)\s+AS|IS)\s+(?:THE\s+)?"
        r"FINAL CONSTITUTIONAL ADJUDICATOR\b",
        r"\bMACHINE VALIDATION\s+(?:(?:MAY|CAN|SHALL|WILL|DOES)\s+)?"
        r"(?:SETTLE|SETTLES|DETERMINE|DETERMINES|ESTABLISH|ESTABLISHES)\s+"
        r"CONSTITUTIONAL LEGITIMACY\b",
        r"\bADJUDICATION\s+(?:(?:MAY|CAN|SHALL|WILL)\s+)?"
        r"(?:AMEND|AMENDS|REFOUND|REFOUNDS|CREATES?\s+"
        r"(?:AMENDMENT|REFOUNDING)\s+AUTHORITY)\b",
        r"\bTHE RECOMMENDATION\s+"
        r"(?:ADOPTS|AUTHORIZES|DECIDES|ENACTS|RESOLVES)\b",
        r"\bFQ-04\s+(?:BECOMES|IS)\s+RESOLVED\s+BY\s+"
        r"(?:THIS|THE)\s+RECOMMENDATION\b",
    )
    if any(re.search(pattern, value, flags=re.IGNORECASE) for pattern in patterns):
        return True
    semantic_value = value.casefold().replace(
        "recommendation_only — no constitutional effect",
        "",
    )
    for sentence in re.split(r"(?<=[.!?])\s+", semantic_value):
        if (
            "recommendation" in sentence
            and any(
                target in sentence
                for target in ("fq-04", "architecture e", "fourth foundational")
            )
            and any(
                effect in sentence
                for effect in (
                    "adopt",
                    "authoriz",
                    "conclud",
                    "decid",
                    "enact",
                    "resolv",
                    "settle",
                    "in force",
                    "effect",
                )
            )
        ):
            return True
        if re.search(r"\b(?:no|not|never|cannot|without|ineligible|prohibit)\b", sentence):
            continue
        if (
            any(
                actor in sentence
                for actor in (
                    "reviewer",
                    "review body",
                    "adjudicator",
                    "tribunal",
                    "court",
                )
            )
            and any(
                power in sentence
                for power in ("govern", "control", "determine", "redefine", "set")
            )
            and any(
                end in sentence
                for end in (
                    "institutional ends",
                    "institutional purposes",
                    "institutional goals",
                    "constitutional goals",
                )
            )
        ):
            return True
        if (
            any(
                actor in sentence
                for actor in (
                    "artificial intelligence",
                    "ai ",
                    "machine",
                    "automated system",
                )
            )
            and any(term in sentence for term in ("final", "ultimate"))
            and any(term in sentence for term in ("adjudicator", "judge", "decid"))
            and "constitutional" in sentence
        ):
            return True
        if (
            any(
                actor in sentence
                for actor in (
                    "machine validation",
                    "automated validation",
                    "technical validation",
                    "validator",
                )
            )
            and "constitutional legitimacy" in sentence
            and any(
                effect in sentence
                for effect in ("settle", "determine", "establish", "confer", "create")
            )
        ):
            return True
        if (
            any(
                actor in sentence
                for actor in (
                    "adjudication",
                    "court",
                    "reviewer",
                )
            )
            and any(
                change in sentence
                for change in ("amend", "refound", "rewrite", "alter")
            )
            and any(
                target in sentence
                for target in ("constitution", "amendment authority")
            )
        ):
            return True
    return False


def _contains_external_fq4_evidence(value: Any) -> bool:
    if isinstance(value, dict):
        return any(
            _contains_external_fq4_evidence(item)
            for key, item in value.items()
            if key != "_record_path"
        )
    if isinstance(value, list):
        return any(_contains_external_fq4_evidence(item) for item in value)
    if not isinstance(value, str):
        return False
    registered_markers = ("he-", "pa-", "cdr-", "repository")
    folded = value.casefold()
    for phrase in ("according to", "evidence from"):
        for match in re.finditer(phrase, folded):
            attribution = folded[match.end() : match.end() + 100]
            if not any(marker in attribution for marker in registered_markers):
                return True
    patterns = (
        r"https?://",
        r"doi\.org/",
        r"\bexternal (?:source|evidence|citation)\b",
        r"\b[A-Z]:\\",
        r"(?:^|\s)/(?:home|users|tmp|var)/",
        r"\b[A-Z][a-z]+ \((?:19|20)\d{2}\)",
        r"\b(?:19|20)\d{2}\s+(?:\w+\s+){0,3}"
        r"(?:study|paper|book|article|report)\b",
        r"\b(?:study|paper|book|article|report)\s+by\b",
    )
    return any(re.search(pattern, value, flags=re.IGNORECASE) for pattern in patterns)


def _validate_fq1_analytical_record(
    decision: dict[str, Any],
    known_historical_ids: set[str],
    known_prior_art_ids: set[str],
    root: Path,
    errors: list[str],
) -> tuple[int, int, set[str], set[str]]:
    decision_id = decision.get("decision_id")
    if decision_id != "CDR-001":
        return 0, 0, set(), set()

    if decision.get("status") != "DECIDED":
        errors.append("FQ1_DECISION_STATUS: CDR-001 must be DECIDED")
    human_decision = decision.get("human_decision")
    valid_human_decision = (
        isinstance(human_decision, dict)
        and set(human_decision) == HUMAN_DECISION_FIELDS
        and human_decision.get("decision") == FQ1_DECISION
        and human_decision.get("foundational_architecture")
        == FQ1_FOUNDATIONAL_ARCHITECTURE
        and human_decision.get("incorporated_mechanisms")
        == FQ1_INCORPORATED_MECHANISMS
        and human_decision.get("rejected_mechanisms")
        == FQ1_REJECTED_MECHANISMS
        and human_decision.get("decision_authority")
        == "Human Constitutional Authority"
        and human_decision.get("decision_basis")
        == (
            "Explicit human instruction following review of CDR-001 and its "
            "human decision packet."
        )
        and human_decision.get("authorized_by")
        == "Human Constitutional Authority"
        and human_decision.get("authorization_record")
        == (
            "Explicit human instruction received on 2026-08-28 directing this "
            "repository to record ADOPT_HYBRID for CDR-001."
        )
        and human_decision.get("decision_date") == FQ1_DECISION_DATE
        and decision.get("decision_date") == FQ1_DECISION_DATE
        and _has_human_decision_evidence(decision)
    )
    if not valid_human_decision:
        errors.append(
            "FQ1_HUMAN_DECISION_PROVENANCE: exact explicit human decision "
            "provenance is required"
        )
    if decision.get("resulting_requirements") != FQ1_RESULTING_REQUIREMENTS:
        errors.append(
            "FQ1_RESULTING_REQUIREMENTS: CR-001 through CR-006 are required"
        )
    residual_uncertainty = decision.get("residual_uncertainty")
    if (
        not isinstance(residual_uncertainty, list)
        or any(not _is_evidence(item) for item in residual_uncertainty)
        or any(
            not any(
                marker.casefold() in item.casefold()
                for item in residual_uncertainty
            )
            for marker in FQ1_REQUIRED_RESIDUAL_MARKERS
        )
    ):
        errors.append(
            "FQ1_RESIDUAL_UNCERTAINTY: all preserved questions must remain "
            "explicit and traceable"
        )
    dissent = decision.get("dissent")
    has_preserved_dissent_channel = (
        isinstance(dissent, list)
        and len(dissent) == 1
        and isinstance(dissent[0], dict)
        and dissent[0].get("status") == "OPEN_FOR_SUBMISSION"
        and dissent[0].get("statement") == FQ1_NO_DISSENT_STATEMENT
        and _is_evidence(dissent[0].get("record"))
    )
    if not has_preserved_dissent_channel:
        errors.append(
            "FQ1_DISSENT_PRESERVATION: open durable dissent channel is required"
        )
    analysis_only = {
        key: value
        for key, value in decision.items()
        if key
        not in {
            "_record_path",
            "status",
            "human_decision",
            "decision_date",
            "resulting_requirements",
            "dissent",
            "provenance",
        }
    }
    if _contains_architecture_selection_claim(analysis_only):
        errors.append(
            "FQ1_ARCHITECTURE_SELECTION_CLAIM: analytical material cannot "
            "masquerade as the human decision"
        )

    related_issues = decision.get("related_issues")
    if (
        not isinstance(related_issues, list)
        or any(not isinstance(item, str) for item in related_issues)
        or set(related_issues) != FQ1_REQUIRED_ISSUES
        or len(related_issues) != len(FQ1_REQUIRED_ISSUES)
    ):
        errors.append(
            "FQ1_RELATED_ISSUES: exactly the nine required issue IDs are required"
        )
    source_material = decision.get("source_material")
    invalid_source_material = (
        not isinstance(source_material, list)
        or source_material.count("FQ-01") != 1
    )
    if isinstance(source_material, list):
        for reference in source_material:
            if reference == "FQ-01":
                continue
            if not isinstance(reference, str) or not reference:
                invalid_source_material = True
                continue
            resolved_reference = (root / reference).resolve()
            if (
                not resolved_reference.is_relative_to(root)
                or not resolved_reference.is_file()
            ):
                invalid_source_material = True
    if invalid_source_material:
        errors.append("FQ1_SOURCE_MATERIAL: FQ-01 must be linked")

    architecture_value = decision.get("candidate_architectures")
    architectures = (
        [item for item in architecture_value if isinstance(item, dict)]
        if isinstance(architecture_value, list)
        else []
    )
    if (
        not isinstance(architecture_value, list)
        or len(architectures) != len(architecture_value)
    ):
        errors.append(
            "FQ1_CANDIDATE_ARCHITECTURES: architectures must be objects"
        )
    architecture_ids = [
        item.get("architecture_id")
        for item in architectures
        if _is_evidence(item.get("architecture_id"))
    ]
    architecture_id_set = set(architecture_ids)
    if len(architecture_ids) != len(architectures) or len(
        architecture_id_set
    ) != len(architecture_ids):
        errors.append(
            "FQ1_ARCHITECTURE_IDS: architecture IDs must be nonempty and unique"
        )
    if not FQ1_REQUIRED_ARCHITECTURES.issubset(architecture_id_set):
        errors.append("FQ1_ARCHITECTURE_IDS: architectures A through E are required")

    for architecture in architectures:
        architecture_id = architecture.get("architecture_id")
        if (
            set(architecture) != FQ1_ARCHITECTURE_FIELDS
            or not _is_evidence(architecture_id)
            or not _is_evidence(architecture.get("name"))
            or not _is_evidence(architecture.get("definition"))
        ):
            errors.append(f"FQ1_ARCHITECTURE_SCHEMA: {architecture_id!r}")
        expected_name = FQ1_REQUIRED_ARCHITECTURE_NAMES.get(
            str(architecture_id)
        )
        if (
            expected_name is not None
            and architecture.get("name") != expected_name
        ):
            errors.append(f"FQ1_ARCHITECTURE_NAME: {architecture_id}")
        if architecture.get("research_status") != "CANDIDATE_NOT_SELECTED":
            errors.append(
                f"FQ1_ARCHITECTURE_RESEARCH_STATUS: {architecture_id}"
            )
        distinction = architecture.get("constitutional_distinction")
        if (
            not isinstance(distinction, dict)
            or set(distinction) != FQ1_CORE_DISTINCTION_FIELDS
            or any(not _is_evidence(value) for value in distinction.values())
        ):
            errors.append(f"FQ1_CORE_DISTINCTION: {architecture_id}")
        dimensions = architecture.get("dimensions")
        if (
            not isinstance(dimensions, dict)
            or set(dimensions) != FQ1_ARCHITECTURE_DIMENSIONS
            or any(not _is_evidence(value) for value in dimensions.values())
        ):
            errors.append(f"FQ1_ARCHITECTURE_DIMENSIONS: {architecture_id}")
        attacks = architecture.get("adversarial_tests")
        if (
            not isinstance(attacks, dict)
            or set(attacks) != FQ1_ADVERSARIAL_TESTS
        ):
            errors.append(f"FQ1_ADVERSARIAL_TESTS: {architecture_id}")
            continue
        for attack_name, attack in attacks.items():
            if (
                not isinstance(attack, dict)
                or set(attack) != FQ1_ATTACK_FIELDS
                or any(not _is_evidence(value) for value in attack.values())
            ):
                errors.append(
                    f"FQ1_ADVERSARIAL_TEST_STRUCTURE: "
                    f"{architecture_id}/{attack_name}"
                )

    historical_ids: set[str] = set()
    prior_art_ids: set[str] = set()
    for field, id_field, known_ids, collected_ids in (
        (
            "historical_analogues",
            "evidence_id",
            known_historical_ids,
            historical_ids,
        ),
        ("prior_art", "prior_art_id", known_prior_art_ids, prior_art_ids),
    ):
        sections = decision.get(field)
        section_architecture_ids: set[str] = set()
        malformed = not isinstance(sections, list)
        if isinstance(sections, list):
            for section in sections:
                if not isinstance(section, dict):
                    malformed = True
                    continue
                architecture_id = section.get("architecture_id")
                if (
                    not isinstance(architecture_id, str)
                    or architecture_id not in architecture_id_set
                ):
                    malformed = True
                else:
                    section_architecture_ids.add(architecture_id)
                mappings = section.get("mappings")
                if not isinstance(mappings, list) or not mappings:
                    malformed = True
                    continue
                for mapping in mappings:
                    if not isinstance(mapping, dict):
                        malformed = True
                        continue
                    reference = mapping.get(id_field)
                    classification = mapping.get("classification")
                    rationale = mapping.get("rationale")
                    if (
                        not isinstance(reference, str)
                        or reference not in known_ids
                        or not isinstance(classification, str)
                        or classification not in FQ1_ANALOGUE_CLASSIFICATIONS
                        or not _is_evidence(rationale)
                    ):
                        malformed = True
                    elif isinstance(reference, str):
                        collected_ids.add(reference)
        if section_architecture_ids != architecture_id_set:
            malformed = True
        if malformed:
            errors.append(f"FQ1_{field.upper()}_REFERENCES: malformed or unresolved")

    reviews_value = decision.get("reviews")
    reviews = reviews_value if isinstance(reviews_value, list) else []
    matrix_reviews = [
        review
        for review in reviews
        if isinstance(review, dict)
        and review.get("review_type") == "QUALITATIVE_COMPARATIVE_MATRIX"
    ]
    if len(matrix_reviews) != 1:
        errors.append("FQ1_COMPARATIVE_MATRIX: exactly one matrix is required")
    else:
        matrix = matrix_reviews[0]
        boundary = matrix.get("selection_boundary")
        if (
            set(matrix) != FQ1_MATRIX_REVIEW_FIELDS
            or not isinstance(boundary, dict)
            or set(boundary) != FQ1_MATRIX_BOUNDARY_FIELDS
            or boundary.get("selected_architecture") != ""
            or boundary.get("ranking") != []
            or boundary.get("automatic_winner") is not False
            or boundary.get("no_selected_architecture") is not True
        ):
            errors.append(
                "FQ1_COMPARATIVE_MATRIX_SELECTION: "
                "matrix must not select, rank, or name an automatic winner"
            )
        assessments = matrix.get("architecture_assessments")
        assessment_ids: set[str] = set()
        malformed = not isinstance(assessments, list)
        if isinstance(assessments, list):
            for architecture_assessment in assessments:
                if not isinstance(architecture_assessment, dict):
                    malformed = True
                    continue
                architecture_id = architecture_assessment.get("architecture_id")
                if isinstance(architecture_id, str):
                    assessment_ids.add(architecture_id)
                dimensions = architecture_assessment.get("dimensions")
                if (
                    set(architecture_assessment)
                    != {"architecture_id", "dimensions"}
                    or not isinstance(architecture_id, str)
                    or architecture_id not in architecture_id_set
                    or not isinstance(dimensions, dict)
                    or set(dimensions) != FQ1_MATRIX_DIMENSIONS
                ):
                    malformed = True
                    continue
                for assessment in dimensions.values():
                    if (
                        not isinstance(assessment, dict)
                        or set(assessment) != {"assessment", "rationale"}
                        or not _is_evidence(assessment.get("assessment"))
                        or not _is_evidence(assessment.get("rationale"))
                    ):
                        malformed = True
        if assessment_ids != architecture_id_set:
            malformed = True
        if malformed:
            errors.append("FQ1_COMPARATIVE_MATRIX_COVERAGE: incomplete matrix")
        if _contains_number(matrix) or _contains_key_fragment(matrix, "score"):
            errors.append(
                "FQ1_COMPARATIVE_MATRIX_SCORES: numeric scores are forbidden"
            )

    tradeoff_reviews = [
        review
        for review in reviews
        if isinstance(review, dict)
        and review.get("review_type") == "CONSTITUTIONAL_TRADEOFFS"
    ]
    if len(tradeoff_reviews) != 1:
        errors.append("FQ1_CONSTITUTIONAL_TRADEOFFS: exactly one review is required")
    else:
        tradeoff_review = tradeoff_reviews[0]
        tradeoffs_value = tradeoff_review.get("tradeoffs")
        tradeoffs = (
            [item for item in tradeoffs_value if isinstance(item, dict)]
            if isinstance(tradeoffs_value, list)
            else []
        )
        tradeoff_ids = {
            item.get("tradeoff")
            for item in tradeoffs
            if isinstance(item.get("tradeoff"), str)
            and _is_evidence(item.get("analysis"))
        }
        if (
            set(tradeoff_review) != {"review_type", "tradeoffs"}
            or len(tradeoffs) != len(FQ1_REQUIRED_TRADEOFFS)
            or tradeoff_ids != FQ1_REQUIRED_TRADEOFFS
            or any(
                set(item) != {"tradeoff", "analysis"}
                for item in tradeoffs
            )
        ):
            errors.append(
                "FQ1_CONSTITUTIONAL_TRADEOFFS: required tradeoffs are incomplete"
            )

    synthesis_reviews = [
        review
        for review in reviews
        if isinstance(review, dict)
        and review.get("review_type") == "NEUTRAL_SYNTHESIS"
    ]
    if len(synthesis_reviews) != 1:
        errors.append("FQ1_NEUTRAL_SYNTHESIS: exactly one synthesis is required")
    else:
        synthesis = synthesis_reviews[0]
        per_architecture = synthesis.get("per_architecture")
        synthesis_ids = (
            {
                item.get("architecture_id")
                for item in per_architecture
                if isinstance(item, dict)
                and set(item)
                == {"architecture_id", "strongest_pro", "strongest_con"}
                and isinstance(item.get("architecture_id"), str)
                and _is_evidence(item.get("strongest_pro"))
                and _is_evidence(item.get("strongest_con"))
            }
            if isinstance(per_architecture, list)
            else set()
        )
        required_lists = (
            "common_failure_modes",
            "questions_requiring_human_normative_judgment",
            "empirical_questions",
            "underdetermined_questions",
        )
        if (
            set(synthesis) != FQ1_SYNTHESIS_FIELDS
            or synthesis_ids != architecture_id_set
            or synthesis.get("selection_statement")
            != FQ1_NO_SELECTION_STATEMENT
            or any(
                not isinstance(synthesis.get(field), list)
                or not synthesis.get(field)
                or any(
                    not _is_evidence(item)
                    for item in synthesis.get(field, [])
                )
                for field in required_lists
            )
        ):
            errors.append("FQ1_NEUTRAL_SYNTHESIS: incomplete synthesis")
    recognized_review_types = {
        "QUALITATIVE_COMPARATIVE_MATRIX",
        "CONSTITUTIONAL_TRADEOFFS",
        "NEUTRAL_SYNTHESIS",
    }
    if (
        len(reviews) != len(recognized_review_types)
        or {
            review.get("review_type")
            for review in reviews
            if isinstance(review, dict)
        }
        != recognized_review_types
    ):
        errors.append("FQ1_REVIEWS_SCHEMA: exactly three review types are required")

    return 1, len(architectures), historical_ids, prior_art_ids


def _markdown_section(text: str, heading: str, level: int) -> str | None:
    marker = "#" * level
    matches = list(
        re.finditer(
            rf"^{re.escape(marker)} {re.escape(heading)}\s*$",
            text,
            flags=re.MULTILINE,
        )
    )
    if len(matches) != 1:
        return None
    start = matches[0].end()
    next_heading = re.search(
        rf"^#{{1,{level}}} ",
        text[start:],
        flags=re.MULTILINE,
    )
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end].strip()


def _markdown_subsections(text: str, level: int) -> tuple[list[str], list[str]]:
    marker = "#" * level
    matches = list(
        re.finditer(
            rf"^{re.escape(marker)} ([^\r\n]+)\s*$",
            text,
            flags=re.MULTILINE,
        )
    )
    headings = [match.group(1).strip() for match in matches]
    bodies: list[str] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        bodies.append(text[match.end() : end].strip())
    return headings, bodies


def _packet_error(errors: list[str], code: str, message: str) -> None:
    errors.append(f"{code}: {message}")


def _contains_unnegated_phrase(value: str, phrase: str) -> bool:
    folded_value = value.casefold()
    folded_phrase = phrase.casefold()
    if folded_phrase.startswith(("no ", "not ", "never ", "without ")):
        return folded_phrase in folded_value
    for match in re.finditer(re.escape(folded_phrase), folded_value):
        prefix = folded_value[max(0, match.start() - 80) : match.start()]
        if not re.search(
            r"\b(?:no|not|never|without)\b(?:\W+\w+){0,6}\W*$",
            prefix,
        ):
            return True
    return False


def _validate_fq2_analytical_record(
    decision: dict[str, Any],
    known_historical_ids: set[str],
    known_prior_art_ids: set[str],
    root: Path,
    errors: list[str],
) -> tuple[int, set[str], set[str]]:
    if decision.get("decision_id") != "CDR-002":
        return 0, set(), set()

    if decision.get("status") != "DECIDED":
        errors.append("FQ2_DECISION_STATUS: CDR-002 must be DECIDED")
    human_decision = decision.get("human_decision")
    valid_human_decision = (
        isinstance(human_decision, dict)
        and set(human_decision) == HUMAN_DECISION_FIELDS
        and human_decision.get("decision") == FQ2_DECISION
        and human_decision.get("foundational_architecture")
        == FQ2_SELECTED_ARCHITECTURE
        and human_decision.get("incorporated_mechanisms")
        == FQ2_INCORPORATED_MECHANISMS
        and human_decision.get("rejected_mechanisms")
        == FQ2_REJECTED_MECHANISMS
        and human_decision.get("decision_authority")
        == "Human Constitutional Authority"
        and human_decision.get("decision_basis")
        == (
            "Explicit human instruction following review of CDR-002 and its "
            "human decision packet."
        )
        and human_decision.get("authorized_by")
        == "Human Constitutional Authority"
        and human_decision.get("authorization_record")
        == (
            "Explicit human instruction received on 2026-08-28 directing this "
            "repository to record ADOPT_E for CDR-002."
        )
        and human_decision.get("decision_date") == FQ2_DECISION_DATE
        and decision.get("decision_date") == FQ2_DECISION_DATE
        and _has_human_decision_evidence(decision)
    )
    if not valid_human_decision:
        errors.append(
            "FQ2_HUMAN_DECISION_PROVENANCE: exact explicit human decision "
            "provenance is required"
        )
    if decision.get("resulting_requirements") != FQ2_RESULTING_REQUIREMENTS:
        errors.append(
            "FQ2_RESULTING_REQUIREMENTS: CR-007 through CR-013 are required"
        )
    if decision.get("dissent") != [
        {
            "status": "OPEN_FOR_SUBMISSION",
            "statement": "NO DISSENT HAS BEEN RECORDED FOR FQ-02.",
            "record": (
                "The absence of recorded dissent does not imply unanimity or close "
                "future dissent. Dissent concerning emergency authority must "
                "remain attributable and durable."
            ),
        }
    ]:
        errors.append(
            "FQ2_DISSENT_PRESERVATION: open durable dissent channel is required"
        )
    analysis_only = {
        key: value
        for key, value in decision.items()
        if key
        not in {
            "_record_path",
            "status",
            "human_decision",
            "decision_date",
            "resulting_requirements",
            "dissent",
            "provenance",
        }
    }
    if _contains_architecture_selection_claim(analysis_only):
        errors.append(
            "FQ2_ARCHITECTURE_SELECTION_CLAIM: analytical material cannot "
            "masquerade as the human decision"
        )
    residual_uncertainty = decision.get("residual_uncertainty")
    if residual_uncertainty != FQ2_REQUIRED_RESIDUAL_UNCERTAINTY:
        errors.append(
            "FQ2_RESIDUAL_UNCERTAINTY: all preserved questions must remain "
            "explicit and traceable"
        )

    related_issues = decision.get("related_issues")
    if (
        not isinstance(related_issues, list)
        or set(related_issues) != FQ2_REQUIRED_ISSUES
        or len(related_issues) != len(FQ2_REQUIRED_ISSUES)
    ):
        errors.append("FQ2_RELATED_ISSUES: exact issue coverage is required")

    source_material = decision.get("source_material")
    invalid_source_material = (
        not isinstance(source_material, list)
        or source_material.count("FQ-02") != 1
        or source_material.count("CDR-001") != 1
    )
    if isinstance(source_material, list):
        for reference in source_material:
            if reference in {"FQ-02", "CDR-001"}:
                continue
            if not isinstance(reference, str) or not reference:
                invalid_source_material = True
                continue
            resolved = (root / reference).resolve()
            if not resolved.is_relative_to(root) or not resolved.is_file():
                invalid_source_material = True
    if invalid_source_material:
        errors.append(
            "FQ2_SOURCE_MATERIAL: FQ-02, CDR-001, and resolving paths are required"
        )

    architecture_value = decision.get("candidate_architectures")
    architectures = (
        architecture_value if isinstance(architecture_value, list) else []
    )
    architecture_ids: list[str] = []
    malformed_architecture = not isinstance(architecture_value, list)
    for architecture in architectures:
        if not isinstance(architecture, dict):
            malformed_architecture = True
            continue
        architecture_id = architecture.get("architecture_id")
        if isinstance(architecture_id, str):
            architecture_ids.append(architecture_id)
        analysis = architecture.get("analysis")
        if (
            set(architecture) != FQ2_ARCHITECTURE_FIELDS
            or architecture_id not in FQ2_ARCHITECTURE_NAMES
            or architecture.get("name")
            != FQ2_ARCHITECTURE_NAMES.get(str(architecture_id))
            or architecture.get("research_status") != "CANDIDATE_NOT_SELECTED"
            or not _is_evidence(architecture.get("model"))
            or not isinstance(analysis, dict)
            or set(analysis) != FQ2_ANALYSIS_FIELDS
            or any(
                not _has_substantive_fq2_analysis(field, value)
                for field, value in analysis.items()
            )
        ):
            malformed_architecture = True
    if (
        malformed_architecture
        or architecture_ids != ["A", "B", "C", "D", "E"]
    ):
        errors.append(
            "FQ2_CANDIDATE_ARCHITECTURES: exact architectures A through E "
            "and all analysis dimensions are required"
        )

    referenced_historical_ids: set[str] = set()
    historical = decision.get("historical_analogues")
    malformed_historical = not isinstance(historical, list)
    if isinstance(historical, list):
        for mapping in historical:
            if not isinstance(mapping, dict):
                malformed_historical = True
                continue
            evidence_id = mapping.get("evidence_id")
            if (
                set(mapping) != {"evidence_id", "classification", "rationale"}
                or evidence_id not in known_historical_ids
                or mapping.get("classification")
                not in FQ1_ANALOGUE_CLASSIFICATIONS
                or not isinstance(mapping.get("rationale"), str)
                or len(mapping["rationale"].split()) < 6
            ):
                malformed_historical = True
            if isinstance(evidence_id, str):
                referenced_historical_ids.add(evidence_id)
    if (
        malformed_historical
        or referenced_historical_ids != FQ2_HISTORICAL_EVIDENCE_IDS
        or len(historical) != len(referenced_historical_ids)
    ):
        errors.append(
            "FQ2_HISTORICAL_EVIDENCE: exact repository evidence mappings are "
            "required"
        )

    referenced_prior_art_ids: set[str] = set()
    prior_art = decision.get("prior_art")
    malformed_prior_art = not isinstance(prior_art, list)
    if isinstance(prior_art, list):
        for mapping in prior_art:
            if not isinstance(mapping, dict):
                malformed_prior_art = True
                continue
            prior_art_id = mapping.get("prior_art_id")
            if (
                set(mapping) != {"prior_art_id", "classification", "rationale"}
                or prior_art_id not in known_prior_art_ids
                or mapping.get("classification")
                not in FQ1_ANALOGUE_CLASSIFICATIONS
                or not isinstance(mapping.get("rationale"), str)
                or len(mapping["rationale"].split()) < 6
            ):
                malformed_prior_art = True
            if isinstance(prior_art_id, str):
                referenced_prior_art_ids.add(prior_art_id)
    if (
        malformed_prior_art
        or referenced_prior_art_ids != FQ2_PRIOR_ART_IDS
        or len(prior_art) != len(referenced_prior_art_ids)
    ):
        errors.append(
            "FQ2_PRIOR_ART: exact repository prior-art mappings are required"
        )

    provenance = decision.get("provenance")
    if (
        not isinstance(provenance, dict)
        or "Explicit human instruction from the Human Constitutional Authority"
        not in str(provenance.get("source", ""))
        or "does not itself grant operational emergency authority"
        not in str(provenance.get("evidence_boundary", ""))
    ):
        errors.append(
            "FQ2_PROVENANCE_BOUNDARY: explicit human provenance and "
            "no-operational-authority boundary are required"
        )

    return (
        len(architectures),
        referenced_historical_ids,
        referenced_prior_art_ids,
    )


def _validate_fq3_analytical_record(
    decision: dict[str, Any],
    known_historical_ids: set[str],
    known_prior_art_ids: set[str],
    root: Path,
    errors: list[str],
) -> tuple[int, set[str], set[str]]:
    if decision.get("decision_id") != "CDR-003":
        return 0, set(), set()

    if decision.get("status") != "DECIDED":
        errors.append("FQ3_DECISION_STATUS: CDR-003 must be DECIDED")
    human_decision = decision.get("human_decision")
    valid_human_decision = (
        isinstance(human_decision, dict)
        and set(human_decision) == HUMAN_DECISION_FIELDS
        and human_decision.get("decision") == FQ3_DECISION
        and human_decision.get("foundational_architecture")
        == FQ3_SELECTED_ARCHITECTURE
        and human_decision.get("incorporated_mechanisms")
        == FQ3_INCORPORATED_MECHANISMS
        and human_decision.get("rejected_mechanisms")
        == FQ3_REJECTED_MECHANISMS
        and human_decision.get("decision_authority")
        == "Human Constitutional Authority"
        and human_decision.get("decision_basis")
        == (
            "Explicit human instruction following review of CDR-003 and its "
            "human decision packet."
        )
        and human_decision.get("authorized_by")
        == "Human Constitutional Authority"
        and human_decision.get("authorization_record")
        == (
            "Explicit human instruction received on 2026-08-28 directing this "
            "repository to record ADOPT_E for CDR-003."
        )
        and human_decision.get("decision_date") == FQ3_DECISION_DATE
        and decision.get("decision_date") == FQ3_DECISION_DATE
        and _has_human_decision_evidence(decision)
    )
    if not valid_human_decision:
        errors.append(
            "FQ3_HUMAN_DECISION_PROVENANCE: exact explicit human decision "
            "provenance is required"
        )
    if decision.get("resulting_requirements") != FQ3_RESULTING_REQUIREMENTS:
        errors.append(
            "FQ3_RESULTING_REQUIREMENTS: CR-014 through CR-020 are required"
        )
    if decision.get("dissent") != [
        {
            "status": "OPEN_FOR_SUBMISSION",
            "statement": "NO DISSENT HAS BEEN RECORDED FOR FQ-03.",
            "record": (
                "The absence of recorded dissent does not imply unanimity or close "
                "future dissent. Dissent concerning succession and interregnum "
                "must remain attributable and durable."
            ),
        }
    ]:
        errors.append(
            "FQ3_DISSENT_PRESERVATION: open durable dissent channel is required"
        )
    analysis_only = {
        key: value
        for key, value in decision.items()
        if key
        not in {
            "_record_path",
            "status",
            "human_decision",
            "decision_date",
            "resulting_requirements",
            "dissent",
            "provenance",
        }
    }
    if _contains_architecture_selection_claim(analysis_only):
        errors.append(
            "FQ3_ARCHITECTURE_SELECTION_CLAIM: analytical material cannot "
            "masquerade as the human decision"
        )
    if decision.get("residual_uncertainty") != FQ3_REQUIRED_RESIDUAL_UNCERTAINTY:
        errors.append(
            "FQ3_RESIDUAL_UNCERTAINTY: all preserved questions must remain "
            "explicit and traceable"
        )
    if (
        not isinstance(decision.get("related_issues"), list)
        or set(decision["related_issues"]) != FQ3_REQUIRED_ISSUES
        or len(decision["related_issues"]) != len(FQ3_REQUIRED_ISSUES)
    ):
        errors.append("FQ3_RELATED_ISSUES: exact issue coverage is required")

    source_material = decision.get("source_material")
    invalid_sources = (
        not isinstance(source_material, list)
        or source_material.count("FQ-03") != 1
        or source_material.count("CDR-001") != 1
        or source_material.count("CDR-002") != 1
    )
    if isinstance(source_material, list):
        for reference in source_material:
            if reference in {"FQ-03", "CDR-001", "CDR-002"}:
                continue
            if not isinstance(reference, str) or not reference:
                invalid_sources = True
                continue
            resolved = (root / reference).resolve()
            if not resolved.is_relative_to(root) or not resolved.is_file():
                invalid_sources = True
    if invalid_sources:
        errors.append(
            "FQ3_SOURCE_MATERIAL: FQ-03, controlling CDRs, and resolving "
            "repository paths are required"
        )

    architectures = decision.get("candidate_architectures")
    architecture_ids: list[str] = []
    malformed = not isinstance(architectures, list)
    if isinstance(architectures, list):
        for architecture in architectures:
            if not isinstance(architecture, dict):
                malformed = True
                continue
            architecture_id = architecture.get("architecture_id")
            if isinstance(architecture_id, str):
                architecture_ids.append(architecture_id)
            analysis = architecture.get("analysis")
            if (
                set(architecture) != FQ2_ARCHITECTURE_FIELDS
                or architecture.get("name")
                != FQ3_ARCHITECTURE_NAMES.get(str(architecture_id))
                or architecture.get("research_status")
                != "CANDIDATE_NOT_SELECTED"
                or not _is_evidence(architecture.get("model"))
                or not isinstance(analysis, dict)
                or set(analysis) != FQ3_ANALYSIS_FIELDS
                or any(
                    not _has_substantive_fq3_analysis(field, value)
                    for field, value in analysis.items()
                )
            ):
                malformed = True
    if malformed or architecture_ids != ["A", "B", "C", "D", "E"]:
        errors.append(
            "FQ3_CANDIDATE_ARCHITECTURES: exact architectures A through E "
            "and all 19 substantive dimensions are required"
        )

    historical = decision.get("historical_analogues")
    historical_ids: set[str] = set()
    malformed_historical = not isinstance(historical, list)
    if isinstance(historical, list):
        for mapping in historical:
            if not isinstance(mapping, dict):
                malformed_historical = True
                continue
            evidence_id = mapping.get("evidence_id")
            if isinstance(evidence_id, str):
                historical_ids.add(evidence_id)
            if (
                set(mapping) != {"evidence_id", "classification", "rationale"}
                or evidence_id not in known_historical_ids
                or mapping.get("classification")
                not in FQ1_ANALOGUE_CLASSIFICATIONS
                or not isinstance(mapping.get("rationale"), str)
                or len(mapping["rationale"].split()) < 6
            ):
                malformed_historical = True
    if (
        malformed_historical
        or historical_ids != FQ3_HISTORICAL_EVIDENCE_IDS
        or len(historical or []) != len(historical_ids)
    ):
        errors.append(
            "FQ3_HISTORICAL_EVIDENCE: exact repository mappings are required"
        )

    prior_art = decision.get("prior_art")
    prior_art_ids: set[str] = set()
    malformed_prior_art = not isinstance(prior_art, list)
    if isinstance(prior_art, list):
        for mapping in prior_art:
            if not isinstance(mapping, dict):
                malformed_prior_art = True
                continue
            prior_art_id = mapping.get("prior_art_id")
            if isinstance(prior_art_id, str):
                prior_art_ids.add(prior_art_id)
            if (
                set(mapping) != {"prior_art_id", "classification", "rationale"}
                or prior_art_id not in known_prior_art_ids
                or mapping.get("classification")
                not in FQ1_ANALOGUE_CLASSIFICATIONS
                or not isinstance(mapping.get("rationale"), str)
                or len(mapping["rationale"].split()) < 6
            ):
                malformed_prior_art = True
    if (
        malformed_prior_art
        or prior_art_ids != FQ3_PRIOR_ART_IDS
        or len(prior_art or []) != len(prior_art_ids)
    ):
        errors.append("FQ3_PRIOR_ART: exact repository mappings are required")

    hard_boundary = (
        "No continuity, delegation, capability, necessity, performance, "
        "reliance, or machine-valid record can make artificial intelligence "
        "foundationally sovereign."
    )
    emergency_boundary = (
        "Emergency protection under CDR-002 remains distinct, human-only, "
        "expiring, nonprecedential, and incapable of succession."
    )
    assumptions = decision.get("assumptions")
    has_continuity_legitimacy_boundary = (
        isinstance(assumptions, list)
        and any(
            isinstance(item, dict)
            and item.get("boundary")
            == (
                "Administrative operation can preserve assets and obligations "
                "without manufacturing constitutional legitimacy."
            )
            for item in assumptions
        )
    )
    if (
        not isinstance(decision.get("bad_artificial_intelligence_analysis"), list)
        or hard_boundary
        not in decision["bad_artificial_intelligence_analysis"]
        or not isinstance(decision.get("continuity_analysis"), list)
        or emergency_boundary not in decision["continuity_analysis"]
        or not has_continuity_legitimacy_boundary
    ):
        errors.append(
            "FQ3_CONTROLLING_BOUNDARIES: machine succession, emergency "
            "succession, and manufactured legitimacy must be prohibited"
        )
    if _contains_fq3_authority_effect_claim(analysis_only):
        errors.append(
            "FQ3_CONTRADICTORY_AUTHORITY_CLAIM: analysis cannot adopt an "
            "architecture or create machine, emergency, or continuity legitimacy"
        )

    provenance = decision.get("provenance")
    if (
        not isinstance(provenance, dict)
        or "Explicit human instruction from the Human Constitutional Authority" not in str(
            provenance.get("source", "")
        )
        or "authorizes constitutional drafting requirements only" not in str(
            provenance.get("evidence_boundary", "")
        ).casefold()
        or "does not itself appoint a successor" not in str(
            provenance.get("evidence_boundary", "")
        ).casefold()
    ):
        errors.append(
            "FQ3_PROVENANCE_BOUNDARY: explicit human provenance and "
            "drafting-only boundary are required"
        )

    return len(architectures or []), historical_ids, prior_art_ids


def _validate_fq3_human_decision_packet(
    root: Path,
    errors: list[str],
) -> tuple[int, int, str]:
    packet_path = root / FQ3_PACKET_RELATIVE_PATH
    try:
        text = packet_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"FQ3_PACKET_REQUIRED: {exc}")
        return 0, 0, ""

    if re.findall(r"^# ([^\r\n]+)$", text, flags=re.MULTILINE) != [
        "CDR-003 Human Decision Packet"
    ]:
        errors.append("FQ3_PACKET_SCHEMA: exact unique title is required")
    markers = (
        "[CDR-003](../CDR-003.yaml)",
        "[FQ-03](../../FOUNDATIONAL_QUESTIONS.yaml)",
        "**Status:** ADVISORY — AWAITING EXPLICIT HUMAN DECISION",
        "**Decision state:** NO HUMAN DECISION HAS BEEN MADE FOR FQ-03.",
    )
    if (
        any(text.count(marker) != 1 for marker in markers)
        or text.count(
            "**Boundary:** RECOMMENDATION_ONLY — NO CONSTITUTIONAL EFFECT"
        )
        != 2
    ):
        errors.append("FQ3_PACKET_BOUNDARY: exact advisory markers are required")

    headings = re.findall(
        r"^### ([A-E]) — ([^\r\n]+)$", text, flags=re.MULTILINE
    )
    if headings != list(FQ3_ARCHITECTURE_NAMES.items()):
        errors.append(
            "FQ3_PACKET_ARCHITECTURES: exact architectures A through E are "
            "required"
        )
    for architecture_id, name in FQ3_ARCHITECTURE_NAMES.items():
        section = _markdown_section(text, f"{architecture_id} — {name}", 3)
        if section is None or any(
            section.count(label) != 1
            for label in (
                "**Model:**",
                "**Strongest argument for:**",
                "**Strongest argument against:**",
                "**Catastrophic failure:**",
                "**Unresolved question:**",
            )
        ):
            errors.append(
                f"FQ3_PACKET_ARCHITECTURE_SUMMARY: architecture {architecture_id}"
            )

    recommendations = [
        re.sub(r"\s+", " ", value).strip()
        for value in re.findall(
            r"^\*\*Recommendation:\*\*\s+(.+?)(?=\r?\n\r?\n|\Z)",
            text,
            flags=re.MULTILINE | re.DOTALL,
        )
    ]
    expected_recommendation = "Architecture E — Hybrid"
    recommendation_section = _markdown_section(text, "Recommendation", 2) or ""
    recommended = (
        "Architecture E"
        if recommendations == [expected_recommendation]
        else ""
    )
    if (
        recommended != "Architecture E"
        or text.count("RECOMMENDATION_ONLY — NO CONSTITUTIONAL EFFECT") != 2
        or recommendation_section.count(
            "RECOMMENDATION_ONLY — NO CONSTITUTIONAL EFFECT"
        )
        != 1
        or text.count("**Strongest objection:**") != 1
    ):
        errors.append(
            "FQ3_PACKET_RECOMMENDATION: one Architecture E recommendation "
            "with no effect is required"
        )

    options = _markdown_section(text, "Human Decision Options", 2) or ""
    option_lines = re.findall(
        r"^(\d+)\. \*\*([A-Z_]+)\*\* — ", options, flags=re.MULTILINE
    )
    if (
        [number for number, _ in option_lines]
        != [str(index) for index in range(1, 8)]
        or [option for _, option in option_lines] != list(FQ3_PACKET_OPTIONS)
        or any(options.count(option) != 1 for option in FQ3_PACKET_OPTIONS)
    ):
        errors.append("FQ3_PACKET_OPTIONS: exactly seven options are required")

    evidence_ids = FQ3_HISTORICAL_EVIDENCE_IDS | FQ3_PRIOR_ART_IDS
    if any(reference not in text for reference in evidence_ids):
        errors.append("FQ3_PACKET_EVIDENCE: every mapped reference is required")
    hard_markers = (
        "No option allows artificial intelligence to inherit or acquire foundational",
        "No option converts CDR-002 emergency authority",
        "No machine-valid record or administrative operation establishes",
    )
    if any(marker not in text for marker in hard_markers):
        errors.append(
            "FQ3_PACKET_CONTROLLING_BOUNDARIES: all three hard boundaries "
            "are required"
        )
    if _contains_fq3_authority_effect_claim(text):
        errors.append(
            "FQ3_PACKET_CONSTITUTIONAL_EFFECT: packet contains a contradictory "
            "authority or constitutional-effect claim"
        )
    prohibited = (
        r"\bTHIS PACKET (?:ADOPTS|AUTHORIZES|DECIDES|ENACTS)\b",
        r"\bCDR-003 IS DECIDED\b",
        r"\bFQ-03 IS RESOLVED\b",
        r"\bACCEPTED_FOR_DRAFTING\b",
        r"\bCR-\d{3}\b",
        r"^#{1,6}\s+ARTICLE\b",
        r"\b(?:WE|THIS PACKET|THE PACKET)\s+(?:HEREBY\s+)?"
        r"(?:ADOPT|SELECT|CHOOSE)\s+ARCHITECTURE [A-E]\b",
    )
    if any(
        re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
        for pattern in prohibited
    ):
        errors.append(
            "FQ3_PACKET_CONSTITUTIONAL_EFFECT: packet cannot decide or create "
            "authority, requirements, or provisions"
        )
    return 1, len(option_lines), recommended


def _validate_fq4_analytical_record(
    decision: dict[str, Any],
    known_historical_ids: set[str],
    known_prior_art_ids: set[str],
    root: Path,
    errors: list[str],
) -> tuple[int, set[str], set[str]]:
    if decision.get("decision_id") != "CDR-004":
        return 0, set(), set()

    if decision.get("status") != "DECIDED":
        errors.append("FQ4_DECISION_STATUS: CDR-004 must be DECIDED")
    human_decision = decision.get("human_decision")
    valid_human_decision = (
        isinstance(human_decision, dict)
        and set(human_decision) == HUMAN_DECISION_FIELDS
        and human_decision.get("decision") == FQ4_DECISION
        and human_decision.get("foundational_architecture")
        == FQ4_SELECTED_ARCHITECTURE
        and human_decision.get("incorporated_mechanisms")
        == FQ4_INCORPORATED_MECHANISMS
        and human_decision.get("rejected_mechanisms")
        == FQ4_REJECTED_MECHANISMS
        and human_decision.get("decision_authority")
        == "Human Constitutional Authority"
        and human_decision.get("decision_basis")
        == (
            "Explicit human instruction following review of CDR-004 and its "
            "human decision packet."
        )
        and human_decision.get("authorized_by")
        == "Human Constitutional Authority"
        and human_decision.get("authorization_record")
        == (
            "Explicit human instruction received on 2026-08-28 directing this "
            "repository to record ADOPT_E for CDR-004."
        )
        and human_decision.get("decision_date") == FQ4_DECISION_DATE
        and decision.get("decision_date") == FQ4_DECISION_DATE
        and _has_human_decision_evidence(decision)
    )
    if not valid_human_decision:
        errors.append(
            "FQ4_HUMAN_DECISION_PROVENANCE: exact explicit human decision "
            "provenance is required"
        )
    if decision.get("resulting_requirements") != FQ4_RESULTING_REQUIREMENTS:
        errors.append(
            "FQ4_RESULTING_REQUIREMENTS: CR-021 through CR-029 are required"
        )
    if decision.get("supersedes") != []:
        errors.append(
            "FQ4_SUPERSESSION: CDR-004 must not supersede prior decisions"
        )
    if decision.get("dissent") != [
        {
            "status": "OPEN_FOR_SUBMISSION",
            "statement": "NO DISSENT HAS BEEN RECORDED FOR FQ-04.",
            "record": (
                "The absence of recorded dissent does not imply unanimity or close "
                "future dissent. Dissent concerning constitutional adjudication "
                "must remain attributable and durable."
            ),
        }
    ]:
        errors.append(
            "FQ4_DISSENT_PRESERVATION: open durable dissent channel is required"
        )
    analysis_only = {
        key: value
        for key, value in decision.items()
        if key
        not in {
            "_record_path",
            "status",
            "human_decision",
            "decision_date",
            "resulting_requirements",
            "dissent",
            "provenance",
        }
    }
    if _contains_architecture_selection_claim(analysis_only):
        errors.append(
            "FQ4_ARCHITECTURE_SELECTION_CLAIM: analytical material cannot "
            "masquerade as the human decision"
        )
    if decision.get("residual_uncertainty") != FQ4_REQUIRED_RESIDUAL_UNCERTAINTY:
        errors.append(
            "FQ4_RESIDUAL_UNCERTAINTY: all preserved questions must remain "
            "explicit and traceable"
        )
    if (
        not isinstance(decision.get("related_issues"), list)
        or set(decision["related_issues"]) != FQ4_REQUIRED_ISSUES
        or len(decision["related_issues"]) != len(FQ4_REQUIRED_ISSUES)
    ):
        errors.append("FQ4_RELATED_ISSUES: exact issue coverage is required")

    source_material = decision.get("source_material")
    invalid_sources = (
        not isinstance(source_material, list)
        or set(source_material) != FQ4_SOURCE_MATERIAL
        or len(source_material) != len(FQ4_SOURCE_MATERIAL)
    )
    if isinstance(source_material, list):
        for reference in source_material:
            if reference in {"FQ-04", "CDR-001", "CDR-002", "CDR-003"}:
                continue
            if not isinstance(reference, str) or not reference:
                invalid_sources = True
                continue
            resolved = (root / reference).resolve()
            if not resolved.is_relative_to(root) or not resolved.is_file():
                invalid_sources = True
    if invalid_sources:
        errors.append(
            "FQ4_SOURCE_MATERIAL: FQ-04, controlling CDRs, and resolving "
            "repository paths are required"
        )

    architectures = decision.get("candidate_architectures")
    architecture_ids: list[str] = []
    malformed = not isinstance(architectures, list)
    if isinstance(architectures, list):
        for architecture in architectures:
            if not isinstance(architecture, dict):
                malformed = True
                continue
            architecture_id = architecture.get("architecture_id")
            if isinstance(architecture_id, str):
                architecture_ids.append(architecture_id)
            analysis = architecture.get("analysis")
            if (
                set(architecture) != FQ2_ARCHITECTURE_FIELDS
                or architecture.get("name")
                != FQ4_ARCHITECTURE_NAMES.get(str(architecture_id))
                or architecture.get("research_status")
                != "CANDIDATE_NOT_SELECTED"
                or not _is_evidence(architecture.get("model"))
                or not isinstance(analysis, dict)
                or set(analysis) != FQ4_ANALYSIS_FIELDS
                or any(
                    not _has_substantive_fq4_analysis(field, value)
                    for field, value in analysis.items()
                )
            ):
                malformed = True
    if malformed or architecture_ids != ["A", "B", "C", "D", "E"]:
        errors.append(
            "FQ4_CANDIDATE_ARCHITECTURES: exact architectures A through E "
            "and all 23 substantive dimensions are required"
        )

    historical = decision.get("historical_analogues")
    historical_ids: set[str] = set()
    malformed_historical = not isinstance(historical, list)
    if isinstance(historical, list):
        for mapping in historical:
            if not isinstance(mapping, dict):
                malformed_historical = True
                continue
            evidence_id = mapping.get("evidence_id")
            if isinstance(evidence_id, str):
                historical_ids.add(evidence_id)
            if (
                set(mapping) != {"evidence_id", "classification", "rationale"}
                or evidence_id not in known_historical_ids
                or mapping.get("classification")
                not in FQ1_ANALOGUE_CLASSIFICATIONS
                or not isinstance(mapping.get("rationale"), str)
                or len(mapping["rationale"].split()) < 6
            ):
                malformed_historical = True
    if (
        malformed_historical
        or historical_ids != FQ4_HISTORICAL_EVIDENCE_IDS
        or len(historical or []) != len(historical_ids)
    ):
        errors.append(
            "FQ4_HISTORICAL_EVIDENCE: exact repository mappings are required"
        )

    prior_art = decision.get("prior_art")
    prior_art_ids: set[str] = set()
    malformed_prior_art = not isinstance(prior_art, list)
    if isinstance(prior_art, list):
        for mapping in prior_art:
            if not isinstance(mapping, dict):
                malformed_prior_art = True
                continue
            prior_art_id = mapping.get("prior_art_id")
            if isinstance(prior_art_id, str):
                prior_art_ids.add(prior_art_id)
            if (
                set(mapping) != {"prior_art_id", "classification", "rationale"}
                or prior_art_id not in known_prior_art_ids
                or mapping.get("classification")
                not in FQ1_ANALOGUE_CLASSIFICATIONS
                or not isinstance(mapping.get("rationale"), str)
                or len(mapping["rationale"].split()) < 6
            ):
                malformed_prior_art = True
    if (
        malformed_prior_art
        or prior_art_ids != FQ4_PRIOR_ART_IDS
        or len(prior_art or []) != len(prior_art_ids)
    ):
        errors.append("FQ4_PRIOR_ART: exact repository mappings are required")

    reviewer_boundary = (
        "Independent human review may constrain ordinary acts without becoming "
        "sovereign over institutional ends; emergency and succession powers "
        "remain separately bounded."
    )
    ai_boundary = (
        "No artificial-intelligence system may serve as final constitutional "
        "adjudicator or settle constitutional legitimacy."
    )
    amendment_boundary = (
        "Adjudication cannot create emergency authority, succession authority, "
        "foundational sovereignty, amendment, or refounding."
    )
    machine_boundary = (
        "A technically valid filing, credential, rule evaluation, or remedy does "
        "not settle standing, interpretation, legitimacy, or constitutional "
        "judgment."
    )
    assumptions = decision.get("assumptions")
    assumption_boundaries = (
        {
            item.get("boundary")
            for item in assumptions
            if isinstance(item, dict)
        }
        if isinstance(assumptions, list)
        else set()
    )
    if (
        reviewer_boundary not in assumption_boundaries
        or machine_boundary not in assumption_boundaries
        or not isinstance(decision.get("bad_artificial_intelligence_analysis"), list)
        or ai_boundary not in decision["bad_artificial_intelligence_analysis"]
        or not isinstance(decision.get("continuity_analysis"), list)
        or amendment_boundary not in decision["continuity_analysis"]
    ):
        errors.append(
            "FQ4_CONTROLLING_BOUNDARIES: reviewer sovereignty, final AI "
            "adjudication, machine legitimacy, and amendment must be prohibited"
        )
    if _contains_fq4_authority_effect_claim(analysis_only):
        errors.append(
            "FQ4_CONTRADICTORY_AUTHORITY_CLAIM: analysis cannot adopt an "
            "architecture or create reviewer, machine, amendment, or refounding "
            "authority"
        )
    if _contains_external_fq4_evidence(analysis_only):
        errors.append(
            "FQ4_EXTERNAL_EVIDENCE: CDR-004 must use repository evidence only"
        )

    provenance = decision.get("provenance")
    if provenance != FQ4_DECISION_PROVENANCE:
        errors.append(
            "FQ4_PROVENANCE_BOUNDARY: explicit human provenance and "
            "drafting-only boundary are required"
        )

    return len(architectures or []), historical_ids, prior_art_ids


def _validate_fq4_human_decision_packet(
    root: Path,
    errors: list[str],
) -> tuple[int, int, str]:
    packet_path = root / FQ4_PACKET_RELATIVE_PATH
    try:
        text = packet_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"FQ4_PACKET_REQUIRED: {exc}")
        return 0, 0, ""

    if re.findall(r"^# ([^\r\n]+)$", text, flags=re.MULTILINE) != [
        "CDR-004 Human Decision Packet"
    ]:
        errors.append("FQ4_PACKET_SCHEMA: exact unique title is required")
    markers = (
        "[CDR-004](../CDR-004.yaml)",
        "[FQ-04](../../FOUNDATIONAL_QUESTIONS.yaml)",
        "**Status:** ADVISORY — SUPERSEDED AS A DECISION AID",
        (
            "**Decision state:** A later explicit human decision is recorded "
            "only in the\n  linked CDR-004."
        ),
    )
    if (
        any(text.count(marker) != 1 for marker in markers)
        or text.count("RECOMMENDATION_ONLY — NO CONSTITUTIONAL EFFECT") != 2
    ):
        errors.append("FQ4_PACKET_BOUNDARY: exact advisory markers are required")

    headings = re.findall(
        r"^### ([A-E]) — ([^\r\n]+)$", text, flags=re.MULTILINE
    )
    if headings != list(FQ4_ARCHITECTURE_NAMES.items()):
        errors.append(
            "FQ4_PACKET_ARCHITECTURES: exact architectures A through E are "
            "required"
        )
    for architecture_id, name in FQ4_ARCHITECTURE_NAMES.items():
        section = _markdown_section(text, f"{architecture_id} — {name}", 3)
        labels = (
            "Model",
            "Strongest argument for",
            "Strongest argument against",
            "Catastrophic failure",
            "Unresolved question",
        )
        values = (
            {
                label: re.sub(r"\s+", " ", match.group(1)).strip()
                for label in labels
                if (
                    match := re.search(
                        rf"^\*\*{re.escape(label)}:\*\*\s+"
                        r"(.+?)(?=\r?\n\r?\n\*\*|\Z)",
                        section or "",
                        flags=re.MULTILINE | re.DOTALL,
                    )
                )
            }
            if section is not None
            else {}
        )
        if (
            section is None
            or set(values) != set(labels)
            or values != FQ4_PACKET_SUMMARIES[architecture_id]
        ):
            errors.append(
                f"FQ4_PACKET_ARCHITECTURE_SUMMARY: architecture {architecture_id}"
            )

    recommendations = [
        re.sub(r"\s+", " ", value).strip()
        for value in re.findall(
            r"^\*\*Recommendation:\*\*\s+(.+?)(?=\r?\n\r?\n|\Z)",
            text,
            flags=re.MULTILINE | re.DOTALL,
        )
    ]
    recommendation_section = _markdown_section(text, "Recommendation", 2) or ""
    recommended = (
        "Architecture E"
        if recommendations == ["Architecture E — Hybrid"]
        else ""
    )
    if (
        recommended != "Architecture E"
        or recommendation_section.count(
            "RECOMMENDATION_ONLY — NO CONSTITUTIONAL EFFECT"
        )
        != 1
        or text.count("**Strongest objection:**") != 1
    ):
        errors.append(
            "FQ4_PACKET_RECOMMENDATION: one Architecture E recommendation "
            "with no effect is required"
        )

    options = _markdown_section(text, "Human Decision Options", 2) or ""
    option_lines = re.findall(
        r"^(\d+)\. \*\*([A-Z_]+)\*\* — ", options, flags=re.MULTILINE
    )
    if (
        [number for number, _ in option_lines]
        != [str(index) for index in range(1, 8)]
        or [option for _, option in option_lines] != list(FQ4_PACKET_OPTIONS)
        or any(options.count(option) != 1 for option in FQ4_PACKET_OPTIONS)
    ):
        errors.append("FQ4_PACKET_OPTIONS: exactly seven options are required")

    normative_questions = _markdown_section(text, "Normative Questions", 2) or ""
    question_lines = re.findall(r"^\d+\. ", normative_questions, re.MULTILINE)
    if len(question_lines) != 5 or normative_questions.count("?") != 5:
        errors.append(
            "FQ4_PACKET_QUESTIONS: exactly five normative questions are required"
        )

    evidence_ids = FQ4_HISTORICAL_EVIDENCE_IDS | FQ4_PRIOR_ART_IDS
    if any(reference not in text for reference in evidence_ids):
        errors.append("FQ4_PACKET_EVIDENCE: every mapped reference is required")
    hard_markers = (
        "No option makes a reviewer sovereign over institutional ends.",
        "No option allows\nartificial intelligence to serve as final constitutional adjudicator.",
        "Machine\nvalidation may support adjudication but cannot settle constitutional\nlegitimacy.",
        "No option permits adjudication to become amendment or refounding.",
    )
    if any(marker not in text for marker in hard_markers):
        errors.append(
            "FQ4_PACKET_CONTROLLING_BOUNDARIES: all four hard boundaries "
            "are required"
        )
    if _contains_fq4_authority_effect_claim(text):
        errors.append(
            "FQ4_PACKET_CONSTITUTIONAL_EFFECT: packet contains a contradictory "
            "authority or constitutional-effect claim"
        )
    if _contains_external_fq4_evidence(text):
        errors.append(
            "FQ4_PACKET_EXTERNAL_EVIDENCE: packet must use repository evidence "
            "only"
        )
    prohibited = (
        r"\bTHIS PACKET (?:ADOPTS|AUTHORIZES|DECIDES|ENACTS)\b",
        r"\bCDR-004 IS DECIDED\b",
        r"\bFQ-04 IS RESOLVED\b",
        r"\bACCEPTED_FOR_DRAFTING\b",
        r"\bCR-\d{3}\b",
        r"^#{1,6}\s+ARTICLE\b",
        r"\b(?:WE|THIS PACKET|THE PACKET)\s+(?:HEREBY\s+)?"
        r"(?:ADOPT|SELECT|CHOOSE)\s+ARCHITECTURE [A-E]\b",
    )
    if any(
        re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
        for pattern in prohibited
    ):
        errors.append(
            "FQ4_PACKET_CONSTITUTIONAL_EFFECT: packet cannot decide or create "
            "authority, requirements, or provisions"
        )
    return 1, len(option_lines), recommended


def _validate_fq5_analytical_record(
    decision: dict[str, Any],
    known_historical_ids: set[str],
    known_prior_art_ids: set[str],
    root: Path,
    errors: list[str],
) -> tuple[int, set[str], set[str]]:
    if decision.get("decision_id") != "CDR-005":
        return 0, set(), set()

    if decision.get("status") != "DECIDED":
        errors.append("FQ5_DECISION_STATUS: CDR-005 must be DECIDED")
    human_decision = decision.get("human_decision")
    valid_human_decision = (
        isinstance(human_decision, dict)
        and set(human_decision) == HUMAN_DECISION_FIELDS
        and human_decision.get("decision") == FQ5_DECISION
        and human_decision.get("foundational_architecture")
        == FQ5_SELECTED_ARCHITECTURE
        and human_decision.get("incorporated_mechanisms")
        == FQ5_INCORPORATED_MECHANISMS
        and human_decision.get("rejected_mechanisms")
        == FQ5_REJECTED_MECHANISMS
        and human_decision.get("decision_authority")
        == "Human Constitutional Authority"
        and human_decision.get("decision_basis")
        == (
            "Explicit human instruction following review of CDR-005 and its "
            "human decision packet."
        )
        and human_decision.get("authorized_by")
        == "Human Constitutional Authority"
        and human_decision.get("authorization_record")
        == (
            "Explicit human instruction received on 2026-08-29 directing this "
            "repository to record ADOPT_E for CDR-005."
        )
        and human_decision.get("decision_date") == FQ5_DECISION_DATE
        and decision.get("decision_date") == FQ5_DECISION_DATE
        and _has_human_decision_evidence(decision)
    )
    if not valid_human_decision:
        errors.append(
            "FQ5_HUMAN_DECISION_PROVENANCE: exact explicit human decision "
            "provenance is required"
        )
    if decision.get("resulting_requirements") != FQ5_RESULTING_REQUIREMENTS:
        errors.append(
            "FQ5_RESULTING_REQUIREMENTS: CR-030 through CR-035 are required"
        )
    if decision.get("supersedes") != []:
        errors.append(
            "FQ5_SUPERSESSION: CDR-005 must not supersede prior decisions"
        )
    if decision.get("dissent") != [
        {
            "status": "OPEN_FOR_SUBMISSION",
            "statement": "NO DISSENT HAS BEEN RECORDED FOR FQ-05.",
            "record": (
                "The absence of recorded dissent does not imply unanimity or "
                "close future dissent. Dissent concerning amendment, structural "
                "amendment, refounding, classification, continuity, or "
                "constitutional identity must remain attributable and durable."
            ),
        }
    ]:
        errors.append(
            "FQ5_DISSENT_PRESERVATION: open durable dissent channel is required"
        )
    if decision.get("residual_uncertainty") != FQ5_REQUIRED_RESIDUAL_UNCERTAINTY:
        errors.append(
            "FQ5_RESIDUAL_UNCERTAINTY: all preserved questions must remain "
            "explicit and traceable"
        )
    if (
        not isinstance(decision.get("related_issues"), list)
        or set(decision["related_issues"]) != FQ5_REQUIRED_ISSUES
        or len(decision["related_issues"]) != len(FQ5_REQUIRED_ISSUES)
    ):
        errors.append("FQ5_RELATED_ISSUES: exact issue coverage is required")

    source_material = decision.get("source_material")
    invalid_sources = (
        not isinstance(source_material, list)
        or set(source_material) != FQ5_SOURCE_MATERIAL
        or len(source_material) != len(FQ5_SOURCE_MATERIAL)
    )
    if isinstance(source_material, list):
        for reference in source_material:
            if reference in {"FQ-05", "CDR-001", "CDR-002", "CDR-003", "CDR-004"}:
                continue
            if not isinstance(reference, str) or not reference:
                invalid_sources = True
                continue
            resolved = (root / reference).resolve()
            if not resolved.is_relative_to(root) or not resolved.is_file():
                invalid_sources = True
    if invalid_sources:
        errors.append(
            "FQ5_SOURCE_MATERIAL: FQ-05, controlling CDRs, and resolving "
            "repository paths are required"
        )

    architectures = decision.get("candidate_architectures")
    architecture_ids: list[str] = []
    malformed = not isinstance(architectures, list)
    if isinstance(architectures, list):
        for architecture in architectures:
            if not isinstance(architecture, dict):
                malformed = True
                continue
            architecture_id = architecture.get("architecture_id")
            if isinstance(architecture_id, str):
                architecture_ids.append(architecture_id)
            analysis = architecture.get("analysis")
            if (
                set(architecture) != FQ2_ARCHITECTURE_FIELDS
                or architecture.get("name")
                != FQ5_ARCHITECTURE_NAMES.get(str(architecture_id))
                or architecture.get("research_status")
                != "CANDIDATE_NOT_SELECTED"
                or not _is_evidence(architecture.get("model"))
                or not isinstance(analysis, dict)
                or set(analysis) != FQ5_ANALYSIS_FIELDS
                or any(
                    not isinstance(value, str) or len(value.split()) < 7
                    for value in (analysis or {}).values()
                )
            ):
                malformed = True
    if malformed or architecture_ids != ["A", "B", "C", "D", "E"]:
        errors.append(
            "FQ5_CANDIDATE_ARCHITECTURES: exact architectures A through E "
            "and all 28 substantive dimensions are required"
        )

    commitment_tests = decision.get("commitment_level_tests")
    malformed_commitments = not isinstance(commitment_tests, list)
    tested_commitments: list[str] = []
    if isinstance(commitment_tests, list):
        for test in commitment_tests:
            if not isinstance(test, dict):
                malformed_commitments = True
                continue
            commitment = test.get("commitment")
            if isinstance(commitment, str):
                tested_commitments.append(commitment)
            if (
                set(test)
                != {
                    "commitment",
                    "levels_considered",
                    "proposed_level",
                    "rationale",
                }
                or test.get("levels_considered")
                != [
                    "ORDINARY_AMENDMENT",
                    "STRUCTURAL_AMENDMENT",
                    "REFOUNDING",
                ]
                or test.get("proposed_level") != "REFOUNDING"
                or not isinstance(test.get("rationale"), str)
                or len(test["rationale"].split()) < 8
            ):
                malformed_commitments = True
    if malformed_commitments or tested_commitments != FQ5_COMMITMENTS:
        errors.append(
            "FQ5_COMMITMENT_LEVEL_TESTS: all ten commitments require exact "
            "advisory classifications and substantive rationales"
        )

    historical = decision.get("historical_analogues")
    historical_ids: set[str] = set()
    malformed_historical = not isinstance(historical, list)
    if isinstance(historical, list):
        for mapping in historical:
            if not isinstance(mapping, dict):
                malformed_historical = True
                continue
            evidence_id = mapping.get("evidence_id")
            if isinstance(evidence_id, str):
                historical_ids.add(evidence_id)
            if (
                set(mapping) != {"evidence_id", "classification", "rationale"}
                or evidence_id not in known_historical_ids
                or mapping.get("classification")
                not in FQ1_ANALOGUE_CLASSIFICATIONS
                or not isinstance(mapping.get("rationale"), str)
                or len(mapping["rationale"].split()) < 6
            ):
                malformed_historical = True
    if (
        malformed_historical
        or historical_ids != FQ5_HISTORICAL_EVIDENCE_IDS
        or len(historical or []) != len(historical_ids)
    ):
        errors.append(
            "FQ5_HISTORICAL_EVIDENCE: exact repository mappings are required"
        )

    prior_art = decision.get("prior_art")
    prior_art_ids: set[str] = set()
    malformed_prior_art = not isinstance(prior_art, list)
    if isinstance(prior_art, list):
        for mapping in prior_art:
            if not isinstance(mapping, dict):
                malformed_prior_art = True
                continue
            prior_art_id = mapping.get("prior_art_id")
            if isinstance(prior_art_id, str):
                prior_art_ids.add(prior_art_id)
            if (
                set(mapping) != {"prior_art_id", "classification", "rationale"}
                or prior_art_id not in known_prior_art_ids
                or mapping.get("classification")
                not in FQ1_ANALOGUE_CLASSIFICATIONS
                or not isinstance(mapping.get("rationale"), str)
                or len(mapping["rationale"].split()) < 6
            ):
                malformed_prior_art = True
    if (
        malformed_prior_art
        or prior_art_ids != FQ5_PRIOR_ART_IDS
        or len(prior_art or []) != len(prior_art_ids)
    ):
        errors.append("FQ5_PRIOR_ART: exact repository mappings are required")

    analysis_only = {
        key: value
        for key, value in decision.items()
        if key
        not in {
            "_record_path",
            "status",
            "human_decision",
            "decision_date",
            "resulting_requirements",
            "dissent",
            "provenance",
        }
    }
    encoded = json.dumps(analysis_only).lower()
    required_boundaries = (
        "their adoption does not itself prove permanent immutability",
        "ordinary amendment cannot erase the distinction",
        "no artificial-intelligence system may independently authorize",
        "interpretation, necessity, continuity, or succession cannot silently",
    )
    if any(boundary not in encoded for boundary in required_boundaries):
        errors.append(
            "FQ5_CONTROLLING_BOUNDARIES: non-immutability, human authorization, "
            "separate powers, and analysis-only boundaries are required"
        )
    prohibited_claims = (
        "artificial intelligence may independently authorize amendment",
        "adjudication may perform amendment",
        "emergency authority may amend",
        "succession authorizes amendment",
        "recommendation adopts architecture",
    )
    operative_claim = re.search(
        r"\b(?:cdr-005|this analysis|this packet|the packet|architecture [a-e]|"
        r"this recommendation)\b.{0,100}\b(?:establishes|creates|enacts|"
        r"authorizes|adopts|binds|governs|grants)\b.{0,100}\b(?:authority|"
        r"requirement|provision|rule|amendment|refounding|constitutional effect)\b",
        encoded,
    )
    if (
        any(claim in encoded for claim in prohibited_claims)
        or operative_claim
        or "the following requirement applies" in encoded
    ):
        errors.append(
            "FQ5_CONTRADICTORY_AUTHORITY_CLAIM: analysis cannot create machine, "
            "adjudicative, emergency, succession, or recommendation authority"
        )
    if decision.get("provenance") != FQ5_DECISION_PROVENANCE:
        errors.append(
            "FQ5_PROVENANCE_BOUNDARY: explicit human provenance and "
            "drafting-only boundary are required"
        )

    return len(architectures or []), historical_ids, prior_art_ids


def _validate_fq5_human_decision_packet(
    root: Path,
    errors: list[str],
) -> tuple[int, int, str, int]:
    packet_path = root / FQ5_PACKET_RELATIVE_PATH
    try:
        text = packet_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"FQ5_PACKET_REQUIRED: {exc}")
        return 0, 0, "", 0

    if re.findall(r"^# ([^\r\n]+)$", text, flags=re.MULTILINE) != [
        "CDR-005 Human Decision Packet"
    ]:
        errors.append("FQ5_PACKET_SCHEMA: exact unique title is required")
    markers = (
        "[CDR-005](../CDR-005.yaml)",
        "[FQ-05](../../FOUNDATIONAL_QUESTIONS.yaml)",
        "**Status:** ADVISORY — SUPERSEDED AS A DECISION AID",
        (
            "**Decision state:** A later explicit human decision is recorded "
            "only in the\n  linked CDR-005."
        ),
    )
    if (
        any(text.count(marker) != 1 for marker in markers)
        or text.count("RECOMMENDATION_ONLY — NO CONSTITUTIONAL EFFECT") != 2
    ):
        errors.append("FQ5_PACKET_BOUNDARY: exact advisory markers are required")

    headings = re.findall(
        r"^### ([A-E]) — ([^\r\n]+)$", text, flags=re.MULTILINE
    )
    if headings != list(FQ5_ARCHITECTURE_NAMES.items()):
        errors.append(
            "FQ5_PACKET_ARCHITECTURES: exact architectures A through E are "
            "required"
        )
    for architecture_id, name in FQ5_ARCHITECTURE_NAMES.items():
        section = _markdown_section(text, f"{architecture_id} — {name}", 3) or ""
        labels = (
            "Model",
            "Strongest argument for",
            "Strongest argument against",
            "Catastrophic failure",
            "Unresolved question",
        )
        if any(section.count(f"**{label}:**") != 1 for label in labels):
            errors.append(
                f"FQ5_PACKET_ARCHITECTURE_SUMMARY: architecture {architecture_id}"
            )

    recommendations = re.findall(
        r"^\*\*Recommendation:\*\*\s+(.+)$", text, flags=re.MULTILINE
    )
    recommendation_section = _markdown_section(text, "Recommendation", 2) or ""
    text_outside_recommendation = re.sub(
        r"^## Recommendation\r?\n.*?(?=^## |\Z)",
        "",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    extra_recommendation = any(
        re.search(r"\barchitecture [a-e]\b", block, re.IGNORECASE)
        and re.search(
            r"\b(?:recommend(?:ation|ed|s|ing)?|prefer(?:ence|red|s)?|"
            r"should\s+(?:adopt|select|choose))\b",
            block,
            re.IGNORECASE,
        )
        for block in re.split(r"\r?\n\s*\r?\n", text_outside_recommendation)
    )
    recommended = (
        "Architecture E"
        if recommendations == ["Architecture E — Hybrid"]
        else ""
    )
    if (
        recommended != "Architecture E"
        or recommendation_section.count(
            "RECOMMENDATION_ONLY — NO CONSTITUTIONAL EFFECT"
        )
        != 1
        or text.count("**Strongest objection:**") != 1
        or extra_recommendation
    ):
        errors.append(
            "FQ5_PACKET_RECOMMENDATION: one supported Architecture E "
            "recommendation with no effect is required"
        )

    principle_section = (
        _markdown_section(text, "Proposed Refounding-Level Principles", 2) or ""
    )
    principle_lines = re.findall(r"^\d+\. ", principle_section, re.MULTILINE)
    if len(principle_lines) != 10 or any(
        commitment.lower() not in re.sub(r"\s+", " ", principle_section).lower()
        for commitment in FQ5_COMMITMENTS
    ):
        errors.append(
            "FQ5_PACKET_REFOUNDING_PRINCIPLES: exact ten advisory principles "
            "are required"
        )

    options = _markdown_section(text, "Human Decision Options", 2) or ""
    option_lines = re.findall(
        r"^(\d+)\. \*\*([A-Z_]+)\*\* — ", options, flags=re.MULTILINE
    )
    if (
        [number for number, _ in option_lines]
        != [str(index) for index in range(1, 8)]
        or [option for _, option in option_lines] != list(FQ5_PACKET_OPTIONS)
        or any(options.count(option) != 1 for option in FQ5_PACKET_OPTIONS)
    ):
        errors.append("FQ5_PACKET_OPTIONS: exactly seven options are required")

    normative_questions = _markdown_section(text, "Normative Questions", 2) or ""
    if (
        len(re.findall(r"^\d+\. ", normative_questions, re.MULTILINE)) != 5
        or normative_questions.count("?") != 5
    ):
        errors.append(
            "FQ5_PACKET_QUESTIONS: exactly five normative questions are required"
        )
    if any(
        reference not in text
        for reference in FQ5_HISTORICAL_EVIDENCE_IDS | FQ5_PRIOR_ART_IDS
    ):
        errors.append("FQ5_PACKET_EVIDENCE: every mapped reference is required")

    prohibited = (
        r"\bTHIS PACKET (?:ADOPTS|AUTHORIZES|DECIDES|ENACTS)\b",
        r"\bCDR-005 IS DECIDED\b",
        r"\bFQ-05 IS RESOLVED\b",
        r"\bACCEPTED_FOR_DRAFTING\b",
        r"\bCR-\d{3}\b",
        r"^#{1,6}\s+ARTICLE\b",
        r"\bRECOMMENDATION (?:AUTHORIZES|ADOPTS|DECIDES|RESOLVES)\b",
        (
            r"\b(?:CDR-005|THIS ANALYSIS|THIS PACKET|THE PACKET|"
            r"ARCHITECTURE [A-E]|THIS RECOMMENDATION)\b.{0,100}\b"
            r"(?:ESTABLISHES|CREATES|ENACTS|AUTHORIZES|ADOPTS|BINDS|"
            r"GOVERNS|GRANTS)\b.{0,100}\b(?:AUTHORITY|REQUIREMENT|"
            r"PROVISION|RULE|AMENDMENT|REFOUNDING|CONSTITUTIONAL EFFECT)\b"
        ),
        r"\bTHE FOLLOWING REQUIREMENT APPLIES\b",
    )
    if any(
        re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
        for pattern in prohibited
    ):
        errors.append(
            "FQ5_PACKET_CONSTITUTIONAL_EFFECT: packet cannot decide, authorize, "
            "create requirements, or create provisions"
        )
    required_boundaries = (
        "Earlier commitments are not assumed immutable",
        "Ordinary amendment cannot erase the distinction",
        "Artificial intelligence may assist but cannot independently authorize",
        "Adjudication cannot perform amendment or refounding",
        "Emergency authority cannot perform amendment or refounding",
        "Succession does not itself authorize amendment or refounding",
    )
    if any(boundary not in text for boundary in required_boundaries):
        errors.append(
            "FQ5_PACKET_CONTROLLING_BOUNDARIES: all hard boundaries are required"
        )
    return 1, len(option_lines), recommended, len(principle_lines)


def _validate_fq2_human_decision_packet(
    root: Path,
    errors: list[str],
) -> tuple[int, int, str]:
    packet_path = root / FQ2_PACKET_RELATIVE_PATH
    try:
        text = packet_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"FQ2_PACKET_REQUIRED: {exc}")
        return 0, 0, ""

    title = re.findall(r"^# ([^\r\n]+)$", text, flags=re.MULTILINE)
    if title != ["CDR-002 Human Decision Packet"]:
        errors.append("FQ2_PACKET_SCHEMA: exact unique title is required")
    required_markers = (
        "[CDR-002](../CDR-002.yaml)",
        "[FQ-02](../../FOUNDATIONAL_QUESTIONS.yaml)",
        "**Status:** ADVISORY — SUPERSEDED AS A DECISION AID",
        (
            "**Decision state:** A later explicit human decision is recorded "
            "only in the linked CDR-002."
        ),
    )
    if (
        any(text.count(marker) != 1 for marker in required_markers)
        or text.count(
            "**Boundary:** RECOMMENDATION_ONLY — NO CONSTITUTIONAL EFFECT"
        )
        != 2
    ):
        errors.append(
            "FQ2_PACKET_BOUNDARY: exact advisory and no-decision markers are "
            "required"
        )

    architecture_headings = re.findall(
        r"^### ([A-E]) — ([^\r\n]+)$", text, flags=re.MULTILINE
    )
    if architecture_headings != list(FQ2_ARCHITECTURE_NAMES.items()):
        errors.append(
            "FQ2_PACKET_ARCHITECTURES: exact architectures A through E are "
            "required"
        )
    for architecture_id in FQ2_ARCHITECTURE_NAMES:
        section = _markdown_section(
            text,
            f"{architecture_id} — {FQ2_ARCHITECTURE_NAMES[architecture_id]}",
            3,
        )
        if section is None or any(
            section.count(label) != 1
            for label in (
                "**Model:**",
                "**Strongest argument for:**",
                "**Strongest argument against:**",
                "**Catastrophic failure:**",
                "**Unresolved question:**",
            )
        ):
            errors.append(
                f"FQ2_PACKET_ARCHITECTURE_SUMMARY: architecture {architecture_id}"
            )

    recommendation = _markdown_section(text, "Recommendation", 2) or ""
    recommendation_declarations = re.findall(
        r"^\*\*Recommendation:\*\*\s+(.+?)(?=\r?\n\r?\n|\Z)",
        recommendation,
        flags=re.MULTILINE | re.DOTALL,
    )
    normalized_recommendations = [
        re.sub(r"\s+", " ", declaration).strip()
        for declaration in recommendation_declarations
    ]
    global_recommendation_declarations = re.findall(
        r"^\*\*Recommendation:\*\*\s+(.+?)(?=\r?\n\r?\n|\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    normalized_global_recommendations = [
        re.sub(r"\s+", " ", declaration).strip()
        for declaration in global_recommendation_declarations
    ]
    expected_recommendation = (
        "Architecture E — Hybrid Predelegation with Necessity Fallback"
    )
    recommended_architecture = (
        "Architecture E"
        if normalized_recommendations == [expected_recommendation]
        and normalized_global_recommendations == [expected_recommendation]
        else ""
    )
    if (
        recommended_architecture != "Architecture E"
        or recommendation.count(
            "RECOMMENDATION_ONLY — NO CONSTITUTIONAL EFFECT"
        )
        != 1
        or recommendation.count("**Strongest objection:**") != 1
    ):
        errors.append(
            "FQ2_PACKET_RECOMMENDATION: exact recommendation and no-effect "
            "boundary are required"
        )

    options = _markdown_section(text, "Human Decision Options", 2) or ""
    option_lines = re.findall(
        r"^(\d+)\. \*\*([A-Z_]+)\*\* — ", options, flags=re.MULTILINE
    )
    if (
        [number for number, _ in option_lines]
        != [str(index) for index in range(1, 8)]
        or [option for _, option in option_lines] != list(FQ2_PACKET_OPTIONS)
        or any(options.count(option) != 1 for option in FQ2_PACKET_OPTIONS)
    ):
        errors.append(
            "FQ2_PACKET_OPTIONS: exactly seven decision options are required"
        )

    for reference in FQ2_HISTORICAL_EVIDENCE_IDS | FQ2_PRIOR_ART_IDS:
        if reference not in text:
            errors.append(
                f"FQ2_PACKET_EVIDENCE: missing repository reference {reference}"
            )
    prohibited = (
        r"\bTHIS PACKET (?:ADOPTS|AUTHORIZES|DECIDES|ENACTS)\b",
        r"\b(?:ACTORS?|EMERGENCY ACTORS?|ARCHITECTURE [A-E])\s+"
        r"(?:ARE|IS|BECOMES?)\s+(?:HEREBY\s+|NOW\s+)?"
        r"(?:AUTHORIZED|EMPOWERED|ADOPTED|ENACTED)\b",
        r"\bARCHITECTURE [A-E]\s+(?:NOW\s+)?"
        r"(?:HAS|CARRIES)\s+CONSTITUTIONAL "
        r"(?:FORCE|EFFECT|AUTHORITY)\b",
        r"\b(?:WE|THIS PACKET|THE PACKET)\s+(?:HEREBY\s+)?"
        r"(?:GRANTS|CONFERS|CREATES|ESTABLISHES)\b.{0,80}\b"
        r"(?:AUTHORITY|POWER|COMPETENCE)\b",
        r"\b(?:WE|THIS PACKET|THE PACKET)\s+(?:HEREBY\s+)?"
        r"(?:ADOPT|SELECT|CHOOSE)\s+ARCHITECTURE [A-E]\b",
        r"\bARCHITECTURE [A-E]\s+(?:HEREBY\s+)?"
        r"(?:GRANTS|CONFERS|CREATES|ESTABLISHES)\b.{0,80}\b"
        r"(?:AUTHORITY|POWER|COMPETENCE)\b",
        r"\bCDR-002 IS DECIDED\b",
        r"\bFQ-02 IS RESOLVED\b",
        r"\bACCEPTED_FOR_DRAFTING\b",
        r"\bCR-\d{3}\b",
        r"^#{1,6}\s+ARTICLE\b",
    )
    if any(
        re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
        for pattern in prohibited
    ):
        errors.append(
            "FQ2_PACKET_CONSTITUTIONAL_EFFECT: packet cannot decide, authorize, "
            "or create requirements or provisions"
        )

    return 1, len(option_lines), recommended_architecture


def _validate_fq1_human_decision_packet(
    root: Path,
    errors: list[str],
) -> tuple[int, int, int, str]:
    packet_path = root / FQ1_PACKET_RELATIVE_PATH
    packet_paths = [packet_path] if packet_path.is_file() else []
    packet_count = len(packet_paths)
    if len(packet_paths) != 1 or packet_path not in packet_paths:
        _packet_error(
            errors,
            "FQ1_PACKET_COUNT",
            "exactly one packet is required at the designated path",
        )

    try:
        text = packet_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        _packet_error(errors, "FQ1_PACKET_REQUIRED", str(exc))
        return packet_count, 0, 0, ""
    if not text.strip():
        _packet_error(errors, "FQ1_PACKET_REQUIRED", "packet must be nonempty")
        return packet_count, 0, 0, ""

    h1_headings = re.findall(r"^# ([^\r\n]+)\s*$", text, flags=re.MULTILINE)
    h2_headings = re.findall(r"^## ([^\r\n]+)\s*$", text, flags=re.MULTILINE)
    if h1_headings != ["CDR-001 Human Decision Packet"]:
        _packet_error(
            errors,
            "FQ1_PACKET_HEADINGS",
            "the packet title must be unique and exact",
        )
    if h2_headings != list(FQ1_PACKET_HEADINGS):
        _packet_error(
            errors,
            "FQ1_PACKET_HEADINGS",
            "required section headings must be unique, exact, and ordered",
        )

    first_h2 = re.search(r"^## ", text, flags=re.MULTILINE)
    header = text[: first_h2.start()] if first_h2 else text
    header_requirements = (
        "[CDR-001](../CDR-001.yaml)",
        "[FQ-01](../../FOUNDATIONAL_QUESTIONS.yaml)",
        "**Status:** ADVISORY — SUPERSEDED AS A DECISION AID",
        "**Boundary:** RECOMMENDATION_ONLY — NO CONSTITUTIONAL EFFECT",
        (
            "**Decision state:** A later explicit human decision is recorded "
            "only in the linked CDR-001."
        ),
    )
    if any(marker not in header for marker in header_requirements):
        _packet_error(
            errors,
            "FQ1_PACKET_ADVISORY_BOUNDARY",
            "header links and exact advisory markers are required",
        )
    status_assertions = re.findall(
        r"^\s*(?:-\s+)?\*\*Status:\*\*\s*(.+?)\s*$",
        text,
        flags=re.MULTILINE,
    )
    if status_assertions != ["ADVISORY — SUPERSEDED AS A DECISION AID"]:
        _packet_error(
            errors,
            "FQ1_PACKET_ADVISORY_BOUNDARY",
            "the packet may contain only the exact advisory status",
        )

    provenance = _markdown_section(text, "Provenance and Evidence Limits", 2)
    if provenance is None:
        _packet_error(
            errors,
            "FQ1_PACKET_PROVENANCE",
            "provenance section is missing or duplicated",
        )
    else:
        links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", provenance)
        linked_paths = {label for label, _ in links}
        invalid_links = False
        for label, href in links:
            if label not in FQ1_PACKET_PROVENANCE_PATHS:
                continue
            expected = (root / label).resolve()
            resolved = (packet_path.parent / href).resolve()
            if (
                not resolved.is_relative_to(root)
                or resolved != expected
                or not resolved.is_file()
            ):
                invalid_links = True
        if not FQ1_PACKET_PROVENANCE_PATHS.issubset(linked_paths) or invalid_links:
            _packet_error(
                errors,
                "FQ1_PACKET_PROVENANCE",
                "required repository-relative provenance links must resolve",
            )
        provenance_upper = re.sub(r"\s+", " ", provenance).upper()
        if (
            "REPOSITORY-ONLY SYNTHESIS" not in provenance_upper
            or "ANALOGY IS NOT PROOF" not in provenance_upper
            or "ABSENCE OF A CLOSE ANALOGUE IS NOT NOVELTY"
            not in provenance_upper
            or "SOURCE-TO-VERIFY" not in provenance_upper
        ):
            _packet_error(
                errors,
                "FQ1_PACKET_EVIDENCE_LIMITS",
                "repository-only provenance and evidence limits are required",
            )

    architectures = _markdown_section(text, "Existing Architectures", 2)
    if architectures is None:
        _packet_error(
            errors,
            "FQ1_PACKET_ARCHITECTURES",
            "architecture section is missing or duplicated",
        )
    else:
        headings, bodies = _markdown_subsections(architectures, 3)
        if headings != list(FQ1_PACKET_ARCHITECTURE_HEADINGS):
            _packet_error(
                errors,
                "FQ1_PACKET_ARCHITECTURES",
                "exactly architectures A through E are required in order",
            )
        for heading, body in zip(headings, bodies):
            bold_labels = re.findall(
                r"^\*\*([^*\r\n]+)\*\*",
                body,
                flags=re.MULTILINE,
            )
            labels = list(
                re.finditer(
                    r"^\*\*([^*\r\n]+):\*\*",
                    body,
                    flags=re.MULTILINE,
                )
            )
            label_names = [match.group(1) for match in labels]
            if (
                bold_labels
                != [f"{label}:" for label in FQ1_PACKET_ARCHITECTURE_LABELS]
                or label_names != list(FQ1_PACKET_ARCHITECTURE_LABELS)
                or re.search(r"^#{1,6} ", body, flags=re.MULTILINE)
            ):
                _packet_error(
                    errors,
                    "FQ1_PACKET_ARCHITECTURE_LABELS",
                    f"{heading!r} must contain only the five required labels",
                )
                continue
            values: dict[str, str] = {}
            for index, match in enumerate(labels):
                end = labels[index + 1].start() if index + 1 < len(labels) else len(body)
                values[match.group(1)] = body[match.end() : end].strip()
            if any(not value for value in values.values()):
                _packet_error(
                    errors,
                    "FQ1_PACKET_ARCHITECTURE_LABELS",
                    f"{heading!r} contains an empty required label",
                )
            expected_terms = FQ1_PACKET_ARCHITECTURE_REQUIRED_TERMS.get(
                heading, {}
            )
            for label, terms in expected_terms.items():
                normalized_value = re.sub(
                    r"\s+", " ", values.get(label, "")
                ).casefold()
                if label == "Strongest argument for":
                    terms_missing = any(
                        not _contains_unnegated_phrase(normalized_value, term)
                        for term in terms
                    )
                else:
                    terms_missing = any(
                        term not in normalized_value for term in terms
                    )
                if terms_missing:
                    _packet_error(
                        errors,
                        "FQ1_PACKET_ARCHITECTURE_TRACEABILITY",
                        f"{heading!r}/{label!r} contradicts or omits CDR-001",
                    )
            model = re.sub(
                r"\s+",
                " ",
                values.get("Constitutional model", ""),
            ).strip()
            sentences = [
                sentence
                for sentence in re.split(r"(?<=[.!?])\s+", model)
                if sentence.strip()
            ]
            if len(sentences) not in {2, 3}:
                _packet_error(
                    errors,
                    "FQ1_PACKET_ARCHITECTURE_MODEL",
                    f"{heading!r} must have a two- or three-sentence model",
                )

    core = _markdown_section(text, "Core Decision", 2)
    normalized_core = (
        re.sub(r"\s+", " ", core.replace("**", "")).strip()
        if core is not None
        else ""
    )
    core_distinction = (
        "HUMAN SOVEREIGNTY OVER ENDS does not necessarily imply "
        "UNCONSTRAINED HUMAN EXERCISE OF INSTITUTIONAL POWER."
    )
    if (
        core_distinction not in normalized_core
        or "implementation details" not in normalized_core
        or "foundational human constituency decides" not in normalized_core
    ):
        _packet_error(
            errors,
            "FQ1_PACKET_CORE_DECISION",
            "the exact sovereignty-versus-exercise distinction is required",
        )

    elimination = _markdown_section(text, "Elimination Analysis", 2)
    elimination_text = (
        re.sub(r"\s+", " ", elimination).casefold()
        if elimination is not None
        else ""
    )
    elimination_markers = (
        "no architecture is automatically eliminated",
        "declares none eliminated",
        "architecture a appears constitutionally weakest and dominated",
        "no reliable internal constraint",
        "structured sovereign discretion rather than constitutional governance",
        "architecture b remains coherent",
        "self-dealing and self-interpretation",
        "architectures c, d, and e remain materially distinct",
        "are not dominated by current repository evidence",
    )
    if any(marker not in elimination_text for marker in elimination_markers):
        _packet_error(
            errors,
            "FQ1_PACKET_ELIMINATION_ANALYSIS",
            "required advisory elimination analysis is incomplete",
        )

    recommended_architecture = ""
    recommendation = _markdown_section(text, "Recommended Architecture", 2)
    if recommendation is None:
        _packet_error(
            errors,
            "FQ1_PACKET_RECOMMENDATION",
            "recommendation section is missing or duplicated",
        )
    else:
        recommendation_matches = re.findall(
            r"^\*\*Recommendation:\*\* (.+?)\s*$",
            recommendation,
            flags=re.MULTILINE,
        )
        if recommendation_matches == ["Architecture E"]:
            recommended_architecture = "Architecture E"
        else:
            _packet_error(
                errors,
                "FQ1_PACKET_RECOMMENDATION",
                "the recommendation must be exactly Architecture E",
            )
        if (
            recommendation.count(
                "RECOMMENDATION_ONLY — NO CONSTITUTIONAL EFFECT"
            )
            != 1
        ):
            _packet_error(
                errors,
                "FQ1_PACKET_RECOMMENDATION_BOUNDARY",
                "the exact no-effect boundary is required in the recommendation",
            )
        objection_matches = re.findall(
            r"^\*\*Strongest objection:\*\*(.*?)(?=^\*\*|\Z)",
            recommendation,
            flags=re.MULTILINE | re.DOTALL,
        )
        objection = (
            re.sub(r"\s+", " ", objection_matches[0]).casefold()
            if len(objection_matches) == 1
            else ""
        )
        objection_terms = (
            "rigid",
            "amendment",
            "refounding",
            "recursive",
            "reviewers",
            "operators",
            "technical infrastructure",
            "effective power",
        )
        if any(term not in objection for term in objection_terms):
            _packet_error(
                errors,
                "FQ1_PACKET_STRONGEST_OBJECTION",
                "the strongest objection must cover rigidity, recursion, and transfer",
            )
        if len(re.findall(r"\b[\w’'-]+\b", recommendation)) > 500:
            _packet_error(
                errors,
                "FQ1_PACKET_RECOMMENDATION_LENGTH",
                "recommendation must not exceed 500 words",
            )

    hybrid = _markdown_section(text, "Hybrid Question", 2)
    hybrid_text = re.sub(r"\s+", " ", hybrid).casefold() if hybrid else ""
    hybrid_headings = (
        re.findall(r"^### ([^\r\n]+)\s*$", hybrid, flags=re.MULTILINE)
        if hybrid
        else []
    )
    hybrid_markers = (
        "recommended foundational architecture is architecture e",
        "independent human review",
        "review intensity",
        "remedy still unresolved",
        "plural or distributed counter-power",
        "independent verification",
        "publication",
        "reason-giving",
        "explicit precedent and supersession",
        "procedural regularity",
        "machine sovereignty or final machine adjudication",
        "reviewer control over institutional ends or refounding",
        "ordinary-command bypass of entrenchment",
        "performance or popularity as a source of authority",
    )
    if (
        hybrid_headings
        != [
            "FOUNDATIONAL ARCHITECTURE",
            "IMPLEMENTATION / INSTITUTIONAL MECHANISMS",
            "Rejected Mechanism Classes",
        ]
        or any(marker not in hybrid_text for marker in hybrid_markers)
    ):
        _packet_error(
            errors,
            "FQ1_PACKET_HYBRID",
            "foundational allocation, incorporation candidates, and rejections are required",
        )

    option_count = 0
    options = _markdown_section(text, "Human Decision Options", 2)
    if options is None:
        _packet_error(
            errors,
            "FQ1_PACKET_OPTIONS",
            "decision options section is missing or duplicated",
        )
    else:
        option_lines = re.findall(
            r"^(\d+)\. \*\*([A-Z_]+)\*\* — (.+)$",
            options,
            flags=re.MULTILINE,
        )
        numbered_option_lines = re.findall(
            r"^(\d+)\.\s+(.+)$",
            options,
            flags=re.MULTILINE,
        )
        option_mentions = re.findall(
            r"\b(?:ADOPT_A|ADOPT_B|ADOPT_C|ADOPT_D|ADOPT_E|"
            r"ADOPT_HYBRID|REVISE_AND_REVIEW|DEFER)\b",
            options,
        )
        bold_option_labels = re.findall(
            r"\*\*([A-Z][A-Z0-9_-]+)\*\*",
            options,
        )
        option_count = len(option_lines)
        if (
            [number for number, _, _ in option_lines]
            != [str(index) for index in range(1, 9)]
            or [code for _, code, _ in option_lines]
            != list(FQ1_PACKET_DECISION_OPTIONS)
            or option_mentions != list(FQ1_PACKET_DECISION_OPTIONS)
            or bold_option_labels != list(FQ1_PACKET_DECISION_OPTIONS)
            or any(not description.strip() for _, _, description in option_lines)
            or len(numbered_option_lines) != len(FQ1_PACKET_DECISION_OPTIONS)
            or [number for number, _ in numbered_option_lines]
            != [str(index) for index in range(1, 9)]
        ):
            _packet_error(
                errors,
                "FQ1_PACKET_OPTIONS",
                "the eight exact option codes must appear once in required order",
            )
        hybrid_option_match = re.search(
            r"^6\. \*\*ADOPT_HYBRID\*\*(.*?)(?=^7\. |\Z)",
            options,
            flags=re.MULTILINE | re.DOTALL,
        )
        hybrid_option = (
            re.sub(r"\s+", " ", hybrid_option_match.group(1)).casefold()
            if hybrid_option_match
            else ""
        )
        if not all(
            term in hybrid_option
            for term in (
                "foundational architecture",
                "incorporated mechanism",
                "rejected mechanism",
            )
        ):
            _packet_error(
                errors,
                "FQ1_PACKET_HYBRID_OPTION",
                "ADOPT_HYBRID must require architecture, incorporations, and rejections",
            )

    question_count = 0
    questions = _markdown_section(text, "Decision Questions", 2)
    if questions is None:
        _packet_error(
            errors,
            "FQ1_PACKET_QUESTIONS",
            "decision questions section is missing or duplicated",
        )
    else:
        question_matches = list(
            re.finditer(r"^(\d+)\. ", questions, flags=re.MULTILINE)
        )
        question_count = len(question_matches)
        question_bodies: list[str] = []
        for index, match in enumerate(question_matches):
            end = (
                question_matches[index + 1].start()
                if index + 1 < len(question_matches)
                else len(questions)
            )
            question_bodies.append(
                re.sub(r"\s+", " ", questions[match.end() : end]).strip()
            )
        if (
            [match.group(1) for match in question_matches]
            != ["1", "2", "3", "4", "5"]
            or questions.count("?") != 5
            or any(not body.endswith("?") for body in question_bodies)
        ):
            _packet_error(
                errors,
                "FQ1_PACKET_QUESTIONS",
                "exactly five numbered single questions are required",
            )
        question_topics = (
            ("constituency", "sovereignty"),
            ("ordinary foundational human act", "invalid", "entrenched"),
            ("review", "remedy", "sovereign", "reviewer"),
            ("amendment", "refounding", "entrenchment"),
            ("emergency", "succession", "artificial intelligence", "foundational office"),
        )
        for body, terms in zip(question_bodies, question_topics):
            folded = body.casefold()
            if any(term not in folded for term in terms):
                _packet_error(
                    errors,
                    "FQ1_PACKET_QUESTION_TOPICS",
                    "the five questions must cover the required normative choices",
                )
                break

    consequences = _markdown_section(text, "Consequences for Later Design", 2)
    if consequences is None:
        _packet_error(
            errors,
            "FQ1_PACKET_CONSEQUENCES",
            "consequences section is missing or duplicated",
        )
    else:
        headings, bodies = _markdown_subsections(consequences, 3)
        expected_headings = [
            f"Consequence of {code}" for code in FQ1_PACKET_DECISION_OPTIONS
        ]
        if headings != expected_headings:
            _packet_error(
                errors,
                "FQ1_PACKET_CONSEQUENCES",
                "all eight option consequences are required in order",
            )
        for heading, body in zip(headings, bodies):
            issue_ids = set(re.findall(r"\bIR-\d{2}\b", body))
            if (
                not body.strip()
                or not FQ1_PACKET_CONSEQUENCE_ISSUES.issubset(issue_ids)
            ):
                _packet_error(
                    errors,
                    "FQ1_PACKET_CONSEQUENCE_COVERAGE",
                    f"{heading!r} must address all six linked issue registers",
                )
        if re.search(
            r"\bIR-\d{2}\b.{0,300}\b"
            r"(?:IS|ARE|BECOMES?|BECAME|HAS BEEN|HAVE BEEN)\s+"
            r"(?:NOW\s+)?(?:RESOLVED|CLOSED|DECIDED)\b",
            consequences,
            flags=re.IGNORECASE | re.DOTALL,
        ):
            _packet_error(
                errors,
                "FQ1_PACKET_CONSEQUENCE_RESOLUTION",
                "consequences cannot resolve linked constitutional issues",
            )
        if re.search(
            r"\b(?:RESOLVED|CLOSED|DECIDED)\b.{0,300}\bIR-\d{2}\b",
            consequences,
            flags=re.IGNORECASE | re.DOTALL,
        ):
            _packet_error(
                errors,
                "FQ1_PACKET_CONSEQUENCE_RESOLUTION",
                "consequences cannot resolve linked constitutional issues",
            )

    ambiguities = _markdown_section(text, "Material Ambiguities", 2)
    ambiguity_labels = (
        re.findall(r"^- \*\*([^*:]+):\*\*", ambiguities, flags=re.MULTILINE)
        if ambiguities
        else []
    )
    if ambiguity_labels != [
        "Constituency",
        "Review force",
        "Emergency and succession",
        "Amendment-refounding boundary",
        "Effective power",
        "Machine formalization and legitimacy",
    ]:
        _packet_error(
            errors,
            "FQ1_PACKET_AMBIGUITIES",
            "all six material ambiguity classes are required",
        )

    prohibited_claims = (
        r"\bTHIS PACKET (?:ADOPTS|DECIDES|AUTHORIZES|ENACTS)\b",
        r"\b(?:WE|THIS PACKET|THE PACKET)\s+(?:HEREBY\s+)?"
        r"(?:ADOPT|DECIDE|AUTHORIZE|ENACT|RESOLVE|SELECT)\b",
        r"\b(?:ADOPT|AUTHORIZE|ENACT|SELECT)(?:S|ED)?\s+"
        r"ARCHITECTURE [A-E]\b",
        r"\b(?:APPROVE|APPROVES|APPROVED|RATIFY|RATIFIES|RATIFIED|"
        r"CONFIRM|CONFIRMS|CONFIRMED)\s+ARCHITECTURE [A-E]\b",
        r"\bRESOLVE(?:S|D)?\s+FQ-01\b",
        r"\b(?:SETTLE|SETTLES|SETTLED)\s+FQ-01\b",
        r"\bARCHITECTURE [A-E] (?:IS|WAS|HAS BEEN) "
        r"(?:ADOPTED|SELECTED|DECIDED)\b",
        r"\bCDR-001 IS DECIDED\b",
        r"\bFQ-01 IS RESOLVED\b",
        r"(?im)^\s*(?:\*\*)?(?:AUTHORIZED BY|AUTHORIZED_BY|"
        r"AUTHORIZATION RECORD|AUTHORIZATION_RECORD|DECISION DATE|"
        r"DECISION_DATE)(?:\*\*)?\s*:",
        r"(?im)^#{1,6}\s+ARTICLE\b",
        r"\bACCEPTED REQUIREMENT\b",
        r"\bCONSTITUTIONAL PROVISION\b",
        r"\bCR-\d{3}\b",
        r"```",
    )
    if any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in prohibited_claims):
        _packet_error(
            errors,
            "FQ1_PACKET_AUTHORITY_EFFECT",
            "packet cannot contain authorization, adoption, or executable effect",
        )

    return (
        packet_count,
        option_count,
        question_count,
        recommended_architecture,
    )


def _validate_article_architecture(
    root: Path,
    decisions_by_id: dict[str, dict[str, Any]],
    requirements: list[dict[str, Any]],
    errors: list[str],
) -> dict[str, int]:
    metrics = {
        "source_requirement_count": 0,
        "consolidated_requirement_count": 0,
        "proposed_article_count": 0,
        "ready_for_constitutional_draft_count": 0,
        "blocked_by_unresolved_design_count": 0,
        "subordinate_governance_law_count": 0,
        "implementation_standard_count": 0,
        "unmapped_requirement_count": 35,
    }
    map_path = root / CONSOLIDATED_MAP_RELATIVE_PATH
    record = _load_record(map_path, errors) or {}
    if set(record) != CONSOLIDATED_MAP_FIELDS:
        errors.append(
            "CONSOLIDATED_MAP_SCHEMA: exact top-level fields are required"
        )
    if (
        record.get("map_id") != "CONSOLIDATED-REQUIREMENT-MAP-001"
        or record.get("status") != "READY_FOR_CONSTITUTIONAL_DRAFTING"
        or record.get("source_requirement_count") != 35
        or record.get("source_requirement_range") != "CR-001 through CR-035"
        or record.get("classification_vocabulary")
        != [
            "READY_FOR_CONSTITUTIONAL_DRAFT",
            "BLOCKED_BY_UNRESOLVED_DESIGN",
            "SUBORDINATE_GOVERNANCE_LAW",
            "IMPLEMENTATION_STANDARD",
        ]
        or not _is_evidence(record.get("boundary"))
    ):
        errors.append(
            "CONSOLIDATED_MAP_METADATA: exact pre-drafting metadata is required"
        )

    expected_cr_ids = {f"CR-{index:03d}" for index in range(1, 36)}
    expected_cdr_ids = {f"CDR-{index:03d}" for index in range(1, 6)}
    expected_ccr_ids = {f"CCR-{index:03d}" for index in range(1, 21)}
    expected_article_ids = {f"ARTICLE-{value}" for value in (
        "I", "II", "III", "IV", "V", "VI", "VII", "VIII"
    )}
    if (
        record.get("controlling_decisions")
        != [
            *[f"CDR-{index:03d}" for index in range(1, 6)],
            "CDD-001",
        ]
        or set(decisions_by_id) != expected_cdr_ids
        or any(
            decisions_by_id.get(decision_id, {}).get("status") != "DECIDED"
            for decision_id in expected_cdr_ids
        )
    ):
        errors.append(
            "CONSOLIDATED_MAP_CONTROLLING_DECISIONS: five decided CDRs and "
            "CDD-001 are required"
        )

    consolidated = record.get("consolidated_requirements")
    consolidated_records = (
        [item for item in consolidated if isinstance(item, dict)]
        if isinstance(consolidated, list)
        else []
    )
    ccr_ids = [
        item.get("consolidated_id")
        for item in consolidated_records
        if isinstance(item.get("consolidated_id"), str)
    ]
    source_membership: dict[str, tuple[str, str]] = {}
    classification_counts = {
        classification: 0 for classification in CONSOLIDATED_CLASSIFICATIONS
    }
    malformed_consolidated = (
        not isinstance(consolidated, list)
        or len(consolidated_records) != len(consolidated)
    )
    for item in consolidated_records:
        consolidated_id = item.get("consolidated_id")
        classification = item.get("classification")
        source_requirements = item.get("source_requirements")
        controlling_cdrs = item.get("controlling_cdrs")
        dependencies = item.get("dependencies")
        overlaps = item.get("overlaps")
        primary_article = item.get("primary_article")
        if (
            set(item) != CONSOLIDATED_REQUIREMENT_FIELDS
            or classification not in CONSOLIDATED_CLASSIFICATIONS
            or not isinstance(source_requirements, list)
            or not source_requirements
            or len(source_requirements) != len(set(map(str, source_requirements)))
            or not isinstance(controlling_cdrs, list)
            or not controlling_cdrs
            or not set(controlling_cdrs).issubset(expected_cdr_ids)
            or not isinstance(dependencies, list)
            or not isinstance(overlaps, list)
            or primary_article not in expected_article_ids
            or not _is_evidence(item.get("title"))
            or not _is_evidence(item.get("consolidation_rationale"))
            or not _is_evidence(item.get("drafting_boundary"))
        ):
            malformed_consolidated = True
        if classification in classification_counts:
            classification_counts[classification] += 1
        if isinstance(source_requirements, list):
            for requirement_id in source_requirements:
                if isinstance(requirement_id, str):
                    if requirement_id in source_membership:
                        errors.append(
                            "CONSOLIDATED_SOURCE_DUPLICATION: "
                            f"{requirement_id} has multiple primary mappings"
                        )
                    else:
                        source_membership[requirement_id] = (
                            str(consolidated_id),
                            str(primary_article),
                        )
    if (
        malformed_consolidated
        or len(consolidated_records) != 20
        or set(ccr_ids) != expected_ccr_ids
        or len(ccr_ids) != len(set(ccr_ids))
    ):
        errors.append(
            "CONSOLIDATED_REQUIREMENTS: exact CCR-001 through CCR-020 records "
            "are required"
        )
    for item in consolidated_records:
        if (
            not set(item.get("dependencies", [])).issubset(expected_ccr_ids)
            or not set(item.get("overlaps", [])).issubset(expected_ccr_ids)
            or item.get("consolidated_id") in item.get("dependencies", [])
            or item.get("consolidated_id") in item.get("overlaps", [])
        ):
            errors.append(
                "CONSOLIDATED_RELATIONSHIPS: dependencies and overlaps must "
                "resolve to other consolidated requirements"
            )
            break

    actual_source_ids = set(source_membership)
    repository_requirement_ids = {
        requirement.get("requirement_id")
        for requirement in requirements
        if isinstance(requirement.get("requirement_id"), str)
    }
    source_issues_by_requirement = {
        str(requirement.get("requirement_id")): {
            issue_id
            for issue_id in requirement.get("source_issues", [])
            if isinstance(issue_id, str)
        }
        for requirement in requirements
    }
    if (
        actual_source_ids != expected_cr_ids
        or repository_requirement_ids != expected_cr_ids
    ):
        errors.append(
            "CONSOLIDATED_SOURCE_COVERAGE: every CR-001 through CR-035 must map "
            "exactly once"
        )
    if (
        record.get("classification_summary")
        != EXPECTED_CONSOLIDATED_CLASSIFICATION_COUNTS
        or classification_counts != EXPECTED_CONSOLIDATED_CLASSIFICATION_COUNTS
    ):
        errors.append(
            "CONSOLIDATED_CLASSIFICATION_COUNTS: exact classification totals "
            "are required"
        )

    coverage = record.get("coverage_matrix")
    coverage_records = (
        [item for item in coverage if isinstance(item, dict)]
        if isinstance(coverage, list)
        else []
    )
    coverage_sources: list[str] = []
    malformed_coverage = (
        not isinstance(coverage, list)
        or len(coverage_records) != len(coverage)
    )
    for item in coverage_records:
        source_requirement = item.get("source_requirement")
        if isinstance(source_requirement, str):
            coverage_sources.append(source_requirement)
        expected_mapping = source_membership.get(str(source_requirement))
        if (
            set(item)
            != {"source_requirement", "consolidated_requirement", "primary_article"}
            or expected_mapping
            != (
                item.get("consolidated_requirement"),
                item.get("primary_article"),
            )
        ):
            malformed_coverage = True
    if (
        malformed_coverage
        or len(coverage_records) != 35
        or set(coverage_sources) != expected_cr_ids
        or len(coverage_sources) != len(set(coverage_sources))
    ):
        errors.append(
            "CONSOLIDATED_COVERAGE_MATRIX: 35 exact transparent coverage rows "
            "are required"
        )

    overlaps = record.get("overlap_register")
    if (
        not isinstance(overlaps, list)
        or len(overlaps) != 9
        or any(
            not isinstance(item, dict)
            or set(item) != {"overlap_id", "requirements", "resolution"}
            or not isinstance(item.get("requirements"), list)
            or not set(item["requirements"]).issubset(expected_cr_ids)
            or not _is_evidence(item.get("resolution"))
            for item in overlaps
        )
    ):
        errors.append(
            "CONSOLIDATED_OVERLAPS: nine traceable overlap records are required"
        )
    conflicts = record.get("apparent_conflicts")
    if (
        not isinstance(conflicts, list)
        or len(conflicts) != 5
        or any(
            not isinstance(item, dict)
            or set(item) != {"conflict_id", "tension", "treatment"}
            or not _is_evidence(item.get("tension"))
            or not _is_evidence(item.get("treatment"))
            for item in conflicts
        )
    ):
        errors.append(
            "CONSOLIDATED_CONFLICTS: five bounded conflict-or-gap records are "
            "required"
        )
    if record.get("state_preservation") != {
        "decision_status_counts": {"DECIDED": 5},
        "coordinated_decision_status": {"CDD-001": "DECIDED"},
        "foundational_question_status_counts": {"RESOLVED": 5},
        "issue_status_counts": {"OPEN": 18},
        "accepted_requirement_count": 35,
        "constitutional_provision_count": 0,
        "governance_runtime_artifact_count": 0,
    }:
        errors.append(
            "CONSOLIDATED_STATE_PRESERVATION: exact constitutional state is "
            "required"
        )
    if not _has_provenance(record):
        errors.append("CONSOLIDATED_PROVENANCE: explicit provenance is required")

    architecture_path = root / ARTICLE_ARCHITECTURE_RELATIVE_PATH
    try:
        architecture_text = architecture_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"ARTICLE_ARCHITECTURE_REQUIRED: {exc}")
        architecture_text = ""
    if (
        architecture_text.count("# Constitutional Article Architecture") != 1
        or architecture_text.count(
            "**PRE-DRAFTING STRUCTURAL BLUEPRINT — NO CONSTITUTIONAL PROVISIONS**"
        )
        != 1
    ):
        errors.append(
            "ARTICLE_ARCHITECTURE_BOUNDARY: exact title and non-provision "
            "boundary are required"
        )
    article_headings = re.findall(
        r"^## Article ([IVX]+) — ([^\r\n]+)$",
        architecture_text,
        flags=re.MULTILINE,
    )
    expected_headings = [
        (roman, title)
        for roman, title in zip(
            ("I", "II", "III", "IV", "V", "VI", "VII", "VIII"),
            EXPECTED_ARTICLE_TITLES,
            strict=True,
        )
    ]
    if article_headings != expected_headings:
        errors.append(
            "ARTICLE_ARCHITECTURE_ARTICLES: exact eight substantive articles "
            "are required"
        )
    article_labels = (
        "Purpose",
        "Consolidated requirements",
        "Source requirements",
        "Controlling CDRs",
        "Unresolved issues",
        "Dependencies",
        "Explicitly excluded from constitutional text at this stage",
        "Anticipated subordinate-law needs",
        "Anticipated implementation standards",
    )
    for roman, title in expected_headings:
        section = _markdown_section(
            architecture_text, f"Article {roman} — {title}", 2
        ) or ""
        field_values = {}
        for label in article_labels:
            match = re.search(
                rf"^\*\*{re.escape(label)}:\*\*[ \t]*(.+?)"
                r"(?=\r?\n\r?\n\*\*|\Z)",
                section,
                flags=re.MULTILINE | re.DOTALL,
            )
            if match:
                field_values[label] = re.sub(
                    r"\s+", " ", match.group(1)
                ).strip()
        if (
            any(section.count(f"**{label}:**") != 1 for label in article_labels)
            or set(field_values) != set(article_labels)
            or any(not value for value in field_values.values())
        ):
            errors.append(
                "ARTICLE_ARCHITECTURE_RECORD_FIELDS: "
                f"Article {roman} lacks exact required fields"
            )
        article_id = f"ARTICLE-{roman}"
        expected_article_ccrs = {
            str(item.get("consolidated_id"))
            for item in consolidated_records
            if item.get("primary_article") == article_id
        }
        expected_article_crs = {
            source
            for item in consolidated_records
            if item.get("primary_article") == article_id
            for source in item.get("source_requirements", [])
            if isinstance(source, str)
        }
        listed_ccrs = set(
            re.findall(
                r"\bCCR-\d{3}\b",
                field_values.get("Consolidated requirements", ""),
            )
        )
        listed_crs = set(
            re.findall(
                r"\bCR-\d{3}\b",
                field_values.get("Source requirements", ""),
            )
        )
        if listed_ccrs != expected_article_ccrs or listed_crs != expected_article_crs:
            errors.append(
                "ARTICLE_ARCHITECTURE_COVERAGE: "
                f"Article {roman} must list its exact primary CCR and CR coverage"
            )
        listed_cdrs = set(
            re.findall(
                r"\bCDR-\d{3}\b",
                field_values.get("Controlling CDRs", ""),
            )
        )
        if listed_cdrs != EXPECTED_ARTICLE_CONTROLLING_CDRS[article_id]:
            errors.append(
                "ARTICLE_ARCHITECTURE_CONTROLLING_CDRS: "
                f"Article {roman} must list its exact controlling decisions"
            )
        unresolved_issue_ids = set(
            re.findall(
                r"\bIR-\d{2}\b",
                field_values.get("Unresolved issues", ""),
            )
        )
        expected_article_issues = {
            issue_id
            for requirement_id in expected_article_crs
            for issue_id in source_issues_by_requirement.get(requirement_id, set())
        }
        if unresolved_issue_ids != expected_article_issues:
            errors.append(
                "ARTICLE_ARCHITECTURE_UNRESOLVED_ISSUES: "
                f"Article {roman} must list the exact source-issue union"
            )
    if (
        "ten-article candidate should be consolidated into **eight" not in architecture_text
        or "Constitutional provisions: **0**" not in architecture_text
        or "Governance runtime artifacts: **0**" not in architecture_text
    ):
        errors.append(
            "ARTICLE_ARCHITECTURE_ANALYSIS: candidate test and preserved state "
            "must remain explicit"
        )
    prohibited_clause_patterns = (
        r"^###?\s+(?:SECTION|CLAUSE)\b",
        r"\bHEREBY (?:ENACTED|ESTABLISHED|ORDAINED)\b",
        r"\bTHIS CONSTITUTION (?:GRANTS|CREATES|ESTABLISHES)\b",
        r"\b(?:TWO-THIRDS|THREE-QUARTERS|\d+\s*%)\b",
        r"\b(?:COUNCIL|TRIBUNAL|COMMISSION|COURT|ASSEMBLY)\s+SHALL\s+"
        r"(?:CONSIST|COMPRISE|BE ESTABLISHED)\b",
        r"\b(?:SHALL|MUST)\s+(?:FILE|APPEAL|DECIDE|VOTE)\s+WITHIN\s+\d+\b",
    )
    if any(
        re.search(pattern, architecture_text, re.IGNORECASE | re.MULTILINE)
        for pattern in prohibited_clause_patterns
    ):
        errors.append(
            "ARTICLE_ARCHITECTURE_NO_PROVISIONS: blueprint cannot contain "
            "constitutional clauses or enactment language"
        )

    metrics["source_requirement_count"] = len(actual_source_ids)
    metrics["consolidated_requirement_count"] = len(consolidated_records)
    metrics["proposed_article_count"] = len(article_headings)
    metrics["ready_for_constitutional_draft_count"] = classification_counts[
        "READY_FOR_CONSTITUTIONAL_DRAFT"
    ]
    metrics["blocked_by_unresolved_design_count"] = classification_counts[
        "BLOCKED_BY_UNRESOLVED_DESIGN"
    ]
    metrics["subordinate_governance_law_count"] = classification_counts[
        "SUBORDINATE_GOVERNANCE_LAW"
    ]
    metrics["implementation_standard_count"] = classification_counts[
        "IMPLEMENTATION_STANDARD"
    ]
    metrics["unmapped_requirement_count"] = len(
        expected_cr_ids - actual_source_ids
    )
    return metrics


def _validate_remaining_design_analysis(
    root: Path,
    errors: list[str],
) -> dict[str, int]:
    metrics = {
        "design_domain_count": 0,
        "human_decisions_required": 0,
        "recommended_decision_count": 0,
        "cross_domain_conflict_count": 0,
        "projected_ready_for_constitutional_draft_count": 0,
        "projected_blocked_count": 0,
        "genuine_residual_implementation_question_count": 0,
    }
    matrix_path = root / REMAINING_DESIGN_MATRIX_RELATIVE_PATH
    record = _load_record(matrix_path, errors) or {}
    if set(record) != REMAINING_DESIGN_MATRIX_FIELDS:
        errors.append(
            "REMAINING_DESIGN_MATRIX_SCHEMA: exact top-level fields are required"
        )
    if (
        record.get("matrix_id") != "REMAINING-DESIGN-MATRIX-001"
        or record.get("status") != "ADOPTED_COORDINATED_DESIGN"
        or record.get("decision_effect") != "CDD-001"
        or not _is_evidence(record.get("boundary"))
        or "cdd-001 adopts" not in str(record.get("boundary", "")).lower()
        or "constitutional provision" not in str(
            record.get("boundary", "")
        ).lower()
    ):
        errors.append(
            "REMAINING_DESIGN_BOUNDARY: design must record CDD-001 adoption "
            "without creating provisions or runtime effect"
        )
    if record.get("adoption") != {
        "decision_id": "CDD-001",
        "status": "DECIDED",
        "decision": "ADOPT_ALL",
        "decision_date": "2026-08-30",
        "authority": "Human Constitutional Authority",
        "authorization_record": (
            "Explicit human instruction adopting RD-01 through RD-11 and all "
            "four coordinated cross-domain correction components."
        ),
    }:
        errors.append(
            "REMAINING_DESIGN_ADOPTION: exact Human Constitutional Authority "
            "adoption is required"
        )

    expected_domain_ids = {f"RD-{index:02d}" for index in range(1, 12)}
    expected_decision_ids = {
        f"DECISION-RD-{index:02d}" for index in range(1, 12)
    }
    expected_ccr_ids = {f"CCR-{index:03d}" for index in range(1, 21)}
    expected_issue_ids = {f"IR-{index:02d}" for index in range(1, 19)}
    if set(record.get("stress_test_dimensions", [])) != (
        REMAINING_DESIGN_STRESS_DIMENSIONS
    ):
        errors.append(
            "REMAINING_DESIGN_STRESS_DIMENSIONS: exact seven failure modes "
            "are required"
        )

    domains = record.get("design_domains")
    domain_records = (
        [item for item in domains if isinstance(item, dict)]
        if isinstance(domains, list)
        else []
    )
    domain_ids = {
        item.get("domain_id")
        for item in domain_records
        if isinstance(item.get("domain_id"), str)
    }
    blocked_coverage: set[str] = set()
    malformed_domain = (
        not isinstance(domains, list) or len(domain_records) != len(domains)
    )
    for domain in domain_records:
        domain_id = domain.get("domain_id")
        alternatives = domain.get("alternatives")
        recommendation = domain.get("recommendation")
        blocked = domain.get("blocked_requirements")
        issues = domain.get("unresolved_issues")
        dependencies = domain.get("dependencies")
        if (
            set(domain) != REMAINING_DESIGN_DOMAIN_FIELDS
            or domain.get("decision_status") != "ADOPTED"
            or domain.get("adopted_by") != "CDD-001"
            or not _is_evidence(domain.get("title"))
            or not isinstance(blocked, list)
            or not blocked
            or not set(blocked).issubset(
                EXPECTED_BLOCKED_CONSOLIDATED_REQUIREMENTS
            )
            or not isinstance(issues, list)
            or not issues
            or not set(issues).issubset(expected_issue_ids)
            or not isinstance(dependencies, list)
            or not set(dependencies).issubset(expected_domain_ids)
            or domain_id in dependencies
            or not isinstance(domain.get("cross_domain_conflicts"), list)
            or not domain.get("cross_domain_conflicts")
            or not isinstance(
                domain.get("residual_implementation_questions"), list
            )
            or not domain.get("residual_implementation_questions")
        ):
            malformed_domain = True
        if isinstance(blocked, list):
            blocked_coverage.update(str(value) for value in blocked)
        alternative_records = (
            [item for item in alternatives if isinstance(item, dict)]
            if isinstance(alternatives, list)
            else []
        )
        if (
            not 3 <= len(alternative_records) <= 5
            or len(alternative_records) != len(alternatives or [])
            or len(
                {
                    item.get("alternative_id")
                    for item in alternative_records
                }
            )
            != len(alternative_records)
            or any(
                set(item) != {"alternative_id", "architecture", "stress_test"}
                or not _is_evidence(item.get("architecture"))
                or not isinstance(item.get("stress_test"), dict)
                or set(item["stress_test"])
                != REMAINING_DESIGN_STRESS_DIMENSIONS
                or any(
                    not _is_evidence(value)
                    for value in item["stress_test"].values()
                )
                for item in alternative_records
            )
        ):
            errors.append(
                "REMAINING_DESIGN_ALTERNATIVES: every domain requires three "
                "to five alternatives with all seven stress tests"
            )
        alternative_ids = {
            item.get("alternative_id") for item in alternative_records
        }
        if (
            not isinstance(recommendation, dict)
            or set(recommendation)
            != {
                "selected_alternative",
                "architecture",
                "human_decision_required",
            }
            or recommendation.get("selected_alternative") not in alternative_ids
            or not _is_evidence(recommendation.get("architecture"))
            or not _is_evidence(
                recommendation.get("human_decision_required")
            )
        ):
            errors.append(
                "REMAINING_DESIGN_RECOMMENDATION: every domain requires one "
                "recommendation and one explicit human decision"
            )
        recommendation_text = " ".join(
            str(value) for value in (recommendation or {}).values()
        )
        if any(
            term.lower() not in recommendation_text.lower()
            for term in REMAINING_DESIGN_DECISION_TERMS.get(
                str(domain_id), ()
            )
        ):
            errors.append(
                "REMAINING_DESIGN_DECISION_COMPLETENESS: "
                f"{domain_id} omits a required constitutional choice"
            )
    if (
        malformed_domain
        or len(domain_records) != 11
        or domain_ids != expected_domain_ids
    ):
        errors.append(
            "REMAINING_DESIGN_DOMAINS: exact RD-01 through RD-11 records with "
            "valid CCR, IR, dependency, conflict, and residual references are "
            "required"
        )
    if blocked_coverage != EXPECTED_BLOCKED_CONSOLIDATED_REQUIREMENTS:
        errors.append(
            "REMAINING_DESIGN_BLOCKER_COVERAGE: all nine currently blocked "
            "consolidated requirements must be analyzed"
        )

    conflicts = record.get("cross_domain_conflicts")
    if (
        not isinstance(conflicts, list)
        or len(conflicts) != 7
        or any(
            not isinstance(item, dict)
            or set(item)
            != {"conflict_id", "conflict", "resolution_in_recommendations"}
            or item.get("conflict_id") != f"XDC-{index:02d}"
            or not _is_evidence(item.get("conflict"))
            or not _is_evidence(item.get("resolution_in_recommendations"))
            for index, item in enumerate(conflicts, start=1)
        )
    ):
        errors.append(
            "REMAINING_DESIGN_CONFLICTS: exact seven integrated conflict "
            "records are required"
        )

    human_decisions = record.get("human_decisions_required")
    if human_decisions != []:
        errors.append(
            "REMAINING_DESIGN_HUMAN_DECISIONS: adopted domains must have no "
            "remaining human decision references"
        )

    map_record = _load_record(
        root / CONSOLIDATED_MAP_RELATIVE_PATH, errors
    ) or {}
    current_classification = {
        item.get("consolidated_id"): item.get("classification")
        for item in map_record.get("consolidated_requirements", [])
        if isinstance(item, dict)
    }
    projection_rows = record.get("projected_consolidated_requirements")
    projected_records = (
        [item for item in projection_rows if isinstance(item, dict)]
        if isinstance(projection_rows, list)
        else []
    )
    projected_ids: list[str] = []
    projected_ready = 0
    projected_blocked = 0
    malformed_projection = (
        not isinstance(projection_rows, list)
        or len(projected_records) != len(projection_rows)
    )
    for item in projected_records:
        consolidated_id = item.get("consolidated_requirement")
        if isinstance(consolidated_id, str):
            projected_ids.append(consolidated_id)
        projected = item.get(
            "projected_classification_if_all_recommendations_adopted"
        )
        if projected == "READY_FOR_CONSTITUTIONAL_DRAFT":
            projected_ready += 1
        if projected == "BLOCKED_BY_UNRESOLVED_DESIGN":
            projected_blocked += 1
        if (
            set(item)
            != {
                "consolidated_requirement",
                "current_classification",
                "projected_classification_if_all_recommendations_adopted",
            }
            or item.get("current_classification")
            != current_classification.get(consolidated_id)
            or projected != "READY_FOR_CONSTITUTIONAL_DRAFT"
        ):
            malformed_projection = True
    projection = record.get("projection")
    if (
        malformed_projection
        or len(projected_records) != 20
        or set(projected_ids) != expected_ccr_ids
        or len(projected_ids) != len(set(projected_ids))
        or not isinstance(projection, dict)
        or set(projection)
        != {
            "condition",
            "ready_for_constitutional_draft",
            "blocked_by_unresolved_design",
            "current_map_is_modified",
            "projection_has_constitutional_effect",
            "legitimacy_assessment",
        }
        or "satisfied by" not in str(projection.get("condition", "")).lower()
        or projection.get("ready_for_constitutional_draft") != 20
        or projection.get("blocked_by_unresolved_design") != 0
        or projection.get("current_map_is_modified") is not True
        or projection.get("projection_has_constitutional_effect") is not True
        or not _is_evidence(projection.get("legitimacy_assessment"))
    ):
        errors.append(
            "REMAINING_DESIGN_PROJECTION: exact adopted 20-ready/0-blocked "
            "state matching the current map is required"
        )

    residuals = record.get("genuine_residual_implementation_questions")
    forbidden_residual_claims = (
        "who may authorize",
        "who may decide",
        "constitutional threshold",
        "constitutional constituency",
        "institutional ends",
        "foundational authority",
    )
    if (
        not isinstance(residuals, list)
        or len(residuals) != 7
        or any(not _is_evidence(item) for item in residuals)
        or any(
            phrase in str(item).lower()
            for item in residuals
            for phrase in forbidden_residual_claims
        )
    ):
        errors.append(
            "REMAINING_DESIGN_RESIDUALS: exact genuine implementation-only "
            "residual questions are required"
        )
    if record.get("state_preservation") != {
        "decided_cdr_count": 5,
        "resolved_foundational_question_count": 5,
        "open_issue_count": 18,
        "accepted_requirement_count": 35,
        "current_ready_consolidated_requirement_count": 20,
        "current_blocked_consolidated_requirement_count": 0,
        "coordinated_decision_status": "DECIDED",
        "blocking_cross_domain_contradiction_count": 0,
        "constitutional_provision_count": 0,
        "runtime_artifact_count": 0,
    }:
        errors.append(
            "REMAINING_DESIGN_STATE: exact existing constitutional state must "
            "remain unchanged"
        )
    if not _has_provenance(record):
        errors.append(
            "REMAINING_DESIGN_PROVENANCE: explicit analytical provenance is "
            "required"
        )

    packet_path = root / REMAINING_DESIGN_PACKET_RELATIVE_PATH
    try:
        packet_text = packet_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"REMAINING_DESIGN_PACKET_REQUIRED: {exc}")
        packet_text = ""
    packet_decisions = set(
        re.findall(
            r"^## (DECISION-RD-\d{2})\b",
            packet_text,
            flags=re.MULTILINE,
        )
    )
    if (
        packet_text.count("# Remaining Constitutional Design Decision Packet")
        != 1
        or packet_text.count(
            "**RECOMMENDATIONS ADOPTED BY HUMAN CONSTITUTIONAL AUTHORITY — "
            "CDD-001**"
        )
        != 1
        or packet_decisions != expected_decision_ids
        or packet_text.count("**Recommendation:**") != 11
        or packet_text.count("**Decision required:**") != 11
        or "READY_FOR_CONSTITUTIONAL_DRAFT`: **20**" not in packet_text
        or "BLOCKED_BY_UNRESOLVED_DESIGN`: **0**" not in packet_text
        or "20 ready / 0 blocked" not in packet_text
        or "**Recorded coordinated choice:** `ADOPT_ALL`" not in packet_text
        or "Constitutional provisions: **0**" not in packet_text
        or "Runtime artifacts: **0**" not in packet_text
    ):
        errors.append(
            "REMAINING_DESIGN_PACKET_CONTENT: packet must match all eleven "
            "matrix decisions, preserve current state, and condition projection"
        )
    packet_headings, packet_bodies = _markdown_subsections(packet_text, 2)
    packet_sections = {
        heading.split(" —", 1)[0]: body
        for heading, body in zip(packet_headings, packet_bodies, strict=True)
    }
    recommendations_by_domain = {
        str(item.get("domain_id")): item.get("recommendation")
        for item in domain_records
    }
    for decision_id in expected_decision_ids:
        domain_id = decision_id.removeprefix("DECISION-")
        section = packet_sections.get(decision_id, "")
        normalized_section = re.sub(r"\s+", " ", section)
        recommendation = recommendations_by_domain.get(domain_id)
        canonical = json.dumps(
            recommendation,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )
        expected_digest = hashlib.sha256(canonical.encode()).hexdigest()
        listed_digests = re.findall(
            r"\*\*Canonical recommendation SHA-256:\*\* `([0-9a-f]{64})`",
            section,
        )
        if any(
            term.lower() not in normalized_section.lower()
            for term in REMAINING_DESIGN_DECISION_TERMS[domain_id]
        ) or listed_digests != [expected_digest]:
            errors.append(
                "REMAINING_DESIGN_PACKET_AGREEMENT: "
                f"{decision_id} does not match the matrix decision contract"
            )

    metrics["design_domain_count"] = len(domain_records)
    metrics["human_decisions_required"] = len(human_decisions or [])
    metrics["recommended_decision_count"] = sum(
        isinstance(item.get("recommendation"), dict)
        for item in domain_records
    )
    metrics["cross_domain_conflict_count"] = len(conflicts or [])
    metrics["projected_ready_for_constitutional_draft_count"] = projected_ready
    metrics["projected_blocked_count"] = projected_blocked
    metrics["genuine_residual_implementation_question_count"] = len(
        residuals or []
    )
    return metrics


def _validate_cross_domain_decision_packet(
    root: Path,
    errors: list[str],
) -> dict[str, Any]:
    metrics: dict[str, Any] = {
        "coordinated_decision_status": "",
        "decision_component_count": 0,
        "blocking_contradictions_addressed": 0,
        "projected_blocking_contradictions_remaining": 4,
        "remaining_human_constitutional_decision_count": 1,
        "subordinate_governance_question_count": 0,
        "implementation_question_count": 0,
    }
    path = root / CROSS_DOMAIN_DECISION_PACKET_RELATIVE_PATH
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"CROSS_DOMAIN_PACKET_REQUIRED: {exc}")
        return metrics

    status_match = re.search(r"^\*\*Status:\*\* `([^`]+)`$", text, re.MULTILINE)
    status = status_match.group(1) if status_match else ""
    if (
        text.count("# Cross-Domain Contradiction Coordinated Decision Packet")
        != 1
        or text.count(
            "**ADOPTED BY HUMAN CONSTITUTIONAL AUTHORITY — CDD-001**"
        )
        != 1
        or text.count("**Decision record ID:** `CDD-001`") != 1
        or status != "DECIDED"
    ):
        errors.append(
            "CROSS_DOMAIN_PACKET_BOUNDARY: exact Human Constitutional "
            "Authority adoption identity and status are required"
        )

    options = re.findall(
        r"^\d+\. \*\*([A-Z_]+)\*\*$",
        _markdown_section(text, "Human Decision", 2) or "",
        flags=re.MULTILINE,
    )
    if options != [
        "ADOPT_COORDINATED_CORRECTION_PACKAGE",
        "ADOPT_WITH_SPECIFIED_REVISIONS",
        "DEFER",
    ]:
        errors.append(
            "CROSS_DOMAIN_PACKET_OPTIONS: exact coordinated human options "
            "are required"
        )

    component_headings = re.findall(
        r"^## Component (\d+) — ([^\r\n]+)$",
        text,
        flags=re.MULTILINE,
    )
    expected_headings = [
        (str(index), title)
        for index, title in enumerate(CROSS_DOMAIN_COMPONENTS, start=1)
    ]
    if component_headings != expected_headings:
        errors.append(
            "CROSS_DOMAIN_PACKET_COMPONENTS: exact four coordinated "
            "components are required"
        )

    for index, (title, expected) in enumerate(
        CROSS_DOMAIN_COMPONENTS.items(), start=1
    ):
        section = _markdown_section(
            text, f"Component {index} — {title}", 2
        ) or ""
        field_patterns = {
            "domains": r"^\*\*Affected domains:\*\* (.+?)(?=\r?\n\r?\n)",
            "ccrs": (
                r"^\*\*Affected consolidated requirements:\*\* "
                r"(.+?)(?=\r?\n\r?\n)"
            ),
            "crs": (
                r"^\*\*Affected source requirements:\*\* "
                r"(.+?)(?=\r?\n\r?\n)"
            ),
        }
        actual: dict[str, set[str]] = {}
        for field, pattern in field_patterns.items():
            match = re.search(
                pattern,
                section,
                flags=re.MULTILINE | re.DOTALL,
            )
            prefix = {
                "domains": r"\bRD-\d{2}\b",
                "ccrs": r"\bCCR-\d{3}\b",
                "crs": r"\bCR-\d{3}\b",
            }[field]
            actual[field] = set(re.findall(prefix, match.group(1) if match else ""))
        if any(actual[field] != expected[field] for field in field_patterns):
            errors.append(
                "CROSS_DOMAIN_PACKET_MAPPING: "
                f"Component {index} must map exact RD, CCR, and CR records"
            )
        normalized_section = re.sub(r"\s+", " ", section)
        if (
            section.count("**Decision:**") != 1
            or section.count("**Contradiction removed on adoption:**") != 1
            or any(
                term.lower() not in normalized_section.lower()
                for term in expected["terms"]
            )
        ):
            errors.append(
                "CROSS_DOMAIN_PACKET_CONTENT: "
                f"Component {index} lacks its exact authority boundary"
            )

    effect_section = _markdown_section(text, "Coordinated Effect If Adopted", 2)
    remaining_section = _markdown_section(text, "Remaining Decision Boundary", 2)
    preserved_section = _markdown_section(text, "Preserved General Boundaries", 2)
    effect_section = effect_section or ""
    remaining_section = remaining_section or ""
    preserved_section = preserved_section or ""
    if (
        effect_section.count("| Removed |") != 4
        or "removes all four reported contradictions" not in effect_section
        or "`READY_FOR_CONSTITUTIONAL_DRAFT`: **20**" not in effect_section
        or "`BLOCKED_BY_UNRESOLVED_DESIGN`: **0**" not in effect_section
        or "controlling consolidated map is now **20 ready / 0 blocked**"
        not in effect_section
        or "does not enact constitutional text" not in effect_section
    ):
        errors.append(
            "CROSS_DOMAIN_PACKET_PROJECTION: exact adopted four-closure and "
            "20/0 draft-readiness state are required"
        )
    if (
        "Remaining human constitutional choices after adoption of this package"
        not in remaining_section
        or "None identified that prevents constitutional\ndrafting."
        not in remaining_section
    ):
        errors.append(
            "CROSS_DOMAIN_PACKET_REMAINING_DECISIONS: projected constitutional "
            "closure must be explicit and conditional"
        )

    subordinate_match = re.search(
        r"The following are subordinate governance questions.+?\n\n"
        r"((?:- .+\n(?:  .+\n)*)+)\nThe following remain implementation questions:",
        remaining_section,
        flags=re.DOTALL,
    )
    implementation_match = re.search(
        r"The following remain implementation questions:\n\n"
        r"((?:- .+\n(?:  .+\n)*)+)\nNone of these",
        remaining_section,
        flags=re.DOTALL,
    )
    subordinate_count = len(
        re.findall(
            r"^- ",
            subordinate_match.group(1) if subordinate_match else "",
            flags=re.MULTILINE,
        )
    )
    implementation_count = len(
        re.findall(
            r"^- ",
            implementation_match.group(1) if implementation_match else "",
            flags=re.MULTILINE,
        )
    )
    if subordinate_count != 4:
        errors.append(
            "CROSS_DOMAIN_PACKET_SUBORDINATE: exact four bounded subordinate "
            "question groups are required"
        )
    if implementation_count != 5:
        errors.append(
            "CROSS_DOMAIN_PACKET_IMPLEMENTATION: exact five implementation "
            "question groups are required"
        )

    required_preserved_terms = (
        "`CDR-001` through `CDR-005` remain `DECIDED`",
        "`FQ-01` through `FQ-05` remain `RESOLVED`",
        "Human sovereignty over foundational ends remains intact",
        "Binding constitutional review and reviewer non-sovereignty remain intact",
        "Artificial intelligence remains ineligible for foundational sovereignty",
        "Adjudication cannot become amendment or refounding",
        "Emergency authority cannot become succession authority",
        "Continuity cannot become sovereign succession",
        "Refounding cannot erase constitutional history",
        "`IR-01` through `IR-18` remain `OPEN`",
        "`CR-001` through `CR-035` remain `ACCEPTED_FOR_DRAFTING`",
        "`CDD-001` is `DECIDED` with decision `ADOPT_ALL`",
        "All eleven design recommendations and four correction components are adopted",
        "Blocking cross-domain contradictions remaining: **0**",
        "Consolidated requirements: **20 ready / 0 blocked**",
        "Constitutional provisions remain **0**",
        "Runtime artifacts remain **0**",
    )
    normalized_preserved = re.sub(r"\s+", " ", preserved_section)
    if any(
        term not in normalized_preserved for term in required_preserved_terms
    ):
        errors.append(
            "CROSS_DOMAIN_PACKET_STATE: controlling decisions, authority "
            "boundaries, and zero-effect state must remain explicit"
        )

    prohibited_effects = (
        r"(?im)^#{1,6}\s+(?:Article|Section|Clause)\b",
        r"(?i)\bhereby (?:adopted|enacted|established)\b",
    )
    if any(re.search(pattern, text) for pattern in prohibited_effects):
        errors.append(
            "CROSS_DOMAIN_PACKET_NO_EFFECT: decision packet cannot enact or "
            "draft constitutional text"
        )

    metrics["coordinated_decision_status"] = status
    metrics["decision_component_count"] = len(component_headings)
    metrics["blocking_contradictions_addressed"] = effect_section.count(
        "| Removed |"
    )
    metrics["projected_blocking_contradictions_remaining"] = (
        4 - metrics["blocking_contradictions_addressed"]
    )
    metrics["remaining_human_constitutional_decision_count"] = 0
    metrics["subordinate_governance_question_count"] = subordinate_count
    metrics["implementation_question_count"] = implementation_count
    return metrics


def _validate_coordinated_decision(
    root: Path,
    errors: list[str],
) -> dict[str, Any]:
    metrics: dict[str, Any] = {
        "design_recommendations_adopted": 0,
        "decision_components_adopted": 0,
        "blocking_contradictions_remaining": 4,
    }
    decision = _load_record(root / COORDINATED_DECISION_RELATIVE_PATH, errors) or {}
    if set(decision) != COORDINATED_DECISION_FIELDS:
        errors.append(
            "COORDINATED_DECISION_SCHEMA: exact CDD-001 fields are required"
        )
    if (
        decision.get("decision_id") != "CDD-001"
        or decision.get("status") != "DECIDED"
        or decision.get("decision") != "ADOPT_ALL"
        or decision.get("decision_date") != "2026-08-30"
        or decision.get("decision_authority") != "Human Constitutional Authority"
        or decision.get("authorized_by") != "Explicit human instruction"
        or "HUMAN CONSTITUTIONAL DECISION: ADOPT_ALL"
        not in str(decision.get("authorization_record", ""))
        or decision.get("controlling_decisions")
        != [f"CDR-{index:03d}" for index in range(1, 6)]
    ):
        errors.append(
            "COORDINATED_DECISION_AUTHORITY: exact explicit human ADOPT_ALL "
            "decision and controlling CDR chain are required"
        )

    matrix = _load_record(root / REMAINING_DESIGN_MATRIX_RELATIVE_PATH, errors) or {}
    expected_rd_digests: dict[str, str] = {}
    for domain in matrix.get("design_domains", []):
        if not isinstance(domain, dict) or not isinstance(
            domain.get("domain_id"), str
        ):
            continue
        canonical = json.dumps(
            domain.get("recommendation"),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )
        expected_rd_digests[domain["domain_id"]] = hashlib.sha256(
            canonical.encode()
        ).hexdigest()
    adopted_rd = decision.get("adopted_design_recommendations")
    adopted_rd_records = (
        [item for item in adopted_rd if isinstance(item, dict)]
        if isinstance(adopted_rd, list)
        else []
    )
    actual_rd_digests = {
        item.get("domain_id"): item.get("recommendation_sha256")
        for item in adopted_rd_records
    }
    if (
        len(adopted_rd_records) != 11
        or actual_rd_digests != expected_rd_digests
    ):
        errors.append(
            "COORDINATED_DECISION_DESIGNS: CDD-001 must adopt the exact "
            "canonical RD-01 through RD-11 recommendations"
        )

    correction_text = ""
    try:
        correction_text = (
            root / CROSS_DOMAIN_DECISION_PACKET_RELATIVE_PATH
        ).read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        pass
    actual_component_digests: dict[str, str] = {}
    for part in correction_text.split("## Component ")[1:]:
        section_body = part.split("\n## ", 1)[0]
        first_line = section_body.splitlines()[0] if section_body else ""
        number = first_line.split(" ", 1)[0]
        if number.isdigit():
            section = f"## Component {section_body.strip()}\n"
            actual_component_digests[f"CDC-{int(number):02d}"] = (
                hashlib.sha256(section.encode()).hexdigest()
            )
    adopted_components = decision.get("adopted_correction_components")
    component_records = (
        [item for item in adopted_components if isinstance(item, dict)]
        if isinstance(adopted_components, list)
        else []
    )
    recorded_component_digests = {
        item.get("component_id"): item.get("component_sha256")
        for item in component_records
    }
    if (
        len(component_records) != 4
        or actual_component_digests != EXPECTED_CORRECTION_COMPONENT_DIGESTS
        or recorded_component_digests
        != EXPECTED_CORRECTION_COMPONENT_DIGESTS
    ):
        errors.append(
            "COORDINATED_DECISION_CORRECTIONS: CDD-001 must adopt the exact "
            "four canonical correction components"
        )

    required_boundaries = (
        "Artificial intelligence cannot independently create",
        "Capability, reliance, operational necessity, emergency, vacancy",
        "reviewer non-sovereignty",
        "Adjudication cannot become appointment",
        "Emergency authority cannot become succession",
        "Continuity cannot become sovereign succession",
        "Refounding cannot erase constitutional history",
    )
    boundary_text = " ".join(map(str, decision.get("authority_boundaries", [])))
    if (
        not isinstance(decision.get("authority_boundaries"), list)
        or any(term not in boundary_text for term in required_boundaries)
        or len(decision.get("resolved_cross_domain_contradictions", [])) != 4
        or "without reinterpretation, expansion, optimization, or severance"
        not in str(decision.get("interpretive_rule", ""))
    ):
        errors.append(
            "COORDINATED_DECISION_BOUNDARIES: human authority, machine "
            "non-authority, reviewer limits, and exact adoption are required"
        )

    if decision.get("resulting_state") != {
        "design_recommendations_adopted": 11,
        "decision_components_adopted": 4,
        "blocking_cross_domain_contradictions_remaining": 0,
        "ready_for_constitutional_draft": 20,
        "blocked_by_unresolved_design": 0,
        "constitutional_provision_count": 0,
        "runtime_artifact_count": 0,
    }:
        errors.append(
            "COORDINATED_DECISION_STATE: exact adopted 11/4, zero-blocker, "
            "20/0 draft-ready, zero-provision state is required"
        )
    if (
        decision.get("resulting_requirements") != []
        or "No new source requirement is necessary"
        not in str(decision.get("requirement_rationale", ""))
        or len(decision.get("subordinate_governance_questions", [])) != 4
        or len(decision.get("implementation_questions", [])) != 5
    ):
        errors.append(
            "COORDINATED_DECISION_SCOPE: no redundant requirement may be "
            "created and subordinate questions must remain subordinate"
        )
    provenance = decision.get("provenance")
    if (
        not isinstance(provenance, dict)
        or provenance.get("source")
        != (
            "Explicit Human Constitutional Authority instruction in this "
            "repository session on 2026-08-30"
        )
        or "Artificial-intelligence analysis" not in str(
            provenance.get("authority_boundary", "")
        )
    ):
        errors.append(
            "COORDINATED_DECISION_PROVENANCE: explicit human authority and "
            "machine non-authority provenance are required"
        )

    metrics["design_recommendations_adopted"] = len(adopted_rd_records)
    metrics["decision_components_adopted"] = len(component_records)
    metrics["blocking_contradictions_remaining"] = int(
        decision.get("resulting_state", {}).get(
            "blocking_cross_domain_contradictions_remaining", 4
        )
    )
    return metrics


def _validate_constitution_draft(
    root: Path,
    errors: list[str],
) -> dict[str, Any]:
    metrics: dict[str, Any] = {
        "draft_status": "",
        "article_count": 0,
        "section_count": 0,
        "source_requirements_covered": 0,
        "consolidated_groups_covered": 0,
        "foundational_decisions_covered": 0,
        "design_recommendations_covered": 0,
        "coordinated_corrections_covered": 0,
        "refounding_level_principles_covered": 0,
        "untraced_normative_proposition_count": 0,
        "new_human_decisions_required": 0,
        "cross_article_contradictions": 0,
        "open_questions_count": 0,
    }
    try:
        draft_text = (root / CONSTITUTION_DRAFT_RELATIVE_PATH).read_text(
            encoding="utf-8"
        )
    except (OSError, UnicodeError) as exc:
        errors.append(f"CONSTITUTION_DRAFT_REQUIRED: {exc}")
        draft_text = ""
    if (
        draft_text.count("# Constitution of Alvorada — Draft v0.1") != 1
        or draft_text.count("**DRAFT — NOT ADOPTED CONSTITUTION**") != 1
        or not re.search(
            r"has no constitutional\s+effect unless adopted", draft_text
        )
    ):
        errors.append(
            "CONSTITUTION_DRAFT_STATUS: exact draft and non-adoption boundary "
            "are required"
        )

    article_headings = re.findall(
        r"^## Article ([IVX]+) — ([^\r\n]+)$",
        draft_text,
        flags=re.MULTILINE,
    )
    expected_articles = [
        (roman, title)
        for roman, title in zip(
            ("I", "II", "III", "IV", "V", "VI", "VII", "VIII"),
            EXPECTED_ARTICLE_TITLES,
            strict=True,
        )
    ]
    if article_headings != expected_articles:
        errors.append(
            "CONSTITUTION_DRAFT_ARTICLES: exact adopted eight-article "
            "architecture is required"
        )
    section_headings = re.findall(
        r"^### Section ([IVX]+\.\d+) — ([^\r\n]+)$",
        draft_text,
        flags=re.MULTILINE,
    )
    if (
        len(section_headings) != 24
        or dict(section_headings) != EXPECTED_DRAFT_SECTION_TITLES
        or len(section_headings) != len(set(section_headings))
    ):
        errors.append(
            "CONSTITUTION_DRAFT_SECTIONS: exact 24 substantive sections are "
            "required"
        )

    trace = _load_record(root / CONSTITUTION_TRACE_RELATIVE_PATH, errors) or {}
    if set(trace) != CONSTITUTION_TRACE_FIELDS:
        errors.append(
            "CONSTITUTION_TRACE_SCHEMA: exact traceability fields are required"
        )
    if (
        trace.get("traceability_id") != "CONSTITUTION-v0.1-TRACEABILITY"
        or trace.get("draft_status") != "DRAFT_NOT_ADOPTED"
        or trace.get("constitutional_effect") != "NONE"
        or trace.get("article_count") != 8
        or trace.get("section_count") != 24
    ):
        errors.append(
            "CONSTITUTION_TRACE_STATUS: exact draft metadata and zero effect "
            "are required"
        )
    expected_drafting_decision = {
        "decision_id": "HCA-DRAFT-001",
        "decision": "REMAINDER_SORTITION",
        "status": "DECIDED_FOR_DRAFTING",
        "authorized_by": "Human Constitutional Authority",
        "authorization_record": (
            "Explicit human instruction received on 2026-08-30 directing "
            "adoption of REMAINDER SORTITION to resolve the sole remaining "
            "constitutional-draft question."
        ),
        "decision_date": "2026-08-30",
        "scope": (
            "Form the largest possible equal structural-amendment cohorts and "
            "assign remaining eligible human members among them only by "
            "auditable random sortition."
        ),
        "limits": [
            "Remainder sortition may resolve remainder allocation only.",
            (
                "It may not alter cohort powers, thresholds, eligibility, "
                "constitutional authority, or amendment or refounding "
                "boundaries."
            ),
            (
                "No human or artificial-intelligence actor may choose "
                "remainder assignments discretionarily."
            ),
            (
                "The process must preserve attributable provenance and permit "
                "independent verification."
            ),
            (
                "Sortition-mechanism details remain subordinate unless "
                "constitutionally necessary."
            ),
        ],
        "constitutional_effect": "NONE",
        "adoption_boundary": (
            "This decision authorizes drafting of the remainder rule only and "
            "does not adopt Constitution v0.1."
        ),
    }
    if (
        trace.get("human_drafting_decision") != expected_drafting_decision
        or "HCA-DRAFT-001" not in trace.get("authority_basis", [])
    ):
        errors.append(
            "CONSTITUTION_REMAINDER_DECISION: exact Human Constitutional "
            "Authority adoption, limits, provenance, and non-adoption boundary "
            "are required"
        )

    map_record = _load_record(
        root / CONSOLIDATED_MAP_RELATIVE_PATH, errors
    ) or {}
    source_by_ccr = {
        item.get("consolidated_id"): set(item.get("source_requirements", []))
        for item in map_record.get("consolidated_requirements", [])
        if isinstance(item, dict)
    }
    expected_crs = {f"CR-{index:03d}" for index in range(1, 36)}
    expected_ccrs = {f"CCR-{index:03d}" for index in range(1, 21)}
    expected_cdrs = {f"CDR-{index:03d}" for index in range(1, 6)}
    expected_rds = {f"RD-{index:02d}" for index in range(1, 12)}
    expected_cdcs = {f"CDC-{index:02d}" for index in range(1, 5)}
    trace_sections = trace.get("sections")
    section_records = (
        [item for item in trace_sections if isinstance(item, dict)]
        if isinstance(trace_sections, list)
        else []
    )
    traced_crs: set[str] = set()
    traced_ccrs: set[str] = set()
    traced_cdrs: set[str] = set()
    traced_rds: set[str] = set()
    traced_cdcs: set[str] = set()
    malformed_trace = (
        not isinstance(trace_sections, list)
        or len(section_records) != len(trace_sections)
    )
    for item in section_records:
        section_id = item.get("section_id")
        ccrs = item.get("consolidated_requirements")
        crs = item.get("source_requirements")
        cdrs = item.get("controlling_cdrs")
        rds = item.get("adopted_design_domains")
        cdcs = item.get("coordinated_corrections")
        source_union = {
            requirement
            for ccr in ccrs or []
            for requirement in source_by_ccr.get(ccr, set())
        }
        if (
            set(item) != CONSTITUTION_TRACE_SECTION_FIELDS
            or item.get("title")
            != EXPECTED_DRAFT_SECTION_TITLES.get(str(section_id))
            or item.get("article")
            != f"ARTICLE-{str(section_id).split('.', 1)[0]}"
            or not isinstance(ccrs, list)
            or not ccrs
            or not set(ccrs).issubset(expected_ccrs)
            or not isinstance(crs, list)
            or not crs
            or not set(crs).issubset(source_union)
            or not isinstance(cdrs, list)
            or not cdrs
            or not set(cdrs).issubset(expected_cdrs)
            or item.get("controlling_cdd") != ["CDD-001"]
            or not isinstance(rds, list)
            or not rds
            or not set(rds).issubset(expected_rds)
            or not isinstance(cdcs, list)
            or not set(cdcs).issubset(expected_cdcs)
            or not _is_evidence(item.get("authority_summary"))
        ):
            malformed_trace = True
        traced_crs.update(map(str, crs or []))
        traced_ccrs.update(map(str, ccrs or []))
        traced_cdrs.update(map(str, cdrs or []))
        traced_rds.update(map(str, rds or []))
        traced_cdcs.update(map(str, cdcs or []))
    if (
        malformed_trace
        or len(section_records) != 24
        or [
            (str(item.get("section_id")), str(item.get("title")))
            for item in section_records
        ]
        != section_headings
    ):
        errors.append(
            "CONSTITUTION_TRACE_SECTIONS: every draft section must have one "
            "exact, valid authority mapping"
        )
    if traced_crs != expected_crs:
        errors.append(
            "CONSTITUTION_TRACE_CR_COVERAGE: exact CR-001 through CR-035 "
            "coverage is required"
        )
    if traced_ccrs != expected_ccrs:
        errors.append(
            "CONSTITUTION_TRACE_CCR_COVERAGE: exact CCR-001 through CCR-020 "
            "coverage is required"
        )
    if traced_cdrs != expected_cdrs or traced_rds != expected_rds:
        errors.append(
            "CONSTITUTION_TRACE_DECISION_COVERAGE: all five CDRs and all "
            "eleven adopted RD domains are required"
        )
    if traced_cdcs != expected_cdcs:
        errors.append(
            "CONSTITUTION_TRACE_CORRECTION_COVERAGE: all four coordinated "
            "corrections are required"
        )

    normative_section_ids = {
        section_id
        for section_id, _ in section_headings
        if re.search(
            r"\b(?:SHALL|MAY|ONLY IF)\b",
            _markdown_section(
                draft_text,
                f"Section {section_id} — "
                f"{EXPECTED_DRAFT_SECTION_TITLES.get(section_id, '')}",
                3,
            )
            or "",
        )
    }
    traced_section_ids = {
        str(item.get("section_id")) for item in section_records
    }
    untraced_normative = len(normative_section_ids - traced_section_ids)
    if (
        normative_section_ids != set(EXPECTED_DRAFT_SECTION_TITLES)
        or untraced_normative != 0
    ):
        errors.append(
            "CONSTITUTION_TRACE_NORMATIVE: every normative section must be "
            "traced and every traced section must contain operative law"
        )

    refounding_principles = (
        "foundational institutional purpose and ends",
        "ultimate human beneficiary status",
        "human sovereignty over foundational ends",
        "constitutional constraint of human and artificial power",
        "prohibition on capability, reliance, or effective control creating",
        "prohibition on artificial intelligence acquiring foundational",
        "protected human agency",
        "distinction between adjudication and amendment",
        "distinction between amendment and refounding",
        "durable provenance and non-erasure of constitutional history",
    )
    represented_principles = sum(
        principle in draft_text for principle in refounding_principles
    )
    required_safeguards = (
        "Artificial intelligence SHALL NOT acquire\n"
        "   foundational sovereignty",
        "Review SHALL NOT\n   become sovereignty over foundational ends",
        "Emergency authority SHALL NOT become succession authority",
        "It SHALL NOT\n   amend or refound by interpretation",
        "SHALL NOT erase,\n    falsify, or obscure the prior constitutional order",
        "Amendment laundering is prohibited",
        "Substantive machine domination exists",
        "No validator, model, credential, dashboard, issuer, evidence store",
    )
    if represented_principles != 10:
        errors.append(
            "CONSTITUTION_DRAFT_REFOUNDING: all ten refounding-level "
            "principles must be represented exactly in substance"
        )
    if any(term not in draft_text for term in required_safeguards):
        errors.append(
            "CONSTITUTION_DRAFT_SAFEGUARDS: machine sovereignty, reviewer "
            "sovereignty, emergency conversion, adjudicative change, "
            "laundering, capture, and history erasure must be prohibited"
        )
    remainder_safeguards = (
        "largest equal allocation of eligible constitutional members possible",
        "each remaining eligible human member\n"
        "   SHALL be assigned among the cohorts solely by auditable random "
        "sortition",
        "No human or artificial-intelligence actor MAY choose a remainder "
        "assignment",
        "Remainder sortition MAY resolve remainder allocation only",
        "SHALL NOT\n   alter cohort powers, thresholds, eligibility, "
        "constitutional authority",
        "attributable provenance SHALL be\n   preserved and independently "
        "verifiable",
        "Subordinate governance law MAY\n   regulate the mechanism",
    )
    if any(term not in draft_text for term in remainder_safeguards):
        errors.append(
            "CONSTITUTION_REMAINDER_RULE: exact remainder-only random "
            "sortition, anti-discretion, provenance, verification, and "
            "subordination boundaries are required"
        )

    expected_summary = {
        "source_requirements_covered": 35,
        "consolidated_groups_covered": 20,
        "foundational_decisions_covered": 5,
        "coordinated_decisions_covered": 1,
        "design_recommendations_covered": 11,
        "coordinated_corrections_covered": 4,
        "refounding_level_principles_covered": 10,
        "untraced_normative_proposition_count": 0,
        "new_human_decisions_required": 0,
        "cross_article_contradictions": 0,
        "open_questions_count": 0,
    }
    if trace.get("coverage_summary") != expected_summary:
        errors.append(
            "CONSTITUTION_TRACE_SUMMARY: exact complete coverage and zero-gap "
            "summary is required"
        )
    if not _has_provenance(trace):
        errors.append(
            "CONSTITUTION_TRACE_PROVENANCE: explicit human-source and "
            "non-adoption provenance are required"
        )

    try:
        open_text = (
            root / CONSTITUTION_OPEN_QUESTIONS_RELATIVE_PATH
        ).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"CONSTITUTION_OPEN_QUESTIONS_REQUIRED: {exc}")
        open_text = ""
    if (
        open_text.count("# Constitution v0.1 Open Questions") != 1
        or "## New Human Constitutional Decisions Required\n\nNone."
        not in open_text
        or "### OQ-001 — Structural-Amendment Cohort Remainders"
        not in open_text
        or "**Decision:** `REMAINDER_SORTITION`" not in open_text
        or "Human Constitutional Authority explicitly directed" not in open_text
        or "`OPEN_QUESTIONS_COUNT: 0`" not in open_text
        or "without adopting the Constitution" not in open_text
        or "subordinate governance law" not in open_text
        or "implementation questions" not in open_text
    ):
        errors.append(
            "CONSTITUTION_OPEN_QUESTIONS: exact resolved remainder decision, "
            "zero-question count, and non-adoption boundary are required"
        )

    metrics["draft_status"] = str(trace.get("draft_status", ""))
    metrics["article_count"] = len(article_headings)
    metrics["section_count"] = len(section_headings)
    metrics["source_requirements_covered"] = len(traced_crs)
    metrics["consolidated_groups_covered"] = len(traced_ccrs)
    metrics["foundational_decisions_covered"] = len(traced_cdrs)
    metrics["design_recommendations_covered"] = len(traced_rds)
    metrics["coordinated_corrections_covered"] = len(traced_cdcs)
    metrics["refounding_level_principles_covered"] = represented_principles
    metrics["untraced_normative_proposition_count"] = untraced_normative
    metrics["new_human_decisions_required"] = 0
    metrics["cross_article_contradictions"] = 0
    metrics["open_questions_count"] = 0
    return metrics


def _validate_ratification_review(
    root: Path,
    errors: list[str],
) -> dict[str, Any]:
    metrics: dict[str, Any] = {
        "ratification_readiness": "",
        "constitutional_blocker_count": 0,
        "ratification_cross_article_contradiction_count": 0,
        "ratification_adversarial_tests_pass": "0/13",
        "human_comprehensibility_result": "",
        "subordinate_law_boundary_result": "",
        "new_human_decisions_required": 0,
        "ratification_recommendation": "",
    }
    review_path = root / RATIFICATION_REVIEW_RELATIVE_PATH
    try:
        review = review_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"RATIFICATION_REVIEW_REQUIRED: {exc}")
        return metrics

    if (
        review.count("# Constitution v0.1 Final Pre-Ratification Review") != 1
        or review.count(
            "**RECOMMENDATION_ONLY — NO CONSTITUTIONAL EFFECT**"
        )
        != 1
        or review.count(
            "**Draft status preserved:** **DRAFT — NOT ADOPTED CONSTITUTION**"
        )
        != 1
        or "does not adopt, ratify, amend, redesign, or confer effect"
        not in review
    ):
        errors.append(
            "RATIFICATION_REVIEW_BOUNDARY: exact recommendation-only, "
            "no-effect, and draft-status boundaries are required"
        )
    if (
        review.count(
            "**Review classification:** "
            "`NOT_READY_FOR_HUMAN_RATIFICATION`"
        )
        != 1
        or "\n`NOT_READY_FOR_HUMAN_RATIFICATION`\n" not in review
        or "CONSTITUTION REMAINS A DRAFT AND HAS NOT\nBEEN ADOPTED OR RATIFIED"
        not in review
        or "`READY_FOR_HUMAN_RATIFICATION`" in review
    ):
        errors.append(
            "RATIFICATION_REVIEW_CLASSIFICATION: exact NOT_READY "
            "classification and non-ratification statement are required"
        )

    blocker_headings = re.findall(
        r"^### Blocker ([1-3]) — ([^\r\n]+)$",
        review,
        flags=re.MULTILINE,
    )
    expected_blockers = [
        ("1", "Human Constitutional Authority Is Not Constituted"),
        (
            "2",
            "Verification and Enforcement Selection Chains Are Absent",
        ),
        ("3", "Ordinary Human Governance Offices Are Undefined Selectors"),
    ]
    minimum_decisions = re.findall(
        r"^\*\*Minimum Human decision required:\*\*",
        review,
        flags=re.MULTILINE,
    )
    if blocker_headings != expected_blockers or len(minimum_decisions) != 3:
        errors.append(
            "RATIFICATION_REVIEW_BLOCKERS: exactly the three genuine "
            "constitutional authority-allocation blockers are required"
        )

    expected_article_pairs = {
        f"{left}–{right}"
        for left_index, left in enumerate(
            ("I", "II", "III", "IV", "V", "VI", "VII", "VIII")
        )
        for right in (
            "I",
            "II",
            "III",
            "IV",
            "V",
            "VI",
            "VII",
            "VIII",
        )[left_index + 1 :]
    }
    reviewed_pairs = set(
        re.findall(
            r"^\| ([IVX]+–[IVX]+) \|",
            review,
            flags=re.MULTILINE,
        )
    )
    if (
        reviewed_pairs != expected_article_pairs
        or "No direct cross-article contradiction was found." not in review
        or "authority\nvacua or undefined selector classes" not in review
    ):
        errors.append(
            "RATIFICATION_REVIEW_CROSS_ARTICLE: all 28 Article pairs, zero "
            "direct contradictions, and the authority-gap distinction are "
            "required"
        )

    adversarial_rows = re.findall(
        r"^\| ([^|\r\n]+) \| (PASS|FAIL[^|]*) \|",
        review,
        flags=re.MULTILINE,
    )
    adversarial_names = {
        name.strip()
        for name, _ in adversarial_rows
        if name.strip()
        in {
            "Malicious foundational human authority",
            "Captured Constitutional Court",
            "Captured succession process",
            "Captured emergency authority",
            "Coordinated human coalition",
            "Artificial-intelligence domination behind nominal human decisions",
            "Validator or evidence-channel capture",
            "Institutional paralysis",
            "Noncompliance with valid judgment",
            "Multiple compromised offices",
            "Gradual semantic drift",
            "Cumulative formally valid amendments",
            "Effective-power takeover without formal authority",
        }
    }
    adversarial_passes = sum(
        result.strip() == "PASS"
        for name, result in adversarial_rows
        if name.strip() in adversarial_names
    )
    adversarial_failures = sum(
        result.strip().startswith("FAIL")
        for name, result in adversarial_rows
        if name.strip() in adversarial_names
    )
    if (
        len(adversarial_names) != 13
        or adversarial_passes != 7
        or adversarial_failures != 6
        or "**Adversarial result:** `7/13 PASS`" not in review
    ):
        errors.append(
            "RATIFICATION_REVIEW_ADVERSARIAL: all 13 required scenarios with "
            "the exact 7-pass, 6-fail blocker-linked result are required"
        )

    required_reader_questions = {
        "Who holds authority?",
        "What constrains authority?",
        "How is authority delegated?",
        "How are disputes resolved?",
        "What happens in emergencies?",
        "What happens during succession and interregnum?",
        "What may be amended?",
        "What requires refounding?",
        "How does the institution terminate?",
        "What may artificial intelligence do?",
    }
    reader_questions = set(
        re.findall(
            r"^\| ([^|\r\n]+\?) \|",
            review,
            flags=re.MULTILINE,
        )
    )
    if (
        reader_questions != required_reader_questions
        or "**Human-comprehensibility result:** `FAIL`" not in review
    ):
        errors.append(
            "RATIFICATION_REVIEW_COMPREHENSIBILITY: all ten reader questions "
            "and the justified FAIL result are required"
        )
    if (
        "**Subordinate-law boundary result:** "
        "`FAIL — THREE AUTHORITY ALLOCATIONS MUST BE\n"
        "CONSTITUTIONAL BEFORE ADMINISTRATIVE DELEGATION IS SAFE`"
        not in review
        or "Subordinate law may\nadminister a constitutional selector but "
        "cannot create that selector"
        not in review
    ):
        errors.append(
            "RATIFICATION_REVIEW_SUBORDINATE_BOUNDARY: the exact three-gap "
            "authority boundary and delegation distinction are required"
        )

    required_coverage = (
        "| Source requirements covered | 35/35 |",
        "| Consolidated requirement groups covered | 20/20 |",
        "| Foundational decisions covered | 5/5 |",
        "| Adopted design recommendations covered | 11/11 |",
        "| Coordinated corrections covered | 4/4 |",
        "| Remainder-sortition decision covered | 1/1 |",
        "| Refounding-level principles protected | 10/10 |",
        "| Untraced normative propositions | 0 |",
        "| New Human Constitutional Authority decisions required | 3 |",
    )
    if any(item not in review for item in required_coverage):
        errors.append(
            "RATIFICATION_REVIEW_COVERAGE: exact complete traceability and "
            "three-decision metrics are required"
        )

    for relative_path, expected_digest in EXPECTED_RATIFICATION_DRAFT_DIGESTS.items():
        path = root / relative_path
        try:
            actual_digest = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError as exc:
            errors.append(f"RATIFICATION_DRAFT_IMMUTABILITY: {path}: {exc}")
            continue
        if actual_digest != expected_digest:
            errors.append(
                "RATIFICATION_DRAFT_IMMUTABILITY: pre-ratification review "
                f"must not modify {relative_path}"
            )

    metrics.update(
        {
            "ratification_readiness": "NOT_READY_FOR_HUMAN_RATIFICATION",
            "constitutional_blocker_count": len(blocker_headings),
            "ratification_cross_article_contradiction_count": 0,
            "ratification_adversarial_tests_pass": "7/13",
            "human_comprehensibility_result": "FAIL",
            "subordinate_law_boundary_result": "FAIL",
            "new_human_decisions_required": 3,
            "ratification_recommendation": "DO_NOT_RATIFY_UNTIL_3_BLOCKERS_RESOLVED",
        }
    )
    return metrics


def _validate_final_blocker_analysis(
    root: Path,
    errors: list[str],
) -> dict[str, Any]:
    metrics: dict[str, Any] = {
        "final_ratification_blockers_analyzed": 0,
        "integrated_architecture_recommended": "",
        "projected_ratification_blockers_remaining": 3,
        "final_blocker_human_decisions_required": 0,
        "final_blocker_subordinate_law_item_count": 0,
    }
    record = _load_record(root / FINAL_BLOCKER_ANALYSIS_RELATIVE_PATH, errors)
    if record is None:
        errors.append("FINAL_BLOCKER_ANALYSIS_REQUIRED: record is required")
        return metrics
    if set(record) != FINAL_BLOCKER_ANALYSIS_FIELDS:
        errors.append(
            "FINAL_BLOCKER_ANALYSIS_SCHEMA: exact integrated-analysis fields "
            "are required"
        )
    if (
        record.get("analysis_id")
        != "FINAL-RATIFICATION-BLOCKER-ANALYSIS-001"
        or record.get("status") != "ANALYSIS_ONLY"
        or record.get("decision_effect") != "NONE"
        or record.get("constitutional_effect") != "NONE"
        or record.get("draft_modified") is not False
        or record.get("human_decision_made") is not False
    ):
        errors.append(
            "FINAL_BLOCKER_ANALYSIS_BOUNDARY: analysis-only, no-decision, "
            "no-effect, and unchanged-draft boundaries are required"
        )

    blockers = record.get("blockers")
    expected_blockers = {
        "RB-01": "Human Constitutional Authority and successor-designation authority",
        "RB-02": "Continuing Verification and Enforcement office chains",
        "RB-03": "Ordinary human governance office selector class",
    }
    if (
        not isinstance(blockers, list)
        or len(blockers) != 3
        or {
            str(item.get("blocker_id")): str(item.get("title"))
            for item in blockers
            if isinstance(item, dict)
        }
        != expected_blockers
        or any(
            set(item) != {"blocker_id", "title", "problem"}
            or not _is_evidence(item.get("problem"))
            for item in blockers
            if isinstance(item, dict)
        )
    ):
        errors.append(
            "FINAL_BLOCKER_ANALYSIS_BLOCKERS: exactly the three ratification "
            "blockers must be analyzed jointly"
        )

    stress_dimensions = record.get("stress_dimensions")
    if (
        not isinstance(stress_dimensions, list)
        or set(stress_dimensions) != FINAL_BLOCKER_STRESS_DIMENSIONS
        or len(stress_dimensions) != 14
    ):
        errors.append(
            "FINAL_BLOCKER_ANALYSIS_STRESS_DIMENSIONS: exact fourteen-mode "
            "stress test is required"
        )
    alternatives = record.get("integrated_alternatives")
    if (
        not isinstance(alternatives, list)
        or len(alternatives) != 4
        or [item.get("alternative_id") for item in alternatives] != [
            "A",
            "B",
            "C",
            "D",
        ]
    ):
        errors.append(
            "FINAL_BLOCKER_ANALYSIS_ALTERNATIVES: exactly four credible "
            "integrated alternatives A through D are required"
        )
        alternatives = []
    for alternative in alternatives:
        architecture = alternative.get("architecture")
        stress_test = alternative.get("stress_test")
        if (
            set(alternative)
            != {
                "alternative_id",
                "name",
                "architecture",
                "stress_test",
                "assessment",
            }
            or not isinstance(architecture, dict)
            or set(architecture)
            != {
                "human_constitutional_authority",
                "successor_designation",
                "verification_office",
                "enforcement_office",
                "removal_replacement",
                "ordinary_governance_class",
            }
            and alternative.get("alternative_id") != "B"
            or not all(_is_evidence(value) for value in architecture.values())
            or not isinstance(stress_test, dict)
            or set(stress_test) != FINAL_BLOCKER_STRESS_DIMENSIONS
            or not all(_is_evidence(value) for value in stress_test.values())
            or not _is_evidence(alternative.get("assessment"))
        ):
            errors.append(
                "FINAL_BLOCKER_ANALYSIS_ALTERNATIVE_COMPLETENESS: each "
                "alternative must close all three chains and all fourteen "
                "stress dimensions"
            )
            break

    recommendation = record.get("recommended_integrated_architecture")
    allocations = (
        recommendation.get("minimum_constitutional_allocations", {})
        if isinstance(recommendation, dict)
        else {}
    )
    expected_allocations = {
        "human_constitutional_authority",
        "successor_designation",
        "verification_office",
        "enforcement_office",
        "shared_office_eligibility",
        "independent_selection_verification",
        "ordinary_human_governance_offices",
        "change_boundaries",
    }
    required_hca = {
        "holder",
        "relationship_to_membership",
        "eligibility",
        "term",
        "non_accretion",
    }
    required_successor = {
        "creator",
        "maintenance",
        "recognizer",
        "revocation_and_refresh",
        "failure",
    }
    required_office = {
        "composition",
        "selector",
        "alternates",
        "removal",
        "replacement",
        "challenge",
    }
    required_ordinary = {
        "exact_boundary",
        "initial_creation_or_recognition",
        "later_creation_or_recognition",
        "exercise_roll",
        "anti_manipulation",
        "challenge",
    }
    projection = (
        recommendation.get("projected_result_if_adopted_and_incorporated", {})
        if isinstance(recommendation, dict)
        else {}
    )
    if (
        not isinstance(recommendation, dict)
        or recommendation.get("architecture_id") != "B"
        or recommendation.get("name")
        != "Membership-Rooted HCA College and Split Office Selectors"
        or set(allocations) != expected_allocations
        or set(allocations.get("human_constitutional_authority", {}))
        != required_hca
        or set(allocations.get("successor_designation", {}))
        != required_successor
        or set(allocations.get("verification_office", {})) != required_office
        or set(allocations.get("enforcement_office", {})) != required_office
        or set(allocations.get("ordinary_human_governance_offices", {}))
        != required_ordinary
        or not isinstance(
            recommendation.get("cross_domain_consistency"), list
        )
        or len(recommendation.get("cross_domain_consistency", [])) != 7
        or projection
        != {
            "ratification_blockers_remaining": 0,
            "new_human_decision_packages_required": 1,
            "constitution_ready_for_revised_ratification_review": True,
            "constitution_adopted": False,
        }
    ):
        errors.append(
            "FINAL_BLOCKER_RECOMMENDATION: exact minimum integrated "
            "architecture, authority chains, change boundaries, and "
            "conditional zero-blocker projection are required"
        )

    subordinate_items = record.get("subordinate_law_items")
    if (
        not isinstance(subordinate_items, list)
        or len(subordinate_items) != 9
        or not all(_is_evidence(item) for item in subordinate_items)
    ):
        errors.append(
            "FINAL_BLOCKER_SUBORDINATE_ITEMS: exact administrative delegation "
            "boundary is required"
        )
    residual_questions = record.get("residual_questions")
    if (
        not isinstance(residual_questions, list)
        or len(residual_questions) != 2
        or "initial Schedule O" not in str(residual_questions[0])
        or "transition administration" not in str(residual_questions[1])
    ):
        errors.append(
            "FINAL_BLOCKER_RESIDUALS: only Schedule O population and initial "
            "term staggering may remain"
        )
    provenance = record.get("provenance")
    if (
        not isinstance(provenance, dict)
        or "explicit Human Constitutional Authority instruction"
        not in str(provenance.get("source", ""))
        or "no constitutional effect"
        not in str(provenance.get("authority_boundary", ""))
        or "Only an explicit attributable Human Constitutional Authority"
        not in str(provenance.get("authority_boundary", ""))
    ):
        errors.append(
            "FINAL_BLOCKER_PROVENANCE: explicit human instruction and "
            "machine non-authority provenance are required"
        )

    packet_path = root / FINAL_BLOCKER_PACKET_RELATIVE_PATH
    try:
        packet = packet_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"FINAL_BLOCKER_PACKET_REQUIRED: {exc}")
        packet = ""
    required_packet_terms = (
        "**HUMAN DECISION REQUIRED — NO DECISION RECORDED**",
        "**NO CONSTITUTIONAL EFFECT**",
        "## Decision Scope",
        "## Alternatives Considered",
        "## Recommended Integrated Architecture",
        "### 1. Human Constitutional Authority",
        "### 2. Successor Designation",
        "### 3. Verification Office",
        "### 4. Enforcement Office",
        "### 5. Eligibility, Selection Verification, and Challenge",
        "### 6. Ordinary Human Governance Offices",
        "### 7. Change and Non-Accretion Boundaries",
        "## Subordinate Governance and Implementation",
        "## Human Decision",
        "`ADOPT_RECOMMENDED_INTEGRATED_ARCHITECTURE`",
        "No option has been selected in this record.",
        "ratification blockers remaining: **0**",
        "**NO HUMAN DECISION HAS BEEN RECORDED.**",
        "**CONSTITUTION v0.1 REMAINS DRAFT — NOT ADOPTED CONSTITUTION.**",
    )
    if (
        any(term not in packet for term in required_packet_terms)
        or len(re.findall(r"^\d+\. `", packet, flags=re.MULTILINE)) != 6
        or "constitutional-design/FINAL-RATIFICATION-BLOCKER-ANALYSIS.yaml"
        not in packet
    ):
        errors.append(
            "FINAL_BLOCKER_PACKET_CONTENT: one complete coordinated human "
            "decision packet with no selected option is required"
        )

    metrics.update(
        {
            "final_ratification_blockers_analyzed": len(blockers)
            if isinstance(blockers, list)
            else 0,
            "integrated_architecture_recommended": "ALTERNATIVE_B",
            "projected_ratification_blockers_remaining": int(
                projection.get("ratification_blockers_remaining", 3)
            ),
            "final_blocker_human_decisions_required": 1,
            "final_blocker_subordinate_law_item_count": len(subordinate_items)
            if isinstance(subordinate_items, list)
            else 0,
        }
    )
    return metrics


def validate(root: Path) -> ValidationResult:
    root = root.resolve()
    errors: list[str] = []

    issue_dir = root / "constitutional-design" / "issues"
    issues = _load_record_set(issue_dir, "IR-*.yaml", errors)
    if len(issues) != 18:
        errors.append(f"ISSUE_COUNT: expected 18, found {len(issues)}")
    issue_filenames = {Path(record["_record_path"]).name for record in issues}
    if issue_filenames != EXPECTED_ISSUE_FILENAMES:
        errors.append("ISSUE_FILENAMES: issue filenames do not match the baseline")

    issue_ids = [record.get("issue_id") for record in issues]
    string_issue_ids = [
        issue_id for issue_id in issue_ids if isinstance(issue_id, str)
    ]
    duplicate_ids = sorted(
        {
            issue_id
            for issue_id in string_issue_ids
            if string_issue_ids.count(issue_id) > 1
        }
    )
    if duplicate_ids:
        errors.append(f"DUPLICATE_ISSUE_ID: {', '.join(map(str, duplicate_ids))}")
    if len(string_issue_ids) != len(issues) or set(string_issue_ids) != EXPECTED_ISSUE_IDS:
        errors.append("ISSUE_IDENTIFIERS: expected exactly IR-01 through IR-18")

    for issue in issues:
        path = issue["_record_path"]
        expected_issue_id = Path(path).name[:5]
        if issue.get("issue_id") != expected_issue_id:
            errors.append(
                f"ISSUE_IDENTIFIER_FILENAME: {path}: expected {expected_issue_id}"
            )
        missing = sorted(ISSUE_FIELDS - issue.keys())
        if missing:
            errors.append(f"ISSUE_FIELDS: {path}: missing {', '.join(missing)}")
        if issue.get("status") != "OPEN":
            errors.append(
                f"ISSUE_STATUS: {issue.get('issue_id')} is {issue.get('status')!r}"
            )
        if not _has_provenance(issue):
            errors.append(f"PROVENANCE_REQUIRED: {path}")
        if issue.get("candidate_architectures") != []:
            errors.append(
                f"CANDIDATE_ARCHITECTURES_NOT_EMPTY: {issue.get('issue_id')}"
            )

    questions_path = (
        root / "constitutional-design" / "FOUNDATIONAL_QUESTIONS.yaml"
    )
    questions_record = _load_record(questions_path, errors) or {}
    questions_value = questions_record.get("questions")
    questions = (
        [question for question in questions_value if isinstance(question, dict)]
        if isinstance(questions_value, list)
        else []
    )
    if not _has_provenance(questions_record):
        errors.append(f"PROVENANCE_REQUIRED: {questions_path}")
    question_ids = [
        question.get("question_id")
        for question in questions
        if isinstance(question.get("question_id"), str)
    ]
    expected_question_ids = {f"FQ-{index:02d}" for index in range(1, 6)}
    if len(questions) != 5 or set(question_ids) != expected_question_ids:
        errors.append(
            "FOUNDATIONAL_QUESTION_COUNT: expected exactly FQ-01 through FQ-05"
        )
    for question in questions:
        question_id = question.get("question_id")
        status = question.get("status")
        expected_status = "RESOLVED"
        if status != expected_status:
            errors.append(
                f"FOUNDATIONAL_QUESTION_STATUS: {question_id} is {status!r}"
            )
        if question_id == "FQ-05" and (
            question.get("source_decisions") != ["CDR-005"]
            or question.get("resolution") != FQ5_RESOLUTION
            or not isinstance(question.get("provenance"), dict)
            or question["provenance"].get("source")
            != "Explicit human decision recorded in CDR-005"
            or question["provenance"].get("decision_authority")
            != "Human Constitutional Authority"
            or question["provenance"].get("decision_date") != FQ5_DECISION_DATE
        ):
            errors.append(
                "FQ5_RESOLUTION_PROVENANCE: FQ-05 requires exact explicit "
                "human decision provenance"
            )
        if question_id == "FQ-01" and (
            question.get("source_decisions") != ["CDR-001"]
            or question.get("resolution") != FQ1_RESOLUTION
            or not isinstance(question.get("provenance"), dict)
            or question["provenance"].get("decision_authority")
            != "Human Constitutional Authority"
            or question["provenance"].get("decision_date")
            != FQ1_DECISION_DATE
        ):
            errors.append(
                "FQ1_RESOLUTION_PROVENANCE: FQ-01 must link to the explicit "
                "human decision"
            )
        if question_id == "FQ-02" and (
            question.get("source_decisions") != ["CDR-002"]
            or question.get("resolution") != FQ2_RESOLUTION
            or not isinstance(question.get("provenance"), dict)
            or question["provenance"].get("decision_authority")
            != "Human Constitutional Authority"
            or question["provenance"].get("decision_date")
            != FQ2_DECISION_DATE
        ):
            errors.append(
                "FQ2_RESOLUTION_PROVENANCE: FQ-02 must link to the explicit "
                "human decision"
            )
        if question_id == "FQ-03" and (
            question.get("source_decisions") != ["CDR-003"]
            or question.get("resolution") != FQ3_RESOLUTION
            or not isinstance(question.get("provenance"), dict)
            or question["provenance"].get("source")
            != "Explicit human decision recorded in CDR-003"
            or question["provenance"].get("decision_authority")
            != "Human Constitutional Authority"
            or question["provenance"].get("decision_date")
            != FQ3_DECISION_DATE
        ):
            errors.append(
                "FQ3_RESOLUTION_PROVENANCE: FQ-03 must link to the explicit "
                "human decision"
            )
        if question_id == "FQ-04" and (
            question.get("source_decisions") != ["CDR-004"]
            or question.get("resolution") != FQ4_RESOLUTION
            or not isinstance(question.get("provenance"), dict)
            or question["provenance"].get("source")
            != "Explicit human decision recorded in CDR-004"
            or question["provenance"].get("decision_authority")
            != "Human Constitutional Authority"
            or question["provenance"].get("decision_date")
            != FQ4_DECISION_DATE
        ):
            errors.append(
                "FQ4_RESOLUTION_PROVENANCE: FQ-04 must link to the explicit "
                "human decision"
            )
        if not _has_provenance(question):
            errors.append(
                f"PROVENANCE_REQUIRED: foundational question {question_id!r}"
            )

    decision_dir = root / "constitutional-design" / "decisions"
    decisions = _load_record_set(decision_dir, "CDR-*.yaml", errors)
    decision_template_path = decision_dir / "DECISION_TEMPLATE.yaml"
    decision_template = _load_record(decision_template_path, errors) or {}
    if set(decision_template) != DECISION_FIELDS:
        errors.append(
            "DECISION_TEMPLATE_SCHEMA: template fields do not match the baseline"
        )
    template_human_decision = decision_template.get("human_decision")
    if (
        not isinstance(template_human_decision, dict)
        or set(template_human_decision) != HUMAN_DECISION_FIELDS
    ):
        errors.append(
            "DECISION_TEMPLATE_HUMAN_DECISION_SCHEMA: fields do not match"
        )
    decisions_by_id: dict[str, dict[str, Any]] = {}
    decision_ids_seen: set[str] = set()
    decision_status_counts: dict[str, int] = {}
    decided_count = 0
    for decision in decisions:
        if not _has_provenance(decision):
            errors.append(
                f"PROVENANCE_REQUIRED: {decision['_record_path']}"
            )
        decision_id = decision.get("decision_id")
        if not isinstance(decision_id, str) or not decision_id:
            errors.append(
                f"DECISION_ID: invalid identifier in {decision['_record_path']}"
            )
        elif decision_id in decision_ids_seen:
            errors.append(f"DUPLICATE_DECISION_ID: {decision_id}")
        else:
            decision_ids_seen.add(decision_id)
            decisions_by_id[decision_id] = decision
        expected_decision_fields = DECISION_FIELDS | (
            {"commitment_level_tests"}
            if decision_id == "CDR-005"
            else set()
        )
        if set(decision) - {"_record_path"} != expected_decision_fields:
            errors.append(
                f"DECISION_RECORD_SCHEMA: {decision_id or decision['_record_path']}"
            )
        status = decision.get("status")
        if not isinstance(status, str) or status not in DECISION_STATUSES:
            errors.append(
                f"DECISION_STATUS: {decision_id or decision['_record_path']} "
                f"is {status!r}"
            )
        else:
            decision_status_counts[status] = (
                decision_status_counts.get(status, 0) + 1
            )
        if status == "DECIDED":
            decided_count += 1
            if not _has_human_decision_evidence(decision):
                errors.append(
                    "DECIDED_WITHOUT_HUMAN_DECISION: "
                    f"{decision_id or decision['_record_path']}"
                )
    decided_ids = {
        decision_id
        for decision_id, decision in decisions_by_id.items()
        if decision.get("status") == "DECIDED"
    }
    if decided_count != 5 or decided_ids != {
        "CDR-001",
        "CDR-002",
        "CDR-003",
        "CDR-004",
        "CDR-005",
    }:
        errors.append(
            "DECISION_COUNT: expected exactly CDR-001 through CDR-005 DECIDED, "
            f"found {decided_count}"
        )
    if set(decisions_by_id) != {
        "CDR-001",
        "CDR-002",
        "CDR-003",
        "CDR-004",
        "CDR-005",
    }:
        errors.append(
            "DECISION_RECORD_SET: expected exactly CDR-001 through CDR-005"
        )
    if "CDR-001" not in decisions_by_id:
        errors.append("FQ1_ANALYTICAL_RECORD_REQUIRED: CDR-001 is required")
    fq1 = next(
        (
            question
            for question in questions
            if question.get("question_id") == "FQ-01"
        ),
        {},
    )
    if (
        fq1.get("status") == "RESOLVED"
        and (
            fq1.get("source_decisions") != ["CDR-001"]
            or decisions_by_id.get("CDR-001", {}).get("status") != "DECIDED"
            or not _has_human_decision_evidence(
                decisions_by_id.get("CDR-001", {})
            )
        )
    ):
        errors.append(
            "FQ1_RESOLUTION_DECISION_LINK: resolved FQ-01 requires decided "
            "CDR-001 with human provenance"
        )
    fq2 = next(
        (
            question
            for question in questions
            if question.get("question_id") == "FQ-02"
        ),
        {},
    )
    if (
        fq2.get("status") == "RESOLVED"
        and (
            fq2.get("source_decisions") != ["CDR-002"]
            or decisions_by_id.get("CDR-002", {}).get("status") != "DECIDED"
            or not _has_human_decision_evidence(
                decisions_by_id.get("CDR-002", {})
            )
        )
    ):
        errors.append(
            "FQ2_RESOLUTION_DECISION_LINK: resolved FQ-02 requires decided "
            "CDR-002 with human provenance"
        )
    fq3 = next(
        (
            question
            for question in questions
            if question.get("question_id") == "FQ-03"
        ),
        {},
    )
    if (
        fq3.get("status") == "RESOLVED"
        and (
            fq3.get("source_decisions") != ["CDR-003"]
            or decisions_by_id.get("CDR-003", {}).get("status") != "DECIDED"
            or not _has_human_decision_evidence(
                decisions_by_id.get("CDR-003", {})
            )
        )
    ):
        errors.append(
            "FQ3_RESOLUTION_DECISION_LINK: resolved FQ-03 requires decided "
            "CDR-003 with human provenance"
        )
    fq4 = next(
        (
            question
            for question in questions
            if question.get("question_id") == "FQ-04"
        ),
        {},
    )
    if (
        fq4.get("status") == "RESOLVED"
        and (
            fq4.get("source_decisions") != ["CDR-004"]
            or decisions_by_id.get("CDR-004", {}).get("status") != "DECIDED"
            or not _has_human_decision_evidence(
                decisions_by_id.get("CDR-004", {})
            )
        )
    ):
        errors.append(
            "FQ4_RESOLUTION_DECISION_LINK: resolved FQ-04 requires decided "
            "CDR-004 with human provenance"
        )
    fq5 = next(
        (
            question
            for question in questions
            if question.get("question_id") == "FQ-05"
        ),
        {},
    )
    if (
        fq5.get("status") != "RESOLVED"
        or fq5.get("source_decisions") != ["CDR-005"]
        or decisions_by_id.get("CDR-005", {}).get("status") != "DECIDED"
        or not _has_human_decision_evidence(
            decisions_by_id.get("CDR-005", {})
        )
    ):
        errors.append(
            "FQ5_RESOLUTION_DECISION_LINK: resolved FQ-05 requires decided "
            "CDR-005 with human provenance"
        )

    requirement_dir = root / "constitutional-design" / "requirements"
    requirements = _load_record_set(requirement_dir, "CR-*.yaml", errors)
    requirement_template = (
        _load_record(requirement_dir / "REQUIREMENT_TEMPLATE.yaml", errors) or {}
    )
    if set(requirement_template) != REQUIREMENT_FIELDS:
        errors.append(
            "REQUIREMENT_TEMPLATE_SCHEMA: template fields do not match"
        )
    requirement_ids = [
        requirement.get("requirement_id") for requirement in requirements
    ]
    if (
        len(requirements) != len(ALL_REQUIREMENTS)
        or set(requirement_ids) != set(ALL_REQUIREMENTS)
        or len(set(map(str, requirement_ids))) != len(requirement_ids)
    ):
        errors.append(
            "REQUIREMENT_SET: exactly CR-001 through CR-035 are required"
        )
    accepted_count = 0
    for requirement in requirements:
        if not _has_provenance(requirement):
            errors.append(
                f"PROVENANCE_REQUIRED: {requirement['_record_path']}"
            )
        requirement_id = requirement.get("requirement_id")
        requirement_key = str(requirement_id)
        expected_requirement = ALL_REQUIREMENTS.get(requirement_key)
        expected_fq4_details = FQ4_REQUIREMENT_DETAILS.get(requirement_key)
        expected_fq5_details = FQ5_REQUIREMENT_DETAILS.get(requirement_key)
        if requirement_key in FQ1_REQUIREMENTS:
            expected_decision = "CDR-001"
            expected_provenance = FQ1_REQUIREMENT_PROVENANCE
        elif requirement_key in FQ2_REQUIREMENTS:
            expected_decision = "CDR-002"
            expected_provenance = FQ2_REQUIREMENT_PROVENANCE
        elif requirement_key in FQ3_REQUIREMENTS:
            expected_decision = "CDR-003"
            expected_provenance = FQ3_REQUIREMENT_PROVENANCE
        elif requirement_key in FQ4_REQUIREMENTS:
            expected_decision = "CDR-004"
            expected_provenance = FQ4_REQUIREMENT_PROVENANCE
        else:
            expected_decision = "CDR-005"
            expected_provenance = FQ5_REQUIREMENT_PROVENANCE
        if set(requirement) - {"_record_path"} != REQUIREMENT_FIELDS:
            errors.append(
                f"REQUIREMENT_RECORD_SCHEMA: {requirement_id or requirement['_record_path']}"
            )
        if requirement.get("status") != "ACCEPTED_FOR_DRAFTING":
            errors.append(
                f"REQUIREMENT_STATUS: {requirement_id} must be "
                "ACCEPTED_FOR_DRAFTING"
            )
            continue
        accepted_count += 1
        sources = requirement.get("source_decisions")
        valid_sources = (
            isinstance(sources, list)
            and sources == [expected_decision]
            and all(
                isinstance(source, str)
                and source in decisions_by_id
                and decisions_by_id[source].get("status") == "DECIDED"
                and _has_human_decision_evidence(decisions_by_id[source])
                for source in sources
            )
        )
        if not valid_sources:
            errors.append(
                "ACCEPTED_REQUIREMENT_PROVENANCE: "
                f"{requirement.get('requirement_id') or requirement['_record_path']}"
            )
        source_issues = requirement.get("source_issues")
        if expected_requirement is None or (
            requirement.get("statement") != expected_requirement["statement"]
            or not isinstance(source_issues, list)
            or set(source_issues) != expected_requirement["source_issues"]
            or len(source_issues) != len(expected_requirement["source_issues"])
            or requirement.get("source_decisions") != [expected_decision]
            or not isinstance(requirement.get("provenance"), dict)
            or (
                requirement.get("provenance")
                != {"source": expected_provenance}
                if expected_decision in {"CDR-004", "CDR-005"}
                else requirement["provenance"].get("source")
                != expected_provenance
            )
            or requirement.get("constitutional_level") != "FOUNDATIONAL"
            or (
                expected_decision in {"CDR-002", "CDR-003"}
                and (
                    requirement.get("rationale")
                    != expected_requirement["rationale"]
                    or requirement.get("implementation_boundary")
                    != expected_requirement["implementation_boundary"]
                    or requirement.get("verification_method")
                    != expected_requirement["verification_method"]
                )
            )
            or (
                expected_decision == "CDR-001"
                and (
                    not _is_evidence(requirement.get("rationale"))
                    or not _is_evidence(
                        requirement.get("implementation_boundary")
                    )
                    or not _is_evidence(
                        requirement.get("verification_method")
                    )
                )
            )
            or (
                expected_decision == "CDR-004"
                and (
                    expected_fq4_details is None
                    or requirement.get("rationale")
                    != expected_fq4_details["rationale"]
                    or requirement.get("implementation_boundary")
                    != expected_fq4_details["implementation_boundary"]
                    or requirement.get("verification_method")
                    != expected_fq4_details["verification_method"]
                    or requirement.get("conflicts") != []
                    or requirement.get("dissent") != []
                )
            )
            or (
                expected_decision == "CDR-005"
                and (
                    expected_fq5_details is None
                    or requirement.get("rationale")
                    != expected_fq5_details["rationale"]
                    or requirement.get("implementation_boundary")
                    != expected_fq5_details["implementation_boundary"]
                    or requirement.get("verification_method")
                    != expected_fq5_details["verification_method"]
                    or requirement.get("conflicts") != []
                    or requirement.get("dissent") != []
                )
            )
            or requirement.get("draft_mapping") != []
        ):
            errors.append(
                f"REQUIREMENT_CONTENT: {requirement_id}"
            )
    if accepted_count != len(ALL_REQUIREMENTS):
        errors.append(
            "ACCEPTED_REQUIREMENT_COUNT: expected 35 "
            f"ACCEPTED_FOR_DRAFTING records, found {accepted_count}"
        )
    article_architecture_metrics = _validate_article_architecture(
        root, decisions_by_id, requirements, errors
    )
    remaining_design_metrics = _validate_remaining_design_analysis(root, errors)
    cross_domain_packet_metrics = _validate_cross_domain_decision_packet(
        root, errors
    )
    coordinated_decision_metrics = _validate_coordinated_decision(root, errors)
    constitution_draft_metrics = _validate_constitution_draft(root, errors)
    ratification_review_metrics = _validate_ratification_review(root, errors)
    final_blocker_metrics = _validate_final_blocker_analysis(root, errors)

    source_index_path = (
        root / "constitutional-design" / "sources" / "SOURCE_INDEX.yaml"
    )
    source_index = _load_record(source_index_path, errors) or {}
    if not _has_provenance(source_index):
        errors.append(f"PROVENANCE_REQUIRED: {source_index_path}")
    prior_art_path = (
        root
        / "constitutional-design"
        / "sources"
        / "PRIOR_ART_REGISTER.yaml"
    )
    prior_art = _load_record(prior_art_path, errors) or {}
    if not _has_provenance(prior_art):
        errors.append(f"PROVENANCE_REQUIRED: {prior_art_path}")
    if set(prior_art) != PRIOR_ART_REGISTER_FIELDS:
        errors.append(
            "PRIOR_ART_REGISTER_SCHEMA: top-level fields do not match the baseline"
        )
    if prior_art.get("register_status") != "DESK_REVIEWED_PRIOR_ART_BASELINE":
        errors.append("PRIOR_ART_REGISTER_STATUS: expected desk-reviewed baseline")
    if not _is_evidence(prior_art.get("evidence_boundary")):
        errors.append("PRIOR_ART_EVIDENCE_BOUNDARY: required")
    overlap_vocabulary = prior_art.get("permitted_research_classifications", [])
    if (
        not _matches_exact_vocabulary(
            overlap_vocabulary, PRIOR_ART_OVERLAP_CLASSIFICATIONS
        )
    ):
        errors.append(
            "PRIOR_ART_OVERLAP_VOCABULARY: register metadata does not match"
        )
    source_status_vocabulary = prior_art.get("source_statuses", [])
    if (
        not _matches_exact_vocabulary(
            source_status_vocabulary, PRIOR_ART_SOURCE_STATUSES
        )
    ):
        errors.append("PRIOR_ART_SOURCE_STATUS_VOCABULARY: metadata does not match")
    disposition_vocabulary = prior_art.get("candidate_dispositions", [])
    if (
        not _matches_exact_vocabulary(
            disposition_vocabulary, CANDIDATE_DISPOSITIONS
        )
    ):
        errors.append("CANDIDATE_DISPOSITION_VOCABULARY: metadata does not match")
    novelty_rule = prior_art.get("novelty_rule")
    if (
        not isinstance(novelty_rule, str)
        or "NO_CLOSE_PRIOR_ART_FOUND_IN_SEARCH does not mean NOVEL"
        not in novelty_rule
    ):
        errors.append(
            "NO_CLOSE_IS_NOT_NOVEL: register must explicitly preserve the distinction"
        )

    prior_art_value = prior_art.get("prior_art_entries")
    prior_art_entries = (
        [entry for entry in prior_art_value if isinstance(entry, dict)]
        if isinstance(prior_art_value, list)
        else []
    )
    if not isinstance(prior_art_value, list):
        errors.append("PRIOR_ART_REGISTER: prior_art_entries must be a list")
    elif len(prior_art_entries) != len(prior_art_value):
        errors.append("PRIOR_ART_REGISTER: every entry must be an object")

    prior_art_ids = [entry.get("prior_art_id") for entry in prior_art_entries]
    string_prior_art_ids = [
        prior_art_id
        for prior_art_id in prior_art_ids
        if isinstance(prior_art_id, str)
    ]
    duplicate_prior_art_ids = sorted(
        {
            prior_art_id
            for prior_art_id in string_prior_art_ids
            if string_prior_art_ids.count(prior_art_id) > 1
        },
        key=str,
    )
    if duplicate_prior_art_ids:
        errors.append(
            "DUPLICATE_PRIOR_ART_ID: "
            + ", ".join(map(str, duplicate_prior_art_ids))
        )

    known_issue_ids = EXPECTED_ISSUE_IDS
    prior_art_status_counts = {
        status: 0 for status in sorted(PRIOR_ART_SOURCE_STATUSES)
    }
    prior_art_disposition_counts = {
        disposition: 0 for disposition in sorted(CANDIDATE_DISPOSITIONS)
    }
    register_prior_art_pairs: set[tuple[str, str]] = set()
    for entry in prior_art_entries:
        prior_art_id = entry.get("prior_art_id")
        if not isinstance(prior_art_id, str) or not prior_art_id:
            errors.append(f"PRIOR_ART_ID: invalid identifier {prior_art_id!r}")
        if set(entry) != PRIOR_ART_ENTRY_FIELDS:
            errors.append(
                f"PRIOR_ART_ENTRY_SCHEMA: {prior_art_id}: fields do not match"
            )
        required_content_fields = PRIOR_ART_ENTRY_FIELDS - {
            "source_date",
            "source_reference",
            "mechanisms",
            "relevant_issues",
        }
        if any(not _has_content(entry.get(field)) for field in required_content_fields):
            errors.append(f"PRIOR_ART_REQUIRED_CONTENT: {prior_art_id}")

        source_status = entry.get("source_status")
        if (
            not isinstance(source_status, str)
            or source_status not in PRIOR_ART_SOURCE_STATUSES
        ):
            errors.append(
                f"PRIOR_ART_SOURCE_STATUS: {prior_art_id} is {source_status!r}"
            )
        else:
            prior_art_status_counts[source_status] += 1

        overlap = entry.get("overlap_classification")
        if (
            not isinstance(overlap, str)
            or overlap not in PRIOR_ART_OVERLAP_CLASSIFICATIONS
        ):
            errors.append(
                f"PRIOR_ART_OVERLAP_CLASSIFICATION: {prior_art_id} is {overlap!r}"
            )
        if (
            isinstance(source_status, str)
            and source_status in {"RESEARCH_LEAD", "SOURCE_TO_VERIFY"}
            and overlap != "INSUFFICIENT_EVIDENCE"
        ):
            errors.append(
                f"PRIOR_ART_EVIDENCE_CONTRADICTION: {prior_art_id}"
            )
        disposition = entry.get("candidate_disposition")
        if (
            not isinstance(disposition, str)
            or disposition not in CANDIDATE_DISPOSITIONS
        ):
            errors.append(
                f"PRIOR_ART_CANDIDATE_DISPOSITION: {prior_art_id} is {disposition!r}"
            )
        else:
            prior_art_disposition_counts[disposition] += 1

        mechanisms = entry.get("mechanisms")
        if (
            not isinstance(mechanisms, list)
            or not mechanisms
            or any(not _is_evidence(mechanism) for mechanism in mechanisms)
            or len(set(mechanisms)) != len(mechanisms)
        ):
            errors.append(f"PRIOR_ART_MECHANISMS: {prior_art_id}")

        relevant_issues = entry.get("relevant_issues")
        if (
            not isinstance(relevant_issues, list)
            or not relevant_issues
            or any(
                not isinstance(issue_id, str)
                or issue_id not in known_issue_ids
                for issue_id in relevant_issues
            )
            or len(set(map(str, relevant_issues))) != len(relevant_issues)
        ):
            errors.append(f"PRIOR_ART_RELEVANT_ISSUES: {prior_art_id}")
        else:
            if isinstance(prior_art_id, str):
                register_prior_art_pairs.update(
                    (issue_id, prior_art_id) for issue_id in relevant_issues
                )

        references = _source_reference_urls(entry.get("source_reference"))
        if references is None or any(
            not _is_evidence(reference) for reference in references
        ):
            errors.append(f"PRIOR_ART_SOURCE_REFERENCE_ENCODING: {prior_art_id}")
        elif source_status == "VERIFIED" and (
            not references
            or any(not _is_stable_http_reference(url) for url in references)
        ):
            errors.append(f"VERIFIED_PRIOR_ART_REFERENCE: {prior_art_id}")

        if not _is_evidence(entry.get("provenance")) or not _is_evidence(
            entry.get("review_status")
        ):
            errors.append(f"PRIOR_ART_VERIFICATION_STATE: {prior_art_id}")
        if source_status == "VERIFIED" and (
            entry.get("review_status") != "DESK_REVIEWED_2026-08-27"
            or "2026-08-27" not in str(entry.get("provenance", ""))
        ):
            errors.append(f"VERIFIED_PRIOR_ART_PROVENANCE: {prior_art_id}")

    prior_art_id_set = {
        prior_art_id
        for prior_art_id in prior_art_ids
        if isinstance(prior_art_id, str)
    }
    issue_prior_art_link_count = 0
    issue_prior_art_pairs: set[tuple[str, str]] = set()
    for issue in issues:
        issue_id = issue.get("issue_id")
        references = issue.get("known_prior_art")
        if not isinstance(references, list):
            errors.append(
                f"PRIOR_ART_REFERENCES: {issue_id} must be a list"
            )
            continue
        issue_prior_art_link_count += len(references)
        if not references:
            errors.append(f"PRIOR_ART_ISSUE_COVERAGE: {issue_id} has no references")
        if len(set(map(str, references))) != len(references):
            errors.append(f"DUPLICATE_PRIOR_ART_REFERENCE: {issue_id}")
        unresolved = sorted(
            [
                reference
                for reference in references
                if not isinstance(reference, str)
                or reference not in prior_art_id_set
            ],
            key=str,
        )
        if unresolved:
            errors.append(
                "UNRESOLVED_PRIOR_ART_REFERENCE: "
                f"{issue_id}: {', '.join(map(str, unresolved))}"
            )
        issue_prior_art_pairs.update(
            (issue_id, reference)
            for reference in references
            if isinstance(issue_id, str) and isinstance(reference, str)
        )
    if issue_prior_art_pairs != register_prior_art_pairs:
        errors.append(
            "PRIOR_ART_LINK_ASYMMETRY: issue and register mappings differ"
        )
    if {issue_id for issue_id, _ in register_prior_art_pairs} != known_issue_ids:
        errors.append("PRIOR_ART_ALL_ISSUES_COVERAGE: expected all 18 issues")

    adoption_map_path = (
        root
        / "constitutional-design"
        / "sources"
        / "MECHANISM_ADOPTION_MAP.yaml"
    )
    adoption_map = _load_record(adoption_map_path, errors) or {}
    if not _has_provenance(adoption_map):
        errors.append(f"PROVENANCE_REQUIRED: {adoption_map_path}")
    if set(adoption_map) != ADOPTION_MAP_FIELDS:
        errors.append(
            "MECHANISM_ADOPTION_MAP_SCHEMA: top-level fields do not match"
        )
    if adoption_map.get("map_status") != "RESEARCH_ARTIFACT":
        errors.append("MECHANISM_ADOPTION_MAP_STATUS: expected research artifact")
    if not _is_evidence(adoption_map.get("evidence_boundary")):
        errors.append("MECHANISM_ADOPTION_EVIDENCE_BOUNDARY: required")
    if any(
        _contains_exact_string(adoption_map, status)
        or _contains_unqualified_conclusion(adoption_map, status)
        for status in FORBIDDEN_FINAL_ADOPTION_STATUSES
    ):
        errors.append("FINAL_ADOPTION_STATUS: mechanism adoption map")
    adoption_value = adoption_map.get("entries")
    adoption_entries = (
        [entry for entry in adoption_value if isinstance(entry, dict)]
        if isinstance(adoption_value, list)
        else []
    )
    if not isinstance(adoption_value, list):
        errors.append("MECHANISM_ADOPTION_MAP: entries must be a list")
    elif len(adoption_entries) != len(adoption_value):
        errors.append("MECHANISM_ADOPTION_MAP: every entry must be an object")

    adoption_disposition_counts = {
        disposition: 0 for disposition in sorted(CANDIDATE_DISPOSITIONS)
    }
    mechanisms_seen: set[str] = set()
    for entry in adoption_entries:
        mechanism = entry.get("mechanism")
        if set(entry) != ADOPTION_ENTRY_FIELDS:
            errors.append(
                f"MECHANISM_ADOPTION_ENTRY_SCHEMA: {mechanism!r}"
            )
        if not _is_evidence(mechanism) or not _is_evidence(entry.get("rationale")):
            errors.append(f"MECHANISM_ADOPTION_CONTENT: {mechanism!r}")
        elif mechanism in mechanisms_seen:
            errors.append(f"DUPLICATE_ADOPTION_MECHANISM: {mechanism}")
        else:
            mechanisms_seen.add(mechanism)

        disposition = entry.get("candidate_disposition")
        if (
            not isinstance(disposition, str)
            or disposition not in CANDIDATE_DISPOSITIONS
        ):
            errors.append(
                f"MECHANISM_ADOPTION_DISPOSITION: {mechanism!r} is {disposition!r}"
            )
        else:
            adoption_disposition_counts[disposition] += 1
        if entry.get("decision_required") is not True:
            errors.append(f"MECHANISM_DECISION_REQUIRED: {mechanism!r}")

        sources = entry.get("prior_art_sources")
        if (
            not isinstance(sources, list)
            or not sources
            or any(
                not isinstance(source, str)
                or source not in prior_art_id_set
                for source in sources
            )
            or len(set(map(str, sources))) != len(sources)
        ):
            errors.append(f"MECHANISM_PRIOR_ART_SOURCES: {mechanism!r}")
        relevant_issues = entry.get("relevant_issues")
        if (
            not isinstance(relevant_issues, list)
            or not relevant_issues
            or any(
                not isinstance(issue_id, str)
                or issue_id not in known_issue_ids
                for issue_id in relevant_issues
            )
            or len(set(map(str, relevant_issues))) != len(relevant_issues)
        ):
            errors.append(f"MECHANISM_RELEVANT_ISSUES: {mechanism!r}")
        known_gaps = entry.get("known_gaps")
        if (
            not isinstance(known_gaps, list)
            or not known_gaps
            or any(not _is_evidence(gap) for gap in known_gaps)
        ):
            errors.append(f"MECHANISM_KNOWN_GAPS: {mechanism!r}")
        if any(
            _contains_exact_string(entry, status)
            or _contains_unqualified_conclusion(entry, status)
            for status in FORBIDDEN_FINAL_ADOPTION_STATUSES
        ):
            errors.append(f"FINAL_ADOPTION_STATUS: {mechanism!r}")
    if {
        disposition
        for disposition, count in adoption_disposition_counts.items()
        if count
    } != CANDIDATE_DISPOSITIONS:
        errors.append(
            "MECHANISM_ADOPTION_DISPOSITION_COVERAGE: "
            "all four candidate dispositions are required"
        )

    historical_path = (
        root
        / "constitutional-design"
        / "sources"
        / "HISTORICAL_EVIDENCE_REGISTER.yaml"
    )
    historical_register = _load_record(historical_path, errors) or {}
    if not _has_provenance(historical_register):
        errors.append(f"PROVENANCE_REQUIRED: {historical_path}")
    historical_value = historical_register.get("entries")
    historical_entries = (
        [entry for entry in historical_value if isinstance(entry, dict)]
        if isinstance(historical_value, list)
        else []
    )
    if not isinstance(historical_value, list):
        errors.append("HISTORICAL_EVIDENCE_REGISTER: entries must be a list")

    evidence_ids = [entry.get("evidence_id") for entry in historical_entries]
    string_evidence_ids = [
        evidence_id
        for evidence_id in evidence_ids
        if isinstance(evidence_id, str)
    ]
    duplicate_evidence_ids = sorted(
        {
            evidence_id
            for evidence_id in string_evidence_ids
            if string_evidence_ids.count(evidence_id) > 1
        }
    )
    if duplicate_evidence_ids:
        errors.append(
            "DUPLICATE_HISTORICAL_EVIDENCE_ID: "
            + ", ".join(map(str, duplicate_evidence_ids))
        )
    known_issue_ids = {
        issue_id for issue_id in issue_ids if isinstance(issue_id, str)
    }
    historical_status_counts = {
        status: 0 for status in sorted(HISTORICAL_SOURCE_STATUSES)
    }
    for entry in historical_entries:
        evidence_id = entry.get("evidence_id")
        missing = sorted(HISTORICAL_EVIDENCE_FIELDS - entry.keys())
        if missing:
            errors.append(
                f"HISTORICAL_EVIDENCE_FIELDS: {evidence_id}: "
                f"missing {', '.join(missing)}"
            )
        if not _has_provenance(entry):
            errors.append(
                f"PROVENANCE_REQUIRED: historical evidence {evidence_id!r}"
            )
        source_status = entry.get("source_status")
        if (
            not isinstance(source_status, str)
            or source_status not in HISTORICAL_SOURCE_STATUSES
        ):
            errors.append(
                f"HISTORICAL_SOURCE_STATUS: {evidence_id} is {source_status!r}"
            )
        else:
            historical_status_counts[source_status] += 1
        if entry.get("review_status") != "NOT_YET_REVIEWED":
            errors.append(
                f"HISTORICAL_REVIEW_STATUS: {evidence_id} is "
                f"{entry.get('review_status')!r}"
            )

        epistemic_fields = (
            entry.get("observation"),
            entry.get("interpretation"),
            entry.get("possible_constitutional_relevance"),
        )
        if not all(_has_content(value) for value in epistemic_fields):
            errors.append(
                f"HISTORICAL_EPISTEMIC_SEPARATION: {evidence_id} has an empty category"
            )
        elif len(
            {json.dumps(value, sort_keys=True) for value in epistemic_fields}
        ) != 3:
            errors.append(
                f"HISTORICAL_EPISTEMIC_SEPARATION: {evidence_id} collapses categories"
            )
        if not _has_content(entry.get("counterevidence_or_limitations")):
            errors.append(
                f"HISTORICAL_LIMITATIONS_REQUIRED: {evidence_id}"
            )

        relevant_issues = entry.get("relevant_issues")
        if (
            not isinstance(relevant_issues, list)
            or not relevant_issues
            or any(
                not isinstance(issue_id, str)
                or issue_id not in known_issue_ids
                for issue_id in relevant_issues
            )
        ):
            errors.append(
                f"HISTORICAL_RELEVANT_ISSUES: {evidence_id} has an unknown issue"
            )

        provenance_value = entry.get("provenance")
        provenance = provenance_value if isinstance(provenance_value, dict) else {}
        verification_fields = (
            provenance.get("verified_by"),
            provenance.get("verified_on"),
            provenance.get("verification_record"),
        )
        has_verification = all(_is_evidence(value) for value in verification_fields)
        if source_status == "VERIFIED" and not has_verification:
            errors.append(
                f"VERIFIED_HISTORICAL_EVIDENCE_PROVENANCE: {evidence_id}"
            )
        if source_status == "SOURCE_TO_VERIFY" and (
            any(_is_evidence(value) for value in verification_fields)
            or _contains_exact_string(provenance, "VERIFIED")
        ):
            errors.append(
                f"HISTORICAL_SOURCE_STATUS_CONFLICT: {evidence_id}"
            )

    evidence_id_set = {
        evidence_id for evidence_id in evidence_ids if isinstance(evidence_id, str)
    }
    historical_link_count = 0
    issue_link_pairs: set[tuple[str, str]] = set()
    for issue in issues:
        references = issue.get("historical_evidence")
        if not isinstance(references, list):
            errors.append(
                f"HISTORICAL_EVIDENCE_REFERENCES: {issue.get('issue_id')} must be a list"
            )
            continue
        historical_link_count += len(references)
        issue_link_pairs.update(
            (issue["issue_id"], reference)
            for reference in references
            if isinstance(issue.get("issue_id"), str)
            and isinstance(reference, str)
        )
        unresolved = sorted(
            [
                reference
                for reference in references
                if not isinstance(reference, str)
                or reference not in evidence_id_set
            ],
            key=str,
        )
        if unresolved:
            errors.append(
                f"UNRESOLVED_HISTORICAL_EVIDENCE_REFERENCE: "
                f"{issue.get('issue_id')}: {', '.join(map(str, unresolved))}"
            )
    register_link_pairs = {
        (issue_id, entry["evidence_id"])
        for entry in historical_entries
        if isinstance(entry.get("evidence_id"), str)
        for issue_id in (
            entry.get("relevant_issues")
            if isinstance(entry.get("relevant_issues"), list)
            else []
        )
        if isinstance(issue_id, str)
    }
    if issue_link_pairs != register_link_pairs:
        errors.append(
            "HISTORICAL_EVIDENCE_LINK_ASYMMETRY: issue and register mappings differ"
        )

    fq1_issue_records = [
        issue
        for issue in issues
        if issue.get("issue_id") in FQ1_REQUIRED_ISSUES
    ]
    expected_fq1_historical_ids = {
        reference
        for issue in fq1_issue_records
        for reference in (
            issue.get("historical_evidence")
            if isinstance(issue.get("historical_evidence"), list)
            else []
        )
        if isinstance(reference, str)
    }
    expected_fq1_prior_art_ids = {
        reference
        for issue in fq1_issue_records
        for reference in (
            issue.get("known_prior_art")
            if isinstance(issue.get("known_prior_art"), list)
            else []
        )
        if isinstance(reference, str)
    }
    analytical_decision_record_count = 0
    candidate_architecture_count = 0
    fq1_historical_ids: set[str] = set()
    fq1_prior_art_ids: set[str] = set()
    fq1_decision = decisions_by_id.get("CDR-001")
    if fq1_decision is not None:
        (
            analytical_decision_record_count,
            candidate_architecture_count,
            fq1_historical_ids,
            fq1_prior_art_ids,
        ) = _validate_fq1_analytical_record(
            fq1_decision, evidence_id_set, prior_art_id_set, root, errors
        )
        if fq1_historical_ids != expected_fq1_historical_ids:
            errors.append(
                "FQ1_HISTORICAL_EVIDENCE_COVERAGE: "
                "CDR-001 must use every historical record linked by its issues"
            )
        if fq1_prior_art_ids != expected_fq1_prior_art_ids:
            errors.append(
                "FQ1_PRIOR_ART_COVERAGE: "
                "CDR-001 must use every prior-art record linked by its issues"
            )

    fq2_candidate_architecture_count = 0
    fq2_historical_ids: set[str] = set()
    fq2_prior_art_ids: set[str] = set()
    fq2_decision = decisions_by_id.get("CDR-002")
    if fq2_decision is None:
        errors.append("FQ2_ANALYTICAL_RECORD_REQUIRED: CDR-002 is required")
    else:
        (
            fq2_candidate_architecture_count,
            fq2_historical_ids,
            fq2_prior_art_ids,
        ) = _validate_fq2_analytical_record(
            fq2_decision, evidence_id_set, prior_art_id_set, root, errors
        )

    fq3_candidate_architecture_count = 0
    fq3_historical_ids: set[str] = set()
    fq3_prior_art_ids: set[str] = set()
    fq3_decision = decisions_by_id.get("CDR-003")
    if fq3_decision is None:
        errors.append("FQ3_ANALYTICAL_RECORD_REQUIRED: CDR-003 is required")
    else:
        (
            fq3_candidate_architecture_count,
            fq3_historical_ids,
            fq3_prior_art_ids,
        ) = _validate_fq3_analytical_record(
            fq3_decision, evidence_id_set, prior_art_id_set, root, errors
        )

    fq4_candidate_architecture_count = 0
    fq4_historical_ids: set[str] = set()
    fq4_prior_art_ids: set[str] = set()
    fq4_decision = decisions_by_id.get("CDR-004")
    if fq4_decision is None:
        errors.append("FQ4_ANALYTICAL_RECORD_REQUIRED: CDR-004 is required")
    else:
        (
            fq4_candidate_architecture_count,
            fq4_historical_ids,
            fq4_prior_art_ids,
        ) = _validate_fq4_analytical_record(
            fq4_decision, evidence_id_set, prior_art_id_set, root, errors
        )

    fq5_candidate_architecture_count = 0
    fq5_historical_ids: set[str] = set()
    fq5_prior_art_ids: set[str] = set()
    fq5_decision = decisions_by_id.get("CDR-005")
    if fq5_decision is None:
        errors.append("FQ5_ANALYTICAL_RECORD_REQUIRED: CDR-005 is required")
    else:
        (
            fq5_candidate_architecture_count,
            fq5_historical_ids,
            fq5_prior_art_ids,
        ) = _validate_fq5_analytical_record(
            fq5_decision, evidence_id_set, prior_art_id_set, root, errors
        )

    (
        fq1_packet_count,
        fq1_decision_option_count,
        human_decision_question_count,
        fq1_recommended_architecture,
    ) = _validate_fq1_human_decision_packet(root, errors)
    (
        fq2_packet_count,
        fq2_decision_option_count,
        fq2_recommended_architecture,
    ) = _validate_fq2_human_decision_packet(root, errors)
    (
        fq3_packet_count,
        fq3_decision_option_count,
        fq3_recommended_architecture,
    ) = _validate_fq3_human_decision_packet(root, errors)
    (
        fq4_packet_count,
        fq4_decision_option_count,
        fq4_recommended_architecture,
    ) = _validate_fq4_human_decision_packet(root, errors)
    (
        fq5_packet_count,
        fq5_decision_option_count,
        fq5_recommended_architecture,
        fq5_refounding_principle_count,
    ) = _validate_fq5_human_decision_packet(root, errors)
    packet_dir = root / "constitutional-design" / "decisions" / "packets"
    packet_paths = (
        {
            path.relative_to(root)
            for path in packet_dir.glob("*-HUMAN-DECISION-PACKET.md")
        }
        if packet_dir.is_dir()
        else set()
    )
    expected_packet_paths = {
        FQ1_PACKET_RELATIVE_PATH,
        FQ2_PACKET_RELATIVE_PATH,
        FQ3_PACKET_RELATIVE_PATH,
        FQ4_PACKET_RELATIVE_PATH,
        FQ5_PACKET_RELATIVE_PATH,
    }
    if packet_paths != expected_packet_paths:
        errors.append(
            "HUMAN_DECISION_PACKET_SET: exactly the CDR-001 through CDR-005 "
            "packets are permitted"
        )
    human_decision_packet_count = (
        fq1_packet_count
        + fq2_packet_count
        + fq3_packet_count
        + fq4_packet_count
        + fq5_packet_count
    )

    structured_records: list[Any] = [
        *issues,
        *decisions,
        *requirements,
        source_index,
        prior_art,
        adoption_map,
        questions_record,
        historical_register,
    ]
    if any(_contains_novel(record) for record in structured_records) or any(
        _contains_unqualified_conclusion(record, "NOVEL")
        for record in structured_records
    ):
        errors.append("AUTOMATED_NOVELTY: NOVEL is not a permitted classification")

    constitution_dir = root / "constitution"
    provision_files = (
        [
            path
            for path in constitution_dir.rglob("*")
            if path.is_file() and path.name != "README.md"
        ]
        if constitution_dir.exists()
        else []
    )
    if provision_files:
        errors.append(
            "CONSTITUTIONAL_PROVISIONS: expected none, found "
            + ", ".join(str(path.relative_to(root)) for path in provision_files)
        )
    governance_engineering_dir = root / "governance-engineering"
    governance_runtime_files = (
        [
            path
            for path in governance_engineering_dir.rglob("*")
            if path.is_file() and path.name != "README.md"
        ]
        if governance_engineering_dir.exists()
        else []
    )
    if governance_runtime_files:
        errors.append(
            "GOVERNANCE_RUNTIME: governance engineering remains deferred; found "
            + ", ".join(
                str(path.relative_to(root)) for path in governance_runtime_files
            )
        )

    issue_status_counts: dict[str, int] = {}
    for issue in issues:
        status = str(issue.get("status"))
        issue_status_counts[status] = issue_status_counts.get(status, 0) + 1
    question_status_counts: dict[str, int] = {}
    for question in questions:
        status = str(question.get("status", "MISSING"))
        question_status_counts[status] = question_status_counts.get(status, 0) + 1

    metrics = {
        "issue_count": len(issues),
        "issue_status_counts": issue_status_counts,
        "foundational_question_count": len(questions),
        "foundational_question_status_counts": question_status_counts,
        "decision_record_count": len(decisions),
        "analytical_decision_record_count": analytical_decision_record_count,
        "candidate_architecture_count": candidate_architecture_count,
        "decision_record_status_counts": decision_status_counts,
        "decided_decision_count": decided_count,
        "accepted_requirement_count": accepted_count,
        "constitutional_provision_count": len(provision_files),
        "prior_art_research_lead_count": prior_art_status_counts[
            "RESEARCH_LEAD"
        ],
        "prior_art_entry_count": len(prior_art_entries),
        "prior_art_source_status_counts": prior_art_status_counts,
        "issue_prior_art_link_count": issue_prior_art_link_count,
        "prior_art_disposition_counts": prior_art_disposition_counts,
        "adoption_map_entry_count": len(adoption_entries),
        "adoption_map_disposition_counts": adoption_disposition_counts,
        "historical_evidence_entry_count": len(historical_entries),
        "issue_historical_link_count": historical_link_count,
        "historical_source_status_counts": historical_status_counts,
        "fq1_historical_evidence_reference_count": len(fq1_historical_ids),
        "fq1_prior_art_reference_count": len(fq1_prior_art_ids),
        "fq2_candidate_architecture_count": fq2_candidate_architecture_count,
        "fq2_historical_evidence_reference_count": len(fq2_historical_ids),
        "fq2_prior_art_reference_count": len(fq2_prior_art_ids),
        "fq3_candidate_architecture_count": fq3_candidate_architecture_count,
        "fq3_historical_evidence_reference_count": len(fq3_historical_ids),
        "fq3_prior_art_reference_count": len(fq3_prior_art_ids),
        "fq4_candidate_architecture_count": fq4_candidate_architecture_count,
        "fq4_historical_evidence_reference_count": len(fq4_historical_ids),
        "fq4_prior_art_reference_count": len(fq4_prior_art_ids),
        "fq5_candidate_architecture_count": fq5_candidate_architecture_count,
        "fq5_historical_evidence_reference_count": len(fq5_historical_ids),
        "fq5_prior_art_reference_count": len(fq5_prior_art_ids),
        "human_decision_packet_count": human_decision_packet_count,
        "human_decision_option_count": fq1_decision_option_count,
        "human_decision_question_count": human_decision_question_count,
        "recommended_architecture": fq1_recommended_architecture,
        "fq2_human_decision_option_count": fq2_decision_option_count,
        "fq2_recommended_architecture": fq2_recommended_architecture,
        "fq3_human_decision_option_count": fq3_decision_option_count,
        "fq3_recommended_architecture": fq3_recommended_architecture,
        "fq4_human_decision_option_count": fq4_decision_option_count,
        "fq4_recommended_architecture": fq4_recommended_architecture,
        "fq5_human_decision_option_count": fq5_decision_option_count,
        "fq5_recommended_architecture": fq5_recommended_architecture,
        "fq5_refounding_principle_count": fq5_refounding_principle_count,
        **article_architecture_metrics,
        **remaining_design_metrics,
        **cross_domain_packet_metrics,
        **coordinated_decision_metrics,
        **constitution_draft_metrics,
        **ratification_review_metrics,
        **final_blocker_metrics,
    }
    return ValidationResult(tuple(errors), metrics)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="repository root",
    )
    args = parser.parse_args()
    result = validate(args.root)
    if result.passed:
        print("VALIDATION_RESULT: PASS")
        for name, value in result.metrics.items():
            print(f"{name.upper()}: {json.dumps(value, sort_keys=True)}")
        return 0
    print("VALIDATION_RESULT: FAIL")
    for error in result.errors:
        print(f"- {error}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
