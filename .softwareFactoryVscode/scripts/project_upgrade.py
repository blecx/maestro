#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from _factorylib import ensure_factory_env, load_json, resolve_factory_root, utc_now, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Refresh softwareFactoryVscode host runtime metadata")
    parser.add_argument("--target", default=".", help="Host repository root")
    parser.add_argument("--factory-root", default="", help="Factory repository root")
    args = parser.parse_args()

    target_repo = Path(args.target).resolve()
    factory_root = Path(args.factory_root).resolve() if args.factory_root else resolve_factory_root(__file__)

    ensure_factory_env(target_repo, factory_root)

    lock_path = target_repo / ".factory.lock.json"
    lock = load_json(lock_path, {})
    lock["lastUpgrade"] = utc_now()
    lock["projectionVersion"] = 1
    lock.setdefault("factoryRepo", "softwareFactoryVscode")
    write_json(lock_path, lock)

    print("No tool-owned workspace artifacts were projected into the host repository")
    print(f"Updated {lock_path.relative_to(target_repo)}")


if __name__ == "__main__":
    main()
