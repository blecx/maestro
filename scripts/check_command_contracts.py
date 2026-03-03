#!/usr/bin/env python3
"""Validate speckit/blecs command-domain contracts and namespace boundaries."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agents.validation_profiles import validate_contract_markers, validate_namespace_collision


def _command_files() -> list[Path]:
    paths = []
    for namespace in ("speckit", "blecs"):
        base = ROOT / ".github" / "agents" / namespace
        if not base.exists():
            continue
        for file in sorted(base.glob("*.md")):
            if file.name.lower() == "readme.md":
                continue
            paths.append(file)
    return paths


def _command_id(path: Path) -> str:
    return path.stem


def main() -> int:
    files = _command_files()
    if not files:
        print("❌ No command contract files found under .github/agents/{speckit,blecs}")
        return 1

    command_ids = [_command_id(file) for file in files]
    errors: list[str] = []

    errors.extend(validate_namespace_collision(command_ids))

    for file in files:
        content = file.read_text(encoding="utf-8")
        missing = validate_contract_markers(content)
        if missing:
            rel = file.relative_to(ROOT)
            errors.append(f"{rel}: missing required markers: {', '.join(missing)}")

    if errors:
        print("❌ Command contract validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"✅ Command contract validation passed ({len(files)} command files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())