#!/usr/bin/env python3
"""Select the next issue across BOTH repositories.

This repo already includes `scripts/next-issue.py`, which implements a Step-1
selection workflow for the client repo (blecx/AI-Agent-Framework-Client).

This helper script:
- Gets the next client Step-1 issue via `scripts/next-issue.py` (dry-run, no reconcile)
- Gets a simple "next" backend issue via `gh issue list --repo blecx/AI-Agent-Framework`
- Prefers the client Step-1 issue when one is available

Usage:
  ./scripts/next-issue-both.py
  ./scripts/next-issue-both.py --json
  ./scripts/next-issue-both.py --prefer backend

Exit codes:
  0: success
  1: no issues found / error
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).parent.parent

CLIENT_REPO = "blecx/AI-Agent-Framework-Client"
BACKEND_REPO = "blecx/AI-Agent-Framework"
DEFAULT_GH_MIN_INTERVAL_SECONDS = 1.0
_GH_LAST_REQUEST_TS: float | None = None


@dataclass(frozen=True)
class Candidate:
    repo: str
    number: int
    title: str | None = None


def _run(cmd: list[str], timeout: int = 60, cwd: Optional[Path] = None) -> subprocess.CompletedProcess[str]:
    if cmd and cmd[0] == "gh":
        _throttle_gh_requests()

    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(cwd) if cwd else None,
    )


def _throttle_gh_requests() -> None:
    global _GH_LAST_REQUEST_TS

    min_interval = max(
        0.0,
        float(os.getenv("NEXT_ISSUE_BOTH_GH_MIN_INTERVAL", str(DEFAULT_GH_MIN_INTERVAL_SECONDS))),
    )
    if min_interval <= 0:
        _GH_LAST_REQUEST_TS = time.monotonic()
        return

    now = time.monotonic()
    if _GH_LAST_REQUEST_TS is not None:
        elapsed = now - _GH_LAST_REQUEST_TS
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)

    _GH_LAST_REQUEST_TS = time.monotonic()


def _check_gh() -> None:
    try:
        _run(["gh", "--version"], timeout=10)
    except FileNotFoundError:
        print("❌ 'gh' CLI not found. Install from https://cli.github.com/", file=sys.stderr)
        sys.exit(1)


def _get_client_candidate() -> Optional[Candidate]:
    """Parse the client candidate by running existing selector."""
    script = REPO_ROOT / "scripts" / "next-issue.py"
    if not script.exists():
        return None

    # dry-run + skip reconcile: fast and read-only
    proc = _run([sys.executable, str(script), "--dry-run", "--skip-reconcile"], timeout=180, cwd=REPO_ROOT)
    if proc.returncode != 0:
        return None

    # Output line: "🎯 Selected Issue: #<number>"
    match = re.search(r"^🎯\s+Selected\s+Issue:\s+#(\d+)\s*$", proc.stdout, re.MULTILINE)
    if not match:
        return None

    issue_number = int(match.group(1))
    return Candidate(repo=CLIENT_REPO, number=issue_number)


def _get_backend_candidate() -> Optional[Candidate]:
    """Simple backend candidate: first open issue by number."""
    proc = _run(
        [
            "gh",
            "issue",
            "list",
            "--repo",
            BACKEND_REPO,
            "--state",
            "open",
            "--limit",
            "50",
            "--json",
            "number,title,labels,createdAt,updatedAt",
        ],
        timeout=60,
        cwd=REPO_ROOT,
    )
    if proc.returncode != 0:
        return None

    try:
        issues: list[dict[str, Any]] = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None

    if not issues:
        return None

    # Heuristic: prefer the smallest issue number (usually oldest / most canonical).
    issues_sorted = sorted(issues, key=lambda i: int(i.get("number") or 10**9))
    best = issues_sorted[0]
    return Candidate(repo=BACKEND_REPO, number=int(best["number"]), title=str(best.get("title") or ""))


def main() -> int:
    parser = argparse.ArgumentParser(description="Select the next issue across backend + client repos")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument(
        "--prefer",
        choices=["client", "backend"],
        default="client",
        help="Which repo to prefer when both have candidates (default: client)",
    )
    args = parser.parse_args()

    _check_gh()

    client = _get_client_candidate()
    backend = _get_backend_candidate()

    selected: Optional[Candidate]
    if args.prefer == "client":
        selected = client or backend
    else:
        selected = backend or client

    if not selected:
        if args.json:
            print(json.dumps({"selected": None, "client": None, "backend": None}, indent=2))
        else:
            print("❌ No open issues found in either repo.")
        return 1

    if args.json:
        payload = {
            "selected": {"repo": selected.repo, "number": selected.number, "title": selected.title},
            "client": None if not client else {"repo": client.repo, "number": client.number, "title": client.title},
            "backend": None if not backend else {"repo": backend.repo, "number": backend.number, "title": backend.title},
        }
        print(json.dumps(payload, indent=2))
        return 0

    print("=" * 80)
    print("Next issue (multi-repo)")
    print("=" * 80)
    print(f"Selected: {selected.repo} #{selected.number}")
    if selected.title:
        print(f"Title: {selected.title}")
    print()
    print("Next commands:")
    print(f"  gh issue view {selected.number} --repo {selected.repo}")
    print("  # then run the appropriate workflow/agent for that repo")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
