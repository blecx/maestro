#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from _factorylib import find_forbidden_tokens

ROOT = Path(__file__).resolve().parent.parent
FORBIDDEN = [
    "blecx" + "/" + "maestro",
    "maestro" + "-" + "Client",
    "_external/" + "maestro" + "-" + "Client",
]
ALLOW_PATHS = {
    "docs/EXTRACTION-SOURCE-MAP.md",
    "SoftwareFactoryVsocdeTestsuite.md",
    "externalDevendenciesSoftwareFactory.md",
    "manifests/extraction-manifest.json",
    "scripts/check_neutrality.py",
}


def main() -> None:
    violations = find_forbidden_tokens(ROOT, FORBIDDEN, allow_paths=ALLOW_PATHS)
    if violations:
        raise SystemExit("Neutrality violations found:\n" + "\n".join(sorted(violations)))
    print("Neutrality check passed")


if __name__ == "__main__":
    main()
