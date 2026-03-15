import os
from pathlib import Path


def test_no_meta_dir_access():
    """Ensure package runtime code stays independent from workspace metadata."""
    root = Path(__file__).resolve().parents[1]
    package_root = root.parent
    dirs_to_check = [root / "agents", root / "apps"]
    violations = []

    for check_dir in dirs_to_check:
        for current_root, _, files in os.walk(check_dir):
            for file in files:
                if not file.endswith(".py"):
                    continue
                filepath = Path(current_root) / file
                if "__pycache__" in str(filepath):
                    continue

                content = filepath.read_text(encoding="utf-8")
                if ".github/agents/" in content or ".copilot/" in content or ".vscode/" in content:
                    violations.append(str(filepath.relative_to(package_root)))

    assert not violations, f"Architectural violation: .github/ or .copilot/ referenced in {violations}"
