#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from _factorylib import resolve_factory_root


def main() -> None:
    factory_root = resolve_factory_root(__file__)
    with tempfile.TemporaryDirectory(prefix="sfvscode-failure-") as tmp:
        host = Path(tmp) / "not-a-git-repo"
        host.mkdir()
        proc = subprocess.run(["python3", str(factory_root / "scripts" / "bootstrap_host.py"), "--target", str(host), "--factory-root", str(factory_root)], capture_output=True, text=True)
        assert proc.returncode != 0
        assert "git repository" in (proc.stderr + proc.stdout)
        print("Failure-mode smoke test passed")


if __name__ == "__main__":
    main()
