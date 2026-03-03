#!/usr/bin/env python3
"""Validate /continue-phase-2 cap policy mechanics.

Enforces:
- default max issues is 25
- cap is 25
- values above cap require explicit override confirmation
"""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
LOOP_SCRIPT = ROOT / "scripts" / "continue-phase-2.sh"
PROMPT_FILE = ROOT / ".github" / "prompts" / "agents" / "continue-phase-2.md"
MODULE_FILE = ROOT / ".github" / "prompts" / "modules" / "continue-phase-2-workflow.md"


def _must_contain(path: Path, snippet: str, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    if snippet not in text:
        errors.append(f"{path}: missing required snippet: {snippet}")


def main() -> int:
    errors: list[str] = []

    if not LOOP_SCRIPT.exists():
        errors.append(f"Missing loop script: {LOOP_SCRIPT}")
    else:
        _must_contain(LOOP_SCRIPT, "MAX_ISSUES=25", errors)
        _must_contain(LOOP_SCRIPT, "MAX_ISSUES_CAP=25", errors)
        _must_contain(LOOP_SCRIPT, 'if [[ "$MAX_ISSUES" -gt "$MAX_ISSUES_CAP" ]]', errors)
        _must_contain(LOOP_SCRIPT, "Override cap and continue? (y/N):", errors)

    if PROMPT_FILE.exists():
        _must_contain(PROMPT_FILE, "Default run limit is `25` issues", errors)

    if MODULE_FILE.exists():
        _must_contain(MODULE_FILE, "Default `max-issues` per run is `25`", errors)

    if errors:
        print("❌ continue-phase-2 policy check failed")
        for err in errors:
            print(f"- {err}")
        return 1

    print("✅ continue-phase-2 policy check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
