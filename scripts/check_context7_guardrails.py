#!/usr/bin/env python3
"""Validate Context7 guardrails in prompt policy and workspace MCP settings."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SETTINGS_FILE = ROOT / ".vscode" / "settings.json"
PROMPT_BASELINE_FILE = ROOT / ".github" / "prompts" / "modules" / "prompt-quality-baseline.md"
CREATE_ISSUE_PROMPT = ROOT / ".github" / "prompts" / "agents" / "create-issue.md"
RESOLVE_ISSUE_PROMPT = ROOT / ".github" / "prompts" / "agents" / "resolve-issue-dev.md"

REQUIRED_BASELINE_SNIPPETS = [
    "Context7",
    "external API",
    "MCP Tool Arbitration Hard Rules",
    "Prompts must treat these as hard rules",
]

REQUIRED_AGENT_SNIPPETS = {
    CREATE_ISSUE_PROMPT: [
        "Context7",
        "docs-grounding",
        "MCP Tool Arbitration Hard Rules",
    ],
    RESOLVE_ISSUE_PROMPT: [
        "Context7",
        "external API",
        "MCP Tool Arbitration Hard Rules",
    ],
}

REQUIRED_MCP_SERVER_URLS = {
    "context7": "http://127.0.0.1:3010/mcp",
    "bashGateway": "http://127.0.0.1:3011/mcp",
    "git": "http://127.0.0.1:3012/mcp",
    "search": "http://127.0.0.1:3013/mcp",
    "filesystem": "http://127.0.0.1:3014/mcp",
    "dockerCompose": "http://127.0.0.1:3015/mcp",
    "testRunner": "http://127.0.0.1:3016/mcp",
    "offlineDocs": "http://127.0.0.1:3017/mcp",
    "githubOps": "http://127.0.0.1:3018/mcp",
}


def _must_contain(path: Path, snippets: list[str], errors: list[str]) -> None:
    if not path.exists():
        errors.append(f"{path}: file missing")
        return
    text = path.read_text(encoding="utf-8")
    missing = [snippet for snippet in snippets if snippet not in text]
    if missing:
        errors.append(f"{path}: missing required snippets: {', '.join(missing)}")


def _check_settings(errors: list[str]) -> None:
    if not SETTINGS_FILE.exists():
        errors.append(f"{SETTINGS_FILE}: file missing")
        return

    try:
        settings = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{SETTINGS_FILE}: invalid JSON ({exc})")
        return

    mcp = settings.get("mcp")
    if not isinstance(mcp, dict):
        errors.append(f"{SETTINGS_FILE}: missing top-level 'mcp' object")
        return

    servers = mcp.get("servers")
    if not isinstance(servers, dict):
        errors.append(f"{SETTINGS_FILE}: missing 'mcp.servers' object")
        return

    for server_name, expected_url in REQUIRED_MCP_SERVER_URLS.items():
        server = servers.get(server_name)
        if not isinstance(server, dict):
            errors.append(f"{SETTINGS_FILE}: missing 'mcp.servers.{server_name}' entry")
            continue
        if server.get("url") != expected_url:
            errors.append(
                f"{SETTINGS_FILE}: {server_name} url must be {expected_url}"
            )

    context7 = servers.get("context7")
    if not isinstance(context7, dict):
        return

    headers = context7.get("headers")
    if not isinstance(headers, dict) or headers.get("CONTEXT7_API_KEY") != "${env:CONTEXT7_API_KEY}":
        errors.append(
            f"{SETTINGS_FILE}: context7 headers must map CONTEXT7_API_KEY to ${'{env:CONTEXT7_API_KEY}'}"
        )


def main() -> int:
    errors: list[str] = []

    _check_settings(errors)
    _must_contain(PROMPT_BASELINE_FILE, REQUIRED_BASELINE_SNIPPETS, errors)
    for path, snippets in REQUIRED_AGENT_SNIPPETS.items():
        _must_contain(path, snippets, errors)

    if errors:
        print("❌ MCP guardrail checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("✅ MCP guardrail checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
