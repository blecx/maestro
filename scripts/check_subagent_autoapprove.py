#!/usr/bin/env python3
"""Validate VS Code subagent auto-approve settings against .github/agents.

Checks the primary workspace settings file and, when present, the external
client workspace settings file:
- .vscode/settings.json (required)
- _external/AI-Agent-Framework-Client/.vscode/settings.json (optional)

The `chat.tools.subagent.autoApprove` block is a *policy* (which agents are
auto-approved), not a registry of all available agents. This script validates:

- Any auto-approved names are valid (exist in `.github/agents/*.md`).
- A small baseline set is present in the primary workspace settings.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENTS_DIR = ROOT / ".github" / "agents"

SETTINGS_FILES = [
    {"path": ROOT / ".vscode" / "settings.json", "required": True},
    {
        "path": ROOT / "_external" / "AI-Agent-Framework-Client" / ".vscode" / "settings.json",
        "required": False,
    },
]

REQUIRED_BASELINE_APPROVALS = {
    "create-issue",
    "resolve-issue",
    "close-issue",
    "pr-merge",
    "Plan",
    "tutorial",
}


def _strip_jsonc(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"^\s*//.*$", "", text, flags=re.M)
    return text


def _load_jsonc(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    return json.loads(_strip_jsonc(raw))


def _available_subagent_names() -> set[str]:
    return {path.name.removesuffix(".md") for path in AGENTS_DIR.glob("*.md") if path.name not in ["README.md", "AUTOMATIONS.md", "agents-catalog-maintainer.md"]}


def _approved_names(settings: dict) -> set[str]:
    block = settings.get("chat.tools.subagent.autoApprove", {})
    if not isinstance(block, dict):
        return set()
    return {key for key, value in block.items() if value is True}


def main() -> int:
    available = _available_subagent_names()
    errors: list[str] = []

    if not available:
        print("⚠️ No agent definitions discovered in .github/agents.")
        return 1

    for settings_meta in SETTINGS_FILES:
        settings_path = settings_meta["path"]
        required = settings_meta["required"]

        if not settings_path.exists():
            if required:
                errors.append(f"Missing settings file: {settings_path}")
            else:
                print(f"ℹ️ Optional settings file not found (skipping): {settings_path}")
            continue

        settings = _load_jsonc(settings_path)
        approved = _approved_names(settings)

        unknown = sorted(approved - available)
        if unknown:
            message = f"{settings_path}: unknown auto-approved agents: {', '.join(unknown)}"
            if required:
                errors.append(message)
            else:
                print(f"ℹ️ Optional settings mismatch (allowed): {message}")

        missing_baseline = sorted(REQUIRED_BASELINE_APPROVALS - approved)
        if missing_baseline:
            message = (
                f"{settings_path}: missing required baseline auto-approvals: "
                f"{', '.join(missing_baseline)}"
            )
            if required:
                errors.append(message)
            else:
                print(f"ℹ️ Optional settings mismatch (allowed): {message}")

    if errors:
        print("❌ Subagent auto-approve consistency check failed")
        for err in errors:
            print(f"- {err}")
        return 1

    print("✅ Subagent auto-approve consistency check passed")
    print(f"Available agents: {', '.join(sorted(available))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
