#!/usr/bin/env python3
"""Validate MCP server wiring and endpoint reachability for local MCP toolbox."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SETTINGS_FILE = ROOT / ".vscode" / "settings.json"

EXPECTED_MCP_SERVERS = {
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


def _load_settings() -> dict:
    return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))


def _check_settings_servers(errors: list[str]) -> dict[str, str]:
    if not SETTINGS_FILE.exists():
        errors.append(f"Missing settings file: {SETTINGS_FILE}")
        return {}

    try:
        settings = _load_settings()
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid JSON in {SETTINGS_FILE}: {exc}")
        return {}

    servers = settings.get("mcp", {}).get("servers")
    if not isinstance(servers, dict):
        errors.append("Missing object: mcp.servers")
        return {}

    configured: dict[str, str] = {}
    for name, expected_url in EXPECTED_MCP_SERVERS.items():
        entry = servers.get(name)
        if not isinstance(entry, dict):
            errors.append(f"Missing mcp.servers.{name}")
            continue
        actual_url = entry.get("url")
        if not isinstance(actual_url, str):
            errors.append(f"mcp.servers.{name}.url must be a string")
            continue
        if actual_url != expected_url:
            errors.append(f"mcp.servers.{name}.url must be {expected_url} (got {actual_url})")
            continue
        configured[name] = actual_url

    return configured


def _check_endpoint(url: str) -> int:
    request = urllib.request.Request(url=url, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.getcode()
    except urllib.error.HTTPError as exc:
        return exc.code


def main() -> int:
    errors: list[str] = []
    configured = _check_settings_servers(errors)

    for name, url in configured.items():
        try:
            status_code = _check_endpoint(url)
        except (urllib.error.URLError, TimeoutError) as exc:
            errors.append(f"{name} endpoint not reachable at {url}: {exc}")
            continue

        if status_code != 406:
            errors.append(f"{name} endpoint {url} expected HTTP 406, got {status_code}")

    if errors:
        print("❌ MCP connection checks failed:")
        for item in errors:
            print(f"- {item}")
        return 1

    print("✅ MCP connection checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
