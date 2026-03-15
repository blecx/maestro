#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from _factorylib import build_runtime_env, compose_command, resolve_factory_root


def main() -> None:
    parser = argparse.ArgumentParser(description="Start softwareFactoryVscode runtime services for a host repository")
    parser.add_argument("--target", default=".", help="Host repository root")
    parser.add_argument("--instance-id", default="default", help="Factory instance suffix")
    parser.add_argument("--build", action="store_true", help="Build images before starting")
    args = parser.parse_args()

    target_repo = Path(args.target).resolve()
    factory_root = resolve_factory_root(__file__)
    runtime_env = build_runtime_env(target_repo, factory_root, args.instance_id)

    cmd = compose_command(factory_root, runtime_env.env_file) + ["up"]
    if args.build:
        cmd.append("--build")
    cmd.append("-d")

    subprocess.run(cmd, check=True)
    print(f"Runtime started for {runtime_env.project_id}")


if __name__ == "__main__":
    main()
