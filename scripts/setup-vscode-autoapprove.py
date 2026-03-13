#!/usr/bin/env python3
"""
Setup VS Code auto-approve settings for Copilot agents.

This script automatically configures auto-approve settings in:
1. Global VS Code user settings (~/.config/Code/User/settings.json)
2. Backend workspace (.vscode/settings.json)
3. Client workspace (../AI-Agent-Framework-Client/.vscode/settings.json)

Run this script to enable auto-approve for all Copilot agent commands
without manual copy-paste.
"""

import argparse
import json
import os
import sys
import copy
from pathlib import Path
from typing import Dict, Any


CONFIG_PATH = Path(__file__).parent.parent / ".copilot/config/vscode-approval-profiles.json"

def load_profile_config() -> Dict[str, Any]:
    """Load canonical approval profiles from .copilot config."""
    with open(CONFIG_PATH, "r", encoding="utf-8") as handle:
        return json.load(handle)

PROFILE_CONFIG = load_profile_config()

def get_vscode_settings_path() -> Path:
    """Get the VS Code user settings path based on OS."""
    if sys.platform == "linux":
        return Path.home() / ".config/Code/User/settings.json"
    elif sys.platform == "darwin":
        return Path.home() / "Library/Application Support/Code/User/settings.json"
    elif sys.platform == "win32":
        return Path(os.environ.get("APPDATA", "")) / "Code/User/settings.json"
    else:
        raise OSError(f"Unsupported platform: {sys.platform}")

def read_json_file(path: Path, *, allow_repair: bool = True) -> Dict[str, Any]:
    """Read JSON file, handling comments and missing files."""
    if not path.exists():
        return {}
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = []
            for line in content.split('\n'):
                if '//' in line:
                    in_string = False
                    cleaned = []
                    i = 0
                    while i < len(line):
                        if line[i] == '"' and (i == 0 or line[i-1] != '\\'):
                            in_string = not in_string
                        if not in_string and i < len(line) - 1 and line[i:i+2] == '//':
                            break
                        cleaned.append(line[i])
                        i += 1
                    line = ''.join(cleaned)
                lines.append(line)
            content = '\n'.join(lines)
            return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"⚠️  Warning: Could not parse {path}: {e}")
        if not allow_repair:
            return {}
        print(f"   Creating backup and starting fresh...")
        backup_path = path.with_suffix('.json.backup')
        path.rename(backup_path)
        return {}

def write_json_file(path: Path, data: Dict[str, Any]) -> None:
    """Write JSON file with nice formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        f.write('\n')

def get_expected_settings(profile_name: str) -> tuple[Dict[str, Any], Dict[str, Any]]:
    profile_data = PROFILE_CONFIG.get(profile_name, {})
    if not profile_data:
        raise ValueError(f"Unknown profile: {profile_name}")

    if profile_name == "low-friction":
        # low-friction inherits trusted-workflow plus its own
        base_profile = PROFILE_CONFIG.get("trusted-workflow", {})
        merged_subagents = {**base_profile.get("chat.tools.subagent.autoApprove", {}), **profile_data.get("chat.tools.subagent.autoApprove", {})}
        merged_terminal = {**base_profile.get("chat.tools.terminal.autoApprove", {}), **profile_data.get("chat.tools.terminal.autoApprove", {})}
    else:
        merged_subagents = profile_data.get("chat.tools.subagent.autoApprove", {})
        merged_terminal = profile_data.get("chat.tools.terminal.autoApprove", {})
        
    return merged_subagents, merged_terminal

def collect_drift(expected: Any, actual: Any, path: str = "") -> list[str]:
    """Check for missing, mismatch, and extra keys in fully managed blocks."""
    drifts: list[str] = []

    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            drifts.append(f"{path or '<root>'}: expected object, found {type(actual).__name__}")
            return drifts

        for key, value in expected.items():
            child_path = f"{path}.{key}" if path else key
            if key not in actual:
                drifts.append(f"{child_path}: missing")
                continue
            drifts.extend(collect_drift(value, actual[key], child_path))
            
        if path: 
            for key in actual:
                if key not in expected:
                    child_path = f"{path}.{key}" if path else key
                    drifts.append(f"{child_path}: extra managed key")
                    
        return drifts

    if expected != actual:
        drifts.append(f"{path}: expected={expected!r} actual={actual!r} (mismatched)")

    return drifts

def reconcile_settings(base: Dict[str, Any], profile_name: str) -> Dict[str, Any]:
    """Reconcile settings based on profile, replacing unused keys."""
    merged_subagents, merged_terminal = get_expected_settings(profile_name)
    cleaned = copy.deepcopy(base)
    
    # Overwrite entirely instead of merging, to ensure reconciliatory nature
    cleaned["chat.tools.subagent.autoApprove"] = merged_subagents
    cleaned["chat.tools.terminal.autoApprove"] = merged_terminal
    
    return cleaned

def configure_workspace(profile: str, global_only: bool = False, workspace_only: bool = False, check: bool = False, dry_run: bool = False) -> int:
    root_dir = Path(__file__).parent.parent
    
    paths = []
    if not workspace_only:
        paths.append(get_vscode_settings_path())
    
    if not global_only:
        paths.extend([
            root_dir / ".vscode/settings.json",
            root_dir / "../AI-Agent-Framework-Client/.vscode/settings.json",
        ])
    
    success_count = 0
    drift_count = 0
    merged_subagents, merged_terminal = get_expected_settings(profile)
    expected_root = {
        "chat.tools.subagent.autoApprove": merged_subagents,
        "chat.tools.terminal.autoApprove": merged_terminal
    }
        
    for path in paths:
        # Check if the external path exists but safely skip
        if path.parts[-3:-2] == ("AI-Agent-Framework-Client",) and not path.parent.parent.exists():
            continue
            
        try:
            settings = read_json_file(path)
            
            actual_root = {}
            if "chat.tools.subagent.autoApprove" in settings:
                actual_root["chat.tools.subagent.autoApprove"] = settings["chat.tools.subagent.autoApprove"]
            if "chat.tools.terminal.autoApprove" in settings:
                actual_root["chat.tools.terminal.autoApprove"] = settings["chat.tools.terminal.autoApprove"]
                
            drifts = collect_drift(expected_root, actual_root)
            
            if check:
                if drifts:
                    print(f"❌ Settings drift detected in {path}:")
                    for d in drifts:
                        print(f"  - {d}")
                    drift_count += 1
                else:
                    print(f"✅ Settings match profile '{profile}' in {path}")
            elif dry_run:
                print(f"🔍 Dry Run: Previewing projection for {path}...")
                if not drifts:
                    print("✅ No changes needed. Settings are fully reconciled.")
                else:
                    print("📝 Would reconcile the following drift:")
                    for drift in drifts:
                        if "extra managed key" in drift:
                            print(f"  🗑️  Would remove: {drift}")
                        else:
                            print(f"  - {drift}")
            else:
                updated = reconcile_settings(settings, profile)
                if drifts:
                    removed = [d for d in drifts if "extra managed key" in d]
                    if removed:
                        print(f"🧹 Removed {len(removed)} stale managed keys in {path}")
                write_json_file(path, updated)
                print(f"✅ Updated {profile} profile in: {path}")
                success_count += 1
        except Exception as e:
            print(f"❌ Failed to process {path}: {e}")
            if "No such file" not in str(e):
                import traceback
                traceback.print_exc()
                
    if check:
        return 1 if drift_count > 0 else 0
    return 0

def main():
    parser = argparse.ArgumentParser(description="Configure VS Code Copilot auto-approve settings.")
    parser.add_argument("--global-only", action="store_true", help="Only configure global user settings")
    parser.add_argument("--workspace-only", action="store_true", help="Only configure workspace settings")
    parser.add_argument("--check", action="store_true", help="Check config instead of updating")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without modifying files")
    parser.add_argument("--profile", choices=["safe", "trusted-workflow", "low-friction"], default="trusted-workflow", help="Approval profile to use")
    args = parser.parse_args()

    try:
        sys.exit(configure_workspace(args.profile, args.global_only, args.workspace_only, args.check, args.dry_run))
    except Exception as e:
        print(f"❌ Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
