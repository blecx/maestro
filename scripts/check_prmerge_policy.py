#!/usr/bin/env python3
"""Validate prmerge policy safeguards.

Enforces:
- workflow-file guard exists and defaults to blocked
- explicit override env var is available for exceptional cases
- domain-specific validation guidance is present
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRMERGE_SCRIPT = ROOT / "scripts" / "prmerge"


REQUIRED_SNIPPETS = [
    "PRMERGE_ALLOW_WORKFLOW_FILES=${PRMERGE_ALLOW_WORKFLOW_FILES:-0}",
    "PR modifies GitHub workflow files; blocked by default merge policy",
    "PRMERGE_ALLOW_WORKFLOW_FILES=1 ./scripts/prmerge $ISSUE_NUMBER",
    "Domain-specific validation guidance",
    "Backend scope detected: run focused pytest for touched domain before merge",
    "Frontend scope detected: run npm lint/build or focused UI tests before merge",
    "Docs-only scope: keep validation lightweight (policy/docs checks)",
    "CI health summary:",
]


def main() -> int:
    if not PRMERGE_SCRIPT.exists():
        print(f"❌ Missing script: {PRMERGE_SCRIPT}")
        return 1

    content = PRMERGE_SCRIPT.read_text(encoding="utf-8")
    missing = [snippet for snippet in REQUIRED_SNIPPETS if snippet not in content]

    if missing:
        print("❌ prmerge policy check failed")
        for snippet in missing:
            print(f"- Missing required snippet: {snippet}")
        return 1

    print("✅ prmerge policy check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
