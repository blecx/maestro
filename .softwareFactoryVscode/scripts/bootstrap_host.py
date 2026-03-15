#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

from _factorylib import ensure_factory_env, ensure_git_repo, ensure_host_layout, resolve_factory_root, verified_python, write_lock_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Bootstrap a host repository for softwareFactoryVscode")
    parser.add_argument("--target", default=".", help="Host repository root")
    parser.add_argument("--factory-root", default="", help="Factory repository root")
    args = parser.parse_args()

    target_repo = Path(args.target).resolve()
    factory_root = Path(args.factory_root).resolve() if args.factory_root else resolve_factory_root(__file__)

    ensure_git_repo(target_repo)
    ensure_host_layout(target_repo)
    lock_file = write_lock_file(target_repo)
    env_file = ensure_factory_env(target_repo, factory_root)

    print(f"Created {lock_file.relative_to(target_repo)}")
    print(f"Created {env_file.relative_to(target_repo)}")
    print("Tool-owned VS Code, Copilot, and GitHub files remain inside the hidden factory tree and are not projected into the host repository")

    python_bin = shutil.which(verified_python())
    docker_bin = shutil.which("docker")
    if not python_bin:
        raise SystemExit("Python 3 is required but was not found in PATH")
    if not docker_bin:
        raise SystemExit("Docker is required but was not found in PATH")

    version = subprocess.run([python_bin, "--version"], capture_output=True, text=True, check=True)
    print(version.stdout.strip() or version.stderr.strip())
    print("Docker detected")


if __name__ == "__main__":
    main()
