#!/usr/bin/env python3
"""Validate Alvorada's constitutional research bootstrap invariants."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


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
SOURCE_LEAD_STATUSES = {"RESEARCH_LEAD", "SOURCE_TO_VERIFY"}
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
    except (OSError, json.JSONDecodeError) as exc:
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
    duplicate_ids = sorted(
        {issue_id for issue_id in issue_ids if issue_ids.count(issue_id) > 1}
    )
    if duplicate_ids:
        errors.append(f"DUPLICATE_ISSUE_ID: {', '.join(map(str, duplicate_ids))}")

    for issue in issues:
        path = issue["_record_path"]
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
    question_ids = [question.get("question_id") for question in questions]
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
    decisions_by_id: dict[str, dict[str, Any]] = {}
    decided_count = 0
    for decision in decisions:
        if not _has_provenance(decision):
            errors.append(
                f"PROVENANCE_REQUIRED: {decision['_record_path']}"
            )
        decision_id = decision.get("decision_id")
        if isinstance(decision_id, str):
            decisions_by_id[decision_id] = decision
        if decision.get("status") == "DECIDED":
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
    source_entries: list[dict[str, Any]] = []
    for collection_name in ("intellectual_neighborhoods", "research_leads"):
        collection = prior_art.get(collection_name)
        if not isinstance(collection, list):
            errors.append(f"SOURCE_REGISTER: {collection_name} must be a list")
            continue
        for entry in collection:
            if not isinstance(entry, dict):
                errors.append(
                    f"SOURCE_REGISTER: invalid entry in {collection_name}"
                )
                continue
            source_entries.append(entry)
            if not _has_provenance(entry):
                errors.append(
                    f"PROVENANCE_REQUIRED: source {entry.get('name')!r}"
                )
                continue
            provenance = entry["provenance"]
            if entry.get("status") not in SOURCE_LEAD_STATUSES:
                errors.append(
                    "RESEARCH_LEAD_STATUS: "
                    f"{entry.get('name')!r} is {entry.get('status')!r}"
                )
            if entry.get("status") == "VERIFIED_SOURCE":
                evidence_fields = (
                    "primary_source_reference",
                    "verified_by",
                    "verified_on",
                )
                if not all(
                    _is_evidence(provenance.get(field))
                    for field in evidence_fields
                ):
                    errors.append(
                        "VERIFIED_SOURCE_PROVENANCE: "
                        f"{entry.get('name')!r}"
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
    duplicate_evidence_ids = sorted(
        {
            evidence_id
            for evidence_id in evidence_ids
            if evidence_ids.count(evidence_id) > 1
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
        if source_status not in HISTORICAL_SOURCE_STATUSES:
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
        if not isinstance(relevant_issues, list) or not relevant_issues or any(
            issue_id not in known_issue_ids for issue_id in relevant_issues
        ):
            errors.append(
                f"HISTORICAL_RELEVANT_ISSUES: {evidence_id} has an unknown issue"
            )

        provenance = entry.get("provenance", {})
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
            {
                reference
                for reference in references
                if not isinstance(reference, str)
                or reference not in evidence_id_set
            },
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
        for issue_id in entry.get("relevant_issues", [])
        if isinstance(issue_id, str)
    }
    if issue_link_pairs != register_link_pairs:
        errors.append(
            "HISTORICAL_EVIDENCE_LINK_ASYMMETRY: issue and register mappings differ"
        )

    structured_records: list[Any] = [
        *issues,
        *decisions,
        *requirements,
        source_index,
        prior_art,
        questions_record,
        historical_register,
    ]
    if any(_contains_novel(record) for record in structured_records):
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
        "decided_decision_count": decided_count,
        "accepted_requirement_count": accepted_count,
        "constitutional_provision_count": len(provision_files),
        "prior_art_research_lead_count": len(source_entries),
        "historical_evidence_entry_count": len(historical_entries),
        "issue_historical_link_count": historical_link_count,
        "historical_source_status_counts": historical_status_counts,
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
