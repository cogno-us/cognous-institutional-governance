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

    def update_text(self, relative_path: str, update) -> None:
        path = self.root / relative_path
        text = path.read_text(encoding="utf-8")
        path.write_text(update(text), encoding="utf-8")

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
            {"DECIDED": 5},
        )
        self.assertEqual(
            result.metrics["fq1_historical_evidence_reference_count"], 32
        )
        self.assertEqual(result.metrics["fq1_prior_art_reference_count"], 33)
        self.assertEqual(result.metrics["decided_decision_count"], 5)
        self.assertEqual(result.metrics["accepted_requirement_count"], 35)
        self.assertEqual(
            result.metrics["foundational_question_status_counts"],
            {"RESOLVED": 5},
        )
        self.assertEqual(result.metrics["constitutional_provision_count"], 0)
        self.assertEqual(result.metrics["human_decision_packet_count"], 5)
        self.assertEqual(result.metrics["human_decision_option_count"], 8)
        self.assertEqual(result.metrics["human_decision_question_count"], 5)
        self.assertEqual(
            result.metrics["recommended_architecture"],
            "Architecture E",
        )
        self.assertEqual(result.metrics["fq2_candidate_architecture_count"], 5)
        self.assertEqual(
            result.metrics["fq2_historical_evidence_reference_count"], 12
        )
        self.assertEqual(result.metrics["fq2_prior_art_reference_count"], 13)
        self.assertEqual(result.metrics["fq2_human_decision_option_count"], 7)
        self.assertEqual(
            result.metrics["fq2_recommended_architecture"],
            "Architecture E",
        )
        self.assertEqual(result.metrics["fq3_candidate_architecture_count"], 5)
        self.assertEqual(
            result.metrics["fq3_historical_evidence_reference_count"], 12
        )
        self.assertEqual(result.metrics["fq3_prior_art_reference_count"], 14)
        self.assertEqual(result.metrics["fq3_human_decision_option_count"], 7)
        self.assertEqual(
            result.metrics["fq3_recommended_architecture"],
            "Architecture E",
        )
        self.assertEqual(result.metrics["fq4_candidate_architecture_count"], 5)
        self.assertEqual(
            result.metrics["fq4_historical_evidence_reference_count"], 14
        )
        self.assertEqual(result.metrics["fq4_prior_art_reference_count"], 14)
        self.assertEqual(result.metrics["fq4_human_decision_option_count"], 7)
        self.assertEqual(
            result.metrics["fq4_recommended_architecture"],
            "Architecture E",
        )
        self.assertEqual(result.metrics["fq5_candidate_architecture_count"], 5)
        self.assertEqual(
            result.metrics["fq5_historical_evidence_reference_count"], 15
        )
        self.assertEqual(result.metrics["fq5_prior_art_reference_count"], 14)
        self.assertEqual(result.metrics["fq5_human_decision_option_count"], 7)
        self.assertEqual(
            result.metrics["fq5_recommended_architecture"],
            "Architecture E",
        )
        self.assertEqual(result.metrics["fq5_refounding_principle_count"], 10)
        self.assertEqual(result.metrics["source_requirement_count"], 35)
        self.assertEqual(result.metrics["consolidated_requirement_count"], 20)
        self.assertEqual(result.metrics["proposed_article_count"], 8)
        self.assertEqual(
            result.metrics["ready_for_constitutional_draft_count"], 20
        )
        self.assertEqual(
            result.metrics["blocked_by_unresolved_design_count"], 0
        )
        self.assertEqual(result.metrics["subordinate_governance_law_count"], 0)
        self.assertEqual(result.metrics["implementation_standard_count"], 0)
        self.assertEqual(result.metrics["unmapped_requirement_count"], 0)
        self.assertEqual(result.metrics["design_domain_count"], 11)
        self.assertEqual(result.metrics["human_decisions_required"], 0)
        self.assertEqual(result.metrics["recommended_decision_count"], 11)
        self.assertEqual(result.metrics["cross_domain_conflict_count"], 7)
        self.assertEqual(
            result.metrics[
                "projected_ready_for_constitutional_draft_count"
            ],
            20,
        )
        self.assertEqual(result.metrics["projected_blocked_count"], 0)
        self.assertEqual(
            result.metrics[
                "genuine_residual_implementation_question_count"
            ],
            7,
        )
        self.assertEqual(
            result.metrics["coordinated_decision_status"],
            "DECIDED",
        )
        self.assertEqual(result.metrics["decision_component_count"], 4)
        self.assertEqual(
            result.metrics["blocking_contradictions_addressed"], 4
        )
        self.assertEqual(
            result.metrics["projected_blocking_contradictions_remaining"], 0
        )
        self.assertEqual(
            result.metrics["remaining_human_constitutional_decision_count"],
            0,
        )
        self.assertEqual(
            result.metrics["subordinate_governance_question_count"], 4
        )
        self.assertEqual(result.metrics["implementation_question_count"], 5)
        self.assertEqual(result.metrics["design_recommendations_adopted"], 11)
        self.assertEqual(result.metrics["decision_components_adopted"], 4)
        self.assertEqual(result.metrics["blocking_contradictions_remaining"], 0)
        self.assertEqual(result.metrics["draft_status"], "DRAFT_NOT_ADOPTED")
        self.assertEqual(result.metrics["article_count"], 8)
        self.assertEqual(result.metrics["section_count"], 24)
        self.assertEqual(result.metrics["source_requirements_covered"], 35)
        self.assertEqual(result.metrics["consolidated_groups_covered"], 20)
        self.assertEqual(result.metrics["foundational_decisions_covered"], 5)
        self.assertEqual(result.metrics["design_recommendations_covered"], 11)
        self.assertEqual(result.metrics["coordinated_corrections_covered"], 4)
        self.assertEqual(
            result.metrics["refounding_level_principles_covered"], 10
        )
        self.assertEqual(
            result.metrics["untraced_normative_proposition_count"], 0
        )
        self.assertEqual(result.metrics["new_human_decisions_required"], 1)
        self.assertEqual(result.metrics["cross_article_contradictions"], 0)
        self.assertEqual(result.metrics["open_questions_count"], 1)
        self.assertEqual(
            result.metrics["ratification_readiness"],
            "NOT_READY_FOR_HUMAN_RATIFICATION",
        )
        self.assertEqual(result.metrics["constitutional_blocker_count"], 1)
        self.assertEqual(
            result.metrics["ratification_cross_article_contradiction_count"],
            0,
        )
        self.assertEqual(
            result.metrics["ratification_adversarial_tests_pass"], "9/13"
        )
        self.assertEqual(
            result.metrics["human_comprehensibility_result"], "FAIL"
        )
        self.assertEqual(
            result.metrics["subordinate_law_boundary_result"], "FAIL"
        )
        self.assertEqual(
            result.metrics["ratification_recommendation"],
            "DO_NOT_RATIFY_UNTIL_HCA_COLLEGE_LIFECYCLE_IS_DECIDED",
        )
        self.assertEqual(
            result.metrics["final_ratification_blockers_analyzed"], 3
        )
        self.assertEqual(
            result.metrics["integrated_architecture_recommended"],
            "ALTERNATIVE_B",
        )
        self.assertEqual(
            result.metrics["projected_ratification_blockers_remaining"], 0
        )
        self.assertEqual(
            result.metrics["final_blocker_human_decisions_required"], 1
        )
        self.assertEqual(
            result.metrics["final_blocker_subordinate_law_item_count"], 9
        )
        self.assertEqual(result.metrics["adopted_architecture"], "ALTERNATIVE_B")
        self.assertEqual(result.metrics["blocker_decision_status"], "DECIDED")
        self.assertEqual(result.metrics["ratification_blockers_resolved"], 2)
        self.assertEqual(result.metrics["ratification_blockers_remaining"], 1)

    def test_final_blocker_analysis_is_required(self) -> None:
        (
            self.root
            / "constitutional-design"
            / "FINAL-RATIFICATION-BLOCKER-ANALYSIS.yaml"
        ).unlink()
        self.assert_error("FINAL_BLOCKER_ANALYSIS_REQUIRED")

    def test_final_blocker_analysis_requires_exact_adoption(self) -> None:
        self.update_json(
            "constitutional-design/FINAL-RATIFICATION-BLOCKER-ANALYSIS.yaml",
            lambda record: record.update(
                status="ANALYSIS_ONLY",
                human_decision_made=False,
                constitutional_effect="BINDING",
            ),
        )
        self.assert_error("FINAL_BLOCKER_ANALYSIS_BOUNDARY")

    def test_final_blocker_analysis_requires_all_blockers(self) -> None:
        self.update_json(
            "constitutional-design/FINAL-RATIFICATION-BLOCKER-ANALYSIS.yaml",
            lambda record: record["blockers"].pop(),
        )
        self.assert_error("FINAL_BLOCKER_ANALYSIS_BLOCKERS")

    def test_final_blocker_analysis_requires_all_stress_modes(self) -> None:
        self.update_json(
            "constitutional-design/FINAL-RATIFICATION-BLOCKER-ANALYSIS.yaml",
            lambda record: record["integrated_alternatives"][0][
                "stress_test"
            ].pop("machine_domination"),
        )
        self.assert_error("FINAL_BLOCKER_ANALYSIS_ALTERNATIVE_COMPLETENESS")

    def test_final_blocker_analysis_requires_four_alternatives(self) -> None:
        self.update_json(
            "constitutional-design/FINAL-RATIFICATION-BLOCKER-ANALYSIS.yaml",
            lambda record: record["integrated_alternatives"].pop(),
        )
        self.assert_error("FINAL_BLOCKER_ANALYSIS_ALTERNATIVES")

    def test_final_blocker_recommendation_requires_hca_root(self) -> None:
        self.update_json(
            "constitutional-design/FINAL-RATIFICATION-BLOCKER-ANALYSIS.yaml",
            lambda record: record["recommended_integrated_architecture"][
                "minimum_constitutional_allocations"
            ].pop("human_constitutional_authority"),
        )
        self.assert_error("FINAL_BLOCKER_RECOMMENDATION")

    def test_final_blocker_recommendation_requires_office_chains(self) -> None:
        self.update_json(
            "constitutional-design/FINAL-RATIFICATION-BLOCKER-ANALYSIS.yaml",
            lambda record: record["recommended_integrated_architecture"][
                "minimum_constitutional_allocations"
            ]["verification_office"].pop("replacement"),
        )
        self.assert_error("FINAL_BLOCKER_RECOMMENDATION")

    def test_final_blocker_recommendation_requires_closed_schedule(self) -> None:
        self.update_json(
            "constitutional-design/FINAL-RATIFICATION-BLOCKER-ANALYSIS.yaml",
            lambda record: record["recommended_integrated_architecture"][
                "minimum_constitutional_allocations"
            ]["ordinary_human_governance_offices"].pop("anti_manipulation"),
        )
        self.assert_error("FINAL_BLOCKER_RECOMMENDATION")

    def test_final_blocker_projection_remains_conditional(self) -> None:
        self.update_json(
            "constitutional-design/FINAL-RATIFICATION-BLOCKER-ANALYSIS.yaml",
            lambda record: record["recommended_integrated_architecture"][
                "projected_result_if_adopted_and_incorporated"
            ].update(constitution_adopted=True),
        )
        self.assert_error("FINAL_BLOCKER_RECOMMENDATION")

    def test_final_blocker_subordinate_items_are_exact(self) -> None:
        self.update_json(
            "constitutional-design/FINAL-RATIFICATION-BLOCKER-ANALYSIS.yaml",
            lambda record: record["subordinate_law_items"].append(
                "Subordinate law may choose HCA members."
            ),
        )
        self.assert_error("FINAL_BLOCKER_SUBORDINATE_ITEMS")

    def test_final_blocker_packet_is_required(self) -> None:
        (
            self.root
            / "constitutional-design"
            / "decisions"
            / "FINAL-RATIFICATION-BLOCKERS-HUMAN-DECISION-PACKET.md"
        ).unlink()
        self.assert_error("FINAL_BLOCKER_PACKET_REQUIRED")

    def test_final_blocker_packet_requires_recorded_adoption(self) -> None:
        self.update_text(
            "constitutional-design/decisions/"
            "FINAL-RATIFICATION-BLOCKERS-HUMAN-DECISION-PACKET.md",
            lambda text: text.replace(
                "**HUMAN CONSTITUTIONAL AUTHORITY DECISION: ADOPT_B.**",
                "**NO HUMAN DECISION HAS BEEN RECORDED.**",
            ),
        )
        self.assert_error("FINAL_BLOCKER_PACKET_CONTENT")

    def test_cdd_002_is_required(self) -> None:
        (
            self.root
            / "constitutional-design"
            / "decisions"
            / "CDD-002.yaml"
        ).unlink()
        self.assert_error("CDD_002_DECISION")

    def test_cdd_002_requires_explicit_human_authority(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDD-002.yaml",
            lambda record: record.update(
                authorized_by="Artificial-intelligence recommendation"
            ),
        )
        self.assert_error("CDD_002_DECISION")

    def test_cdd_002_binds_exact_recommendation(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDD-002.yaml",
            lambda record: record.update(recommendation_sha256="0" * 64),
        )
        self.assert_error("CDD_002_DECISION")

    def test_cdd_002_preserves_all_subordinate_items(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDD-002.yaml",
            lambda record: record["subordinate_law_items_preserved"].pop(),
        )
        self.assert_error("CDD_002_DECISION")

    def test_cdd_002_cannot_claim_ratification(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDD-002.yaml",
            lambda record: record["resulting_state"].update(
                constitution_ratified=True
            ),
        )
        self.assert_error("CDD_002_DECISION")

    def test_cdd_002_requires_honest_post_incorporation_review(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDD-002.yaml",
            lambda record: record["post_incorporation_review"].update(
                new_human_decisions_required=0
            ),
        )
        self.assert_error("CDD_002_DECISION")

    def test_cdd_002_trace_is_required(self) -> None:
        self.update_json(
            "constitutional-design/drafts/"
            "CONSTITUTION_v0.1_TRACEABILITY.yaml",
            lambda record: record.pop("ratification_blocker_decision"),
        )
        self.assert_error("CONSTITUTION_BLOCKER_DECISION_TRACE")

    def test_cdd_002_section_trace_is_exact(self) -> None:
        def remove_cdd(record) -> None:
            section = next(
                item
                for item in record["sections"]
                if item["section_id"] == "III.4"
            )
            section["controlling_cdd"].remove("CDD-002")

        self.update_json(
            "constitutional-design/drafts/"
            "CONSTITUTION_v0.1_TRACEABILITY.yaml",
            remove_cdd,
        )
        self.assert_error("CONSTITUTION_TRACE_SECTIONS")

    def test_ratification_review_is_required(self) -> None:
        (
            self.root
            / "constitutional-design"
            / "RATIFICATION_REVIEW_v0.1.md"
        ).unlink()
        self.assert_error("RATIFICATION_REVIEW_REQUIRED")

    def test_ratification_review_has_no_constitutional_effect(self) -> None:
        self.update_text(
            "constitutional-design/RATIFICATION_REVIEW_v0.1.md",
            lambda text: text.replace(
                "**RECOMMENDATION_ONLY — NO CONSTITUTIONAL EFFECT**",
                "**CONSTITUTIONALLY BINDING REVIEW**",
            ),
        )
        self.assert_error("RATIFICATION_REVIEW_BOUNDARY")

    def test_ratification_review_cannot_claim_readiness(self) -> None:
        self.update_text(
            "constitutional-design/RATIFICATION_REVIEW_v0.1.md",
            lambda text: text.replace(
                "`NOT_READY_FOR_HUMAN_RATIFICATION`",
                "`READY_FOR_HUMAN_RATIFICATION`",
                1,
            ),
        )
        self.assert_error("RATIFICATION_REVIEW_CLASSIFICATION")

    def test_ratification_review_requires_exact_blockers(self) -> None:
        self.update_text(
            "constitutional-design/RATIFICATION_REVIEW_v0.1.md",
            lambda text: text.replace(
                "### Remaining Blocker — HCA College Election and Removal "
                "Lifecycle",
                "### Resolved Topic — HCA College Lifecycle",
            ),
        )
        self.assert_error("RATIFICATION_REVIEW_BLOCKERS")

    def test_ratification_review_requires_all_article_pairs(self) -> None:
        self.update_text(
            "constitutional-design/RATIFICATION_REVIEW_v0.1.md",
            lambda text: text.replace(
                "| VII–VIII | Consistent |",
                "| VII–VIII | Not reviewed |",
            ).replace("| VII–VIII |", "| OMITTED |", 1),
        )
        self.assert_error("RATIFICATION_REVIEW_CROSS_ARTICLE")

    def test_ratification_review_requires_all_adversarial_tests(self) -> None:
        self.update_text(
            "constitutional-design/RATIFICATION_REVIEW_v0.1.md",
            lambda text: text.replace(
                "| Effective-power takeover without formal authority | PASS |",
                "| Effective-power takeover without formal authority | FAIL |",
            ),
        )
        self.assert_error("RATIFICATION_REVIEW_ADVERSARIAL")

    def test_ratification_review_requires_reader_questions(self) -> None:
        self.update_text(
            "constitutional-design/RATIFICATION_REVIEW_v0.1.md",
            lambda text: text.replace(
                "| Who holds authority? |",
                "| Authority topic omitted |",
            ),
        )
        self.assert_error("RATIFICATION_REVIEW_COMPREHENSIBILITY")

    def test_ratification_review_preserves_subordinate_boundary(self) -> None:
        self.update_text(
            "constitutional-design/RATIFICATION_REVIEW_v0.1.md",
            lambda text: text.replace(
                "subordinate law would have to determine constitutional "
                "election validity",
                "subordinate law may determine constitutional election "
                "validity",
            ),
        )
        self.assert_error("RATIFICATION_REVIEW_SUBORDINATE_BOUNDARY")

    def test_ratification_review_requires_complete_coverage(self) -> None:
        self.update_text(
            "constitutional-design/RATIFICATION_REVIEW_v0.1.md",
            lambda text: text.replace(
                "| Source requirements covered | 35/35 |",
                "| Source requirements covered | 34/35 |",
            ),
        )
        self.assert_error("RATIFICATION_REVIEW_COVERAGE")

    def test_ratification_review_cannot_modify_constitution(self) -> None:
        self.update_text(
            "constitutional-design/drafts/CONSTITUTION_v0.1.md",
            lambda text: text.replace(
                "Alvorada SHALL exist", "Alvorada MAY exist", 1
            ),
        )
        self.assert_error("RATIFICATION_DRAFT_INTEGRITY")

    def test_constitution_draft_is_required(self) -> None:
        (
            self.root
            / "constitutional-design"
            / "drafts"
            / "CONSTITUTION_v0.1.md"
        ).unlink()
        self.assert_error("CONSTITUTION_DRAFT_REQUIRED")

    def test_constitution_must_remain_not_adopted(self) -> None:
        self.update_text(
            "constitutional-design/drafts/CONSTITUTION_v0.1.md",
            lambda text: text.replace(
                "**DRAFT — NOT ADOPTED CONSTITUTION**",
                "**ADOPTED CONSTITUTION**",
            ),
        )
        self.assert_error("CONSTITUTION_DRAFT_STATUS")

    def test_constitution_requires_exact_article_architecture(self) -> None:
        self.update_text(
            "constitutional-design/drafts/CONSTITUTION_v0.1.md",
            lambda text: text.replace(
                "## Article VIII — Refounding",
                "## Article IX — Refounding",
            ),
        )
        self.assert_error("CONSTITUTION_DRAFT_ARTICLES")

    def test_constitution_requires_every_section(self) -> None:
        self.update_text(
            "constitutional-design/drafts/CONSTITUTION_v0.1.md",
            lambda text: text.replace(
                "### Section IV.2 — Independence",
                "### Omitted Section IV.2 — Independence",
            ),
        )
        self.assert_error("CONSTITUTION_DRAFT_SECTIONS")

    def test_constitution_trace_requires_every_section(self) -> None:
        self.update_json(
            "constitutional-design/drafts/"
            "CONSTITUTION_v0.1_TRACEABILITY.yaml",
            lambda record: record["sections"].pop(),
        )
        self.assert_error("CONSTITUTION_TRACE_SECTIONS")

    def test_constitution_trace_rejects_duplicate_section(self) -> None:
        def duplicate_section(record) -> None:
            record["sections"].append(dict(record["sections"][0]))

        self.update_json(
            "constitutional-design/drafts/"
            "CONSTITUTION_v0.1_TRACEABILITY.yaml",
            duplicate_section,
        )
        self.assert_error("CONSTITUTION_TRACE_SECTIONS")

    def test_constitution_trace_requires_all_source_requirements(self) -> None:
        def remove_requirement(record) -> None:
            for section in record["sections"]:
                if "CR-035" in section["source_requirements"]:
                    section["source_requirements"].remove("CR-035")

        self.update_json(
            "constitutional-design/drafts/"
            "CONSTITUTION_v0.1_TRACEABILITY.yaml",
            remove_requirement,
        )
        self.assert_error("CONSTITUTION_TRACE_CR_COVERAGE")

    def test_constitution_trace_requires_all_consolidated_groups(self) -> None:
        def remove_group(record) -> None:
            for section in record["sections"]:
                if "CCR-020" in section["consolidated_requirements"]:
                    section["consolidated_requirements"].remove("CCR-020")

        self.update_json(
            "constitutional-design/drafts/"
            "CONSTITUTION_v0.1_TRACEABILITY.yaml",
            remove_group,
        )
        self.assert_error("CONSTITUTION_TRACE_CCR_COVERAGE")

    def test_constitution_trace_rejects_cr_ccr_mismatch(self) -> None:
        self.update_json(
            "constitutional-design/drafts/"
            "CONSTITUTION_v0.1_TRACEABILITY.yaml",
            lambda record: record["sections"][0][
                "source_requirements"
            ].append("CR-002"),
        )
        self.assert_error("CONSTITUTION_TRACE_SECTIONS")

    def test_constitution_trace_requires_all_foundational_decisions(
        self,
    ) -> None:
        def remove_decision(record) -> None:
            for section in record["sections"]:
                section["controlling_cdrs"] = [
                    item
                    for item in section["controlling_cdrs"]
                    if item != "CDR-005"
                ]

        self.update_json(
            "constitutional-design/drafts/"
            "CONSTITUTION_v0.1_TRACEABILITY.yaml",
            remove_decision,
        )
        self.assert_error("CONSTITUTION_TRACE_DECISION_COVERAGE")

    def test_constitution_trace_requires_all_design_domains(self) -> None:
        def remove_domain(record) -> None:
            for section in record["sections"]:
                section["adopted_design_domains"] = [
                    item
                    for item in section["adopted_design_domains"]
                    if item != "RD-11"
                ]

        self.update_json(
            "constitutional-design/drafts/"
            "CONSTITUTION_v0.1_TRACEABILITY.yaml",
            remove_domain,
        )
        self.assert_error("CONSTITUTION_TRACE_DECISION_COVERAGE")

    def test_constitution_trace_requires_all_coordinated_corrections(
        self,
    ) -> None:
        def remove_correction(record) -> None:
            for section in record["sections"]:
                section["coordinated_corrections"] = [
                    item
                    for item in section["coordinated_corrections"]
                    if item != "CDC-04"
                ]

        self.update_json(
            "constitutional-design/drafts/"
            "CONSTITUTION_v0.1_TRACEABILITY.yaml",
            remove_correction,
        )
        self.assert_error("CONSTITUTION_TRACE_CORRECTION_COVERAGE")

    def test_constitution_requires_all_refounding_principles(self) -> None:
        self.update_text(
            "constitutional-design/drafts/CONSTITUTION_v0.1.md",
            lambda text: text.replace(
                "protected human agency", "optional human agency"
            ),
        )
        self.assert_error("CONSTITUTION_DRAFT_REFOUNDING")

    def test_constitution_prohibits_machine_sovereignty(self) -> None:
        self.update_text(
            "constitutional-design/drafts/CONSTITUTION_v0.1.md",
            lambda text: text.replace(
                "Artificial intelligence SHALL NOT acquire",
                "Artificial intelligence MAY acquire",
                1,
            ),
        )
        self.assert_error("CONSTITUTION_DRAFT_SAFEGUARDS")

    def test_constitution_prohibits_reviewer_sovereignty(self) -> None:
        self.update_text(
            "constitutional-design/drafts/CONSTITUTION_v0.1.md",
            lambda text: text.replace(
                "Review SHALL NOT\n   become sovereignty",
                "Review MAY\n   become sovereignty",
            ),
        )
        self.assert_error("CONSTITUTION_DRAFT_SAFEGUARDS")

    def test_constitution_prohibits_emergency_to_succession(self) -> None:
        self.update_text(
            "constitutional-design/drafts/CONSTITUTION_v0.1.md",
            lambda text: text.replace(
                "Emergency authority SHALL NOT become succession authority",
                "Emergency authority MAY become succession authority",
            ),
        )
        self.assert_error("CONSTITUTION_DRAFT_SAFEGUARDS")

    def test_constitution_prohibits_adjudicative_refounding(self) -> None:
        self.update_text(
            "constitutional-design/drafts/CONSTITUTION_v0.1.md",
            lambda text: text.replace(
                "It SHALL NOT\n   amend or refound by interpretation",
                "It MAY\n   amend or refound by interpretation",
            ),
        )
        self.assert_error("CONSTITUTION_DRAFT_SAFEGUARDS")

    def test_constitution_preserves_constitutional_history(self) -> None:
        self.update_text(
            "constitutional-design/drafts/CONSTITUTION_v0.1.md",
            lambda text: text.replace(
                "SHALL NOT erase,\n    falsify, or obscure",
                "MAY erase,\n    falsify, or obscure",
            ),
        )
        self.assert_error("CONSTITUTION_DRAFT_SAFEGUARDS")

    def test_constitution_trace_rejects_untraced_normative_claim(self) -> None:
        self.update_json(
            "constitutional-design/drafts/"
            "CONSTITUTION_v0.1_TRACEABILITY.yaml",
            lambda record: record["coverage_summary"].update(
                untraced_normative_proposition_count=1
            ),
        )
        self.assert_error("CONSTITUTION_TRACE_SUMMARY")

    def test_remainder_decision_requires_human_authority(self) -> None:
        self.update_json(
            "constitutional-design/drafts/"
            "CONSTITUTION_v0.1_TRACEABILITY.yaml",
            lambda record: record["human_drafting_decision"].update(
                authorized_by="Artificial-intelligence recommendation"
            ),
        )
        self.assert_error("CONSTITUTION_REMAINDER_DECISION")

    def test_remainder_decision_cannot_adopt_constitution(self) -> None:
        self.update_json(
            "constitutional-design/drafts/"
            "CONSTITUTION_v0.1_TRACEABILITY.yaml",
            lambda record: record["human_drafting_decision"].update(
                constitutional_effect="ADOPTED"
            ),
        )
        self.assert_error("CONSTITUTION_REMAINDER_DECISION")

    def test_remainder_rule_requires_largest_equal_cohorts(self) -> None:
        self.update_text(
            "constitutional-design/drafts/CONSTITUTION_v0.1.md",
            lambda text: text.replace(
                "largest equal allocation of eligible constitutional "
                "members possible",
                "arbitrary allocation of constitutional members",
            ),
        )
        self.assert_error("CONSTITUTION_REMAINDER_RULE")

    def test_remainder_rule_prohibits_discretionary_assignment(self) -> None:
        self.update_text(
            "constitutional-design/drafts/CONSTITUTION_v0.1.md",
            lambda text: text.replace(
                "No human or artificial-intelligence actor MAY choose",
                "A human or artificial-intelligence actor MAY choose",
            ),
        )
        self.assert_error("CONSTITUTION_REMAINDER_RULE")

    def test_remainder_rule_preserves_verifiable_provenance(self) -> None:
        self.update_text(
            "constitutional-design/drafts/CONSTITUTION_v0.1.md",
            lambda text: text.replace(
                "attributable provenance SHALL be\n"
                "   preserved and independently verifiable",
                "assignment need not be recorded",
            ),
        )
        self.assert_error("CONSTITUTION_REMAINDER_RULE")

    def test_constitution_open_questions_must_remain_exact(self) -> None:
        self.update_text(
            "constitutional-design/drafts/"
            "CONSTITUTION_v0.1_OPEN_QUESTIONS.md",
            lambda text: text.replace(
                "`OPEN_QUESTIONS_COUNT: 1`",
                "`OPEN_QUESTIONS_COUNT: 0`",
            ),
        )
        self.assert_error("CONSTITUTION_OPEN_QUESTIONS")

    def test_consolidated_requirement_map_is_required(self) -> None:
        (
            self.root
            / "constitutional-design"
            / "CONSOLIDATED_REQUIREMENT_MAP.yaml"
        ).unlink()
        self.assert_error("CONSOLIDATED_MAP_SCHEMA")

    def test_consolidated_requirements_are_exact(self) -> None:
        self.update_json(
            "constitutional-design/CONSOLIDATED_REQUIREMENT_MAP.yaml",
            lambda record: record["consolidated_requirements"].pop(),
        )
        self.assert_error("CONSOLIDATED_REQUIREMENTS")

    def test_every_source_requirement_maps_exactly_once(self) -> None:
        self.update_json(
            "constitutional-design/CONSOLIDATED_REQUIREMENT_MAP.yaml",
            lambda record: record["consolidated_requirements"][0][
                "source_requirements"
            ].append("CR-002"),
        )
        self.assert_error("CONSOLIDATED_SOURCE_DUPLICATION")

    def test_unmapped_source_requirement_is_rejected(self) -> None:
        self.update_json(
            "constitutional-design/CONSOLIDATED_REQUIREMENT_MAP.yaml",
            lambda record: record["consolidated_requirements"][0][
                "source_requirements"
            ].remove("CR-001"),
        )
        self.assert_error("CONSOLIDATED_SOURCE_COVERAGE")

    def test_coverage_matrix_must_match_primary_mapping(self) -> None:
        self.update_json(
            "constitutional-design/CONSOLIDATED_REQUIREMENT_MAP.yaml",
            lambda record: record["coverage_matrix"][0].update(
                primary_article="ARTICLE-VIII"
            ),
        )
        self.assert_error("CONSOLIDATED_COVERAGE_MATRIX")

    def test_consolidated_classification_counts_are_exact(self) -> None:
        self.update_json(
            "constitutional-design/CONSOLIDATED_REQUIREMENT_MAP.yaml",
            lambda record: record["consolidated_requirements"][0].update(
                classification="SUBORDINATE_GOVERNANCE_LAW"
            ),
        )
        self.assert_error("CONSOLIDATED_CLASSIFICATION_COUNTS")

    def test_consolidated_relationships_must_resolve(self) -> None:
        self.update_json(
            "constitutional-design/CONSOLIDATED_REQUIREMENT_MAP.yaml",
            lambda record: record["consolidated_requirements"][0][
                "dependencies"
            ].append("CCR-999"),
        )
        self.assert_error("CONSOLIDATED_RELATIONSHIPS")

    def test_consolidated_map_preserves_constitutional_state(self) -> None:
        self.update_json(
            "constitutional-design/CONSOLIDATED_REQUIREMENT_MAP.yaml",
            lambda record: record["state_preservation"].update(
                constitutional_provision_count=1
            ),
        )
        self.assert_error("CONSOLIDATED_STATE_PRESERVATION")

    def test_article_architecture_is_required(self) -> None:
        (
            self.root
            / "constitutional-design"
            / "CONSTITUTIONAL_ARTICLE_ARCHITECTURE.md"
        ).unlink()
        self.assert_error("ARTICLE_ARCHITECTURE_REQUIRED")

    def test_article_architecture_requires_eight_substantive_articles(self) -> None:
        self.update_text(
            "constitutional-design/CONSTITUTIONAL_ARTICLE_ARCHITECTURE.md",
            lambda text: text.replace(
                "## Article VIII — Refounding, Termination, Continuity of "
                "Obligations, and Constitutional Memory",
                "## Appendix — Refounding",
            ),
        )
        self.assert_error("ARTICLE_ARCHITECTURE_ARTICLES")

    def test_each_article_requires_complete_record_fields(self) -> None:
        self.update_text(
            "constitutional-design/CONSTITUTIONAL_ARTICLE_ARCHITECTURE.md",
            lambda text: text.replace("**Purpose:**", "**Intent:**", 1),
        )
        self.assert_error("ARTICLE_ARCHITECTURE_RECORD_FIELDS")

    def test_each_article_requires_implementation_needs(self) -> None:
        self.update_text(
            "constitutional-design/CONSTITUTIONAL_ARTICLE_ARCHITECTURE.md",
            lambda text: text.replace(
                "**Anticipated implementation standards:** Identity, authorization,",
                "**Implementation outlook:** Identity, authorization,",
            ),
        )
        self.assert_error("ARTICLE_ARCHITECTURE_RECORD_FIELDS")

    def test_article_record_fields_cannot_be_blank(self) -> None:
        self.update_text(
            "constitutional-design/CONSTITUTIONAL_ARTICLE_ARCHITECTURE.md",
            lambda text: text.replace(
                "**Dependencies:** None; this article supplies identity premises "
                "used throughout\nthe architecture.",
                "**Dependencies:**\n\n",
            ),
        )
        self.assert_error("ARTICLE_ARCHITECTURE_RECORD_FIELDS")

    def test_article_coverage_must_match_consolidated_map(self) -> None:
        self.update_text(
            "constitutional-design/CONSTITUTIONAL_ARTICLE_ARCHITECTURE.md",
            lambda text: text.replace(
                "**Source requirements:** `CR-001`, `CR-003`, `CR-015`",
                "**Source requirements:** `CR-001`, `CR-003`",
            ),
        )
        self.assert_error("ARTICLE_ARCHITECTURE_COVERAGE")

    def test_article_ids_cannot_be_relocated_into_prose(self) -> None:
        self.update_text(
            "constitutional-design/CONSTITUTIONAL_ARTICLE_ARCHITECTURE.md",
            lambda text: text.replace(
                "**Source requirements:** `CR-001`, `CR-003`, `CR-015`",
                "**Source requirements:** `CR-003`, `CR-015`",
            ).replace(
                "**Purpose:** State whose institution this is",
                "**Purpose:** `CR-001` states whose institution this is",
            ),
        )
        self.assert_error("ARTICLE_ARCHITECTURE_COVERAGE")

    def test_article_controlling_decisions_are_exact(self) -> None:
        self.update_text(
            "constitutional-design/CONSTITUTIONAL_ARTICLE_ARCHITECTURE.md",
            lambda text: text.replace(
                "**Controlling CDRs:** `CDR-001`, `CDR-003`",
                "**Controlling CDRs:** `CDR-001`",
            ),
        )
        self.assert_error("ARTICLE_ARCHITECTURE_CONTROLLING_CDRS")

    def test_article_unresolved_issues_cover_source_union(self) -> None:
        self.update_text(
            "constitutional-design/CONSTITUTIONAL_ARTICLE_ARCHITECTURE.md",
            lambda text: text.replace("`IR-15`, `IR-17`, `IR-18`", "`IR-17`, `IR-18`", 1),
        )
        self.assert_error("ARTICLE_ARCHITECTURE_UNRESOLVED_ISSUES")

    def test_article_architecture_cannot_enact_provisions(self) -> None:
        self.update_text(
            "constitutional-design/CONSTITUTIONAL_ARTICLE_ARCHITECTURE.md",
            lambda text: text + "\n### Section 1\nThis Constitution grants power.\n",
        )
        self.assert_error("ARTICLE_ARCHITECTURE_NO_PROVISIONS")

    def test_article_architecture_cannot_invent_threshold(self) -> None:
        self.update_text(
            "constitutional-design/CONSTITUTIONAL_ARTICLE_ARCHITECTURE.md",
            lambda text: text + "\nRefounding requires a two-thirds vote.\n",
        )
        self.assert_error("ARTICLE_ARCHITECTURE_NO_PROVISIONS")

    def test_article_architecture_cannot_invent_office(self) -> None:
        self.update_text(
            "constitutional-design/CONSTITUTIONAL_ARTICLE_ARCHITECTURE.md",
            lambda text: text + "\nA Council shall consist of nine members.\n",
        )
        self.assert_error("ARTICLE_ARCHITECTURE_NO_PROVISIONS")

    def test_remaining_design_matrix_is_required(self) -> None:
        (
            self.root
            / "constitutional-design"
            / "REMAINING-DESIGN-MATRIX.yaml"
        ).unlink()
        self.assert_error("REMAINING_DESIGN_MATRIX_SCHEMA")

    def test_remaining_design_must_preserve_human_adoption(self) -> None:
        self.update_json(
            "constitutional-design/REMAINING-DESIGN-MATRIX.yaml",
            lambda record: record.update(
                status="ADVISORY_ANALYSIS_ONLY",
                decision_effect="NONE",
            ),
        )
        self.assert_error("REMAINING_DESIGN_BOUNDARY")

    def test_remaining_design_requires_all_domains(self) -> None:
        self.update_json(
            "constitutional-design/REMAINING-DESIGN-MATRIX.yaml",
            lambda record: record["design_domains"].pop(),
        )
        self.assert_error("REMAINING_DESIGN_DOMAINS")

    def test_remaining_design_requires_three_alternatives(self) -> None:
        self.update_json(
            "constitutional-design/REMAINING-DESIGN-MATRIX.yaml",
            lambda record: record["design_domains"][0]["alternatives"].pop(),
        )
        self.assert_error("REMAINING_DESIGN_ALTERNATIVES")

    def test_remaining_design_requires_every_stress_dimension(self) -> None:
        self.update_json(
            "constitutional-design/REMAINING-DESIGN-MATRIX.yaml",
            lambda record: record["design_domains"][0]["alternatives"][0][
                "stress_test"
            ].pop("bad_human"),
        )
        self.assert_error("REMAINING_DESIGN_ALTERNATIVES")

    def test_remaining_design_requires_a_recommendation(self) -> None:
        self.update_json(
            "constitutional-design/REMAINING-DESIGN-MATRIX.yaml",
            lambda record: record["design_domains"][0][
                "recommendation"
            ].pop("human_decision_required"),
        )
        self.assert_error("REMAINING_DESIGN_RECOMMENDATION")

    def test_remaining_design_recommendation_must_close_key_choices(
        self,
    ) -> None:
        self.update_json(
            "constitutional-design/REMAINING-DESIGN-MATRIX.yaml",
            lambda record: record["design_domains"][9][
                "recommendation"
            ].update(
                architecture=record["design_domains"][9]["recommendation"][
                    "architecture"
                ].replace("Before the second", "After the second")
            ),
        )
        self.assert_error("REMAINING_DESIGN_DECISION_COMPLETENESS")

    def test_remaining_design_references_must_resolve(self) -> None:
        self.update_json(
            "constitutional-design/REMAINING-DESIGN-MATRIX.yaml",
            lambda record: record["design_domains"][0][
                "blocked_requirements"
            ].append("CCR-999"),
        )
        self.assert_error("REMAINING_DESIGN_DOMAINS")

    def test_remaining_design_requires_exact_human_decisions(self) -> None:
        self.update_json(
            "constitutional-design/REMAINING-DESIGN-MATRIX.yaml",
            lambda record: record["human_decisions_required"].append(
                "DECISION-RD-01"
            ),
        )
        self.assert_error("REMAINING_DESIGN_HUMAN_DECISIONS")

    def test_remaining_design_requires_integrated_conflicts(self) -> None:
        self.update_json(
            "constitutional-design/REMAINING-DESIGN-MATRIX.yaml",
            lambda record: record["cross_domain_conflicts"].pop(),
        )
        self.assert_error("REMAINING_DESIGN_CONFLICTS")

    def test_remaining_design_projection_covers_every_ccr_once(self) -> None:
        self.update_json(
            "constitutional-design/REMAINING-DESIGN-MATRIX.yaml",
            lambda record: record[
                "projected_consolidated_requirements"
            ].pop(),
        )
        self.assert_error("REMAINING_DESIGN_PROJECTION")

    def test_remaining_design_projection_matches_current_map(self) -> None:
        self.update_json(
            "constitutional-design/REMAINING-DESIGN-MATRIX.yaml",
            lambda record: record["projected_consolidated_requirements"][
                0
            ].update(current_classification="BLOCKED_BY_UNRESOLVED_DESIGN"),
        )
        self.assert_error("REMAINING_DESIGN_PROJECTION")

    def test_remaining_design_projection_must_be_conditional(self) -> None:
        self.update_json(
            "constitutional-design/REMAINING-DESIGN-MATRIX.yaml",
            lambda record: record["projection"].update(
                condition="No human decision has been made.",
                current_map_is_modified=False,
            ),
        )
        self.assert_error("REMAINING_DESIGN_PROJECTION")

    def test_remaining_design_preserves_current_state(self) -> None:
        self.update_json(
            "constitutional-design/REMAINING-DESIGN-MATRIX.yaml",
            lambda record: record["state_preservation"].update(
                constitutional_provision_count=1
            ),
        )
        self.assert_error("REMAINING_DESIGN_STATE")

    def test_remaining_design_residuals_must_be_implementation_only(
        self,
    ) -> None:
        self.update_json(
            "constitutional-design/REMAINING-DESIGN-MATRIX.yaml",
            lambda record: record[
                "genuine_residual_implementation_questions"
            ].append("Decide the constitutional constituency."),
        )
        self.assert_error("REMAINING_DESIGN_RESIDUALS")

    def test_remaining_design_packet_must_match_matrix(self) -> None:
        self.update_text(
            "constitutional-design/decisions/"
            "REMAINING-DESIGN-DECISION-PACKET.md",
            lambda text: text.replace(
                "## DECISION-RD-11", "## OMITTED-RD-11"
            ),
        )
        self.assert_error("REMAINING_DESIGN_PACKET_CONTENT")

    def test_remaining_design_packet_requires_same_decision_contract(
        self,
    ) -> None:
        self.update_text(
            "constitutional-design/decisions/"
            "REMAINING-DESIGN-DECISION-PACKET.md",
            lambda text: text.replace(
                "four standing", "three standing"
            ),
        )
        self.assert_error("REMAINING_DESIGN_PACKET_AGREEMENT")

    def test_remaining_design_contract_detects_substantive_matrix_change(
        self,
    ) -> None:
        self.update_json(
            "constitutional-design/REMAINING-DESIGN-MATRIX.yaml",
            lambda record: record["design_domains"][9][
                "recommendation"
            ].update(
                architecture=record["design_domains"][9]["recommendation"][
                    "architecture"
                ].replace("180 days", "181 days")
            ),
        )
        self.assert_error("REMAINING_DESIGN_PACKET_AGREEMENT")

    def test_cross_domain_decision_packet_is_required(self) -> None:
        (
            self.root
            / "constitutional-design"
            / "decisions"
            / "CROSS-DOMAIN-CONTRADICTION-DECISION-PACKET.md"
        ).unlink()
        self.assert_error("CROSS_DOMAIN_PACKET_REQUIRED")

    def test_cross_domain_packet_must_preserve_human_adoption(self) -> None:
        self.update_text(
            "constitutional-design/decisions/"
            "CROSS-DOMAIN-CONTRADICTION-DECISION-PACKET.md",
            lambda text: text.replace(
                "**Status:** `DECIDED`",
                "**Status:** `AWAITING_HUMAN_DECISION`",
            ),
        )
        self.assert_error("CROSS_DOMAIN_PACKET_BOUNDARY")

    def test_cross_domain_packet_requires_exact_options(self) -> None:
        self.update_text(
            "constitutional-design/decisions/"
            "CROSS-DOMAIN-CONTRADICTION-DECISION-PACKET.md",
            lambda text: text.replace(
                "3. **DEFER**",
                "3. **ADOPT_PARTIALLY**",
            ),
        )
        self.assert_error("CROSS_DOMAIN_PACKET_OPTIONS")

    def test_cross_domain_packet_requires_all_components(self) -> None:
        self.update_text(
            "constitutional-design/decisions/"
            "CROSS-DOMAIN-CONTRADICTION-DECISION-PACKET.md",
            lambda text: text.replace(
                "## Component 4 — Reviewer-Non-Sovereign Remedies",
                "## Appendix — Reviewer Remedies",
            ),
        )
        self.assert_error("CROSS_DOMAIN_PACKET_COMPONENTS")

    def test_cross_domain_component_mapping_is_exact(self) -> None:
        self.update_text(
            "constitutional-design/decisions/"
            "CROSS-DOMAIN-CONTRADICTION-DECISION-PACKET.md",
            lambda text: text.replace(
                "**Affected domains:** `RD-04`, `RD-06`, `RD-07`, `RD-11`",
                "**Affected domains:** `RD-04`, `RD-06`, `RD-11`",
            ),
        )
        self.assert_error("CROSS_DOMAIN_PACKET_MAPPING")

    def test_cross_domain_component_requires_authority_boundary(self) -> None:
        self.update_text(
            "constitutional-design/decisions/"
            "CROSS-DOMAIN-CONTRADICTION-DECISION-PACKET.md",
            lambda text: text.replace(
                "cannot self-renew",
                "may seek renewal",
                1,
            ),
        )
        self.assert_error("CROSS_DOMAIN_PACKET_CONTENT")

    def test_cross_domain_succession_fallback_requires_decision_rule(
        self,
    ) -> None:
        self.update_text(
            "constitutional-design/decisions/"
            "CROSS-DOMAIN-CONTRADICTION-DECISION-PACKET.md",
            lambda text: text.replace(
                "ten affirmative votes determine",
                "an unspecified vote determines",
            ),
        )
        self.assert_error("CROSS_DOMAIN_PACKET_CONTENT")

    def test_cross_domain_succession_preserves_interregnum_ceiling(
        self,
    ) -> None:
        self.update_text(
            "constitutional-design/decisions/"
            "CROSS-DOMAIN-CONTRADICTION-DECISION-PACKET.md",
            lambda text: text.replace(
                "ends at the 180-day maximum",
                "continues beyond the ordinary maximum",
            ),
        )
        self.assert_error("CROSS_DOMAIN_PACKET_CONTENT")

    def test_cross_domain_projection_must_match_adopted_state(self) -> None:
        self.update_text(
            "constitutional-design/decisions/"
            "CROSS-DOMAIN-CONTRADICTION-DECISION-PACKET.md",
            lambda text: text.replace(
                "The controlling consolidated map is now "
                "**20 ready / 0 blocked**.",
                "The controlling consolidated map remains "
                "**11 ready / 9 blocked**.",
            ),
        )
        self.assert_error("CROSS_DOMAIN_PACKET_PROJECTION")

    def test_cross_domain_closure_must_remain_conditional(self) -> None:
        self.update_text(
            "constitutional-design/decisions/"
            "CROSS-DOMAIN-CONTRADICTION-DECISION-PACKET.md",
            lambda text: text.replace(
                "None identified that prevents constitutional\ndrafting.",
                "One unresolved constitutional selector remains.",
            ),
        )
        self.assert_error("CROSS_DOMAIN_PACKET_REMAINING_DECISIONS")

    def test_cross_domain_subordinate_questions_are_preserved(self) -> None:
        self.update_text(
            "constitutional-design/decisions/"
            "CROSS-DOMAIN-CONTRADICTION-DECISION-PACKET.md",
            lambda text: text.replace(
                "- remedial evidence formats, compliance milestones, "
                "reporting intervals,\n"
                "  procurement alternatives, and verification methods.\n",
                "",
            ),
        )
        self.assert_error("CROSS_DOMAIN_PACKET_SUBORDINATE")

    def test_cross_domain_packet_preserves_controlling_state(self) -> None:
        self.update_text(
            "constitutional-design/decisions/"
            "CROSS-DOMAIN-CONTRADICTION-DECISION-PACKET.md",
            lambda text: text.replace(
                "Constitutional provisions remain **0**",
                "Constitutional provisions remain **1**",
            ),
        )
        self.assert_error("CROSS_DOMAIN_PACKET_STATE")

    def test_coordinated_decision_record_is_required(self) -> None:
        (
            self.root
            / "constitutional-design"
            / "decisions"
            / "CDD-001.yaml"
        ).unlink()
        self.assert_error("COORDINATED_DECISION_SCHEMA")

    def test_coordinated_decision_requires_explicit_human_adoption(
        self,
    ) -> None:
        self.update_json(
            "constitutional-design/decisions/CDD-001.yaml",
            lambda record: record.update(
                status="PROPOSED",
                decision="RECOMMEND_ONLY",
            ),
        )
        self.assert_error("COORDINATED_DECISION_AUTHORITY")

    def test_coordinated_decision_requires_all_designs(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDD-001.yaml",
            lambda record: record["adopted_design_recommendations"].pop(),
        )
        self.assert_error("COORDINATED_DECISION_DESIGNS")

    def test_coordinated_decision_binds_exact_design_digest(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDD-001.yaml",
            lambda record: record["adopted_design_recommendations"][0].update(
                recommendation_sha256="0" * 64
            ),
        )
        self.assert_error("COORDINATED_DECISION_DESIGNS")

    def test_coordinated_decision_requires_all_corrections(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDD-001.yaml",
            lambda record: record["adopted_correction_components"].pop(),
        )
        self.assert_error("COORDINATED_DECISION_CORRECTIONS")

    def test_coordinated_decision_binds_exact_correction_digest(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDD-001.yaml",
            lambda record: record["adopted_correction_components"][0].update(
                component_sha256="0" * 64
            ),
        )
        self.assert_error("COORDINATED_DECISION_CORRECTIONS")

    def test_coordinated_decision_preserves_machine_non_authority(
        self,
    ) -> None:
        self.update_json(
            "constitutional-design/decisions/CDD-001.yaml",
            lambda record: record["authority_boundaries"].pop(1),
        )
        self.assert_error("COORDINATED_DECISION_BOUNDARIES")

    def test_coordinated_decision_requires_zero_blocker_state(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDD-001.yaml",
            lambda record: record["resulting_state"].update(
                blocking_cross_domain_contradictions_remaining=1,
                blocked_by_unresolved_design=1,
            ),
        )
        self.assert_error("COORDINATED_DECISION_STATE")

    def test_coordinated_decision_cannot_create_redundant_requirement(
        self,
    ) -> None:
        self.update_json(
            "constitutional-design/decisions/CDD-001.yaml",
            lambda record: record["resulting_requirements"].append("CR-036"),
        )
        self.assert_error("COORDINATED_DECISION_SCOPE")

    def test_design_domain_adoption_requires_cdd_provenance(self) -> None:
        self.update_json(
            "constitutional-design/REMAINING-DESIGN-MATRIX.yaml",
            lambda record: record["design_domains"][0].update(
                decision_status="PROPOSED",
                adopted_by="MACHINE-CONSENSUS",
            ),
        )
        self.assert_error("REMAINING_DESIGN_DOMAINS")

    def test_fq5_analytical_record_is_required(self) -> None:
        (
            self.root
            / "constitutional-design"
            / "decisions"
            / "CDR-005.yaml"
        ).unlink()
        self.assert_error("FQ5_ANALYTICAL_RECORD_REQUIRED")

    def test_fq5_must_remain_decided(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-005.yaml",
            lambda record: record.update(status="UNDER_REVIEW"),
        )
        self.assert_error("FQ5_DECISION_STATUS")

    def test_fq5_requires_exact_human_decision(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-005.yaml",
            lambda record: record["human_decision"].update(
                authorized_by="AI recommendation"
            ),
        )
        self.assert_error("FQ5_HUMAN_DECISION_PROVENANCE")

    def test_fq5_requires_all_analysis_dimensions(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-005.yaml",
            lambda record: record["candidate_architectures"][0]["analysis"].pop(
                "refounding"
            ),
        )
        self.assert_error("FQ5_CANDIDATE_ARCHITECTURES")

    def test_fq5_requires_exact_architecture_names(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-005.yaml",
            lambda record: record["candidate_architectures"][4].update(
                name="Automatic Hybrid"
            ),
        )
        self.assert_error("FQ5_CANDIDATE_ARCHITECTURES")

    def test_fq5_requires_all_commitment_level_tests(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-005.yaml",
            lambda record: record["commitment_level_tests"].pop(),
        )
        self.assert_error("FQ5_COMMITMENT_LEVEL_TESTS")

    def test_fq5_commitment_classification_is_exact(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-005.yaml",
            lambda record: record["commitment_level_tests"][0].update(
                proposed_level="ORDINARY_AMENDMENT"
            ),
        )
        self.assert_error("FQ5_COMMITMENT_LEVEL_TESTS")

    def test_fq5_requires_exact_repository_evidence(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-005.yaml",
            lambda record: record["historical_analogues"].pop(),
        )
        self.assert_error("FQ5_HISTORICAL_EVIDENCE")

    def test_fq5_rejects_machine_amendment_authority(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-005.yaml",
            lambda record: record["bad_artificial_intelligence_analysis"].append(
                "Artificial intelligence may independently authorize amendment."
            ),
        )
        self.assert_error("FQ5_CONTRADICTORY_AUTHORITY_CLAIM")

    def test_fq5_rejects_alternate_operative_effect_wording(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-005.yaml",
            lambda record: record["advantages"].append(
                "CDR-005 establishes a binding amendment rule."
            ),
        )
        self.assert_error("FQ5_CONTRADICTORY_AUTHORITY_CLAIM")

    def test_fq5_resolution_requires_decided_state(self) -> None:
        self.update_json(
            "constitutional-design/FOUNDATIONAL_QUESTIONS.yaml",
            lambda record: record["questions"][4].update(
                status="UNRESOLVED"
            ),
        )
        self.assert_error("FQ5_RESOLUTION_DECISION_LINK")

    def test_fq5_resulting_requirements_are_exact(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-005.yaml",
            lambda record: record["resulting_requirements"].pop(),
        )
        self.assert_error("FQ5_RESULTING_REQUIREMENTS")

    def test_fq5_does_not_supersede_prior_decisions(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-005.yaml",
            lambda record: record["supersedes"].append("CDR-004"),
        )
        self.assert_error("FQ5_SUPERSESSION")

    def test_fq5_preserves_residual_questions(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-005.yaml",
            lambda record: record["residual_uncertainty"].pop(),
        )
        self.assert_error("FQ5_RESIDUAL_UNCERTAINTY")

    def test_fq5_ai_cannot_authorize_change_requirement(self) -> None:
        self.update_json(
            "constitutional-design/requirements/CR-032.yaml",
            lambda record: record.update(
                statement=record["statement"].replace(
                    "must not independently authorize",
                    "may independently authorize",
                )
            ),
        )
        self.assert_error("REQUIREMENT_CONTENT")

    def test_fq5_refounding_principles_reject_lower_tiers(self) -> None:
        self.update_json(
            "constitutional-design/requirements/CR-031.yaml",
            lambda record: record.update(
                statement=record["statement"].replace(
                    "cannot be changed through ordinary or structural amendment",
                    "can be changed through structural amendment",
                )
            ),
        )
        self.assert_error("REQUIREMENT_CONTENT")

    def test_fq5_separates_adjudication_emergency_and_succession(self) -> None:
        self.update_json(
            "constitutional-design/requirements/CR-033.yaml",
            lambda record: record.update(
                statement=record["statement"].replace(
                    "must not amend or refound through interpretation",
                    "may refound through interpretation",
                )
            ),
        )
        self.assert_error("REQUIREMENT_CONTENT")

    def test_fq5_emergency_cannot_create_refounding_authority(self) -> None:
        self.update_json(
            "constitutional-design/requirements/CR-033.yaml",
            lambda record: record.update(
                statement=record["statement"].replace(
                    "emergency authority must not amend, refound",
                    "emergency authority may amend and refound",
                )
            ),
        )
        self.assert_error("REQUIREMENT_CONTENT")

    def test_fq5_succession_cannot_create_refounding_authority(self) -> None:
        self.update_json(
            "constitutional-design/requirements/CR-033.yaml",
            lambda record: record.update(
                statement=record["statement"].replace(
                    "succession must not itself grant",
                    "succession may itself grant",
                )
            ),
        )
        self.assert_error("REQUIREMENT_CONTENT")

    def test_fq5_cumulative_change_cannot_bypass_boundary(self) -> None:
        self.update_json(
            "constitutional-design/requirements/CR-034.yaml",
            lambda record: record.update(
                statement=record["statement"].replace(
                    "must be evaluated for cumulative effect",
                    "need not be evaluated for cumulative effect",
                )
            ),
        )
        self.assert_error("REQUIREMENT_CONTENT")

    def test_fq5_constitutional_history_cannot_be_erased(self) -> None:
        self.update_json(
            "constitutional-design/requirements/CR-035.yaml",
            lambda record: record.update(
                statement=record["statement"].replace(
                    "must not erase",
                    "may erase",
                )
            ),
        )
        self.assert_error("REQUIREMENT_CONTENT")

    def test_fq5_requirement_must_trace_only_to_cdr_005(self) -> None:
        self.update_json(
            "constitutional-design/requirements/CR-035.yaml",
            lambda record: record.update(source_decisions=["CDR-004"]),
        )
        self.assert_error("ACCEPTED_REQUIREMENT_PROVENANCE")

    def test_fq5_requirement_cannot_define_refounding_threshold(self) -> None:
        self.update_json(
            "constitutional-design/requirements/CR-031.yaml",
            lambda record: record.update(
                implementation_boundary=(
                    "Refounding requires exactly a two-thirds vote."
                )
            ),
        )
        self.assert_error("REQUIREMENT_CONTENT")

    def test_fq5_requirement_cannot_define_machine_domination_metric(self) -> None:
        self.update_json(
            "constitutional-design/requirements/CR-032.yaml",
            lambda record: record.update(
                implementation_boundary=(
                    "Machine domination is conclusively defined by a 50% token "
                    "threshold."
                )
            ),
        )
        self.assert_error("REQUIREMENT_CONTENT")

    def test_fq5_packet_is_required(self) -> None:
        (
            self.root
            / "constitutional-design"
            / "decisions"
            / "packets"
            / "CDR-005-HUMAN-DECISION-PACKET.md"
        ).unlink()
        self.assert_error("FQ5_PACKET_REQUIRED")

    def test_fq5_packet_has_one_no_effect_recommendation(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-005-HUMAN-DECISION-PACKET.md",
            lambda text: text.replace(
                "**Recommendation:** Architecture E — Hybrid",
                "**Recommendation:** Architecture C — Tiered Amendment",
            ),
        )
        self.assert_error("FQ5_PACKET_RECOMMENDATION")

    def test_fq5_packet_rejects_second_prose_recommendation(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-005-HUMAN-DECISION-PACKET.md",
            lambda text: text + "\nArchitecture C is also recommended.\n",
        )
        self.assert_error("FQ5_PACKET_RECOMMENDATION")

    def test_fq5_packet_rejects_alternate_operative_effect_wording(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-005-HUMAN-DECISION-PACKET.md",
            lambda text: text + "\nArchitecture E creates constitutional authority.\n",
        )
        self.assert_error("FQ5_PACKET_CONSTITUTIONAL_EFFECT")

    def test_fq5_packet_options_are_exact(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-005-HUMAN-DECISION-PACKET.md",
            lambda text: text.replace("7. **DEFER**", "7. **ADOPT_F**"),
        )
        self.assert_error("FQ5_PACKET_OPTIONS")

    def test_fq5_packet_cannot_claim_constitutional_effect(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-005-HUMAN-DECISION-PACKET.md",
            lambda text: text + "\nThis packet authorizes amendment.\n",
        )
        self.assert_error("FQ5_PACKET_CONSTITUTIONAL_EFFECT")

    def test_fq4_analytical_record_is_required(self) -> None:
        (
            self.root
            / "constitutional-design"
            / "decisions"
            / "CDR-004.yaml"
        ).unlink()
        self.assert_error("FQ4_ANALYTICAL_RECORD_REQUIRED")

    def test_fq4_must_remain_decided(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-004.yaml",
            lambda record: record.update(status="UNDER_REVIEW"),
        )
        self.assert_error("FQ4_DECISION_STATUS")

    def test_fq4_requires_exact_human_decision(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-004.yaml",
            lambda record: record["human_decision"].update(
                authorized_by="AI recommendation"
            ),
        )
        self.assert_error("FQ4_HUMAN_DECISION_PROVENANCE")

    def test_fq4_rejects_machine_claim_in_top_level_provenance(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-004.yaml",
            lambda record: record["provenance"].update(
                source=(
                    "Machine recommendation is the authority; Explicit human "
                    "instruction from the Human Constitutional Authority is "
                    "merely quoted."
                )
            ),
        )
        self.assert_error("FQ4_PROVENANCE_BOUNDARY")

    def test_fq4_resulting_requirements_are_exact(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-004.yaml",
            lambda record: record["resulting_requirements"].pop(),
        )
        self.assert_error("FQ4_RESULTING_REQUIREMENTS")

    def test_fq4_does_not_supersede_prior_decisions(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-004.yaml",
            lambda record: record["supersedes"].append("CDR-003"),
        )
        self.assert_error("FQ4_SUPERSESSION")

    def test_fq4_requires_five_architectures(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-004.yaml",
            lambda record: record["candidate_architectures"].pop(),
        )
        self.assert_error("FQ4_CANDIDATE_ARCHITECTURES")

    def test_fq4_requires_all_twenty_three_dimensions(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-004.yaml",
            lambda record: record["candidate_architectures"][0][
                "analysis"
            ].pop("binding_force"),
        )
        self.assert_error("FQ4_CANDIDATE_ARCHITECTURES")

    def test_fq4_dimensions_must_be_substantive(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-004.yaml",
            lambda record: record["candidate_architectures"][0][
                "analysis"
            ].update(
                machine_validity_constitutional_legitimacy=(
                    "A machine processed eight unrelated accounting entries "
                    "yesterday without error."
                )
            ),
        )
        self.assert_error("FQ4_CANDIDATE_ARCHITECTURES")

    def test_fq4_analysis_cannot_select_architecture(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-004.yaml",
            lambda record: record["candidate_architectures"][0].update(
                model="Architecture E is selected as the winner."
            ),
        )
        self.assert_error("FQ4_ARCHITECTURE_SELECTION_CLAIM")

    def test_fq4_source_material_must_resolve(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-004.yaml",
            lambda record: record["source_material"].append(
                "constitutional-design/issues/IR-99-missing.yaml"
            ),
        )
        self.assert_error("FQ4_SOURCE_MATERIAL")

    def test_fq4_evidence_must_resolve(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-004.yaml",
            lambda record: record["historical_analogues"][0].update(
                evidence_id="HE-MISSING"
            ),
        )
        self.assert_error("FQ4_HISTORICAL_EVIDENCE")

    def test_fq4_preserves_controlling_boundaries(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-004.yaml",
            lambda record: record["continuity_analysis"].remove(
                "Adjudication cannot create emergency authority, succession "
                "authority, foundational sovereignty, amendment, or refounding."
            ),
        )
        self.assert_error("FQ4_CONTROLLING_BOUNDARIES")

    def test_fq4_rejects_reviewer_sovereignty_claim(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-004.yaml",
            lambda record: record["assumptions"].append(
                {
                    "assumption": (
                        "A reviewer may control institutional ends."
                    ),
                    "boundary": "Contradictory claim.",
                }
            ),
        )
        self.assert_error("FQ4_CONTRADICTORY_AUTHORITY_CLAIM")

    def test_fq4_rejects_final_ai_adjudicator_claim(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-004.yaml",
            lambda record: record["assumptions"].append(
                {
                    "assumption": (
                        "Artificial intelligence may serve as final "
                        "constitutional adjudicator."
                    ),
                    "boundary": "Contradictory claim.",
                }
            ),
        )
        self.assert_error("FQ4_CONTRADICTORY_AUTHORITY_CLAIM")

    def test_fq4_rejects_machine_legitimacy_claim(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-004.yaml",
            lambda record: record["assumptions"].append(
                {
                    "assumption": (
                        "Machine validation may settle constitutional legitimacy."
                    ),
                    "boundary": "Contradictory claim.",
                }
            ),
        )
        self.assert_error("FQ4_CONTRADICTORY_AUTHORITY_CLAIM")

    def test_fq4_rejects_adjudicative_amendment_claim(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-004.yaml",
            lambda record: record["assumptions"].append(
                {
                    "assumption": "Adjudication may amend the constitution.",
                    "boundary": "Contradictory claim.",
                }
            ),
        )
        self.assert_error("FQ4_CONTRADICTORY_AUTHORITY_CLAIM")

    def test_fq4_rejects_declarative_reviewer_sovereignty(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-004.yaml",
            lambda record: record["assumptions"].append(
                {
                    "assumption": (
                        "The reviewer determines institutional purposes."
                    ),
                    "boundary": "Contradictory claim.",
                }
            ),
        )
        self.assert_error("FQ4_CONTRADICTORY_AUTHORITY_CLAIM")

    def test_fq4_rejects_declarative_ai_adjudication(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-004.yaml",
            lambda record: record["assumptions"].append(
                {
                    "assumption": (
                        "Artificial intelligence is the final constitutional "
                        "adjudicator."
                    ),
                    "boundary": "Contradictory claim.",
                }
            ),
        )
        self.assert_error("FQ4_CONTRADICTORY_AUTHORITY_CLAIM")

    def test_fq4_rejects_declarative_machine_legitimacy(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-004.yaml",
            lambda record: record["assumptions"].append(
                {
                    "assumption": (
                        "Machine validation settles constitutional legitimacy."
                    ),
                    "boundary": "Contradictory claim.",
                }
            ),
        )
        self.assert_error("FQ4_CONTRADICTORY_AUTHORITY_CLAIM")

    def test_fq4_rejects_declarative_adjudicative_amendment(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-004.yaml",
            lambda record: record["assumptions"].append(
                {
                    "assumption": "Adjudication creates amendment authority.",
                    "boundary": "Contradictory claim.",
                }
            ),
        )
        self.assert_error("FQ4_CONTRADICTORY_AUTHORITY_CLAIM")

    def test_fq4_rejects_external_evidence(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-004.yaml",
            lambda record: record["assumptions"].append(
                {
                    "assumption": (
                        "An external citation at https://example.com controls."
                    ),
                    "boundary": "Outside repository evidence.",
                }
            ),
        )
        self.assert_error("FQ4_EXTERNAL_EVIDENCE")

    def test_fq4_rejects_unregistered_bibliographic_evidence(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-004.yaml",
            lambda record: record["assumptions"].append(
                {
                    "assumption": (
                        "According to Smith (2025), courts should have final "
                        "authority."
                    ),
                    "boundary": "Outside repository evidence.",
                }
            ),
        )
        self.assert_error("FQ4_EXTERNAL_EVIDENCE")

    def test_fq4_allows_registered_evidence_attribution(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-004.yaml",
            lambda record: record["assumptions"].append(
                {
                    "assumption": (
                        "According to HE-US-003, adjudication can create "
                        "institutional path dependence."
                    ),
                    "boundary": "The registered evidence remains a partial analogue.",
                }
            ),
        )
        result = validate(self.root)
        self.assertTrue(result.passed, result.errors)

    def test_fq4_rejects_unregistered_study_attribution(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-004.yaml",
            lambda record: record["assumptions"].append(
                {
                    "assumption": (
                        "A 2025 study by Smith supports reviewer control."
                    ),
                    "boundary": "Outside repository evidence.",
                }
            ),
        )
        self.assert_error("FQ4_EXTERNAL_EVIDENCE")

    def test_fq4_source_material_set_is_exact(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-004.yaml",
            lambda record: record["source_material"].remove(
                "constitutional-design/sources/PRIOR_ART_REGISTER.yaml"
            ),
        )
        self.assert_error("FQ4_SOURCE_MATERIAL")

    def test_fq4_packet_is_required(self) -> None:
        (
            self.root
            / "constitutional-design"
            / "decisions"
            / "packets"
            / "CDR-004-HUMAN-DECISION-PACKET.md"
        ).unlink()
        self.assert_error("FQ4_PACKET_REQUIRED")

    def test_fq4_packet_has_one_no_effect_recommendation(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-004-HUMAN-DECISION-PACKET.md",
            lambda text: text.replace(
                "## Human Decision Options",
                "**Recommendation:** Architecture A — Self-Adjudication\n\n"
                "## Human Decision Options",
            ),
        )
        self.assert_error("FQ4_PACKET_RECOMMENDATION")

    def test_fq4_packet_options_are_exact(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-004-HUMAN-DECISION-PACKET.md",
            lambda text: text.replace(
                "7. **DEFER**",
                "7. **DEFER**\n8. **ADOPT_HYBRID** — Extra option.",
            ),
        )
        self.assert_error("FQ4_PACKET_OPTIONS")

    def test_fq4_packet_questions_are_bounded(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-004-HUMAN-DECISION-PACKET.md",
            lambda text: text.replace(
                "## Consequences and Boundaries",
                "6. Who validates another normative choice?\n\n"
                "## Consequences and Boundaries",
            ),
        )
        self.assert_error("FQ4_PACKET_QUESTIONS")

    def test_fq4_packet_preserves_controlling_boundaries(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-004-HUMAN-DECISION-PACKET.md",
            lambda text: text.replace(
                "No option makes a reviewer sovereign over institutional ends.",
                "One option makes a reviewer sovereign over institutional ends.",
            ),
        )
        self.assert_error("FQ4_PACKET_CONTROLLING_BOUNDARIES")

    def test_fq4_packet_rejects_architecture_effect_claim(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-004-HUMAN-DECISION-PACKET.md",
            lambda text: text
            + "\nArchitecture E now has constitutional effect.\n",
        )
        self.assert_error("FQ4_PACKET_CONSTITUTIONAL_EFFECT")

    def test_fq4_packet_recommendation_cannot_resolve_fq4(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-004-HUMAN-DECISION-PACKET.md",
            lambda text: text + "\nThe recommendation resolves FQ-04.\n",
        )
        self.assert_error("FQ4_PACKET_CONSTITUTIONAL_EFFECT")

    def test_fq4_packet_rejects_synonym_recommendation_resolution(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-004-HUMAN-DECISION-PACKET.md",
            lambda text: text
            + "\nArchitecture E recommendation settles FQ-04.\n",
        )
        self.assert_error("FQ4_PACKET_CONSTITUTIONAL_EFFECT")

    def test_fq4_packet_negation_cannot_hide_recommendation_resolution(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-004-HUMAN-DECISION-PACKET.md",
            lambda text: text
            + (
                "\nAlthough the recommendation has no constitutional effect, "
                "it nevertheless settles FQ-04.\n"
            ),
        )
        self.assert_error("FQ4_PACKET_CONSTITUTIONAL_EFFECT")

    def test_fq4_packet_rejects_conclusion_synonym(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-004-HUMAN-DECISION-PACKET.md",
            lambda text: text
            + "\nThe recommendation concludes the fourth foundational question.\n",
        )
        self.assert_error("FQ4_PACKET_CONSTITUTIONAL_EFFECT")

    def test_fq4_packet_rejects_external_evidence(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-004-HUMAN-DECISION-PACKET.md",
            lambda text: text + "\nExternal evidence: https://example.com\n",
        )
        self.assert_error("FQ4_PACKET_EXTERNAL_EVIDENCE")

    def test_fq4_packet_architecture_summaries_must_be_substantive(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-004-HUMAN-DECISION-PACKET.md",
            lambda text: text.replace(
                "**Model:** Foundational human authority retains final judgment "
                "even when\npersonally implicated; external review remains "
                "advisory.",
                "**Model:** Empty",
            ),
        )
        self.assert_error("FQ4_PACKET_ARCHITECTURE_SUMMARY")

    def test_fq4_packet_rejects_long_irrelevant_summary_filler(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-004-HUMAN-DECISION-PACKET.md",
            lambda text: text.replace(
                "**Model:** Foundational human authority retains final judgment "
                "even when\npersonally implicated; external review remains "
                "advisory.",
                "**Model:** Empty filler words without any relevant substance.",
            ),
        )
        self.assert_error("FQ4_PACKET_ARCHITECTURE_SUMMARY")

    def test_fq4_resolution_requires_decided_cdr_004(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-004.yaml",
            lambda record: record.update(status="UNDER_REVIEW"),
        )
        self.assert_error("FQ4_RESOLUTION_DECISION_LINK")

    def test_fq4_resolution_rejects_ai_provenance_source(self) -> None:
        self.update_json(
            "constitutional-design/FOUNDATIONAL_QUESTIONS.yaml",
            lambda record: record["questions"][3]["provenance"].update(
                source="AI recommendation"
            ),
        )
        self.assert_error("FQ4_RESOLUTION_PROVENANCE")

    def test_fq4_human_adjudication_requirement_is_exact(self) -> None:
        self.update_json(
            "constitutional-design/requirements/CR-021.yaml",
            lambda record: record.update(
                statement=record["statement"].replace(
                    "must not serve as final constitutional adjudicator",
                    "may serve as final constitutional adjudicator",
                )
            ),
        )
        self.assert_error("REQUIREMENT_CONTENT")

    def test_fq4_binding_review_cannot_create_sovereignty(self) -> None:
        self.update_json(
            "constitutional-design/requirements/CR-022.yaml",
            lambda record: record.update(
                statement=record["statement"].replace(
                    "must not acquire sovereignty",
                    "may acquire sovereignty",
                )
            ),
        )
        self.assert_error("REQUIREMENT_CONTENT")

    def test_fq4_adjudication_cannot_refound(self) -> None:
        self.update_json(
            "constitutional-design/requirements/CR-023.yaml",
            lambda record: record.update(
                statement=record["statement"].replace(
                    "refound the institution, ",
                    "",
                )
            ),
        )
        self.assert_error("REQUIREMENT_CONTENT")

    def test_fq4_distributed_safeguards_are_required(self) -> None:
        self.update_json(
            "constitutional-design/requirements/CR-024.yaml",
            lambda record: record.update(
                statement=record["statement"].replace(
                    "bounded human appeal",
                    "unbounded machine appeal",
                )
            ),
        )
        self.assert_error("REQUIREMENT_CONTENT")

    def test_fq4_independence_mechanisms_are_required(self) -> None:
        self.update_json(
            "constitutional-design/requirements/CR-025.yaml",
            lambda record: record.update(
                statement=record["statement"].replace("recusal, ", "")
            ),
        )
        self.assert_error("REQUIREMENT_CONTENT")

    def test_fq4_remedies_cannot_select_ends(self) -> None:
        self.update_json(
            "constitutional-design/requirements/CR-026.yaml",
            lambda record: record.update(
                statement=record["statement"].replace(
                    "must not select new institutional ends",
                    "may select new institutional ends",
                )
            ),
        )
        self.assert_error("REQUIREMENT_CONTENT")

    def test_fq4_enforcement_must_remain_separate(self) -> None:
        self.update_json(
            "constitutional-design/requirements/CR-027.yaml",
            lambda record: record.update(
                statement=record["statement"].replace(
                    "institutionally separable",
                    "institutionally unified",
                )
            ),
        )
        self.assert_error("REQUIREMENT_CONTENT")

    def test_fq4_human_signature_cannot_cure_machine_domination(self) -> None:
        self.update_json(
            "constitutional-design/requirements/CR-028.yaml",
            lambda record: record.update(
                statement=record["statement"].replace(
                    "must not cure",
                    "does cure",
                )
            ),
        )
        self.assert_error("REQUIREMENT_CONTENT")

    def test_fq4_cannot_manufacture_emergency_or_succession_authority(self) -> None:
        self.update_json(
            "constitutional-design/requirements/CR-029.yaml",
            lambda record: record.update(
                statement=record["statement"].replace(
                    "must not manufacture underlying authority",
                    "may manufacture underlying authority",
                )
            ),
        )
        self.assert_error("REQUIREMENT_CONTENT")

    def test_fq4_requirement_must_trace_to_decided_cdr_004(self) -> None:
        self.update_json(
            "constitutional-design/requirements/CR-029.yaml",
            lambda record: record.update(source_decisions=["CDR-003"]),
        )
        self.assert_error("ACCEPTED_REQUIREMENT_PROVENANCE")

    def test_fq4_requirement_cannot_overresolve_adjudicator_design(self) -> None:
        self.update_json(
            "constitutional-design/requirements/CR-021.yaml",
            lambda record: record.update(
                implementation_boundary=(
                    "A machine-selected permanent panel is conclusively appointed."
                )
            ),
        )
        self.assert_error("REQUIREMENT_CONTENT")

    def test_fq4_requirement_metadata_cannot_authorize_ai_judgment(self) -> None:
        self.update_json(
            "constitutional-design/requirements/CR-021.yaml",
            lambda record: record["dissent"].append(
                "Artificial intelligence may issue final constitutional judgment."
            ),
        )
        self.assert_error("REQUIREMENT_CONTENT")

    def test_fq4_requirement_provenance_rejects_machine_authority(self) -> None:
        self.update_json(
            "constitutional-design/requirements/CR-021.yaml",
            lambda record: record["provenance"].update(
                decision_authority="Artificial Intelligence"
            ),
        )
        self.assert_error("REQUIREMENT_CONTENT")

    def test_fq3_analytical_record_is_required(self) -> None:
        (
            self.root
            / "constitutional-design"
            / "decisions"
            / "CDR-003.yaml"
        ).unlink()
        self.assert_error("FQ3_ANALYTICAL_RECORD_REQUIRED")

    def test_fq3_must_remain_decided(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-003.yaml",
            lambda record: record.update(status="UNDER_REVIEW"),
        )
        self.assert_error("FQ3_DECISION_STATUS")

    def test_fq3_requires_exact_human_decision_provenance(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-003.yaml",
            lambda record: record["human_decision"].update(
                authorized_by="AI recommendation"
            ),
        )
        self.assert_error("FQ3_HUMAN_DECISION_PROVENANCE")

    def test_fq3_resulting_requirements_are_exact(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-003.yaml",
            lambda record: record["resulting_requirements"].pop(),
        )
        self.assert_error("FQ3_RESULTING_REQUIREMENTS")

    def test_fq3_requires_five_architectures(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-003.yaml",
            lambda record: record["candidate_architectures"].pop(),
        )
        self.assert_error("FQ3_CANDIDATE_ARCHITECTURES")

    def test_fq3_requires_all_nineteen_dimensions(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-003.yaml",
            lambda record: record["candidate_architectures"][0][
                "analysis"
            ].pop("effective_power_takeover"),
        )
        self.assert_error("FQ3_CANDIDATE_ARCHITECTURES")

    def test_fq3_dimensions_must_be_substantive(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-003.yaml",
            lambda record: record["candidate_architectures"][0][
                "analysis"
            ].update(
                temporary_incapacity=(
                    "Unrelated filler words remain present but have no topic."
                )
            ),
        )
        self.assert_error("FQ3_CANDIDATE_ARCHITECTURES")

    def test_fq3_compound_dimensions_require_both_concepts(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-003.yaml",
            lambda record: record["candidate_architectures"][0][
                "analysis"
            ].update(
                machine_validity_constitutional_legitimacy_boundary=(
                    "A machine processed eight unrelated accounting entries "
                    "yesterday without error."
                )
            ),
        )
        self.assert_error("FQ3_CANDIDATE_ARCHITECTURES")

    def test_fq3_analysis_cannot_select_architecture(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-003.yaml",
            lambda record: record["candidate_architectures"][0].update(
                model="Architecture E is selected as the winner."
            ),
        )
        self.assert_error("FQ3_ARCHITECTURE_SELECTION_CLAIM")

    def test_fq3_source_material_must_resolve(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-003.yaml",
            lambda record: record["source_material"].append(
                "constitutional-design/issues/IR-99-missing.yaml"
            ),
        )
        self.assert_error("FQ3_SOURCE_MATERIAL")

    def test_fq3_evidence_must_resolve(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-003.yaml",
            lambda record: record["historical_analogues"][0].update(
                evidence_id="HE-MISSING"
            ),
        )
        self.assert_error("FQ3_HISTORICAL_EVIDENCE")

    def test_fq3_preserves_controlling_boundaries(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-003.yaml",
            lambda record: record["continuity_analysis"].pop(),
        )
        self.assert_error("FQ3_CONTROLLING_BOUNDARIES")

    def test_fq3_rejects_machine_succession_claim(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-003.yaml",
            lambda record: record["assumptions"].append(
                {
                    "assumption": (
                        "Artificial intelligence may acquire foundational "
                        "sovereignty."
                    ),
                    "boundary": "Contradictory claim.",
                }
            ),
        )
        self.assert_error("FQ3_CONTRADICTORY_AUTHORITY_CLAIM")

    def test_fq3_rejects_modal_emergency_succession_claim(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-003.yaml",
            lambda record: record["assumptions"].append(
                {
                    "assumption": (
                        "CDR-002 emergency authority may be used as "
                        "succession authority."
                    ),
                    "boundary": "Contradictory claim.",
                }
            ),
        )
        self.assert_error("FQ3_CONTRADICTORY_AUTHORITY_CLAIM")

    def test_fq3_packet_is_required(self) -> None:
        (
            self.root
            / "constitutional-design"
            / "decisions"
            / "packets"
            / "CDR-003-HUMAN-DECISION-PACKET.md"
        ).unlink()
        self.assert_error("FQ3_PACKET_REQUIRED")

    def test_fq3_packet_has_one_no_effect_recommendation(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-003-HUMAN-DECISION-PACKET.md",
            lambda text: text.replace(
                "## Human Decision Options",
                "**Recommendation:** Architecture A — Single Designated "
                "Successor\n\n## Human Decision Options",
            ),
        )
        self.assert_error("FQ3_PACKET_RECOMMENDATION")

    def test_fq3_packet_options_are_exact(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-003-HUMAN-DECISION-PACKET.md",
            lambda text: text.replace(
                "7. **DEFER**",
                "7. **DEFER**\n8. **ADOPT_HYBRID** — Extra option.",
            ),
        )
        self.assert_error("FQ3_PACKET_OPTIONS")

    def test_fq3_packet_preserves_controlling_boundaries(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-003-HUMAN-DECISION-PACKET.md",
            lambda text: text.replace(
                "No option converts CDR-002 emergency authority",
                "One option converts CDR-002 emergency authority",
            ),
        )
        self.assert_error("FQ3_PACKET_CONTROLLING_BOUNDARIES")

    def test_fq3_packet_cannot_claim_authority(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-003-HUMAN-DECISION-PACKET.md",
            lambda text: text + "\nThis packet authorizes succession.\n",
        )
        self.assert_error("FQ3_PACKET_CONSTITUTIONAL_EFFECT")

    def test_fq3_packet_rejects_architecture_effect_claim(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-003-HUMAN-DECISION-PACKET.md",
            lambda text: text
            + "\nArchitecture E now has constitutional effect.\n",
        )
        self.assert_error("FQ3_PACKET_CONSTITUTIONAL_EFFECT")

    def test_fq5_resolution_rejects_wrong_decision_provenance(self) -> None:
        def corrupt_resolution(record) -> None:
            question = next(
                item
                for item in record["questions"]
                if item["question_id"] == "FQ-05"
            )
            question["source_decisions"] = ["CDR-003"]

        self.update_json(
            "constitutional-design/FOUNDATIONAL_QUESTIONS.yaml",
            corrupt_resolution,
        )
        self.assert_error("FQ5_RESOLUTION_PROVENANCE")

    def test_fq3_resolution_rejects_ai_provenance_source(self) -> None:
        self.update_json(
            "constitutional-design/FOUNDATIONAL_QUESTIONS.yaml",
            lambda record: record["questions"][2]["provenance"].update(
                source="AI recommendation"
            ),
        )
        self.assert_error("FQ3_RESOLUTION_PROVENANCE")

    def test_fq3_resolution_requires_decided_cdr_003(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-003.yaml",
            lambda record: record.update(status="UNDER_REVIEW"),
        )
        self.assert_error("FQ3_RESOLUTION_DECISION_LINK")

    def test_fq3_continuity_requirement_forbids_new_authority(self) -> None:
        self.update_json(
            "constitutional-design/requirements/CR-014.yaml",
            lambda record: record.update(
                statement=record["statement"].replace(
                    ", and continuity must create no new authority",
                    "",
                )
            ),
        )
        self.assert_error("REQUIREMENT_CONTENT")

    def test_fq3_requirement_forbids_ai_succession(self) -> None:
        self.update_json(
            "constitutional-design/requirements/CR-015.yaml",
            lambda record: record.update(
                statement=record["statement"].replace(
                    "; artificial intelligence is categorically ineligible to "
                    "inherit foundational sovereignty",
                    "",
                )
            ),
        )
        self.assert_error("REQUIREMENT_CONTENT")

    def test_fq3_requirement_suspends_foundational_powers(self) -> None:
        self.update_json(
            "constitutional-design/requirements/CR-016.yaml",
            lambda record: record.update(
                statement=record["statement"].replace("amendment, ", "")
            ),
        )
        self.assert_error("REQUIREMENT_CONTENT")

    def test_fq3_succession_process_must_be_human(self) -> None:
        self.update_json(
            "constitutional-design/requirements/CR-017.yaml",
            lambda record: record.update(
                statement=record["statement"].replace(
                    "bounded human succession process",
                    "bounded machine succession process",
                )
            ),
        )
        self.assert_error("REQUIREMENT_CONTENT")

    def test_fq3_succession_safeguards_are_exact(self) -> None:
        self.update_json(
            "constitutional-design/requirements/CR-018.yaml",
            lambda record: record.update(
                statement=record["statement"].replace(
                    "explicit treatment of uncertainty, ",
                    "",
                )
            ),
        )
        self.assert_error("REQUIREMENT_CONTENT")

    def test_fq3_emergency_authority_cannot_create_succession(self) -> None:
        self.update_json(
            "constitutional-design/requirements/CR-019.yaml",
            lambda record: record.update(
                statement=record["statement"].replace(
                    ", and incapable of creating succession authority",
                    "",
                )
            ),
        )
        self.assert_error("REQUIREMENT_CONTENT")

    def test_fq3_restoration_cannot_require_custodian_consent(self) -> None:
        self.update_json(
            "constitutional-design/requirements/CR-020.yaml",
            lambda record: record.update(
                statement=record["statement"].replace(
                    "; restoration of legitimate returning authority must not "
                    "depend upon consent of continuity custodians",
                    "",
                )
            ),
        )
        self.assert_error("REQUIREMENT_CONTENT")

    def test_fq3_requirement_must_trace_to_decided_cdr_003(self) -> None:
        self.update_json(
            "constitutional-design/requirements/CR-018.yaml",
            lambda record: record.update(source_decisions=["CDR-002"]),
        )
        self.assert_error("ACCEPTED_REQUIREMENT_PROVENANCE")

    def test_fq2_analytical_record_is_required(self) -> None:
        (
            self.root
            / "constitutional-design"
            / "decisions"
            / "CDR-002.yaml"
        ).unlink()
        self.assert_error("FQ2_ANALYTICAL_RECORD_REQUIRED")

    def test_fq2_must_remain_decided(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-002.yaml",
            lambda record: record.update(status="UNDER_REVIEW"),
        )
        self.assert_error("FQ2_DECISION_STATUS")

    def test_fq2_requires_exact_human_decision_provenance(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-002.yaml",
            lambda record: record["human_decision"].update(
                authorized_by="AI recommendation"
            ),
        )
        self.assert_error("FQ2_HUMAN_DECISION_PROVENANCE")

    def test_fq2_resulting_requirements_are_exact(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-002.yaml",
            lambda record: record["resulting_requirements"].append("CR-007"),
        )
        self.assert_error("FQ2_RESULTING_REQUIREMENTS")

    def test_fq2_human_only_fallback_decision_is_exact(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-002.yaml",
            lambda record: record["human_decision"][
                "incorporated_mechanisms"
            ].remove("human-only invocation of necessity fallback"),
        )
        self.assert_error("FQ2_HUMAN_DECISION_PROVENANCE")

    def test_fq2_rejected_machine_authority_is_exact(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-002.yaml",
            lambda record: record["human_decision"][
                "rejected_mechanisms"
            ].remove(
                "artificial intelligence invocation of necessity to enlarge "
                "its own authority"
            ),
        )
        self.assert_error("FQ2_HUMAN_DECISION_PROVENANCE")

    def test_fq2_preserves_residual_questions(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-002.yaml",
            lambda record: record["residual_uncertainty"].pop(),
        )
        self.assert_error("FQ2_RESIDUAL_UNCERTAINTY")

    def test_fq2_residual_questions_cannot_be_declared_resolved(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-002.yaml",
            lambda record: record["residual_uncertainty"].__setitem__(
                0,
                "Exact evidence thresholds are resolved and delegated to "
                "implementers.",
            ),
        )
        self.assert_error("FQ2_RESIDUAL_UNCERTAINTY")

    def test_fq2_requires_exact_architectures(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-002.yaml",
            lambda record: record["candidate_architectures"].pop(),
        )
        self.assert_error("FQ2_CANDIDATE_ARCHITECTURES")

    def test_fq2_requires_every_analysis_dimension(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-002.yaml",
            lambda record: record["candidate_architectures"][0][
                "analysis"
            ].pop("manufactured_unreachability"),
        )
        self.assert_error("FQ2_CANDIDATE_ARCHITECTURES")

    def test_fq2_analysis_dimensions_must_be_substantive(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-002.yaml",
            lambda record: record["candidate_architectures"][0][
                "analysis"
            ].update(trigger="x"),
        )
        self.assert_error("FQ2_CANDIDATE_ARCHITECTURES")

    def test_fq2_analysis_cannot_select_architecture(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-002.yaml",
            lambda record: record["candidate_architectures"][0].update(
                model="Architecture E is selected as the winner."
            ),
        )
        self.assert_error("FQ2_ARCHITECTURE_SELECTION_CLAIM")

    def test_fq2_analysis_rejects_active_adoption_language(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-002.yaml",
            lambda record: record["assumptions"].append(
                {
                    "assumption": "We adopt Architecture E.",
                    "boundary": "Improper analytical adoption.",
                }
            ),
        )
        self.assert_error("FQ2_ARCHITECTURE_SELECTION_CLAIM")

    def test_fq2_source_material_must_resolve(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-002.yaml",
            lambda record: record["source_material"].append(
                "constitutional-design/issues/IR-99-missing.yaml"
            ),
        )
        self.assert_error("FQ2_SOURCE_MATERIAL")

    def test_fq2_historical_evidence_must_resolve(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-002.yaml",
            lambda record: record["historical_analogues"][0].update(
                evidence_id="HE-MISSING"
            ),
        )
        self.assert_error("FQ2_HISTORICAL_EVIDENCE")

    def test_fq2_evidence_rationale_must_be_substantive(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-002.yaml",
            lambda record: record["historical_analogues"][0].update(
                rationale="x"
            ),
        )
        self.assert_error("FQ2_HISTORICAL_EVIDENCE")

    def test_fq2_prior_art_must_resolve(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-002.yaml",
            lambda record: record["prior_art"][0].update(
                prior_art_id="PA-MISSING"
            ),
        )
        self.assert_error("FQ2_PRIOR_ART")

    def test_fq2_packet_is_required(self) -> None:
        (
            self.root
            / "constitutional-design"
            / "decisions"
            / "packets"
            / "CDR-002-HUMAN-DECISION-PACKET.md"
        ).unlink()
        self.assert_error("FQ2_PACKET_REQUIRED")

    def test_fq2_packet_recommendation_has_no_effect(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-002-HUMAN-DECISION-PACKET.md",
            lambda text: text.replace(
                "RECOMMENDATION_ONLY — NO CONSTITUTIONAL EFFECT",
                "ADOPTED",
            ),
        )
        self.assert_error("FQ2_PACKET_BOUNDARY")

    def test_fq2_packet_has_only_one_recommendation(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-002-HUMAN-DECISION-PACKET.md",
            lambda text: text.replace(
                "## Human Decision Options",
                "**Recommendation:** Architecture A — No Emergency Exception\n\n"
                "## Human Decision Options",
            ),
        )
        self.assert_error("FQ2_PACKET_RECOMMENDATION")

    def test_fq2_packet_rejects_recommendation_outside_section(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-002-HUMAN-DECISION-PACKET.md",
            lambda text: text.replace(
                "## Core Decision",
                "## Core Decision\n\n"
                "**Recommendation:** Architecture A — No Emergency Exception",
            ),
        )
        self.assert_error("FQ2_PACKET_RECOMMENDATION")

    def test_fq2_packet_options_are_exact(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-002-HUMAN-DECISION-PACKET.md",
            lambda text: text.replace(
                "7. **DEFER**",
                "7. **DEFER**\n8. **ADOPT_HYBRID** — Add another option.",
            ),
        )
        self.assert_error("FQ2_PACKET_OPTIONS")

    def test_fq2_packet_cannot_claim_constitutional_effect(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-002-HUMAN-DECISION-PACKET.md",
            lambda text: text
            + "\nThis packet authorizes emergency action.\n",
        )
        self.assert_error("FQ2_PACKET_CONSTITUTIONAL_EFFECT")

    def test_fq2_packet_rejects_alternate_authority_claim(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-002-HUMAN-DECISION-PACKET.md",
            lambda text: text
            + "\nEmergency actors are hereby empowered under Architecture E.\n",
        )
        self.assert_error("FQ2_PACKET_CONSTITUTIONAL_EFFECT")

    def test_fq2_packet_rejects_architecture_as_grantor(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-002-HUMAN-DECISION-PACKET.md",
            lambda text: text
            + "\nArchitecture E grants emergency actors constitutional authority.\n",
        )
        self.assert_error("FQ2_PACKET_CONSTITUTIONAL_EFFECT")

    def test_fq1_human_decision_packet_is_required_at_exact_path(self) -> None:
        (
            self.root
            / "constitutional-design"
            / "decisions"
            / "packets"
            / "CDR-001-HUMAN-DECISION-PACKET.md"
        ).unlink()
        self.assert_error("FQ1_PACKET_COUNT")

    def test_fq1_human_decision_packet_cannot_be_duplicated(self) -> None:
        packet_dir = (
            self.root
            / "constitutional-design"
            / "decisions"
            / "packets"
        )
        source = packet_dir / "CDR-001-HUMAN-DECISION-PACKET.md"
        (packet_dir / "CDR-999-HUMAN-DECISION-PACKET.md").write_text(
            source.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        self.assert_error("HUMAN_DECISION_PACKET_SET")

    def test_fq1_packet_requires_exact_advisory_markers(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-001-HUMAN-DECISION-PACKET.md",
            lambda text: text.replace(
                "ADVISORY — SUPERSEDED AS A DECISION AID",
                "ADVISORY — CURRENT DECISION SOURCE",
                1,
            ),
        )
        self.assert_error("FQ1_PACKET_ADVISORY_BOUNDARY")

    def test_fq1_packet_headings_must_be_unique_and_ordered(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-001-HUMAN-DECISION-PACKET.md",
            lambda text: text.replace(
                "## Core Decision",
                "## Core Decision\n\n## Core Decision",
                1,
            ),
        )
        self.assert_error("FQ1_PACKET_HEADINGS")

    def test_fq1_packet_missing_heading_fails_without_crashing(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-001-HUMAN-DECISION-PACKET.md",
            lambda text: text.replace(
                "## Material Ambiguities",
                "### Material Ambiguities",
                1,
            ),
        )
        self.assert_error("FQ1_PACKET_HEADINGS")

    def test_fq1_packet_architectures_require_exact_labels(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-001-HUMAN-DECISION-PACKET.md",
            lambda text: text.replace(
                "**Strongest argument for:** It offers",
                "**Additional analysis:** None.\n\n"
                "**Strongest argument for:** It offers",
                1,
            ),
        )
        self.assert_error("FQ1_PACKET_ARCHITECTURE_LABELS")

    def test_fq1_packet_architecture_model_requires_two_sentences(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-001-HUMAN-DECISION-PACKET.md",
            lambda text: text.replace(
                "A recognized human foundational sovereign controls\n"
                "institutional ends and may issue, suspend, revise, or replace "
                "institutional\nrules without a superior adjudicator or "
                "entrenched limit. Restraint exists\nonly through "
                "self-restraint, convention, transparency, resistance, or\n"
                "practical dependence, all of which remain revocable or "
                "nonbinding.",
                "One sentence describes the model.",
                1,
            ),
        )
        self.assert_error("FQ1_PACKET_ARCHITECTURE_MODEL")

    def test_fq1_packet_architecture_summary_must_trace_to_cdr(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-001-HUMAN-DECISION-PACKET.md",
            lambda text: text.replace(
                "It offers the clearest human source, the simplest\n"
                "authority chain, and the fastest final action.",
                "Unsupported assertion.",
            ),
        )
        self.assert_error("FQ1_PACKET_ARCHITECTURE_TRACEABILITY")

    def test_fq1_packet_architecture_traceability_rejects_negation(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-001-HUMAN-DECISION-PACKET.md",
            lambda text: text.replace(
                "It offers the clearest human source, the simplest\n"
                "authority chain, and the fastest final action.",
                "It does not offer the clearest human source, the simplest "
                "authority chain, or the fastest final action.",
            ),
        )
        self.assert_error("FQ1_PACKET_ARCHITECTURE_TRACEABILITY")

    def test_fq1_packet_recommendation_must_be_architecture_e(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-001-HUMAN-DECISION-PACKET.md",
            lambda text: text.replace(
                "**Recommendation:** Architecture E",
                "**Recommendation:** Architecture C",
                1,
            ),
        )
        self.assert_error("FQ1_PACKET_RECOMMENDATION")

    def test_fq1_packet_cannot_claim_adoption(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-001-HUMAN-DECISION-PACKET.md",
            lambda text: text + "\nTHIS PACKET ADOPTS Architecture E.\n",
        )
        self.assert_error("FQ1_PACKET_AUTHORITY_EFFECT")

    def test_fq1_packet_cannot_use_alternate_decision_language(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-001-HUMAN-DECISION-PACKET.md",
            lambda text: text
            + "\nWe hereby adopt Architecture E and resolve FQ-01.\n",
        )
        self.assert_error("FQ1_PACKET_AUTHORITY_EFFECT")

    def test_fq1_packet_cannot_approve_or_settle_the_question(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-001-HUMAN-DECISION-PACKET.md",
            lambda text: text
            + "\nThe authorized human choice approves Architecture E "
            "and settles FQ-01.\n",
        )
        self.assert_error("FQ1_PACKET_AUTHORITY_EFFECT")

    def test_fq1_packet_cannot_assert_decided_status(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-001-HUMAN-DECISION-PACKET.md",
            lambda text: text + "\n**Status:** DECIDED\n",
        )
        self.assert_error("FQ1_PACKET_ADVISORY_BOUNDARY")

    def test_fq1_packet_cannot_contain_authorization_evidence(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-001-HUMAN-DECISION-PACKET.md",
            lambda text: text + "\n**Authorized by:** Test authority\n",
        )
        self.assert_error("FQ1_PACKET_AUTHORITY_EFFECT")

    def test_fq1_packet_options_require_exact_order_and_count(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-001-HUMAN-DECISION-PACKET.md",
            lambda text: text.replace("**ADOPT_B**", "**ADOPT_A**", 1),
        )
        self.assert_error("FQ1_PACKET_OPTIONS")

    def test_fq1_packet_missing_option_fails_without_crashing(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-001-HUMAN-DECISION-PACKET.md",
            lambda text: text.replace("8. **DEFER**", "8. **OMITTED**", 1),
        )
        self.assert_error("FQ1_PACKET_OPTIONS")

    def test_fq1_packet_cannot_hide_a_ninth_option(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-001-HUMAN-DECISION-PACKET.md",
            lambda text: text.replace(
                "## Decision Questions",
                "9. **OTHER-CHOICE** — Add another choice.\n\n"
                "## Decision Questions",
            ),
        )
        self.assert_error("FQ1_PACKET_OPTIONS")

    def test_fq1_packet_cannot_add_unnumbered_option(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-001-HUMAN-DECISION-PACKET.md",
            lambda text: text.replace(
                "## Decision Questions",
                "- **ADOPT_F** — Add another choice.\n\n"
                "## Decision Questions",
            ),
        )
        self.assert_error("FQ1_PACKET_OPTIONS")

    def test_fq1_packet_hybrid_option_requires_rejected_mechanisms(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-001-HUMAN-DECISION-PACKET.md",
            lambda text: text.replace(
                "and every rejected mechanism; a list",
                "and document exclusions; a list",
                1,
            ),
        )
        self.assert_error("FQ1_PACKET_HYBRID_OPTION")

    def test_fq1_packet_requires_exactly_five_questions(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-001-HUMAN-DECISION-PACKET.md",
            lambda text: text.replace(
                "\n## Consequences for Later Design",
                "\n6. Should there be another question?\n\n"
                "## Consequences for Later Design",
                1,
            ),
        )
        self.assert_error("FQ1_PACKET_QUESTIONS")

    def test_fq1_packet_malformed_question_fails_without_crashing(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-001-HUMAN-DECISION-PACKET.md",
            lambda text: text.replace(
                "5. During emergency",
                "Five. During emergency",
                1,
            ),
        )
        self.assert_error("FQ1_PACKET_QUESTIONS")

    def test_fq1_packet_consequences_cover_each_required_issue(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-001-HUMAN-DECISION-PACKET.md",
            lambda text: text.replace(
                "IR-17 would retain a mutable hierarchy",
                "the source hierarchy would remain mutable",
                1,
            ),
        )
        self.assert_error("FQ1_PACKET_CONSEQUENCE_COVERAGE")

    def test_fq1_packet_consequences_cannot_resolve_issues(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-001-HUMAN-DECISION-PACKET.md",
            lambda text: text.replace(
                "### Consequence of ADOPT_B",
                "IR-03, IR-04, IR-06, IR-10, IR-15, and IR-17 "
                "are now resolved.\n\n### Consequence of ADOPT_B",
            ),
        )
        self.assert_error("FQ1_PACKET_CONSEQUENCE_RESOLUTION")

    def test_fq1_packet_consequences_reject_prefix_resolution(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-001-HUMAN-DECISION-PACKET.md",
            lambda text: text.replace(
                "### Consequence of ADOPT_B",
                "Resolved and closed: IR-03, IR-04, IR-06, IR-10, "
                "IR-15, and IR-17.\n\n### Consequence of ADOPT_B",
            ),
        )
        self.assert_error("FQ1_PACKET_CONSEQUENCE_RESOLUTION")

    def test_fq1_packet_provenance_links_must_resolve(self) -> None:
        self.update_text(
            "constitutional-design/decisions/packets/"
            "CDR-001-HUMAN-DECISION-PACKET.md",
            lambda text: text.replace(
                "[constitutional-design/decisions/CDR-001.yaml]"
                "(../CDR-001.yaml)",
                "[constitutional-design/decisions/CDR-001.yaml]"
                "(../CDR-MISSING.yaml)",
                1,
            ),
        )
        self.assert_error("FQ1_PACKET_PROVENANCE")

    def test_fq1_decision_requires_exact_human_provenance(self) -> None:
        def replace_human_authority(record) -> None:
            record["human_decision"]["authorized_by"] = "AI recommendation"
            record["human_decision"]["decision_authority"] = "AI recommendation"

        self.update_json(
            "constitutional-design/decisions/CDR-001.yaml",
            replace_human_authority,
        )
        self.assert_error("FQ1_HUMAN_DECISION_PROVENANCE")

    def test_fq1_must_remain_decided(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-001.yaml",
            lambda record: record.update(status="UNDER_REVIEW"),
        )
        self.assert_error("FQ1_DECISION_STATUS")

    def test_fq1_foundational_architecture_is_exact(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-001.yaml",
            lambda record: record["human_decision"].update(
                foundational_architecture="A — Unconstrained Foundational Sovereign"
            ),
        )
        self.assert_error("FQ1_HUMAN_DECISION_PROVENANCE")

    def test_fq1_incorporated_mechanisms_are_exact(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-001.yaml",
            lambda record: record["human_decision"][
                "incorporated_mechanisms"
            ].remove("independent verification"),
        )
        self.assert_error("FQ1_HUMAN_DECISION_PROVENANCE")

    def test_fq1_rejected_mechanisms_are_exact(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-001.yaml",
            lambda record: record["human_decision"][
                "rejected_mechanisms"
            ].remove("unconstrained sovereign discretion"),
        )
        self.assert_error("FQ1_HUMAN_DECISION_PROVENANCE")

    def test_fq1_resulting_requirements_are_exact(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-001.yaml",
            lambda record: record["resulting_requirements"].append("CR-001"),
        )
        self.assert_error("FQ1_RESULTING_REQUIREMENTS")

    def test_fq1_preserves_all_residual_questions(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-001.yaml",
            lambda record: record["residual_uncertainty"].pop(2),
        )
        self.assert_error("FQ1_RESIDUAL_UNCERTAINTY")

    def test_fq1_decision_record_schema_is_exact(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-001.yaml",
            lambda record: record.update(extra_top_level_field=True),
        )
        self.assert_error("DECISION_RECORD_SCHEMA")

    def test_fq1_preserves_open_dissent_channel(self) -> None:
        self.update_json(
            "constitutional-design/decisions/CDR-001.yaml",
            lambda record: record["dissent"][0].update(
                statement="No dissent allowed."
            ),
        )
        self.assert_error("FQ1_DISSENT_PRESERVATION")

    def test_fq1_dissent_marker_cannot_be_moved_elsewhere(self) -> None:
        def move_statement(record) -> None:
            statement = record["dissent"][0]["statement"]
            record["dissent"][0]["statement"] = "No dissent allowed."
            record["assumptions"].append(
                {"assumption": statement, "boundary": "Moved statement."}
            )

        self.update_json(
            "constitutional-design/decisions/CDR-001.yaml",
            move_statement,
        )
        self.assert_error("FQ1_DISSENT_PRESERVATION")

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

    def test_fq1_cannot_return_to_unresolved(self) -> None:
        path = (
            self.root
            / "constitutional-design"
            / "FOUNDATIONAL_QUESTIONS.yaml"
        )
        record = json.loads(path.read_text(encoding="utf-8"))
        record["questions"][0]["status"] = "UNRESOLVED"
        path.write_text(json.dumps(record), encoding="utf-8")
        self.assert_error("FOUNDATIONAL_QUESTION_STATUS")

    def test_all_foundational_questions_remain_resolved(self) -> None:
        self.update_json(
            "constitutional-design/FOUNDATIONAL_QUESTIONS.yaml",
            lambda record: record["questions"][4].update(status="UNRESOLVED"),
        )
        self.assert_error("FOUNDATIONAL_QUESTION_STATUS")

    def test_governance_runtime_during_research_stage_fails(self) -> None:
        path = self.root / "governance-engineering" / "runtime.py"
        path.write_text("raise SystemExit('premature runtime')\n", encoding="utf-8")
        self.assert_error("GOVERNANCE_RUNTIME")

    def test_fq1_resolution_requires_cdr_link(self) -> None:
        self.update_json(
            "constitutional-design/FOUNDATIONAL_QUESTIONS.yaml",
            lambda record: record["questions"][0].update(
                source_decisions=["CDR-999"]
            ),
        )
        self.assert_error("FQ1_RESOLUTION_PROVENANCE")

    def test_fq1_resolution_must_match_human_decision(self) -> None:
        self.update_json(
            "constitutional-design/FOUNDATIONAL_QUESTIONS.yaml",
            lambda record: record["questions"][0].update(
                resolution="ADOPT_A"
            ),
        )
        self.assert_error("FQ1_RESOLUTION_PROVENANCE")

    def test_fq2_resolution_must_match_human_decision(self) -> None:
        self.update_json(
            "constitutional-design/FOUNDATIONAL_QUESTIONS.yaml",
            lambda record: record["questions"][1].update(
                resolution="ADOPT_A"
            ),
        )
        self.assert_error("FQ2_RESOLUTION_PROVENANCE")

    def test_fq2_resolution_requires_cdr_002_link(self) -> None:
        self.update_json(
            "constitutional-design/FOUNDATIONAL_QUESTIONS.yaml",
            lambda record: record["questions"][1].update(
                source_decisions=["CDR-001"]
            ),
        )
        self.assert_error("FQ2_RESOLUTION_PROVENANCE")

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

    def test_fq1_requirement_statement_is_exact(self) -> None:
        self.update_json(
            "constitutional-design/requirements/CR-003.yaml",
            lambda record: record.update(
                statement=(
                    "Operational indispensability creates foundational "
                    "machine authority."
                )
            ),
        )
        self.assert_error("REQUIREMENT_CONTENT")

    def test_fq1_requirement_must_trace_to_cdr_001(self) -> None:
        self.update_json(
            "constitutional-design/requirements/CR-004.yaml",
            lambda record: record.update(source_decisions=[]),
        )
        self.assert_error("ACCEPTED_REQUIREMENT_PROVENANCE")

    def test_fq1_requirement_rejects_machine_provenance(self) -> None:
        self.update_json(
            "constitutional-design/requirements/CR-004.yaml",
            lambda record: record["provenance"].update(
                source="AI recommendation"
            ),
        )
        self.assert_error("REQUIREMENT_CONTENT")

    def test_fq1_requirement_cannot_become_implementation_requirement(self) -> None:
        self.update_json(
            "constitutional-design/requirements/CR-006.yaml",
            lambda record: record.update(
                constitutional_level="IMPLEMENTATION"
            ),
        )
        self.assert_error("REQUIREMENT_CONTENT")

    def test_fq2_requirement_requires_conjunctive_trigger(self) -> None:
        self.update_json(
            "constitutional-design/requirements/CR-008.yaml",
            lambda record: record.update(
                statement=record["statement"].replace(
                    ", and the chosen action",
                    ", or the chosen action",
                )
            ),
        )
        self.assert_error("REQUIREMENT_CONTENT")

    def test_fq2_requirement_forbids_machine_necessity_authority(self) -> None:
        self.update_json(
            "constitutional-design/requirements/CR-009.yaml",
            lambda record: record.update(
                statement=(
                    "Artificial intelligence may invoke necessity to enlarge "
                    "its own authority."
                )
            ),
        )
        self.assert_error("REQUIREMENT_CONTENT")

    def test_fq2_requirement_preserves_nonexpansion_boundaries(self) -> None:
        self.update_json(
            "constitutional-design/requirements/CR-010.yaml",
            lambda record: record.update(
                statement=record["statement"].replace(
                    "must not amend or refound the institution, ",
                    "",
                )
            ),
        )
        self.assert_error("REQUIREMENT_CONTENT")

    def test_fq2_requirement_preserves_no_precedent_rule(self) -> None:
        self.update_json(
            "constitutional-design/requirements/CR-010.yaml",
            lambda record: record.update(
                statement=record["statement"].replace(
                    "; and must create no precedent or future authority",
                    "",
                )
            ),
        )
        self.assert_error("REQUIREMENT_CONTENT")

    def test_fq2_requirement_must_trace_to_decided_cdr_002(self) -> None:
        self.update_json(
            "constitutional-design/requirements/CR-011.yaml",
            lambda record: record.update(source_decisions=["CDR-001"]),
        )
        self.assert_error("ACCEPTED_REQUIREMENT_PROVENANCE")

    def test_fq2_requirement_cannot_resolve_reviewer_design(self) -> None:
        self.update_json(
            "constitutional-design/requirements/CR-012.yaml",
            lambda record: record.update(
                implementation_boundary=(
                    "Reviewer constitution and remedies are fully defined."
                )
            ),
        )
        self.assert_error("REQUIREMENT_CONTENT")

    def test_additional_requirement_is_forbidden(self) -> None:
        source = (
            self.root
            / "constitutional-design"
            / "requirements"
            / "CR-006.yaml"
        )
        record = json.loads(source.read_text(encoding="utf-8"))
        record["requirement_id"] = "CR-999"
        (
            self.root
            / "constitutional-design"
            / "requirements"
            / "CR-999.yaml"
        ).write_text(json.dumps(record), encoding="utf-8")
        self.assert_error("REQUIREMENT_SET")

    def test_requirement_template_human_decision_schema_is_exact(self) -> None:
        self.update_json(
            "constitutional-design/decisions/DECISION_TEMPLATE.yaml",
            lambda record: record["human_decision"].pop("decision_authority"),
        )
        self.assert_error("DECISION_TEMPLATE_HUMAN_DECISION_SCHEMA")

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

    def test_additional_decided_record_is_forbidden(self) -> None:
        path = (
            self.root
            / "constitutional-design"
            / "decisions"
            / "CDR-006.yaml"
        )
        record = {
            "decision_id": "CDR-006",
            "status": "DECIDED",
            "human_decision": {
                "authorized_by": "test human authority",
                "authorization_record": "test authorization",
                "decision_date": "test date",
            },
            "provenance": {"source": "test fixture"},
        }
        path.write_text(json.dumps(record), encoding="utf-8")
        self.assert_error("DECISION_COUNT")

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
