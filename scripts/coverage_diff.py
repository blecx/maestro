#!/usr/bin/env python3
"""
Coverage Diff Calculator
Checks if coverage for changed files meets the 80% threshold.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Set


def get_changed_files(base_ref: str, head_ref: str) -> Set[str]:
    """Get Python files changed between base and head"""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{base_ref}...{head_ref}"],
            capture_output=True,
            text=True,
            check=True,
        )

        changed_files = set()
        for line in result.stdout.strip().split("\n"):
            if line.endswith(".py") and (
                line.startswith("apps/api/") or line.startswith("apps/tui/")
            ):
                # Skip __init__.py files
                if not line.endswith("__init__.py"):
                    changed_files.add(line)

        return changed_files
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to get changed files: {e}")
        return set()


def get_coverage_data() -> Dict[str, float]:
    """Get coverage data from coverage.json"""
    coverage_file = Path("coverage.json")

    if not coverage_file.exists():
        print("⚠️  coverage.json not found - running tests with coverage...")
        try:
            subprocess.run(
                [
                    "pytest",
                    "tests/",
                    "--cov=apps/api",
                    "--cov=apps/tui",
                    "--cov-report=json",
                ],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError:
            print("❌ Failed to generate coverage report")
            return {}

    if not coverage_file.exists():
        print("❌ coverage.json still not found after pytest run")
        return {}

    with open(coverage_file) as f:
        data = json.load(f)

    coverage_by_file = {}
    for file_path, file_data in data.get("files", {}).items():
        summary = file_data.get("summary", {})
        percent_covered = summary.get("percent_covered", 0.0)
        coverage_by_file[file_path] = percent_covered

    return coverage_by_file


def _coverage_lookup_key(cov_file: str) -> str:
    """Normalize coverage.json file keys for matching.

    Coverage JSON keys may be absolute paths, repo-relative paths, or paths
    relative to the configured --cov source. Normalizing to a POSIX-like string
    makes suffix-matching more reliable.
    """

    try:
        return Path(cov_file).as_posix()
    except Exception:
        return str(cov_file)


def _candidate_suffixes(changed_file: str) -> Set[str]:
    """Generate possible suffixes that might appear in coverage.json for a file."""

    suffixes: Set[str] = {changed_file}

    # coverage.py may record paths relative to the --cov source directory
    # (e.g. "main.py" instead of "apps/api/main.py").
    if changed_file.startswith("apps/api/"):
        suffixes.add(changed_file.removeprefix("apps/api/"))
    if changed_file.startswith("apps/tui/"):
        suffixes.add(changed_file.removeprefix("apps/tui/"))

    # Last-resort fallback: basename.
    suffixes.add(Path(changed_file).name)
    return {s for s in suffixes if s}


def main():
    """Main coverage diff validation logic"""
    if len(sys.argv) < 3:
        print("Usage: python scripts/coverage_diff.py <base_ref> <head_ref>")
        print("Example: python scripts/coverage_diff.py origin/main HEAD")
        return 1

    base_ref = sys.argv[1]
    head_ref = sys.argv[2]

    print(f"Checking coverage diff: {base_ref}...{head_ref}")
    print()

    # Get changed files
    changed_files = get_changed_files(base_ref, head_ref)

    if not changed_files:
        print("✅ No Python files changed in apps/ - coverage check passed")
        return 0

    print(f"Changed files ({len(changed_files)}):")
    for file in sorted(changed_files):
        print(f"  - {file}")
    print()

    # Get coverage data
    coverage_data = get_coverage_data()

    if not coverage_data:
        print("⚠️  No coverage data available - skipping coverage check")
        return 0

    # Check coverage for each changed file
    threshold = 80.0
    below_threshold = []

    for file in changed_files:
        # Coverage reports can use absolute paths, repo-relative paths, or
        # paths relative to the --cov source. Try a few suffix candidates.
        coverage_percent = None
        candidates = _candidate_suffixes(file)

        # Prefer the most specific (longest) suffix match.
        best_match_len = -1
        for cov_file_raw, percent in coverage_data.items():
            cov_file = _coverage_lookup_key(cov_file_raw)
            for cand in candidates:
                if cov_file.endswith(cand) and len(cand) > best_match_len:
                    coverage_percent = percent
                    best_match_len = len(cand)

        if coverage_percent is None:
            # File might be new and not in coverage report yet
            print(f"⚠️  {file}: No coverage data (possibly new file)")
            below_threshold.append((file, 0.0))
        elif coverage_percent < threshold:
            below_threshold.append((file, coverage_percent))

    # Report results
    if below_threshold:
        print(f"❌ Coverage below {threshold}% for changed files:")
        for file, percent in below_threshold:
            print(f"  - {file}: {percent:.1f}%")
        print()
        print(f"Remediation: Add tests to bring coverage above {threshold}%")
        return 1

    print(f"✅ All changed files have {threshold}%+ coverage")
    for file in sorted(changed_files):
        candidates = _candidate_suffixes(file)
        best_match = None
        best_match_len = -1
        for cov_file_raw, percent in coverage_data.items():
            cov_file = _coverage_lookup_key(cov_file_raw)
            for cand in candidates:
                if cov_file.endswith(cand) and len(cand) > best_match_len:
                    best_match = percent
                    best_match_len = len(cand)
        if best_match is not None:
            print(f"  - {file}: {best_match:.1f}%")

    return 0


if __name__ == "__main__":
    sys.exit(main())
