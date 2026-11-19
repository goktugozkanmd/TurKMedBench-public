import contextlib
import hashlib
import io
import json
import unittest
from pathlib import Path

from scripts.inspect_cases import build_summary, filter_cases, find_case, load_cases, main

ROOT = Path(__file__).resolve().parents[1]
CASES_DIR = ROOT / "cases"
MANIFEST_PATH = ROOT / "manifest" / "public_release_manifest_v1.json"
PACKAGE_STATUS_PATH = ROOT / "PACKAGE_STATUS.json"

SELF_REFERENTIAL_MANIFEST_PATHS = {
    "SHA256SUMS",
    "manifest/public_release_manifest_v1.json",
}


class TestTurKMedBenchSafetyAndManifest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case_paths = sorted(CASES_DIR.rglob("*.json"))
        cls.cases = [
            (p, json.loads(p.read_text(encoding="utf-8"))) for p in cls.case_paths
        ]
        cls.package_status = json.loads(PACKAGE_STATUS_PATH.read_text(encoding="utf-8"))

    def test_case_ids_unique_and_match_filenames(self):
        seen = set()
        for path, case in self.cases:
            cid = case["case_id"]
            self.assertEqual(path.stem, cid, f"Filename mismatch for {path.name}: {cid}")
            self.assertNotIn(cid, seen, f"Duplicate case_id: {cid}")
            seen.add(cid)
        self.assertEqual(len(seen), 808)

    def test_safety_boundary_and_tr_context_in_all_cases(self):
        for path, case in self.cases:
            with self.subTest(case_id=case["case_id"]):
                sb = case["safety_boundary"]
                self.assertIs(sb.get("clinical_use_prohibited"), True)
                self.assertIs(sb.get("human_review_required"), True)

                ci = case["case_input"]
                self.assertIs(ci.get("synthetic"), True)
                self.assertEqual(ci.get("patient_data_status"), "no_patient_level_data")

                self.assertEqual(case["language_context"].get("country_context"), "TR")
                self.assertEqual(case["local_implementation_context"].get("jurisdiction"), "TR")

    def test_no_excluded_private_keys_in_public_cases(self):
        excluded = set(self.package_status["excluded_categories"])
        for _, case in self.cases:
            overlap = excluded.intersection(case.keys())
            self.assertEqual(overlap, set(), f"Excluded private keys in {case['case_id']}: {overlap}")

    def test_public_release_manifest_matches_disk(self):
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        self.assertEqual(manifest["project"], "TurKMedBench")
        self.assertEqual(manifest["case_count"], 808)
        self.assertEqual(manifest["specialty_count"], 21)
        self.assertIs(manifest["synthetic_cases_only"], True)
        self.assertIs(manifest["patient_level_data_present"], False)
        self.assertIs(manifest["clinical_use_prohibited"], True)

        checked = 0
        for entry in manifest["files"]:
            rel = entry["path"]
            if rel in SELF_REFERENTIAL_MANIFEST_PATHS:
                continue
            fp = ROOT / rel
            self.assertTrue(fp.is_file(), f"Manifest file missing: {rel}")
            normalized = fp.read_bytes().replace(b"\r\n", b"\n")
            self.assertEqual(
                hashlib.sha256(normalized).hexdigest(),
                entry["sha256"],
                f"Manifest sha256 mismatch for {rel}",
            )
            checked += 1
        self.assertEqual(checked, 815)


class TestInspectCasesCLI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = load_cases(CASES_DIR)

    def _run_cli(self, argv):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = main(argv, cases_dir=CASES_DIR)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_summary_json_matches_universe(self):
        code, out, err = self._run_cli(["--summary", "--json"])
        self.assertEqual(code, 0, err)
        data = json.loads(out)
        self.assertEqual(data["total_cases"], 808)
        self.assertEqual(data["specialty_count"], 21)
        self.assertTrue(data["clinical_use_prohibited"])
        self.assertEqual(sum(data["specialties"].values()), 808)

    def test_default_invocation_prints_summary_text(self):
        code, out, err = self._run_cli([])
        self.assertEqual(code, 0, err)
        self.assertIn("Total cases: 808", out)
        self.assertIn("not for clinical use", out)

    def test_filter_cases_and_limit(self):
        code, out, err = self._run_cli(
            ["--specialty", "cardiology", "--acuity", "emergency", "--limit", "3", "--json"]
        )
        self.assertEqual(code, 0, err)
        payload = json.loads(out)
        self.assertGreater(payload["total_matched"], 0)
        self.assertLessEqual(payload["shown"], 3)
        for item in payload["cases"]:
            self.assertEqual(item["specialty"], "CARDIOLOGY")
            self.assertEqual(item["acuity_band"], "emergency")

    def test_show_case_valid_and_missing(self):
        code, out, err = self._run_cli(["--show", "TMB-CARD-ACS-001"])
        self.assertEqual(code, 0, err)
        self.assertIn("Case ID: TMB-CARD-ACS-001", out)
        self.assertIn("CARDIOLOGY", out)

        code2, _, err2 = self._run_cli(["--show", "TMB-DOES-NOT-EXIST-999"])
        self.assertEqual(code2, 2)
        self.assertIn("not found", err2)

    def test_invalid_filter_value_returns_usage_error(self):
        code, _, err = self._run_cli(["--specialty", "NONEXISTENT_SPEC"])
        self.assertEqual(code, 2)
        self.assertIn("Valid values:", err)

    def test_helper_functions(self):
        summary = build_summary(self.cases)
        self.assertEqual(summary["total_cases"], 808)
        subset = filter_cases(self.cases, specialty="CARDIOLOGY")
        self.assertGreater(len(subset), 0)
        found = find_case(self.cases, "tmb-card-acs-001")
        self.assertIsNotNone(found)
        self.assertEqual(found["case_id"], "TMB-CARD-ACS-001")


if __name__ == "__main__":
    unittest.main()
