#!/usr/bin/env python3
"""Validate Alvorada's constitutional research bootstrap invariants."""

from __future__ import annotations

import argparse
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
FQ1_NO_DECISION_STATEMENT = "NO HUMAN DECISION HAS BEEN MADE."
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
        and set(decision)
        == {"authorized_by", "authorization_record", "decision_date"}
        and all(decision.get(field) == "" for field in decision)
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
    return re.search(
        r"\bARCHITECTURE\s+[A-Z0-9_-]+\s+"
        r"(?:IS|WAS|HAS\s+BEEN)\s+"
        r"(?:SELECTED|ADOPTED|DECIDED|THE\s+WINNER)\b",
        value,
        flags=re.IGNORECASE,
    ) is not None


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

    if decision.get("status") != "UNDER_REVIEW":
        errors.append("FQ1_ANALYTICAL_STATUS: CDR-001 must be UNDER_REVIEW")
    if (
        not _is_empty_human_decision(decision)
        or _has_human_decision_evidence(decision)
        or decision.get("resulting_requirements") != []
    ):
        errors.append(
            "ANALYTICAL_CDR_MASQUERADING_DECISION: "
            "CDR-001 cannot contain decision evidence or requirements"
        )
    dissent = decision.get("dissent")
    has_designated_no_decision_statement = (
        isinstance(dissent, list)
        and len(dissent) == 1
        and isinstance(dissent[0], dict)
        and dissent[0].get("status") == "OPEN_FOR_SUBMISSION"
        and dissent[0].get("statement") == FQ1_NO_DECISION_STATEMENT
        and _is_evidence(dissent[0].get("record"))
    )
    if not has_designated_no_decision_statement:
        errors.append(
            "FQ1_NO_HUMAN_DECISION_STATEMENT: exact statement is required"
        )
    if _contains_architecture_selection_claim(decision):
        errors.append(
            "FQ1_ARCHITECTURE_SELECTION_CLAIM: "
            "analytical CDR cannot select an architecture"
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
        if status != "UNRESOLVED":
            errors.append(
                f"FOUNDATIONAL_QUESTION_STATUS: {question_id} is {status!r}"
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
        if set(decision) - {"_record_path"} != DECISION_FIELDS:
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
    if decided_count:
        errors.append(
            f"HISTORICAL_BASELINE_DECISION: expected 0 DECIDED records, found {decided_count}"
        )
    if "CDR-001" not in decisions_by_id:
        errors.append("FQ1_ANALYTICAL_RECORD_REQUIRED: CDR-001 is required")

    requirement_dir = root / "constitutional-design" / "requirements"
    requirements = _load_record_set(requirement_dir, "CR-*.yaml", errors)
    accepted_count = 0
    for requirement in requirements:
        if not _has_provenance(requirement):
            errors.append(
                f"PROVENANCE_REQUIRED: {requirement['_record_path']}"
            )
        if requirement.get("status") != "ACCEPTED_FOR_DRAFTING":
            continue
        accepted_count += 1
        sources = requirement.get("source_decisions")
        valid_sources = (
            isinstance(sources, list)
            and bool(sources)
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
    if accepted_count:
        errors.append(
            "HISTORICAL_BASELINE_REQUIREMENT: expected 0 "
            f"ACCEPTED_FOR_DRAFTING records, found {accepted_count}"
        )

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
