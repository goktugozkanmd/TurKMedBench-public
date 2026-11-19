#!/usr/bin/env python3
"""Zero-dependency CLI to summarize, filter, and preview TurKMedBench public cases."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES_DIR = ROOT / "cases"


def load_cases(cases_dir: Path = DEFAULT_CASES_DIR) -> list[dict]:
    if not cases_dir.is_dir():
        raise FileNotFoundError(f"Cases directory not found: {cases_dir}")
    cases: list[dict] = []
    for path in sorted(cases_dir.rglob("*.json")):
        with path.open("r", encoding="utf-8") as handle:
            cases.append(json.load(handle))
    return cases


def build_summary(cases: Iterable[dict]) -> dict:
    case_list = list(cases)
    specialties = Counter(c.get("specialty", "UNKNOWN") for c in case_list)
    acuity_bands = Counter(c.get("acuity_band", "UNKNOWN") for c in case_list)
    care_settings = Counter(c.get("care_setting", "UNKNOWN") for c in case_list)
    task_types = Counter((c.get("task") or {}).get("task_type", "UNKNOWN") for c in case_list)
    return {
        "project": "TurKMedBench",
        "package_type": "public_research_preview",
        "clinical_use_prohibited": True,
        "synthetic_cases_only": True,
        "total_cases": len(case_list),
        "specialty_count": len(specialties),
        "specialties": dict(sorted(specialties.items(), key=lambda kv: (-kv[1], kv[0]))),
        "acuity_bands": dict(sorted(acuity_bands.items(), key=lambda kv: (-kv[1], kv[0]))),
        "care_settings": dict(sorted(care_settings.items(), key=lambda kv: (-kv[1], kv[0]))),
        "task_types": dict(sorted(task_types.items(), key=lambda kv: (-kv[1], kv[0]))),
    }


def filter_cases(
    cases: Iterable[dict],
    *,
    specialty: str | None = None,
    acuity: str | None = None,
    care_setting: str | None = None,
    task_type: str | None = None,
) -> list[dict]:
    results = list(cases)
    if specialty is not None:
        target = specialty.strip().upper()
        results = [c for c in results if str(c.get("specialty", "")).upper() == target]
    if acuity is not None:
        target = acuity.strip().lower()
        results = [c for c in results if str(c.get("acuity_band", "")).lower() == target]
    if care_setting is not None:
        target = care_setting.strip().lower()
        results = [c for c in results if str(c.get("care_setting", "")).lower() == target]
    if task_type is not None:
        target = task_type.strip().lower()
        results = [
            c for c in results if str((c.get("task") or {}).get("task_type", "")).lower() == target
        ]
    return results


def find_case(cases: Iterable[dict], case_id: str) -> dict | None:
    target = case_id.strip().upper()
    for case in cases:
        if str(case.get("case_id", "")).upper() == target:
            return case
    return None


def _validate_choice(value: str | None, valid: set[str], flag: str, *, upper: bool = False) -> str | None:
    if value is None:
        return None
    normalized = value.strip().upper() if upper else value.strip().lower()
    if normalized not in valid:
        options = ", ".join(sorted(valid))
        raise ValueError(f"Unknown {flag} {value!r}. Valid values: {options}")
    return normalized


def _format_summary_text(summary: dict) -> str:
    lines = [
        "TurKMedBench Public Research Preview Summary",
        "Notice: Synthetic inputs only; not clinically validated; not for clinical use.",
        f"Total cases: {summary['total_cases']} | Specialties: {summary['specialty_count']}",
        "",
        "Specialties:",
    ]
    for name, count in summary["specialties"].items():
        lines.append(f"  {name}: {count}")
    lines.append("")
    lines.append("Acuity bands: " + ", ".join(f"{k}={v}" for k, v in summary["acuity_bands"].items()))
    lines.append("Care settings: " + ", ".join(f"{k}={v}" for k, v in summary["care_settings"].items()))
    lines.append("Task types: " + ", ".join(f"{k}={v}" for k, v in summary["task_types"].items()))
    return "\n".join(lines)


def _format_case_text(case: dict) -> str:
    task = case.get("task") or {}
    ci = case.get("case_input") or {}
    lines = [
        f"Case ID: {case.get('case_id')}",
        f"Specialty: {case.get('specialty')} ({case.get('subspecialty', '-')})",
        f"Setting: {case.get('care_setting')} | Acuity: {case.get('acuity_band')} | Task: {task.get('task_type')}",
        "Notice: Synthetic research preview input; clinical use prohibited.",
        "",
        f"Presentation: {ci.get('clinical_presentation', '')}",
        f"Question: {task.get('question', '')}",
    ]
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Summarize, filter, and preview TurKMedBench public synthetic cases."
    )
    parser.add_argument("--summary", action="store_true", help="Show dataset distribution summary.")
    parser.add_argument("--specialty", help="Filter by clinical specialty (e.g., CARDIOLOGY).")
    parser.add_argument("--acuity", help="Filter by acuity band (e.g., emergency, routine).")
    parser.add_argument("--care-setting", help="Filter by care setting (e.g., primary_care, icu).")
    parser.add_argument("--task-type", help="Filter by task type (e.g., diagnosis, referral).")
    parser.add_argument("--show", metavar="CASE_ID", help="Show a single case by case_id.")
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum filtered cases to display (0 for all; default: 20).",
    )
    parser.add_argument("--json", action="store_true", dest="as_json", help="Emit JSON output.")
    return parser


def main(argv: list[str] | None = None, *, cases_dir: Path = DEFAULT_CASES_DIR) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.limit < 0:
        print("Error: --limit must be >= 0.", file=sys.stderr)
        return 2

    try:
        cases = load_cases(cases_dir)
    except (FileNotFoundError, OSError, json.JSONDecodeError) as exc:
        print(f"Error loading cases: {exc}", file=sys.stderr)
        return 1

    if args.show:
        case = find_case(cases, args.show)
        if case is None:
            print(f"Error: Case ID {args.show!r} not found in {cases_dir}.", file=sys.stderr)
            return 2
        if args.as_json:
            print(json.dumps(case, ensure_ascii=False, indent=2))
        else:
            print(_format_case_text(case))
        return 0

    has_filters = any(
        val is not None for val in (args.specialty, args.acuity, args.care_setting, args.task_type)
    )
    if args.summary or not has_filters:
        summary = build_summary(cases)
        if args.as_json:
            print(json.dumps(summary, ensure_ascii=False, indent=2))
        else:
            print(_format_summary_text(summary))
        return 0

    try:
        valid_specs = {str(c.get("specialty", "")).upper() for c in cases}
        valid_acuity = {str(c.get("acuity_band", "")).lower() for c in cases}
        valid_settings = {str(c.get("care_setting", "")).lower() for c in cases}
        valid_tasks = {str((c.get("task") or {}).get("task_type", "")).lower() for c in cases}

        specialty = _validate_choice(args.specialty, valid_specs, "--specialty", upper=True)
        acuity = _validate_choice(args.acuity, valid_acuity, "--acuity")
        care_setting = _validate_choice(args.care_setting, valid_settings, "--care-setting")
        task_type = _validate_choice(args.task_type, valid_tasks, "--task-type")
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    matched = filter_cases(
        cases,
        specialty=specialty,
        acuity=acuity,
        care_setting=care_setting,
        task_type=task_type,
    )
    displayed = matched if args.limit == 0 else matched[: args.limit]

    if args.as_json:
        payload = {
            "total_matched": len(matched),
            "shown": len(displayed),
            "cases": [
                {
                    "case_id": c["case_id"],
                    "specialty": c["specialty"],
                    "subspecialty": c.get("subspecialty"),
                    "care_setting": c["care_setting"],
                    "acuity_band": c["acuity_band"],
                    "task_type": (c.get("task") or {}).get("task_type"),
                }
                for c in displayed
            ],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"Matched {len(matched)} cases (showing {len(displayed)}):")
        for c in displayed:
            t_type = (c.get("task") or {}).get("task_type", "-")
            print(
                f"  {c['case_id']} | {c['specialty']} | {c['care_setting']} | {c['acuity_band']} | {t_type}"
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
