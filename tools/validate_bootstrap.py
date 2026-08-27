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


def _contains_novel(value: Any) -> bool:
    if isinstance(value, dict):
        return any(_contains_novel(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_novel(item) for item in value)
    return isinstance(value, str) and value.strip().upper() == "NOVEL"


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
        if not isinstance(issue.get("provenance"), dict):
            errors.append(f"PROVENANCE_REQUIRED: {path}")

    questions_path = (
        root / "constitutional-design" / "FOUNDATIONAL_QUESTIONS.md"
    )
    try:
        questions_text = questions_path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"FOUNDATIONAL_QUESTION_COUNT: cannot read file: {exc}")
        questions_text = ""

    question_blocks = re.findall(
        r"^## (FQ-\d{2})\s*$([\s\S]*?)(?=^## FQ-\d{2}\s*$|\Z)",
        questions_text,
        flags=re.MULTILINE,
    )
    question_ids = [question_id for question_id, _ in question_blocks]
    expected_question_ids = {f"FQ-{index:02d}" for index in range(1, 6)}
    if len(question_blocks) != 5 or set(question_ids) != expected_question_ids:
        errors.append(
            "FOUNDATIONAL_QUESTION_COUNT: expected exactly FQ-01 through FQ-05"
        )
    for question_id, block in question_blocks:
        status_match = re.search(r"\*\*Status:\*\*\s*`([^`]+)`", block)
        status = status_match.group(1) if status_match else None
        if status != "UNRESOLVED":
            errors.append(
                f"FOUNDATIONAL_QUESTION_STATUS: {question_id} is {status!r}"
            )

    decision_dir = root / "constitutional-design" / "decisions"
    decisions = _load_record_set(decision_dir, "CDR-*.yaml", errors)
    decisions_by_id: dict[str, dict[str, Any]] = {}
    decided_count = 0
    for decision in decisions:
        if not isinstance(decision.get("provenance"), dict):
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

    requirement_dir = root / "constitutional-design" / "requirements"
    requirements = _load_record_set(requirement_dir, "CR-*.yaml", errors)
    accepted_count = 0
    for requirement in requirements:
        if not isinstance(requirement.get("provenance"), dict):
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

    source_path = (
        root / "constitutional-design" / "sources" / "SOURCE_INDEX.yaml"
    )
    source_index = _load_record(source_path, errors) or {}
    if not isinstance(source_index.get("provenance"), dict):
        errors.append(f"PROVENANCE_REQUIRED: {source_path}")
    source_entries: list[dict[str, Any]] = []
    for collection_name in ("intellectual_neighborhoods", "research_leads"):
        collection = source_index.get(collection_name)
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
            provenance = entry.get("provenance")
            if not isinstance(provenance, dict):
                errors.append(
                    f"PROVENANCE_REQUIRED: source {entry.get('name')!r}"
                )
                continue
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

    structured_records: list[Any] = [
        *issues,
        *decisions,
        *requirements,
        source_index,
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
    for _, block in question_blocks:
        status_match = re.search(r"\*\*Status:\*\*\s*`([^`]+)`", block)
        status = status_match.group(1) if status_match else "MISSING"
        question_status_counts[status] = question_status_counts.get(status, 0) + 1

    metrics = {
        "issue_count": len(issues),
        "issue_status_counts": issue_status_counts,
        "foundational_question_count": len(question_blocks),
        "foundational_question_status_counts": question_status_counts,
        "decided_decision_count": decided_count,
        "accepted_requirement_count": accepted_count,
        "constitutional_provision_count": len(provision_files),
        "source_entry_count": len(source_entries),
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

