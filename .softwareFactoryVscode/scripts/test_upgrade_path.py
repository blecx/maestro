#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

from _factorylib import resolve_factory_root


def main() -> None:
    factory_root = resolve_factory_root(__file__)
    with tempfile.TemporaryDirectory(prefix="sfvscode-upgrade-") as tmp:
        host = Path(tmp) / "host"
        host.mkdir()
        subprocess.run(["git", "init", "-b", "main"], cwd=host, check=True, capture_output=True)
        subprocess.run(["python3", str(factory_root / "scripts" / "bootstrap_host.py"), "--target", str(host), "--factory-root", str(factory_root)], check=True)
        subprocess.run(["python3", str(factory_root / "scripts" / "project_upgrade.py"), "--target", str(host), "--factory-root", str(factory_root)], check=True)
        assert not (host / ".vscode").exists()
        lock = json.loads((host / ".factory.lock.json").read_text(encoding="utf-8"))
        assert lock["projectionVersion"] == 1
        print("Upgrade path smoke test passed")


if __name__ == "__main__":
    main()
