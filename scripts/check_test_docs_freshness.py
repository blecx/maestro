#!/usr/bin/env python3
"""
check_test_docs_freshness.py — Step 3R backend test-doc freshness checker.

Scans Step 3 test documentation files and verifies that required sections
are present. Exits non-zero with actionable remediation messages when any
required section is missing.

Usage:
    .venv/bin/python scripts/check_test_docs_freshness.py
"""

import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration: file → required ## headings (exact, case-sensitive)
# ---------------------------------------------------------------------------
REQUIRED_SECTIONS: dict[str, list[str]] = {
    "tests/e2e/tui/README.md": [
        "## Architecture",
        "## Fixtures",
        "## Running Tests",
    ],
    "tests/README.md": [
        "## Running tests locally",
        "## TUI E2E notes",
    ],
}

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)


def extract_headings(text: str) -> list[str]:
    """Return a sorted list of all Markdown headings found in *text*."""
    return sorted(f"{m.group(1)} {m.group(2)}" for m in _HEADING_RE.finditer(text))


def check_file(repo_root: Path, rel_path: str, required: list[str]) -> list[str]:
    """
    Check one doc file for required sections.

    Returns a list of missing-section error strings (empty = all good).
    """
    abs_path = repo_root / rel_path
    errors: list[str] = []

    if not abs_path.exists():
        errors.append(
            f"  MISSING FILE  {rel_path}\n"
            f"    → Create the file and add the required sections."
        )
        return errors

    text = abs_path.read_text(encoding="utf-8")
    present = set(extract_headings(text))

    for section in sorted(required):
        # Match by exact string
        if section not in present:
            errors.append(
                f"  MISSING SECTION  \"{section}\"  in  {rel_path}\n"
                f"    → Add a `{section}` heading to {rel_path}."
            )

    return errors


def main() -> int:
    """Run all checks. Returns 0 on success, 1 on any failure."""
    repo_root = Path(__file__).resolve().parent.parent

    all_errors: list[str] = []

    for rel_path in sorted(REQUIRED_SECTIONS):
        required = REQUIRED_SECTIONS[rel_path]
        errors = check_file(repo_root, rel_path, required)
        all_errors.extend(errors)

    if all_errors:
        print("❌ Test-doc freshness check FAILED\n", file=sys.stderr)
        for err in all_errors:
            print(err, file=sys.stderr)
        print(
            "\nPlease update the listed files to include the missing sections.",
            file=sys.stderr,
        )
        return 1

    print("✅ Test-doc freshness check passed — all required sections present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
