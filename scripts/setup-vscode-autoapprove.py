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

import json
import os
import sys
import argparse
from pathlib import Path
from typing import Dict, Any


LOW_FRICTION_ONLY_TERMINAL_KEYS = [
    "/^\\s*.+$/",
    "/^\\s*.*(?:\\/tmp\\/|\\.tmp\\/|\\$TMPDIR|TMPDIR=).*$/",
]

# Auto-approve settings to be applied
AUTO_APPROVE_SETTINGS = {
    "chat.agent.maxRequests": 50,
    "chat.allowAnonymousAccess": True,
    "chat.checkpoints.showFileChanges": True,
    "chat.customAgentInSubagent.enabled": True,
    "chat.tools.subagent.autoApprove": {
        "create-issue": True,
        "resolve-issue": True,
        "close-issue": True,
        "pr-merge": True,
        "Plan": True,
        "tutorial": True
    },
    "chat.tools.terminal.autoApprove": {
        # Core executables
        "bash": True,
        "python3": True,
        "python": True,
        
        # Git commands
        "git add": True,
        "git reset": True,
        "git commit": True,
        "git push": True,
        "git pull": True,
        "git fetch": True,
        "git switch": True,
        "git status": True,
        "git log": True,
        "git diff": True,
        "git branch": True,
        "git merge": True,
        "git rebase": True,
        "git show": True,
        "git rev-parse": True,
        "git checkout": True,
        "git restore": True,
        "git rm": True,
        "git stash": True,
        
        # Python tooling
        "python -m black": True,
        "python -m flake8": True,
        "python -m pytest": True,
        "pytest": True,
        
        # NPM/Node
        "npm install": True,
        "npm run dev": True,
        "npm test": True,
        "npm run test": True,
        "npm run build": True,
        "npm run lint": True,
        "npm ci": True,
        "npm audit": True,
        "npx vitest": True,
        "vitest": True,
        
        # GitHub CLI
        "gh": True,
        
        # Search tools
        "rg": True,
        "fd": True,
        "grep": True,
        "awk": True,
        "sed": True,
        "find": True,
        "wc": True,
        
        # Shell utilities
        "cat": True,
        "head": True,
        "tail": True,
        "which": True,
        "command": True,
        "cd": True,
        "ls": True,
        "pwd": True,
        "echo": True,
        "sleep": True,
        "curl": True,
        "mkdir": True,
        "rm": True,
        "cp": True,
        "chmod": True,
        "mv": True,
        "pushd": True,
        "popd": True,
        "source": True,
        "env": True,
        "true": True,
        "printf": True,
        "getent": True,
        
        # Docker
        "docker": True,
        "docker-compose": True,
        "docker compose": True,
        
        # Dev tools
        "act": True,
        "pre-commit": True,
        "uv": True,

        # Repo workflow scripts
        "./scripts/work-issue.py": True,
        "./scripts/next-issue.py": True,
        "./scripts/next-issue-both.py": True,
        "./scripts/next-pr.py": True,
        "./scripts/prmerge": True,
        "./scripts/close-issue.sh": True,
        "./scripts/validate-pr-template.sh": True,
        "./scripts/check_issue_specs.py": True,
        "./scripts/validate_issue_specs.sh": True,
        "./next-issue": True,
        "./next-pr": True,

        # Allow command lines with optional leading whitespace, env, and VAR=... prefixes
        "/^\\s*(?:env\\s+)?(?:[A-Za-z_][A-Za-z0-9_]*=[^\\s]+\\s+)*(git|gh|npm|python|pytest|docker|curl|uvicorn|ssh-add|cd|ls|cat|rg|fd|find|awk|sed|grep|jq|xargs|head|tail|wc|echo|sleep|mkdir|rm|cp|mv|chmod|source|env|\\./setup\\.sh|\\./scripts\\/[^\\s]+|\\./next-issue|\\./next-pr)(\\s+.*)?$/": {
            "approve": True,
            "matchCommandLine": True,
            "description": "Allow safe commands with optional leading whitespace, env, and VAR=... prefixes"
        },
        "/^\\s*for\\s+.+;\\s*do\\s+.+;\\s*done(?:;\\s*exit\\s+\\d+)?\\s*$/": {
            "approve": True,
            "matchCommandLine": True,
            "description": "Allow polling loops used in issue/pr/merge workflows"
        },
        "/^\\s*cd\\s+.*\\s+&&\\s+.*$/": {
            "approve": True,
            "matchCommandLine": True,
            "description": "Allow cd with command chaining"
        },
    }
    ,
    "terminal.integrated.env.linux": {
        "TMPDIR": "${workspaceFolder}/.tmp",
        "TMP": "${workspaceFolder}/.tmp",
        "TEMP": "${workspaceFolder}/.tmp"
    }
}


def _with_low_friction_settings(base: Dict[str, Any]) -> Dict[str, Any]:
    """Return extended settings for near-zero terminal approval friction."""
    low = json.loads(json.dumps(base))

    terminal_auto = low.setdefault("chat.tools.terminal.autoApprove", {})
    terminal_auto["/^\\s*.+$/"] = {
        "approve": True,
        "matchCommandLine": True,
        "description": "Low-friction mode: approve nearly all terminal command lines"
    }
    terminal_auto["/^\\s*.*(?:\\/tmp\\/|\\.tmp\\/|\\$TMPDIR|TMPDIR=).*$/"] = {
        "approve": True,
        "matchCommandLine": True,
        "description": "Approve command lines that reference /tmp, .tmp, or TMPDIR"
    }

    return low


def _strip_low_friction_overrides(settings_obj: Dict[str, Any]) -> Dict[str, Any]:
    """Remove ultra-broad low-friction approvals to enforce safe profile."""
    cleaned = json.loads(json.dumps(settings_obj))
    terminal_auto = cleaned.get("chat.tools.terminal.autoApprove", {})
    if isinstance(terminal_auto, dict):
        for key in LOW_FRICTION_ONLY_TERMINAL_KEYS:
            terminal_auto.pop(key, None)
    return cleaned


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


def read_json_file(path: Path) -> Dict[str, Any]:
    """Read JSON file, handling comments and missing files."""
    if not path.exists():
        return {}
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Remove JSON5 style comments (VS Code allows them)
            lines = []
            for line in content.split('\n'):
                # Remove trailing comments
                if '//' in line:
                    # Keep strings with //
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
        print(f"   Creating backup and starting fresh...")
        # Backup the file
        backup_path = path.with_suffix('.json.backup')
        path.rename(backup_path)
        print(f"   Backup saved to: {backup_path}")
        return {}


def merge_settings(existing: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge settings, with new settings taking precedence."""
    result = existing.copy()
    
    for key, value in new.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_settings(result[key], value)
        else:
            result[key] = value
    
    return result


def write_json_file(path: Path, data: Dict[str, Any]) -> None:
    """Write JSON file with pretty formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')  # Add trailing newline


def update_settings(path: Path, name: str, settings_payload: Dict[str, Any], profile: str) -> bool:
    """Update settings file with auto-approve configuration."""
    print(f"\n📝 Updating {name}...")
    print(f"   Path: {path}")
    
    # Read existing settings
    existing = read_json_file(path)
    
    if profile == "safe":
        existing = _strip_low_friction_overrides(existing)

    # Merge with auto-approve settings
    updated = merge_settings(existing, settings_payload)
    
    # Write back
    try:
        write_json_file(path, updated)
        print(f"   ✅ Successfully updated {name}")
        return True
    except Exception as e:
        print(f"   ❌ Failed to update {name}: {e}")
        return False


def _collect_drift(expected: Any, actual: Any, path: str = "") -> list[str]:
    """Collect deterministic drift messages between expected and actual values."""
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
            drifts.extend(_collect_drift(value, actual[key], child_path))
        return drifts

    if expected != actual:
        drifts.append(f"{path}: expected={expected!r} actual={actual!r}")

    return drifts


def verify_settings(path: Path, name: str, settings_payload: Dict[str, Any], profile: str) -> bool:
    """Verify managed settings keys exactly match source-of-truth values."""
    print(f"\n🔎 Verifying {name}...")
    print(f"   Path: {path}")

    existing = read_json_file(path)
    drifts = _collect_drift(settings_payload, existing)

    if profile == "safe":
        terminal_auto = existing.get("chat.tools.terminal.autoApprove", {})
        if isinstance(terminal_auto, dict):
            for key in LOW_FRICTION_ONLY_TERMINAL_KEYS:
                if key in terminal_auto:
                    drifts.append(f"chat.tools.terminal.autoApprove.{key}: disallowed in safe profile")

    if not drifts:
        print(f"   ✅ No drift detected in {name}")
        return True

    print(f"   ❌ Drift detected in {name} ({len(drifts)} differences):")
    for diff in drifts[:20]:
        print(f"      - {diff}")
    if len(drifts) > 20:
        print(f"      - ... and {len(drifts) - 20} more")
    return False


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Configure or verify VS Code Copilot auto-approve settings."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check for drift without modifying files (non-zero exit on mismatch).",
    )
    parser.add_argument(
        "--workspace-only",
        action="store_true",
        help="Operate only on backend/client workspace settings (skip global user settings).",
    )
    parser.add_argument(
        "--profile",
        choices=["safe", "low-friction"],
        default="safe",
        help="Approval profile: 'safe' (default) or explicit high-trust 'low-friction'.",
    )
    parser.add_argument(
        "--low-friction",
        action="store_true",
        help="Backward-compatible alias for --profile low-friction.",
    )
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    profile = "low-friction" if args.low_friction else args.profile

    settings_payload = AUTO_APPROVE_SETTINGS
    if profile == "low-friction":
        settings_payload = _with_low_friction_settings(AUTO_APPROVE_SETTINGS)

    print(f"🔐 Profile: {profile}")
    if profile == "low-friction":
        print("⚠️  High-trust mode enabled: near-zero command approvals are active.")

    print("🚀 VS Code Auto-Approve Setup")
    print("=" * 60)
    
    success_count = 0
    total_count = 0
    
    # 1. Global VS Code settings (optional)
    if not args.workspace_only:
        try:
            global_settings = get_vscode_settings_path()
            total_count += 1
            if args.check:
                if verify_settings(global_settings, "Global VS Code settings", settings_payload, profile):
                    success_count += 1
            else:
                if update_settings(global_settings, "Global VS Code settings", settings_payload, profile):
                    success_count += 1
        except Exception as e:
            mode = "verify" if args.check else "update"
            print(f"\n❌ Could not {mode} global settings: {e}")
    
    # 2. Update backend workspace settings
    backend_workspace = Path(__file__).parent.parent / ".vscode/settings.json"
    total_count += 1
    if args.check:
        if verify_settings(backend_workspace, "Backend workspace", settings_payload, profile):
            success_count += 1
    else:
        if update_settings(backend_workspace, "Backend workspace", settings_payload, profile):
            success_count += 1
    
    # 3. Update client workspace settings
    client_workspace = Path(__file__).parent.parent.parent / "AI-Agent-Framework-Client/.vscode/settings.json"
    total_count += 1
    if args.check:
        if verify_settings(client_workspace, "Client workspace", settings_payload, profile):
            success_count += 1
    else:
        if update_settings(client_workspace, "Client workspace", settings_payload, profile):
            success_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 Summary: {success_count}/{total_count} settings files updated")
    
    if success_count == total_count:
        if args.check:
            print("\n✅ No drift detected for selected settings files")
            return 0

        print("\n✅ All settings configured successfully!")
        print("\n📝 Next steps:")
        print("   1. Reload VS Code window: Ctrl+Shift+P → 'Developer: Reload Window'")
        print("   2. Start a fresh chat - commands should auto-approve")
        print("   3. Verify drift with: ./scripts/setup-autoapprove.sh --check --workspace-only")
        return 0

    if args.check:
        print("\n⚠️  Drift detected. Run ./scripts/setup-autoapprove.sh --workspace-only to reconcile.")
    else:
        print("\n⚠️  Some settings could not be updated")
        print("   Check the errors above and try again")
    return 1


if __name__ == "__main__":
    sys.exit(main())
