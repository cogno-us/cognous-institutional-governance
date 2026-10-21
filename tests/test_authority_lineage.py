"""Scoped qualification for authority-lineage evidence profile 0.1.0."""
import copy, importlib.util, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "testing" / "harness"))

@unittest.skipUnless(importlib.util.find_spec("jsonschema"), "install testing/harness/requirements-authority-lineage.txt")
class AuthorityLineageTests(unittest.TestCase):
    def test_schema_and_semantic_oracles(self):
        from run_authority_lineage import execute
        result=execute()
        self.assertEqual(result["case_count"],10)
        for row in result["results"]:
            with self.subTest(case=row["id"]):
                self.assertTrue(row["oracle_satisfied"],row)

    def test_profile_is_non_authorizing_by_construction(self):
        from run_authority_lineage import fixture_bundle
        bundle=fixture_bundle()
        self.assertFalse(bundle["portability"]["transfers_permission"])
        for section in ("origins","delegations","mutations","successions","resolution_commitments","use_links"):
            for record in bundle[section]: self.assertTrue(record["non_authorizing"])
        self.assertFalse(bundle["use_links"][0]["transfers_permission"])

    def test_non_finite_parent_or_child_amount_is_rejected(self):
        from run_authority_lineage import fixture_bundle, semantic_errors, validate
        for label,value in (("nan",float("nan")),("+inf",float("inf")),("-inf",float("-inf"))):
            for side,path in (("parent",("origins",)),("child",("delegations",))):
                with self.subTest(side=side,value=label):
                    bundle=fixture_bundle()
                    bundle[path[0]][0]["permission_scope"]["max_amount"]=value
                    self.assertIn("delegation amount is not finite",semantic_errors(bundle))
                    self.assertTrue(validate(bundle))

    def test_schema_errors_short_circuit_semantics(self):
        import run_authority_lineage as lineage
        bundle=lineage.fixture_bundle(); del bundle["delegations"]
        original=lineage.semantic_errors
        lineage.semantic_errors=lambda b:self.fail("semantics ran after schema errors")
        try: errors=lineage.validate(bundle)
        finally: lineage.semantic_errors=original
        self.assertTrue(errors)

    def test_malformed_input_returns_errors_not_exceptions(self):
        from run_authority_lineage import fixture_bundle, semantic_errors, validate
        missing=fixture_bundle(); del missing["successions"]
        bad_time=fixture_bundle(); bad_time["resolution_commitments"][0]["resolution_time"]="not-a-timestamp"
        naive=fixture_bundle(); naive["use_links"][0]["used_at"]="2026-10-03T00:00:01"
        wrong_container=fixture_bundle(); wrong_container["mutations"]=[None]
        for name,bundle in (("missing_section",missing),("bad_timestamp",bad_time),("naive_vs_aware",naive),("wrong_container",wrong_container)):
            with self.subTest(case=name):
                errors=semantic_errors(bundle)
                self.assertTrue(errors)
                self.assertTrue(all(isinstance(e,str) for e in errors))
                self.assertTrue(validate(bundle))
        self.assertIn("malformed lineage input: KeyError: 'successions'",semantic_errors(missing))
        self.assertTrue(any(e.startswith("malformed lineage input: TypeError") for e in semantic_errors(naive)))


# Validity dates (origin effective_at, delegation valid_from/expires_at)
AGENT = "urn:cognous:authority:refund-agent"


def two_level(bundle):
    """Add a second delegation (agent -> sub-agent) under the base delegation."""
    from run_authority_lineage import _scope
    edge = copy.deepcopy(bundle["delegations"][0])
    edge.update(delegation_id="urn:cognous:delegation:edge-2", parent_authority_id=AGENT,
                child_authority_id="urn:cognous:authority:refund-subagent", delegated_at="2026-10-03T00:00:00Z",
                valid_from="2026-10-03T00:00:00Z", expires_at="2026-10-20T00:00:00Z",
                permission_scope=_scope(["refund"], ["urn:cognous:acct:customer-7"], ["billing"], 50, "USD", 1))
    edge["source_evidence_refs"] = ["urn:cognous:evidence:delegation-2"]
    bundle["delegations"].append(edge)
    bundle["delegations"][0].update(may_redelegate=True, remaining_depth=1)
    return edge


@unittest.skipUnless(importlib.util.find_spec("jsonschema"), "install testing/harness/requirements-authority-lineage.txt")
class AuthorityLineageValidityTests(unittest.TestCase):
    def bundle(self):
        from run_authority_lineage import fixture_bundle
        return fixture_bundle()

    def validate(self, bundle):
        from run_authority_lineage import validate
        return validate(bundle)

    def test_valid_controls_still_pass(self):
        b = self.bundle()
        self.assertEqual(self.validate(b), [])
        nested = self.bundle(); two_level(nested)
        self.assertEqual(self.validate(nested), [])
        open_ended = self.bundle(); open_ended["delegations"][0]["expires_at"] = None
        self.assertEqual(self.validate(open_ended), [])

    def test_referenced_use_after_delegation_expiry_is_refused(self):
        b = self.bundle(); b["delegations"][0]["expires_at"] = "2026-10-03T00:00:02Z"
        self.assertEqual(self.validate(b), [])
        b["delegations"][0]["expires_at"] = "2026-10-03T00:00:01Z"  # the end instant itself is outside the window
        self.assertIn("use link references authority outside its delegation validity window", self.validate(b))

    def test_referenced_use_before_delegation_start_is_refused(self):
        b = self.bundle(); b["delegations"][0].update(delegated_at="2026-10-02T00:00:00Z", valid_from="2026-10-03T00:00:02Z")
        self.assertIn("use link references authority outside its delegation validity window", self.validate(b))

    def test_held_use_after_expiry_keeps_the_negative_fact(self):
        b = self.bundle(); b["delegations"][0]["expires_at"] = "2026-10-03T00:00:00.500000Z"
        b["use_links"][0]["use_disposition"] = "held"
        self.assertEqual(self.validate(b), [])
        b["use_links"][0]["use_disposition"] = "rejected"
        self.assertEqual(self.validate(b), [])

    def test_active_resolution_outside_the_window_is_refused(self):
        b = self.bundle(); b["delegations"][0]["expires_at"] = "2026-10-02T12:00:00Z"
        self.assertIn("resolution status active outside delegation validity window", self.validate(b))
        early = self.bundle(); early["resolution_commitments"][0]["resolution_time"] = "2026-10-01T12:00:00Z"
        early["use_links"][0]["used_at"] = "2026-10-01T12:00:01Z"
        self.assertIn("resolution status active outside delegation validity window", self.validate(early))

    def test_resolution_before_origin_effective_time_is_refused(self):
        b = self.bundle(); b["origins"][0].update(effective_at="2026-10-04T00:00:00Z", recorded_at="2026-10-04T00:00:00Z")
        self.assertIn("resolution status active outside delegation validity window", self.validate(b))

    def test_delegation_window_must_be_ordered_and_inside_its_parent(self):
        inverted = self.bundle(); inverted["delegations"][0].update(valid_from="2026-11-02T00:00:00Z")
        self.assertIn("delegation validity window is empty or inverted", self.validate(inverted))
        late = self.bundle(); edge = two_level(late); edge["expires_at"] = "2026-12-01T00:00:00Z"
        self.assertIn("delegation validity extends beyond its parent", self.validate(late))
        early = self.bundle(); edge = two_level(early); edge.update(delegated_at="2026-10-01T12:00:00Z", valid_from="2026-10-01T12:00:00Z")
        self.assertIn("delegation validity extends beyond its parent", self.validate(early))
        unbounded = self.bundle(); edge = two_level(unbounded); edge["expires_at"] = None
        self.assertIn("delegation validity extends beyond its parent", self.validate(unbounded))

    def test_nested_use_is_bounded_by_every_edge_on_the_chain(self):
        b = self.bundle(); edge = two_level(b)
        b["delegations"][0]["expires_at"] = "2026-10-03T12:00:00Z"
        edge["expires_at"] = "2026-10-03T12:00:00Z"
        b["resolution_commitments"][0].update(authority_id=edge["child_authority_id"], resolution_time="2026-10-04T00:00:00Z")
        b["use_links"][0].update(authority_id=edge["child_authority_id"], used_at="2026-10-04T00:00:01Z")
        errors = self.validate(b)
        self.assertIn("use link references authority outside its delegation validity window", errors)

    def test_malformed_dates_return_errors_not_exceptions(self):
        b = self.bundle(); b["delegations"][0]["expires_at"] = "2026-10-03T00:00:00"
        errors = self.validate(b)
        self.assertTrue(errors)
        self.assertTrue(all(isinstance(e, str) for e in errors))


@unittest.skipUnless(importlib.util.find_spec("jsonschema"), "install testing/harness/requirements-authority-lineage.txt")
class AuthorityLineageRestrictionTests(unittest.TestCase):
    """Redelegation limits of a delegation edge and the one-origin-per-authority rule (static scan findings IG-S01, IG-S02)."""

    SUB = "urn:cognous:authority:refund-subagent"
    NO_REDELEGATION = "parent delegation does not permit redelegation"
    DEPTH = "delegation depth does not decrease below its parent"
    CONFLICT = "conflicting origins for one authority"

    def bundle(self):
        from run_authority_lineage import fixture_bundle
        return fixture_bundle()

    def validate(self, bundle):
        from run_authority_lineage import validate
        return validate(bundle)

    def third_level(self, bundle, parent_depth, middle_depth, may_middle=True):
        """Chain root -> agent -> sub-agent -> leaf with the stated remaining depths on the first two edges."""
        from run_authority_lineage import _scope
        two_level(bundle)
        bundle["delegations"][0].update(may_redelegate=parent_depth > 0, remaining_depth=parent_depth)
        bundle["delegations"][1].update(may_redelegate=may_middle, remaining_depth=middle_depth)
        leaf = copy.deepcopy(bundle["delegations"][1])
        leaf.update(delegation_id="urn:cognous:delegation:edge-3", parent_authority_id=self.SUB,
                    child_authority_id="urn:cognous:authority:refund-leaf", valid_from="2026-10-03T00:00:00Z",
                    expires_at="2026-10-19T00:00:00Z", may_redelegate=False, remaining_depth=0,
                    permission_scope=_scope(["refund"], ["urn:cognous:acct:customer-7"], ["billing"], 20, "USD", 1))
        leaf["source_evidence_refs"] = ["urn:cognous:evidence:delegation-3"]
        bundle["delegations"].append(leaf)
        return leaf

    def test_valid_controls_still_pass(self):
        nested = self.bundle(); two_level(nested)
        self.assertEqual(self.validate(nested), [])
        chain = self.bundle(); self.third_level(chain, parent_depth=2, middle_depth=1)
        self.assertEqual(self.validate(chain), [])
        other = self.bundle()
        origin = copy.deepcopy(other["origins"][0])
        origin.update(origin_id="urn:cognous:authority-origin:root-2", authority_id="urn:cognous:authority:other-manager")
        other["origins"].append(origin)
        self.assertEqual(self.validate(other), [])

    def test_redelegation_under_a_parent_edge_that_forbids_it_is_refused(self):
        b = self.bundle(); two_level(b)
        b["delegations"][0].update(may_redelegate=False, remaining_depth=0)
        self.assertIn(self.NO_REDELEGATION, self.validate(b))

    def test_redelegation_with_no_depth_left_is_refused(self):
        b = self.bundle(); two_level(b)
        b["delegations"][0].update(may_redelegate=True, remaining_depth=0)
        self.assertIn(self.NO_REDELEGATION, self.validate(b))
        flag = self.bundle(); two_level(flag)
        flag["delegations"][0].update(may_redelegate=False, remaining_depth=1)
        self.assertIn(self.NO_REDELEGATION, self.validate(flag))

    def test_depth_must_decrease_strictly_along_the_chain(self):
        same = self.bundle(); two_level(same)
        same["delegations"][1].update(may_redelegate=True, remaining_depth=1)
        self.assertIn(self.DEPTH, self.validate(same))
        more = self.bundle(); two_level(more)
        more["delegations"][1].update(may_redelegate=True, remaining_depth=5)
        self.assertIn(self.DEPTH, self.validate(more))

    def test_third_level_obeys_the_middle_edge(self):
        b = self.bundle(); self.third_level(b, parent_depth=2, middle_depth=0, may_middle=False)
        self.assertIn(self.NO_REDELEGATION, self.validate(b))
        deep = self.bundle(); self.third_level(deep, parent_depth=1, middle_depth=1)
        self.assertIn(self.DEPTH, self.validate(deep))

    def test_conflicting_origins_for_one_authority_are_refused(self):
        b = self.bundle()
        second = copy.deepcopy(b["origins"][0])
        second.update(origin_id="urn:cognous:authority-origin:root-2", effective_at="2026-10-20T00:00:00Z",
                      recorded_at="2026-10-20T00:01:00Z")
        second["permission_scope"]["max_amount"] = 500
        b["origins"][0]["permission_scope"]["max_amount"] = 0
        b["origins"].append(second)
        self.assertIn(self.CONFLICT, self.validate(b))
        same_revision = self.bundle()
        dup = copy.deepcopy(same_revision["origins"][0]); dup["origin_id"] = "urn:cognous:authority-origin:root-3"
        same_revision["origins"].append(dup)
        self.assertIn(self.CONFLICT, self.validate(same_revision))
        other_revision = self.bundle()
        dup = copy.deepcopy(other_revision["origins"][0])
        dup.update(origin_id="urn:cognous:authority-origin:root-4", authority_revision="r2")
        other_revision["origins"].append(dup)
        self.assertIn(self.CONFLICT, self.validate(other_revision))


if __name__=="__main__": unittest.main()
