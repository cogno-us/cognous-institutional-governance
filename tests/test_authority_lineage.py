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

if __name__=="__main__": unittest.main()
