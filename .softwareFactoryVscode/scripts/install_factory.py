#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from _factorylib import DEFAULT_INSTALL_PATH, resolve_factory_root


def main() -> None:
    parser = argparse.ArgumentParser(description="Install softwareFactoryVscode into a host repository")
    parser.add_argument("target_repo", help="Host repository path")
    parser.add_argument("--install-path", default=DEFAULT_INSTALL_PATH, help="Nested install path inside the host repo")
    args = parser.parse_args()

    target_repo = Path(args.target_repo).resolve()
    install_root = target_repo / args.install_path
    install_root.parent.mkdir(parents=True, exist_ok=True)

    factory_root = resolve_factory_root(__file__)
    if install_root.exists():
        print(f"Factory already present at {install_root}")
    else:
        subprocess.run(["cp", "-R", str(factory_root), str(install_root)], check=True)
        print(f"Installed factory to {install_root}")

    bootstrap = install_root / "scripts" / "bootstrap_host.py"
    subprocess.run(["python3", str(bootstrap), "--target", str(target_repo), "--factory-root", str(install_root)], check=True)


if __name__ == "__main__":
    main()
