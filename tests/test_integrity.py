import hashlib
import json
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_STATUS_PATH = ROOT / "PACKAGE_STATUS.json"
CASES_DIR = ROOT / "cases"
SHA256SUMS_PATH = ROOT / "SHA256SUMS"
CONTRACTS_DIR = ROOT / "contracts"

REQUIRED_CASE_FIELDS = [
    "project",
    "schema_version",
    "case_id",
    "visibility",
    "specialty",
    "language_context",
    "local_implementation_context",
    "care_setting",
    "acuity_band",
    "task",
    "case_input",
    "safety_boundary",
    "synthetic_provenance",
]


def _load_json(path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _case_json_files():
    return sorted(CASES_DIR.rglob("*.json"))


class TestTurKMedBenchIntegrity(unittest.TestCase):
    def test_package_status(self):
        self.assertTrue(
            PACKAGE_STATUS_PATH.is_file(),
            f"Missing package status file: {PACKAGE_STATUS_PATH}",
        )

        status = _load_json(PACKAGE_STATUS_PATH)
        self.assertIsInstance(status, dict)

        self.assertEqual(status.get("case_count"), 808)
        self.assertEqual(status.get("specialty_count"), 21)
        self.assertIs(status.get("synthetic_cases_only"), True)
        self.assertIs(status.get("patient_level_data_present"), False)

    def test_case_counts_and_specialties(self):
        self.assertTrue(CASES_DIR.is_dir(), f"Missing cases directory: {CASES_DIR}")

        case_files = _case_json_files()
        self.assertEqual(len(case_files), 808)

        specialties = set()
        for case_path in case_files:
            with self.subTest(path=str(case_path)):
                try:
                    case = _load_json(case_path)
                except (json.JSONDecodeError, OSError) as exc:
                    self.fail(f"Invalid JSON in {case_path}: {exc}")

                self.assertIsInstance(case, dict)

                specialty = case.get("specialty")
                self.assertIsInstance(specialty, str)
                self.assertTrue(specialty)
                specialties.add(specialty)

        self.assertEqual(len(specialties), 21)

    def test_case_contract_required_fields(self):
        self.assertTrue(CASES_DIR.is_dir(), f"Missing cases directory: {CASES_DIR}")

        for case_path in _case_json_files():
            with self.subTest(path=str(case_path)):
                try:
                    case = _load_json(case_path)
                except (json.JSONDecodeError, OSError) as exc:
                    self.fail(f"Invalid JSON in {case_path}: {exc}")

                self.assertIsInstance(case, dict)

                self.assertEqual(case.get("project"), "TurKMedBench")
                self.assertEqual(case.get("schema_version"), "public_case_input.v1")
                self.assertEqual(case.get("visibility"), "public_model_input")

                missing = [
                    field for field in REQUIRED_CASE_FIELDS if field not in case
                ]
                self.assertEqual(
                    missing,
                    [],
                    f"Missing required fields in {case_path}: {missing}",
                )

    def test_sha256sums_all_files(self):
        self.assertTrue(
            SHA256SUMS_PATH.is_file(),
            f"Missing SHA256SUMS file: {SHA256SUMS_PATH}",
        )

        entries = []
        text = SHA256SUMS_PATH.read_text(encoding="utf-8")

        for line_number, raw_line in enumerate(text.splitlines(), start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            parts = line.split(None, 1)
            if len(parts) != 2:
                self.fail(f"Malformed SHA256SUMS line {line_number}: {raw_line!r}")

            expected_hash, rel_path = parts
            expected_hash = expected_hash.lower()

            if rel_path.startswith("*"):
                rel_path = rel_path[1:]

            entries.append((line_number, expected_hash, rel_path))

        self.assertEqual(
            len(entries),
            816,
            f"Expected 816 SHA256SUMS entries, found {len(entries)}",
        )

        for line_number, expected_hash, rel_path in entries:
            with self.subTest(line=line_number, path=rel_path):
                file_path = ROOT / rel_path
                self.assertTrue(
                    file_path.is_file(),
                    f"File listed in SHA256SUMS does not exist: {rel_path}",
                )

                normalized = file_path.read_bytes().replace(b"\r\n", b"\n")
                actual_hash = hashlib.sha256(normalized).hexdigest()

                self.assertEqual(
                    actual_hash,
                    expected_hash,
                    f"SHA256 mismatch for {rel_path} (SHA256SUMS line {line_number})",
                )

    def test_contracts_presence(self):
        self.assertTrue(
            CONTRACTS_DIR.is_dir(),
            f"Missing contracts directory: {CONTRACTS_DIR}",
        )

        contract_paths = [
            CONTRACTS_DIR / "turkmedbench_local_implementation_policy_v1.json",
            CONTRACTS_DIR / "turkmedbench_public_case_input_schema_v1.json",
        ]

        for contract_path in contract_paths:
            with self.subTest(path=str(contract_path)):
                self.assertTrue(
                    contract_path.is_file(),
                    f"Missing contract file: {contract_path}",
                )

                try:
                    _load_json(contract_path)
                except (json.JSONDecodeError, OSError) as exc:
                    self.fail(f"Invalid JSON in {contract_path}: {exc}")


if __name__ == "__main__":
    unittest.main()
