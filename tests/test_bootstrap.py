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
            {"DECIDED": 3},
        )
        self.assertEqual(
            result.metrics["fq1_historical_evidence_reference_count"], 32
        )
        self.assertEqual(result.metrics["fq1_prior_art_reference_count"], 33)
        self.assertEqual(result.metrics["decided_decision_count"], 3)
        self.assertEqual(result.metrics["accepted_requirement_count"], 20)
        self.assertEqual(
            result.metrics["foundational_question_status_counts"],
            {"RESOLVED": 3, "UNRESOLVED": 2},
        )
        self.assertEqual(result.metrics["constitutional_provision_count"], 0)
        self.assertEqual(result.metrics["human_decision_packet_count"], 3)
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

    def test_unresolved_fq4_cannot_carry_resolution_fields(self) -> None:
        def add_false_resolution(record) -> None:
            question = next(
                item
                for item in record["questions"]
                if item["question_id"] == "FQ-04"
            )
            question["source_decisions"] = ["CDR-003"]
            question["resolution"] = "Architecture E is adopted."
            question["provenance"]["decision_authority"] = (
                "Human Constitutional Authority"
            )

        self.update_json(
            "constitutional-design/FOUNDATIONAL_QUESTIONS.yaml",
            add_false_resolution,
        )
        self.assert_error("UNRESOLVED_FOUNDATIONAL_QUESTION_STATE")

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

    def test_other_foundational_questions_remain_unresolved(self) -> None:
        self.update_json(
            "constitutional-design/FOUNDATIONAL_QUESTIONS.yaml",
            lambda record: record["questions"][3].update(status="RESOLVED"),
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
        record["requirement_id"] = "CR-021"
        (
            self.root
            / "constitutional-design"
            / "requirements"
            / "CR-021.yaml"
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
            / "CDR-004.yaml"
        )
        record = {
            "decision_id": "CDR-004",
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
