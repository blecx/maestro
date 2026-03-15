#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from _factorylib import build_runtime_env, resolve_factory_root


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate isolated runtime environment for a host repository")
    parser.add_argument("--target", default=".", help="Host repository root")
    parser.add_argument("--instance-id", default="default", help="Factory instance suffix")
    parser.add_argument("--quiet", action="store_true", help="Print only env file path")
    args = parser.parse_args()

    target_repo = Path(args.target).resolve()
    runtime_env = build_runtime_env(target_repo, resolve_factory_root(__file__), instance_id=args.instance_id)

    if args.quiet:
        print(runtime_env.env_file)
        return

    print(f"Generated env file: {runtime_env.env_file}")
    for key, value in runtime_env.values.items():
        print(f"{key}={value}")


if __name__ == "__main__":
    main()
