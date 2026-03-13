#!/usr/bin/env python3
"""Validate VS Code workspace settings against canonical .copilot config.

Checks settings drift for:
- Subagent auto-approvals (based on profiles)
- Terminal auto-approvals
- Custom agent defaults
- General MCP settings

Separates validation into:
- Registry checks
- Policy checks
- Profile-specific checks
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
AGENTS_DIR = ROOT / ".github" / "agents"
AGENT_SETTINGS_PATH = ROOT / ".copilot" / "config" / "vscode-agent-settings.json"
APPROVAL_PROFILES_PATH = ROOT / ".copilot" / "config" / "vscode-approval-profiles.json"

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

def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    raw = path.read_text(encoding="utf-8")
    return json.loads(_strip_jsonc(raw))

def _available_subagent_names() -> set[str]:
    return {path.name.removesuffix(".md") for path in AGENTS_DIR.glob("*.md") if path.name not in ["README.md", "AUTOMATIONS.md", "agents-catalog-maintainer.md", "operator-criteria-requirements-for-maestro.md"]}

def _get_profile_baseline(profile: str) -> dict:
    profiles = load_json(APPROVAL_PROFILES_PATH)
    if profile == "low-friction":
        base = profiles.get("trusted-workflow", {})
        add = profiles.get("low-friction", {})
        merged_sub = {**base.get("chat.tools.subagent.autoApprove", {}), **add.get("chat.tools.subagent.autoApprove", {})}
        merged_term = {**base.get("chat.tools.terminal.autoApprove", {}), **add.get("chat.tools.terminal.autoApprove", {})}
        return {
            "chat.tools.subagent.autoApprove": merged_sub,
            "chat.tools.terminal.autoApprove": merged_term
        }
    return profiles.get(profile, {})

def collect_drift(expected: Any, actual: Any, path: str = "", exact: bool = False) -> list[str]:
    """Check for missing, mismatch, and extra keys in fully managed blocks."""
    drifts: list[str] = []

    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            drifts.append(f"{path or '<root>'}: expected object, found {type(actual).__name__}")
            return drifts

        for key, value in expected.items():
            child_path = f"{path}.{key}" if path else key
            if key not in actual:
                drifts.append(f"{child_path}: missing baseline value")
                continue
            drifts.extend(collect_drift(value, actual[key], child_path, exact=exact))
            
        if exact and path: 
            for key in actual:
                if key not in expected:
                    child_path = f"{path}.{key}" if path else key
                    drifts.append(f"{child_path}: extra unauthorized key detected")
        return drifts

    if expected != actual:
        drifts.append(f"{path}: expected={expected!r} actual={actual!r} (mismatched)")
    return drifts

def run_validation(profile: str, exact: bool) -> int:
    errors = []
    warnings = []
    
    # --- 1. Registry Checks ---
    available_agents = _available_subagent_names()
    if not available_agents:
        warnings.append("No agent definitions discovered in .github/agents.")
    
    # --- 2. Policy & Profile Checks ---
    agent_settings_expected = load_json(AGENT_SETTINGS_PATH).get("workspace", {})
    profile_baseline = _get_profile_baseline(profile)
    
    # Merge them to create the complete expected baseline
    expected = copy.deepcopy(agent_settings_expected)
    if "chat.tools.subagent.autoApprove" in profile_baseline:
        expected["chat.tools.subagent.autoApprove"] = profile_baseline["chat.tools.subagent.autoApprove"]
    if "chat.tools.terminal.autoApprove" in profile_baseline:
        expected["chat.tools.terminal.autoApprove"] = profile_baseline["chat.tools.terminal.autoApprove"]
        
    # Validation against actual settings
    for settings_meta in SETTINGS_FILES:
        settings_path = settings_meta["path"]
        required = settings_meta["required"]

        if not settings_path.exists():
            if required:
                errors.append(f"Missing settings file: {settings_path}")
            continue

        actual = load_json(settings_path)
        
        # Drift check
        drifts = collect_drift(expected, actual, exact=exact)
        for d in drifts:
            errors.append(f"[{settings_path.name}] {d}")
            
        # Specific subagent registry verification
        actual_subagents = actual.get("chat.tools.subagent.autoApprove", {})
        if isinstance(actual_subagents, dict):
            for agent_name, is_approved in actual_subagents.items():
                if is_approved and agent_name not in available_agents:
                    errors.append(f"[{settings_path.name}] Unknown auto-approved agent (registry check failed): {agent_name}")
                    
        # Check custom agent defaults
        custom_agent = actual.get("issueagent.customAgent")
        if custom_agent and custom_agent not in available_agents:
            errors.append(f"[{settings_path.name}] customAgent refers to unknown agent: {custom_agent}")
            
        # Optional Agents: We do NOT force them. If they exist in available_agents but we didn't require them, that's fine.
        # They aren't treated as required defaults.

    if warnings:
        print("⚠️ Warnings:")
        for w in warnings:
            print(f"  - {w}")

    if errors:
        print(f"❌ Workspace settings validation failed (Profile: {profile}, Exact: {exact})")
        for err in errors[:30]:
            print(f"  - {err}")
        if len(errors) > 30:
            print(f"  - ... and {len(errors) - 30} more")
        return 1

    print(f"✅ Workspace settings validation passed (Profile: {profile}, Exact: {exact})")
    return 0

def main() -> int:
    parser = argparse.ArgumentParser(description="Validate VS Code workspace settings against canonical .copilot config.")
    parser.add_argument("--profile", choices=["safe", "trusted-workflow", "low-friction"], default="trusted-workflow", help="Validation profile to use.")
    parser.add_argument("--exact", action="store_true", help="Enforce exact profile equality (no extra custom overrides permitted).")
    args = parser.parse_args()
    return run_validation(args.profile, args.exact)

if __name__ == "__main__":
    sys.exit(main())
