#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
DEPRECATED = (
    "PROJECT_" + "WORKSPACE_DIR",
    "WORKSPACE_" + "PATH",
    "MAESTRO_" + "INSTANCE_ID",
    "MAESTRO_" + "AUDIT_DIR",
    "MAESTRO_" + "DATA_DIR",
)
SCOPES = [ROOT / "compose", ROOT / "scripts", ROOT / "docs"]
ALLOWLIST = {
    "SoftwareFactoryVsocdeTestsuite.md",
    "docs/EXTRACTION-SOURCE-MAP.md",
    "scripts/check_variable_contract.py",
}


def main() -> None:
    violations: list[str] = []
    for scope in SCOPES:
        for path in scope.rglob("*"):
            if not path.is_file():
                continue
            relative = path.relative_to(ROOT).as_posix()
            if relative in ALLOWLIST:
                continue
            try:
                content = path.read_text(encoding="utf-8")
            except Exception:
                continue
            for token in DEPRECATED:
                if re.search(rf"(?<![A-Z0-9_]){re.escape(token)}(?![A-Z0-9_])", content):
                    violations.append(f"{relative} -> {token}")
    if violations:
        raise SystemExit("Deprecated variable names detected:\n" + "\n".join(sorted(violations)))
    print("Variable contract check passed")


if __name__ == "__main__":
    main()
