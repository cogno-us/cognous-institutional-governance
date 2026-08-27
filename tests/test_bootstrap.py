from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tools.validate_bootstrap import validate


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class ConstitutionalResearchBaselineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name) / "repository"
        shutil.copytree(
            REPOSITORY_ROOT,
            self.root,
            ignore=shutil.ignore_patterns(
                ".git",
                "__pycache__",
                ".pytest_cache",
                ".ruff_cache",
                "*.pyc",
            ),
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def assert_error(self, code: str) -> None:
        result = validate(self.root)
        self.assertFalse(result.passed)
        self.assertTrue(
            any(error.startswith(f"{code}:") for error in result.errors),
            f"expected {code}, found {result.errors}",
        )

    def update_json(self, relative_path: str, update) -> None:
        path = self.root / relative_path
        record = json.loads(path.read_text(encoding="utf-8"))
        update(record)
        path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    def test_valid_bootstrap_passes(self) -> None:
        self.assertTrue(validate(self.root).passed)

    def test_missing_issue_fails(self) -> None:
        (
            self.root
            / "constitutional-design"
            / "issues"
            / "IR-18-human-control-and-comprehensibility.yaml"
        ).unlink()
        self.assert_error("ISSUE_COUNT")

    def test_duplicate_issue_identifier_fails(self) -> None:
        self.update_json(
            "constitutional-design/issues/IR-18-human-control-and-comprehensibility.yaml",
            lambda record: record.update(issue_id="IR-17"),
        )
        self.assert_error("DUPLICATE_ISSUE_ID")

    def test_resolved_issue_during_bootstrap_fails(self) -> None:
        self.update_json(
            "constitutional-design/issues/IR-01-human-sovereignty.yaml",
            lambda record: record.update(status="RESOLVED"),
        )
        self.assert_error("ISSUE_STATUS")

    def test_missing_foundational_question_fails(self) -> None:
        path = (
            self.root
            / "constitutional-design"
            / "FOUNDATIONAL_QUESTIONS.yaml"
        )
        record = json.loads(path.read_text(encoding="utf-8"))
        record["questions"].pop()
        path.write_text(json.dumps(record), encoding="utf-8")
        self.assert_error("FOUNDATIONAL_QUESTION_COUNT")

    def test_resolved_foundational_question_fails(self) -> None:
        path = (
            self.root
            / "constitutional-design"
            / "FOUNDATIONAL_QUESTIONS.yaml"
        )
        record = json.loads(path.read_text(encoding="utf-8"))
        record["questions"][0]["status"] = "RESOLVED"
        path.write_text(json.dumps(record), encoding="utf-8")
        self.assert_error("FOUNDATIONAL_QUESTION_STATUS")

    def test_decided_decision_without_human_evidence_fails(self) -> None:
        path = (
            self.root
            / "constitutional-design"
            / "decisions"
            / "CDR-001.yaml"
        )
        record = {
            "decision_id": "CDR-001",
            "status": "DECIDED",
            "human_decision": {
                "authorized_by": "",
                "authorization_record": "",
                "decision_date": "",
            },
            "provenance": {"source": "test fixture"},
        }
        path.write_text(json.dumps(record), encoding="utf-8")
        self.assert_error("DECIDED_WITHOUT_HUMAN_DECISION")

    def test_verified_source_without_provenance_fails(self) -> None:
        def mark_verified(record) -> None:
            record["research_leads"][0]["status"] = "VERIFIED_SOURCE"

        self.update_json(
            "constitutional-design/sources/PRIOR_ART_REGISTER.yaml",
            mark_verified,
        )
        self.assert_error("VERIFIED_SOURCE_PROVENANCE")

    def test_automated_novel_classification_fails(self) -> None:
        self.update_json(
            "constitutional-design/sources/PRIOR_ART_REGISTER.yaml",
            lambda record: record.update(automated_classification="NOVEL"),
        )
        self.assert_error("AUTOMATED_NOVELTY")

    def test_accepted_requirement_without_provenance_fails(self) -> None:
        path = (
            self.root
            / "constitutional-design"
            / "requirements"
            / "CR-001.yaml"
        )
        record = {
            "requirement_id": "CR-001",
            "status": "ACCEPTED_FOR_DRAFTING",
            "source_decisions": [],
            "provenance": {"source": "test fixture"},
        }
        path.write_text(json.dumps(record), encoding="utf-8")
        self.assert_error("ACCEPTED_REQUIREMENT_PROVENANCE")

    def test_missing_provenance_fails(self) -> None:
        self.update_json(
            "constitutional-design/issues/IR-01-human-sovereignty.yaml",
            lambda record: record.pop("provenance"),
        )
        self.assert_error("PROVENANCE_REQUIRED")

    def test_constitutional_provision_during_baseline_fails(self) -> None:
        path = self.root / "constitution" / "Article-01.md"
        path.write_text("Premature provision.", encoding="utf-8")
        self.assert_error("CONSTITUTIONAL_PROVISIONS")

    def test_duplicate_historical_evidence_identifier_fails(self) -> None:
        def duplicate_identifier(record) -> None:
            record["entries"][1]["evidence_id"] = record["entries"][0][
                "evidence_id"
            ]

        self.update_json(
            "constitutional-design/sources/HISTORICAL_EVIDENCE_REGISTER.yaml",
            duplicate_identifier,
        )
        self.assert_error("DUPLICATE_HISTORICAL_EVIDENCE_ID")

    def test_unresolved_historical_evidence_reference_fails(self) -> None:
        self.update_json(
            "constitutional-design/issues/IR-01-human-sovereignty.yaml",
            lambda record: record["historical_evidence"].append("HE-MISSING"),
        )
        self.assert_error("UNRESOLVED_HISTORICAL_EVIDENCE_REFERENCE")

    def test_collapsed_historical_epistemic_categories_fail(self) -> None:
        def collapse_categories(record) -> None:
            record["entries"][0]["interpretation"] = record["entries"][0][
                "observation"
            ]

        self.update_json(
            "constitutional-design/sources/HISTORICAL_EVIDENCE_REGISTER.yaml",
            collapse_categories,
        )
        self.assert_error("HISTORICAL_EPISTEMIC_SEPARATION")

    def test_verified_historical_evidence_without_provenance_fails(self) -> None:
        def mark_verified(record) -> None:
            record["entries"][0]["source_status"] = "VERIFIED"

        self.update_json(
            "constitutional-design/sources/HISTORICAL_EVIDENCE_REGISTER.yaml",
            mark_verified,
        )
        self.assert_error("VERIFIED_HISTORICAL_EVIDENCE_PROVENANCE")

    def test_historical_evidence_without_limitations_fails(self) -> None:
        def remove_limitations(record) -> None:
            record["entries"][0]["counterevidence_or_limitations"] = []

        self.update_json(
            "constitutional-design/sources/HISTORICAL_EVIDENCE_REGISTER.yaml",
            remove_limitations,
        )
        self.assert_error("HISTORICAL_LIMITATIONS_REQUIRED")

    def test_decided_record_is_forbidden_during_historical_ingestion(self) -> None:
        path = (
            self.root
            / "constitutional-design"
            / "decisions"
            / "CDR-002.yaml"
        )
        record = {
            "decision_id": "CDR-002",
            "status": "DECIDED",
            "human_decision": {
                "authorized_by": "test human authority",
                "authorization_record": "test authorization",
                "decision_date": "test date",
            },
            "provenance": {"source": "test fixture"},
        }
        path.write_text(json.dumps(record), encoding="utf-8")
        self.assert_error("HISTORICAL_BASELINE_DECISION")

    def test_asymmetric_historical_evidence_mapping_fails(self) -> None:
        def remove_register_mapping(record) -> None:
            record["entries"][0]["relevant_issues"].remove("IR-02")

        self.update_json(
            "constitutional-design/sources/HISTORICAL_EVIDENCE_REGISTER.yaml",
            remove_register_mapping,
        )
        self.assert_error("HISTORICAL_EVIDENCE_LINK_ASYMMETRY")

    def test_source_to_verify_cannot_claim_verified_provenance(self) -> None:
        def claim_verification(record) -> None:
            record["entries"][0]["provenance"]["verification"] = "VERIFIED"

        self.update_json(
            "constitutional-design/sources/HISTORICAL_EVIDENCE_REGISTER.yaml",
            claim_verification,
        )
        self.assert_error("HISTORICAL_SOURCE_STATUS_CONFLICT")


if __name__ == "__main__":
    unittest.main()
