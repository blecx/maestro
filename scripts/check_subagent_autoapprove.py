#!/usr/bin/env python3
"""Validate VS Code subagent auto-approve settings against .github/agents.

Checks the primary workspace settings file and, when present, the external
client workspace settings file:
- .vscode/settings.json (required)
- _external/AI-Agent-Framework-Client/.vscode/settings.json (optional)

The `chat.tools.subagent.autoApprove` block is a *policy* (which agents are
auto-approved), not a registry of all available agents. This script validates:

1. Registry Validation: Any auto-approved names are valid (exist in `.github/agents/*.md`).
2. Policy Validation: Approvals match the canonical baseline based on the selected profile.

Dry-run verification guidance:
Run this script manually or during CI to detect drift:
    ./scripts/check_subagent_autoapprove.py --profile safe
    ./scripts/check_subagent_autoapprove.py --profile trusted
    ./scripts/check_subagent_autoapprove.py --profile low-friction
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENTS_DIR = ROOT / ".github" / "agents"
CANONICAL_SETTINGS = ROOT / ".copilot" / "config" / "vscode-agent-settings.json"

SETTINGS_FILES = [
    {"path": ROOT / ".vscode" / "settings.json", "required": True},
    {
        "path": ROOT / "_external" / "AI-Agent-Framework-Client" / ".vscode" / "settings.json",
        "required": False,
    },
]

CONTINUATION_AGENTS = {"continue-backend", "continue-phase-2", "workflow"}

def _strip_jsonc(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"^\s*//.*$", "", text, flags=re.M)
    return text


def _load_jsonc(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    return json.loads(_strip_jsonc(raw))


def _available_subagent_names() -> set[str]:
    return {path.name.removesuffix(".md") for path in AGENTS_DIR.glob("*.md") if path.name not in ["README.md", "AUTOMATIONS.md", "agents-catalog-maintainer.md"]}


def _get_canonical_approvals() -> set[str]:
    if not CANONICAL_SETTINGS.exists():
        return set()
    settings = _load_jsonc(CANONICAL_SETTINGS)
    workspace = settings.get("workspace", {})
    return _approved_names(workspace)


def _approved_names(settings: dict) -> set[str]:
    block = settings.get("chat.tools.subagent.autoApprove", {})
    if not isinstance(block, dict):
        return set()
    return {key for key, value in block.items() if value is True}


def run_validation(profile: str) -> int:
    available = _available_subagent_names()
    canonical_approvals = _get_canonical_approvals()
    errors: list[str] = []

    if not available:
        print("⚠️ No agent definitions discovered in .github/agents.")
        return 1

    # Define policy rules per profile
    required_baseline = set()

    if profile == "trusted":
        # Trusted workflow: requires canonical baseline from .copilot
        required_baseline = canonical_approvals
    elif profile == "low-friction":
        # Low-friction: requires canonical baseline, but allows developers
        # to add experimental/custom agents (registry validation still applies).
        required_baseline = canonical_approvals
    elif profile == "safe":
        # Safe: requires none to be auto-approved, leaving maximum human control.
        # It only validates that any explicitly approved ones are valid in registry.
        pass

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

        # 1. Registry validation: Are the approved agents actually defined?
        unknown = sorted(approved - available)
        if unknown:
            message = f"{settings_path}: unknown auto-approved agents (registry validation failed): {', '.join(unknown)}"
            if required:
                errors.append(message)
            else:
                print(f"ℹ️ Optional settings mismatch (allowed): {message}")

        # 2. Policy validation: Is the approved set compliant with the configured profile?
        missing_baseline = sorted(required_baseline - approved)
        if missing_baseline:
            message = (
                f"{settings_path}: missing required baseline auto-approvals for '{profile}' profile: "
                f"{', '.join(missing_baseline)}"
            )
            if required:
                errors.append(message)
            else:
                print(f"ℹ️ Optional settings mismatch (allowed): {message}")
                
        # (Continuation agents are handled purely as optional across the board,
        # hence no strict requirements or failures if they are present or omitted.)

    if errors:
        print(f"❌ Subagent auto-approve consistency check failed (Profile: {profile})")
        for err in errors:
            print(f"- {err}")
        return 1

    print(f"✅ Subagent auto-approve consistency check passed (Profile: {profile})")
    print(f"Available agents: {', '.join(sorted(available))}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate VS Code subagent auto-approve settings.")
    parser.add_argument(
        "--profile",
        choices=["safe", "trusted", "low-friction"],
        default="trusted",
        help="Validation profile to use (default: trusted)."
    )
    args = parser.parse_args()
    return run_validation(args.profile)


if __name__ == "__main__":
    sys.exit(main())
