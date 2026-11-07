"""G2 DEVELOPMENT-ONLY functional checks: IG root lineage -> pinned Control Plane Resolver (three frozen oracles).

Synthetic, decision-only, builder-lineage; not independent qualification. Requires G2_CP_ROOT (a clean checkout of
cogno-us/cognous-control-plane at the pinned commit and its dependencies, notably pydantic). G2_REQUIRE=1 turns a
missing environment into a failure (a skip is not a pass). G2_EVIDENCE_DIR optionally retains the raw results.
"""
import json
import os
import sys
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
G2 = ROOT / "process" / "implementation" / "g2-cp-resolver-dev"
sys.path.insert(0, str(G2))

try:
    import jsonschema  # noqa: F401
    HAVE_JSONSCHEMA = True
except ImportError:  # pragma: no cover
    HAVE_JSONSCHEMA = False

CP_ROOT = os.environ.get("G2_CP_ROOT")


def _environment_problem():
    if not HAVE_JSONSCHEMA:
        return "jsonschema not installed"
    if not CP_ROOT or not Path(CP_ROOT).is_dir():
        return "G2_CP_ROOT not set"
    return None


@unittest.skipIf(_environment_problem() is not None and os.environ.get("G2_REQUIRE") != "1", _environment_problem() or "")
class G2RootLineageToControlPlane(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        problem = _environment_problem()
        if problem:
            raise AssertionError("G2_REQUIRE=1 but " + problem)
        import g2_driver  # noqa: PLC0415
        cls.d = g2_driver
        cls.tmp = tempfile.TemporaryDirectory()

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_case(self, name, bundle, **kw):
        result = self.d.run_case(CP_ROOT, bundle, Path(self.tmp.name) / name, **kw)
        out = os.environ.get("G2_EVIDENCE_DIR")
        if out:
            Path(out).mkdir(parents=True, exist_ok=True)
            (Path(out) / f"{name}.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
        print(name, result["result"], result["reasons"])
        return result

    def test_1_valid_root_is_authorized_by_cp_in_synthetic_developer_mode(self):
        r = self.run_case("check1_valid_root", "root_lineage.json")
        self.assertEqual(r["result"], "authorized", r["reasons"])
        self.assertEqual(r["reasons"], [])
        self.assertEqual(r["reason_vocabulary_version"], "runtime-authority-reasons/0.1")
        self.assertIs(r["resolver_authenticated"], False)
        self.assertEqual(r["destination_effects"], {})
        self.assertFalse(r["executed"])
        self.assertIn("SYNTHETIC", r["label"])

    def test_2_revoked_root_holds_with_native_grant_revoked(self):
        r = self.run_case("check2_revoked_root", "root_lineage_revoked.json")
        self.assertEqual(r["result"], "hold", r["reasons"])
        self.assertIn("grant_revoked", r["reasons"])  # generic grant_not_active would not satisfy this oracle
        self.assertIs(r["resolver_authenticated"], False)
        self.assertEqual(r["destination_effects"], {})

    def test_3_stale_status_holds_with_native_grant_status_stale_or_future(self):
        def stale(facts):
            at = self.d.AT - timedelta(seconds=120)
            facts["evaluation"]["status_observed_at"] = at.isoformat()
        r = self.run_case("check3_stale_status", "root_lineage.json", facts_edit=stale)
        self.assertEqual(r["result"], "hold", r["reasons"])
        self.assertIn("grant_status_stale_or_future", r["reasons"])
        self.assertIs(r["resolver_authenticated"], False)
        self.assertEqual(r["destination_effects"], {})


if __name__ == "__main__":
    unittest.main()
