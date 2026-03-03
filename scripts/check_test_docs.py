#!/usr/bin/env python3
"""
Documentation Sync Checker
Validates that tests/README.md accurately reflects the current test directory structure.
"""

import os
import sys
from pathlib import Path
from typing import List, Set


def get_test_directories(tests_root: Path) -> Set[str]:
    """Get all test directories under tests/"""
    directories = set()

    for root, dirs, files in os.walk(tests_root):
        # Skip __pycache__ and hidden directories
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]

        # Only include directories that have Python test files
        has_tests = any(f.startswith("test_") and f.endswith(".py") for f in files)

        if has_tests:
            rel_path = Path(root).relative_to(tests_root)
            if rel_path != Path("."):
                directories.add(str(rel_path))

    return directories


def get_documented_directories(readme_path: Path) -> Set[str]:
    """Extract test directories mentioned in tests/README.md"""
    if not readme_path.exists():
        return set()

    documented = set()
    content = readme_path.read_text()

    # Look for common patterns: `tests/unit/`, **tests/integration/**, etc.
    import re

    patterns = [
        r"`tests/([^`]+)/?`",
        r"\*\*tests/([^*]+)/?\*\*",
        # Allow digits in directory names (e.g. tests/e2e/)
        r"tests/([a-z0-9_/]+)/?",
    ]

    for pattern in patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            # Clean up the path
            clean_path = match.strip("/").strip()
            if clean_path and not clean_path.startswith("test_"):
                documented.add(clean_path)

    return documented


def get_test_commands(readme_path: Path) -> List[str]:
    """Extract pytest commands from tests/README.md"""
    if not readme_path.exists():
        return []

    commands = []
    content = readme_path.read_text()

    # Look for code blocks with pytest commands
    import re

    code_blocks = re.findall(r"```(?:bash|shell)?\n(.*?)```", content, re.DOTALL)

    for block in code_blocks:
        lines = block.strip().split("\n")
        for line in lines:
            if "pytest" in line and not line.strip().startswith("#"):
                commands.append(line.strip())

    return commands


def validate_test_commands(commands: List[str], test_dirs: Set[str]) -> List[str]:
    """Validate that pytest commands reference existing test directories"""
    issues = []

    for cmd in commands:
        # Extract directory references from pytest commands
        import re

        dir_refs = re.findall(r"tests/([a-z_/]+)", cmd)

        for dir_ref in dir_refs:
            dir_ref = dir_ref.strip("/")
            # Check if this directory exists
            if dir_ref not in test_dirs and not any(
                d.startswith(dir_ref) for d in test_dirs
            ):
                issues.append(f"Command references non-existent directory: {cmd}")

    return issues


def main():
    """Main validation logic"""
    project_root = Path(__file__).parent.parent
    tests_root = project_root / "tests"
    readme_path = tests_root / "README.md"

    if not tests_root.exists():
        print("❌ tests/ directory not found")
        return 1

    if not readme_path.exists():
        print("❌ tests/README.md not found")
        print("Remediation: Create tests/README.md documenting test structure")
        return 1

    # Get actual test structure
    actual_dirs = get_test_directories(tests_root)

    # Get documented structure
    documented_dirs = get_documented_directories(readme_path)

    # Find discrepancies
    missing_docs = actual_dirs - documented_dirs
    outdated_docs = documented_dirs - actual_dirs

    # Validate commands
    commands = get_test_commands(readme_path)
    command_issues = validate_test_commands(commands, actual_dirs)

    # Report findings
    has_issues = False

    if missing_docs:
        has_issues = True
        print("❌ Test directories not documented in tests/README.md:")
        for dir_path in sorted(missing_docs):
            print(f"  - tests/{dir_path}")
        print()

    if outdated_docs:
        has_issues = True
        print("⚠️  Documented directories that no longer exist:")
        for dir_path in sorted(outdated_docs):
            print(f"  - tests/{dir_path}")
        print()

    if command_issues:
        has_issues = True
        print("❌ Issues with pytest commands in tests/README.md:")
        for issue in command_issues:
            print(f"  - {issue}")
        print()

    if not commands:
        has_issues = True
        print("⚠️  No pytest commands found in tests/README.md")
        print("Remediation: Add example pytest commands for running tests")
        print()

    if has_issues:
        print("❌ Documentation sync check FAILED")
        print()
        print("Remediation steps:")
        print("1. Update tests/README.md to document all test directories")
        print("2. Remove references to deleted test directories")
        print("3. Ensure pytest commands reference existing directories")
        print("4. Add example commands for running different test suites")
        return 1

    print("✅ Documentation sync check PASSED")
    print(f"   - {len(actual_dirs)} test directories documented")
    print(f"   - {len(commands)} pytest commands validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
