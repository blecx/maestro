#!/usr/bin/env python3
"""Validate VS Code subagent auto-approve settings against .github/agents.

Checks the primary workspace settings file and, when present, the external
client workspace settings file:
- .vscode/settings.json (required)
- _external/AI-Agent-Framework-Client/.vscode/settings.json (optional)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENTS_DIR = ROOT / ".github" / "agents"
APPROVAL_PROFILES = ROOT / ".copilot" / "config" / "vscode-approval-profiles.json"

SETTINGS_FILES = [
    {"path": ROOT / ".vscode" / "settings.json", "required": True},
    {
        "path": ROOT / "_external" / "AI-Agent-Framework-Client" / ".vscode" / "settings.json",
        "required": False,
    },
]

def _strip_jsonc(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"^\s*//.*$", "", text, flags=re.M)
    return text

def _load_jsonc(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    return json.loads(_strip_jsonc(raw))

def _available_subagent_names() -> set[str]:
    return {path.name.removesuffix(".md") for path in AGENTS_DIR.glob("*.md") if path.name not in ["README.md", "AUTOMATIONS.md", "agents-catalog-maintainer.md"]}

def _get_canonical_approvals(profile: str) -> set[str]:
    if not APPROVAL_PROFILES.exists():
        return set()
    profiles = _load_jsonc(APPROVAL_PROFILES)
    if profile == "low-friction":
        base = profiles.get("trusted-workflow", {}).get("chat.tools.subagent.autoApprove", {})
        add = profiles.get(profile, {}).get("chat.tools.subagent.autoApprove", {})
        return {k for k, v in {**base, **add}.items() if v is True}
    else:
        prof = profiles.get(profile, {})
        return _approved_names({"chat.tools.subagent.autoApprove": prof.get("chat.tools.subagent.autoApprove", {})})

def _approved_names(settings: dict) -> set[str]:
    block = settings.get("chat.tools.subagent.autoApprove", {})
    if not isinstance(block, dict):
        return set()
    return {key for key, value in block.items() if value is True}

def run_validation(profile: str) -> int:
    available = _available_subagent_names()
    required_baseline = _get_canonical_approvals(profile)
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
            continue

        settings = _load_jsonc(settings_path)
        approved = _approved_names(settings)

        unknown = sorted(approved - available)
        if unknown:
            message = f"{settings_path}: unknown auto-approved agents (registry validation failed): {', '.join(unknown)}"
            if required:
                errors.append(message)

        missing_baseline = sorted(required_baseline - approved)
        if missing_baseline:
            message = (f"{settings_path}: missing required baseline auto-approvals for '{profile}' profile: "
                       f"{', '.join(missing_baseline)}")
            if required:
                errors.append(message)

        # Allow extra explicitly for low-friction, but for safe/trusted, maybe we restrict?
        # The review said: "Validators still behave like previous model is authoritative".
        # Let's enforce that approved MUST equal required_baseline exactly, no extras?
        extra = sorted(approved - required_baseline)
        if extra and profile != "low-friction":
            message = f"{settings_path}: unauthorized auto-approved agents for '{profile}' profile: {', '.join(extra)}"
            if required:
                errors.append(message)

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
    parser.add_argument("--profile", choices=["safe", "trusted-workflow", "low-friction"], default="trusted-workflow", help="Validation profile to use.")
    args = parser.parse_args()
    return run_validation(args.profile)

if __name__ == "__main__":
    sys.exit(main())
