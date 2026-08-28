from __future__ import annotations

import json
import shutil
import unittest
from pathlib import Path
from uuid import uuid4

from tools.validate_bootstrap import validate


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class ConstitutionalResearchBaselineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = (
            REPOSITORY_ROOT
            / ".bootstrap-test-workspace"
            / str(uuid4())
            / "repository"
        )
        shutil.copytree(
            REPOSITORY_ROOT,
            self.root,
            ignore=shutil.ignore_patterns(
                ".git",
                ".bootstrap-test-workspace",
                "__pycache__",
                ".pytest_cache",
                ".ruff_cache",
                "*.pyc",
            ),
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.root.parent, ignore_errors=True)
        workspace_root = REPOSITORY_ROOT / ".bootstrap-test-workspace"
        if workspace_root.exists() and not any(workspace_root.iterdir()):
            workspace_root.rmdir()

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
        result = validate(self.root)
        self.assertTrue(result.passed)
        self.assertEqual(result.metrics["prior_art_entry_count"], 33)
        self.assertEqual(result.metrics["issue_prior_art_link_count"], 164)
        self.assertEqual(result.metrics["adoption_map_entry_count"], 18)
        self.assertEqual(result.metrics["analytical_decision_record_count"], 1)
        self.assertEqual(result.metrics["candidate_architecture_count"], 5)
        self.assertEqual(
            result.metrics["decision_record_status_counts"],
            {"UNDER_REVIEW": 1},
        )
        self.assertEqual(
            result.metrics["fq1_historical_evidence_reference_count"], 32
        )
        self.assertEqual(result.metrics["fq1_prior_art_reference_count"], 33)
        self.assertEqual(result.metrics["decided_decision_count"], 0)
        self.assertEqual(result.metrics["accepted_requirement_count"], 0)
        self.assertEqual(result.metrics["constitutional_provision_count"], 0)

    def test_fq1_analytical_record_cannot_masquerade_as_decided(self) -> None:
        def add_decision_evidence(record) -> None:
            record["status"] = "DECIDED"
            record["human_decision"] = {
                "authorized_by": "test authority",
                "authorization_record": "test record",
                "decision_date": "test date",
            }
            record["decision_date"] = "test date"

        self.update_json(
            "constitutional-design/decisions/CDR-001.yaml",
            add_decision_evidence,
        )
        self.assert_error("ANALYTICAL_CDR_MASQUERADING_DECISION")

    def test_fq1_analytical_record_cannot_create_requirements(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-001.yaml",
            lambda record: record["resulting_requirements"].append("CR-001"),
        )
        self.assert_error("ANALYTICAL_CDR_MASQUERADING_DECISION")

    def test_fq1_decision_record_schema_is_exact(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-001.yaml",
            lambda record: record.update(extra_top_level_field=True),
        )
        self.assert_error("DECISION_RECORD_SCHEMA")

    def test_fq1_requires_explicit_no_human_decision_statement(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-001.yaml",
            lambda record: record["dissent"][0].update(
                statement="No decision yet."
            ),
        )
        self.assert_error("FQ1_NO_HUMAN_DECISION_STATEMENT")

    def test_fq1_no_decision_statement_cannot_be_moved_elsewhere(self) -> None:
        def move_statement(record) -> None:
            statement = record["dissent"][0]["statement"]
            record["dissent"][0]["statement"] = "A decision was made."
            record["assumptions"].append(
                {"assumption": statement, "boundary": "Moved statement."}
            )

        self.update_json(
            "constitutional-design/decisions/CDR-001.yaml",
            move_statement,
        )
        self.assert_error("FQ1_NO_HUMAN_DECISION_STATEMENT")

    def test_fq1_source_material_paths_must_resolve(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-001.yaml",
            lambda record: record["source_material"].append(
                "constitutional-design/sources/DOES-NOT-EXIST.yaml"
            ),
        )
        self.assert_error("FQ1_SOURCE_MATERIAL")

    def test_fq1_historical_reference_must_resolve(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-001.yaml",
            lambda record: record["historical_analogues"][0]["mappings"][
                0
            ].update(evidence_id="HE-MISSING"),
        )
        self.assert_error("FQ1_HISTORICAL_ANALOGUES_REFERENCES")

    def test_fq1_prior_art_reference_must_resolve(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-001.yaml",
            lambda record: record["prior_art"][0]["mappings"][0].update(
                prior_art_id="PA-MISSING"
            ),
        )
        self.assert_error("FQ1_PRIOR_ART_REFERENCES")

    def test_fq1_matrix_cannot_select_automatic_winner(self) -> None:
        def select_winner(record) -> None:
            matrix = record["reviews"][0]
            matrix["selection_boundary"]["selected_architecture"] = "E"
            matrix["selection_boundary"]["automatic_winner"] = True

        self.update_json(
            "constitutional-design/decisions/CDR-001.yaml",
            select_winner,
        )
        self.assert_error("FQ1_COMPARATIVE_MATRIX_SELECTION")

    def test_fq1_synthesis_cannot_select_a_winner(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-001.yaml",
            lambda record: record["reviews"][2].update(
                selection_statement="Architecture E is selected as the winner."
            ),
        )
        self.assert_error("FQ1_NEUTRAL_SYNTHESIS")

    def test_fq1_architecture_cannot_add_selection_marker(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-001.yaml",
            lambda record: record["candidate_architectures"][4].update(
                selected=True,
                decision_status="ADOPTED",
            ),
        )
        self.assert_error("FQ1_ARCHITECTURE_SCHEMA")

    def test_fq1_cannot_select_architecture_in_analysis_prose(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-001.yaml",
            lambda record: record["candidate_architectures"][0].update(
                definition="Architecture E is selected as the winner."
            ),
        )
        self.assert_error("FQ1_ARCHITECTURE_SELECTION_CLAIM")

    def test_additional_fq1_architecture_requires_substantive_identity(self) -> None:
        def add_empty_architecture(record) -> None:
            architecture = dict(record["candidate_architectures"][0])
            architecture["architecture_id"] = ""
            architecture["name"] = ""
            architecture["definition"] = ""
            record["candidate_architectures"].append(architecture)

        self.update_json(
            "constitutional-design/decisions/CDR-001.yaml",
            add_empty_architecture,
        )
        result = validate(self.root)
        self.assertFalse(result.passed)
        codes = {error.split(":", 1)[0] for error in result.errors}
        self.assertIn("FQ1_ARCHITECTURE_IDS", codes)
        self.assertIn("FQ1_ARCHITECTURE_SCHEMA", codes)

    def test_fq1_matrix_cannot_use_numeric_scores(self) -> None:
        def add_score(record) -> None:
            matrix = record["reviews"][0]
            first = matrix["architecture_assessments"][0]
            first["dimensions"]["preservation_of_human_sovereignty"][
                "assessment"
            ] = 10

        self.update_json(
            "constitutional-design/decisions/CDR-001.yaml",
            add_score,
        )
        result = validate(self.root)
        self.assertFalse(result.passed)
        codes = {error.split(":", 1)[0] for error in result.errors}
        self.assertIn("FQ1_COMPARATIVE_MATRIX_SCORES", codes)
        self.assertIn("FQ1_COMPARATIVE_MATRIX_COVERAGE", codes)

    def test_fq1_architecture_dimension_is_required(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-001.yaml",
            lambda record: record["candidate_architectures"][0][
                "dimensions"
            ].pop("appeal"),
        )
        self.assert_error("FQ1_ARCHITECTURE_DIMENSIONS")

    def test_fq1_architecture_attack_is_required(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-001.yaml",
            lambda record: record["candidate_architectures"][0][
                "adversarial_tests"
            ].pop("validator_capture"),
        )
        self.assert_error("FQ1_ADVERSARIAL_TESTS")

    def test_fq1_core_distinction_is_required(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-001.yaml",
            lambda record: record["candidate_architectures"][0][
                "constitutional_distinction"
            ].pop("sovereignty_over_institutional_ends"),
        )
        self.assert_error("FQ1_CORE_DISTINCTION")

    def test_malformed_fq1_structures_fail_without_crashing(self) -> None:
        def malform_record(record) -> None:
            record["candidate_architectures"] = [None]
            record["historical_analogues"][0]["architecture_id"] = {}
            record["historical_analogues"][0]["mappings"][0][
                "classification"
            ] = {}
            record["prior_art"][0]["mappings"][0]["prior_art_id"] = {}
            record["reviews"][0]["architecture_assessments"][0][
                "architecture_id"
            ] = {}

        self.update_json(
            "constitutional-design/decisions/CDR-001.yaml",
            malform_record,
        )
        result = validate(self.root)
        self.assertFalse(result.passed)
        self.assertTrue(
            any(
                error.startswith("FQ1_CANDIDATE_ARCHITECTURES:")
                for error in result.errors
            )
        )

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

    def test_prior_art_entry_with_wrong_schema_fails(self) -> None:
        self.update_json(
            "constitutional-design/sources/PRIOR_ART_REGISTER.yaml",
            lambda record: record["prior_art_entries"][0].pop("name"),
        )
        self.assert_error("PRIOR_ART_ENTRY_SCHEMA")

    def test_prior_art_status_vocabulary_is_exact(self) -> None:
        self.update_json(
            "constitutional-design/sources/PRIOR_ART_REGISTER.yaml",
            lambda record: record["source_statuses"].append("UNVERIFIED"),
        )
        self.assert_error("PRIOR_ART_SOURCE_STATUS_VOCABULARY")

    def test_malformed_prior_art_vocabulary_fails_without_crashing(self) -> None:
        self.update_json(
            "constitutional-design/sources/PRIOR_ART_REGISTER.yaml",
            lambda record: record.update(
                permitted_research_classifications=None
            ),
        )
        self.assert_error("PRIOR_ART_OVERLAP_VOCABULARY")

    def test_unverified_source_cannot_claim_established_prior_art(self) -> None:
        self.update_json(
            "constitutional-design/sources/PRIOR_ART_REGISTER.yaml",
            lambda record: record["prior_art_entries"][0].update(
                source_status="SOURCE_TO_VERIFY"
            ),
        )
        self.assert_error("PRIOR_ART_EVIDENCE_CONTRADICTION")

    def test_duplicate_prior_art_identifier_fails(self) -> None:
        def duplicate_identifier(record) -> None:
            record["prior_art_entries"][1]["prior_art_id"] = record[
                "prior_art_entries"
            ][0]["prior_art_id"]

        self.update_json(
            "constitutional-design/sources/PRIOR_ART_REGISTER.yaml",
            duplicate_identifier,
        )
        self.assert_error("DUPLICATE_PRIOR_ART_ID")

    def test_malformed_prior_art_identifier_fails_without_crashing(self) -> None:
        self.update_json(
            "constitutional-design/sources/PRIOR_ART_REGISTER.yaml",
            lambda record: record["prior_art_entries"][0].update(
                prior_art_id={}
            ),
        )
        self.assert_error("PRIOR_ART_ID")

    def test_malformed_prior_art_enums_fail_without_crashing(self) -> None:
        def use_malformed_enums(record) -> None:
            entry = record["prior_art_entries"][0]
            entry["source_status"] = {}
            entry["overlap_classification"] = []
            entry["candidate_disposition"] = {}

        self.update_json(
            "constitutional-design/sources/PRIOR_ART_REGISTER.yaml",
            use_malformed_enums,
        )
        result = validate(self.root)
        self.assertFalse(result.passed)
        expected_codes = {
            "PRIOR_ART_SOURCE_STATUS",
            "PRIOR_ART_OVERLAP_CLASSIFICATION",
            "PRIOR_ART_CANDIDATE_DISPOSITION",
        }
        actual_codes = {error.split(":", 1)[0] for error in result.errors}
        self.assertTrue(expected_codes.issubset(actual_codes))

    def test_verified_prior_art_requires_stable_http_reference(self) -> None:
        self.update_json(
            "constitutional-design/sources/PRIOR_ART_REGISTER.yaml",
            lambda record: record["prior_art_entries"][0].update(
                source_reference="not-a-url"
            ),
        )
        self.assert_error("VERIFIED_PRIOR_ART_REFERENCE")

    def test_multiple_prior_art_urls_require_safe_list_encoding(self) -> None:
        def use_delimited_urls(record) -> None:
            record["prior_art_entries"][7]["source_reference"] = (
                "https://example.com/one ; https://example.com/two"
            )

        self.update_json(
            "constitutional-design/sources/PRIOR_ART_REGISTER.yaml",
            use_delimited_urls,
        )
        self.assert_error("PRIOR_ART_SOURCE_REFERENCE_ENCODING")

    def test_verified_prior_art_requires_provenance_and_review_state(self) -> None:
        def remove_verification_state(record) -> None:
            record["prior_art_entries"][0]["provenance"] = ""
            record["prior_art_entries"][0]["review_status"] = ""

        self.update_json(
            "constitutional-design/sources/PRIOR_ART_REGISTER.yaml",
            remove_verification_state,
        )
        self.assert_error("PRIOR_ART_VERIFICATION_STATE")

    def test_verified_prior_art_requires_dated_review_provenance(self) -> None:
        self.update_json(
            "constitutional-design/sources/PRIOR_ART_REGISTER.yaml",
            lambda record: record["prior_art_entries"][0].update(
                provenance="reviewed",
                review_status="DESK_REVIEWED",
            ),
        )
        self.assert_error("VERIFIED_PRIOR_ART_PROVENANCE")

    def test_unresolved_prior_art_reference_fails(self) -> None:
        self.update_json(
            "constitutional-design/issues/IR-01-human-sovereignty.yaml",
            lambda record: record["known_prior_art"].append("PA-MISSING"),
        )
        self.assert_error("UNRESOLVED_PRIOR_ART_REFERENCE")

    def test_malformed_issue_prior_art_reference_fails_without_crashing(self) -> None:
        self.update_json(
            "constitutional-design/issues/IR-01-human-sovereignty.yaml",
            lambda record: record["known_prior_art"].append({}),
        )
        self.assert_error("UNRESOLVED_PRIOR_ART_REFERENCE")

    def test_asymmetric_prior_art_mapping_fails(self) -> None:
        def remove_register_mapping(record) -> None:
            record["prior_art_entries"][0]["relevant_issues"].remove("IR-02")

        self.update_json(
            "constitutional-design/sources/PRIOR_ART_REGISTER.yaml",
            remove_register_mapping,
        )
        self.assert_error("PRIOR_ART_LINK_ASYMMETRY")

    def test_every_issue_requires_prior_art_coverage(self) -> None:
        self.update_json(
            "constitutional-design/issues/IR-03-emergency-necessity.yaml",
            lambda record: record.update(known_prior_art=[]),
        )
        self.assert_error("PRIOR_ART_ISSUE_COVERAGE")

    def test_prior_art_candidate_disposition_is_exact(self) -> None:
        self.update_json(
            "constitutional-design/sources/PRIOR_ART_REGISTER.yaml",
            lambda record: record["prior_art_entries"][0].update(
                candidate_disposition="ADOPTED"
            ),
        )
        self.assert_error("PRIOR_ART_CANDIDATE_DISPOSITION")

    def test_adoption_map_source_reference_must_resolve(self) -> None:
        self.update_json(
            "constitutional-design/sources/MECHANISM_ADOPTION_MAP.yaml",
            lambda record: record["entries"][0]["prior_art_sources"].append(
                "PA-MISSING"
            ),
        )
        self.assert_error("MECHANISM_PRIOR_ART_SOURCES")

    def test_adoption_map_issue_reference_must_resolve(self) -> None:
        self.update_json(
            "constitutional-design/sources/MECHANISM_ADOPTION_MAP.yaml",
            lambda record: record["entries"][0]["relevant_issues"].append(
                "IR-99"
            ),
        )
        self.assert_error("MECHANISM_RELEVANT_ISSUES")

    def test_malformed_adoption_map_identifiers_fail_without_crashing(self) -> None:
        def add_malformed_identifiers(record) -> None:
            record["entries"][0]["prior_art_sources"].append({})
            record["entries"][0]["relevant_issues"].append([])

        self.update_json(
            "constitutional-design/sources/MECHANISM_ADOPTION_MAP.yaml",
            add_malformed_identifiers,
        )
        result = validate(self.root)
        self.assertFalse(result.passed)
        self.assertTrue(
            any(
                error.startswith("MECHANISM_PRIOR_ART_SOURCES:")
                for error in result.errors
            )
        )
        self.assertTrue(
            any(
                error.startswith("MECHANISM_RELEVANT_ISSUES:")
                for error in result.errors
            )
        )

    def test_adoption_map_requires_human_decision(self) -> None:
        self.update_json(
            "constitutional-design/sources/MECHANISM_ADOPTION_MAP.yaml",
            lambda record: record["entries"][0].update(
                decision_required=False
            ),
        )
        self.assert_error("MECHANISM_DECISION_REQUIRED")

    def test_adoption_map_must_remain_a_research_artifact(self) -> None:
        self.update_json(
            "constitutional-design/sources/MECHANISM_ADOPTION_MAP.yaml",
            lambda record: record.update(map_status="ADOPTED"),
        )
        self.assert_error("MECHANISM_ADOPTION_MAP_STATUS")

    def test_final_adoption_status_is_forbidden(self) -> None:
        self.update_json(
            "constitutional-design/sources/MECHANISM_ADOPTION_MAP.yaml",
            lambda record: record["entries"][0].update(
                candidate_disposition="ADOPTED"
            ),
        )
        self.assert_error("FINAL_ADOPTION_STATUS")

    def test_affirmative_adoption_claim_in_prose_is_forbidden(self) -> None:
        self.update_json(
            "constitutional-design/sources/MECHANISM_ADOPTION_MAP.yaml",
            lambda record: record["entries"][0].update(
                rationale="This mechanism is adopted."
            ),
        )
        self.assert_error("FINAL_ADOPTION_STATUS")

    def test_passive_adoption_claim_in_prose_is_forbidden(self) -> None:
        self.update_json(
            "constitutional-design/sources/MECHANISM_ADOPTION_MAP.yaml",
            lambda record: record["entries"][0].update(
                rationale="This mechanism has been adopted."
            ),
        )
        self.assert_error("FINAL_ADOPTION_STATUS")

    def test_adoption_map_must_represent_all_candidate_dispositions(self) -> None:
        def remove_not_applicable(record) -> None:
            for entry in record["entries"]:
                if entry["candidate_disposition"] == "NOT_APPLICABLE":
                    entry["candidate_disposition"] = "CANDIDATE_EXTEND"

        self.update_json(
            "constitutional-design/sources/MECHANISM_ADOPTION_MAP.yaml",
            remove_not_applicable,
        )
        self.assert_error("MECHANISM_ADOPTION_DISPOSITION_COVERAGE")

    def test_no_close_prior_art_is_not_novel_rule_is_required(self) -> None:
        self.update_json(
            "constitutional-design/sources/PRIOR_ART_REGISTER.yaml",
            lambda record: record.update(
                novelty_rule="NO_CLOSE_PRIOR_ART_FOUND_IN_SEARCH means NOVEL."
            ),
        )
        self.assert_error("NO_CLOSE_IS_NOT_NOVEL")

    def test_candidate_architecture_during_baseline_fails(self) -> None:
        self.update_json(
            "constitutional-design/issues/IR-01-human-sovereignty.yaml",
            lambda record: record["candidate_architectures"].append("test"),
        )
        self.assert_error("CANDIDATE_ARCHITECTURES_NOT_EMPTY")

    def test_automated_novel_classification_fails(self) -> None:
        self.update_json(
            "constitutional-design/sources/PRIOR_ART_REGISTER.yaml",
            lambda record: record.update(automated_classification="NOVEL"),
        )
        self.assert_error("AUTOMATED_NOVELTY")

    def test_affirmative_novelty_claim_in_prose_fails(self) -> None:
        self.update_json(
            "constitutional-design/sources/PRIOR_ART_REGISTER.yaml",
            lambda record: record["prior_art_entries"][0].update(
                limitations="This mechanism is novel."
            ),
        )
        self.assert_error("AUTOMATED_NOVELTY")

    def test_issue_identifiers_are_anchored_to_filenames(self) -> None:
        def replace_issue_identifier(record) -> None:
            record["issue_id"] = "IR-99"
            record["known_prior_art"] = []

        self.update_json(
            "constitutional-design/issues/IR-18-human-control-and-comprehensibility.yaml",
            replace_issue_identifier,
        )
        result = validate(self.root)
        self.assertFalse(result.passed)
        self.assertTrue(
            any(
                error.startswith("ISSUE_IDENTIFIERS:")
                for error in result.errors
            )
        )
        self.assertTrue(
            any(
                error.startswith("ISSUE_IDENTIFIER_FILENAME:")
                for error in result.errors
            )
        )

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
