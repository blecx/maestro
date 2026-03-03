#!/usr/bin/env python3
"""Validate /continue-backend and /continue-phase-3 cap policy mechanics.

Enforces:
- default max issues is 25
- cap is 25
- values below 25 are forbidden
- values above baseline require explicit override confirmation
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND_LOOP_SCRIPT = ROOT / "scripts" / "continue-backend.sh"
PHASE3_LOOP_SCRIPT = ROOT / "scripts" / "continue-phase-3.sh"
PROMPT_FILE = ROOT / ".github" / "prompts" / "agents" / "continue-backend.md"
MODULE_FILE = ROOT / ".github" / "prompts" / "modules" / "continue-backend-workflow.md"


def _must_contain(path: Path, snippet: str, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    if snippet not in text:
        errors.append(f"{path}: missing required snippet: {snippet}")


def _check_loop_file(path: Path, errors: list[str]) -> None:
    if not path.exists():
        errors.append(f"Missing loop script: {path}")
        return

    _must_contain(path, "MAX_ISSUES=25", errors)
    _must_contain(path, "MAX_ISSUES_CAP=25", errors)
    _must_contain(path, 'if [[ "$MAX_ISSUES" -lt "$MAX_ISSUES_CAP" ]]', errors)
    _must_contain(path, 'if [[ "$MAX_ISSUES" -gt "$MAX_ISSUES_CAP" ]]', errors)
    _must_contain(path, "Override baseline and continue", errors)


def main() -> int:
    errors: list[str] = []

    _check_loop_file(BACKEND_LOOP_SCRIPT, errors)
    _check_loop_file(PHASE3_LOOP_SCRIPT, errors)

    if PROMPT_FILE.exists():
        _must_contain(PROMPT_FILE, "Default run limit is `25` issues", errors)

    if MODULE_FILE.exists():
        _must_contain(MODULE_FILE, "Default `max-issues` per run is `25`", errors)

    if errors:
        print("❌ continue-backend policy check failed")
        for err in errors:
            print(f"- {err}")
        return 1

    print("✅ continue-backend policy check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
