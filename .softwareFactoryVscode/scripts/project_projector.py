#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from _factorylib import DEFAULT_INSTALL_PATH, resolve_factory_root


def main() -> None:
    parser = argparse.ArgumentParser(description="Report the hidden-tree workspace isolation model")
    parser.add_argument("--target", default=".", help="Host repository root")
    parser.add_argument("--factory-root", default="", help="Factory repository root; defaults to this repo")
    args = parser.parse_args()

    target_repo = Path(args.target).resolve()
    factory_root = Path(args.factory_root).resolve() if args.factory_root else resolve_factory_root(__file__)

    print("No workspace artifacts are projected into the host repository.")
    print(f"Tool workspace remains self-contained under: {factory_root}")
    print(f"Factory expected at: {DEFAULT_INSTALL_PATH}")


if __name__ == "__main__":
    main()
