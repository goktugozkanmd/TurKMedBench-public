#!/usr/bin/env python3
"""CLI runner for TurKMedBench integrity checks."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import unittest
from tests.test_integrity import TestTurKMedBenchIntegrity


def main():
    print("==> TurKMedBench Public Research Preview Integrity Check")
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestTurKMedBenchIntegrity)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if result.wasSuccessful():
        print("\n[SUCCESS] All integrity checks passed successfully.")
        return 0
    else:
        print(f"\n[FAILURE] Integrity check failed: {len(result.failures)} failures, {len(result.errors)} errors.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
