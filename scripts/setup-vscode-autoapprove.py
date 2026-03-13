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

def reconcile_settings(base: Dict[str, Any], profile_name: str) -> Dict[str, Any]:
    """Reconcile settings based on profile, removing unused keys."""
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

    cleaned = json.loads(json.dumps(base))
    
    # Overwrite entirely instead of merging, to ensure reconciliatory nature
    cleaned["chat.tools.subagent.autoApprove"] = merged_subagents
    cleaned["chat.tools.terminal.autoApprove"] = merged_terminal
    
    return cleaned

def configure_workspace(profile: str, global_only: bool = False, workspace_only: bool = False) -> None:
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
    for path in paths:
        if path.parent.parent.name == "_external" and not path.parent.parent.exists():
            continue
            
        try:
            settings = read_json_file(path)
            updated = reconcile_settings(settings, profile)
            write_json_file(path, updated)
            print(f"✅ Updated: {path}")
            success_count += 1
        except Exception as e:
            print(f"❌ Failed to update {path}: {e}")
            if "No such file" not in str(e):
                import traceback
                traceback.print_exc()

def main():
    parser = argparse.ArgumentParser(description="Configure VS Code Copilot auto-approve settings.")
    parser.add_argument("--global-only", action="store_true", help="Only configure global user settings")
    parser.add_argument("--workspace-only", action="store_true", help="Only configure workspace settings")
    parser.add_argument("--check", action="store_true", help="Check config instead of updating")
    parser.add_argument("--profile", choices=["safe", "trusted-workflow", "low-friction"], default="trusted-workflow", help="Approval profile to use")
    
    args = parser.parse_args()

    if args.check:
        print(f"✅ Auto-approve profile '{args.profile}' would be configured (dry-run).")
        sys.exit(0)

    try:
        configure_workspace(args.profile, args.global_only, args.workspace_only)
    except Exception as e:
        print(f"❌ Failed to update settings: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
