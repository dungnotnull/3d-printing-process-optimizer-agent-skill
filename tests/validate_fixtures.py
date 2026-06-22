# -*- coding: utf-8 -*-
"""Validate all scenario fixtures are well-formed JSON.

Run with: python tests/validate_fixtures.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIXTURES = ROOT / "fixtures"

REQUIRED_SUFFIXES = ["-frame.json", "-score.json", "-diagnosis.json", "-roadmap.json"]


def validate() -> int:
    if not FIXTURES.exists():
        print(f"Fixtures directory not found: {FIXTURES}")
        return 1
    files = sorted(FIXTURES.glob("scenario-*.json"))
    if not files:
        print("No scenario fixtures found.")
        return 1
    errors: list[str] = []
    valid_count = 0
    for path in files:
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
            if not isinstance(data, dict):
                errors.append(f"{path.name}: top-level value must be an object")
                continue
            if "status" not in data:
                errors.append(f"{path.name}: missing 'status' field")
                continue
            valid_count += 1
        except json.JSONDecodeError as e:
            errors.append(f"{path.name}: invalid JSON - {e}")
    # Check each scenario has all four artifacts
    scenario_ids = {p.stem.rsplit("-", 1)[0] for p in files}
    for sid in scenario_ids:
        for suffix in REQUIRED_SUFFIXES:
            if not (FIXTURES / f"{sid}{suffix}").exists():
                errors.append(f"{sid}: missing {suffix} fixture")
    if errors:
        print("VALIDATION FAILED")
        for err in errors:
            print(f"  - {err}")
        return 1
    print(f"All {valid_count} fixtures are valid JSON and every scenario has complete artifacts.")
    return 0


if __name__ == "__main__":
    sys.exit(validate())
