#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUIRED_DOCS = [
    ROOT / "README.md",
    ROOT / "docs" / "INSTALL.md",
    ROOT / "docs" / "TESTING.md",
    ROOT / "docs" / "VSCODE-WORKSPACE.md",
    ROOT / "docs" / "UPGRADE.md",
    ROOT / "docs" / "MAINTENANCE.md",
    ROOT / "docs" / "ARCHITECTURE.md",
    ROOT / "docs" / "EXTRACTION-SOURCE-MAP.md",
    ROOT / "SoftwareFactoryVsocdeTestsuite.md",
    ROOT / "externalDevendenciesSoftwareFactory.md",
]

NEEDED_PHRASES = {
    "README.md": ["softwareFactoryVscode", ".softwareFactoryVscode", "docs/INSTALL.md"],
    "INSTALL.md": ["bootstrap_host.py", "project_runtime_up.py", "CONTEXT7_API_KEY"],
    "TESTING.md": ["check_neutrality.py", "check_vscode_workspace.py", "test_fresh_install.py"],
    "VSCODE-WORKSPACE.md": [
        "GitHub.copilot",
        "Context7",
        "does not ship a replacement workspace-local `issueagent` extension",
        ".softwareFactoryVscode",
    ],
}


def main() -> None:
    for path in REQUIRED_DOCS:
        if not path.exists():
            raise SystemExit(f"Missing required documentation file: {path.relative_to(ROOT)}")

    for name, phrases in NEEDED_PHRASES.items():
        path = ROOT / name if name == "README.md" else ROOT / "docs" / name
        content = path.read_text(encoding="utf-8")
        missing = [phrase for phrase in phrases if phrase not in content]
        if missing:
            raise SystemExit(f"{path.relative_to(ROOT)} missing phrases: {missing}")

    print("Documentation accuracy check passed")


if __name__ == "__main__":
    main()
