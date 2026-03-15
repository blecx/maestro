#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNTIME_ROOT = ROOT / "factory_runtime"
FORBIDDEN = (".copilot/", ".github/agents/", ".vscode/")
SCOPES = [RUNTIME_ROOT / "agents", RUNTIME_ROOT / "apps"]


def main() -> None:
    violations: list[str] = []
    for scope in SCOPES:
        for path in scope.rglob("*.py"):
            content = path.read_text(encoding="utf-8")
            for token in FORBIDDEN:
                if token in content:
                    violations.append(f"{path.relative_to(ROOT)} -> {token}")
                    break
    if violations:
        raise SystemExit("Boundary violations found:\n" + "\n".join(violations))
    print("Boundary check passed")


if __name__ == "__main__":
    main()
