"""Scoped qualification for authority-lineage evidence profile 0.1.0."""
import importlib.util, sys, unittest
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

if __name__=="__main__": unittest.main()
