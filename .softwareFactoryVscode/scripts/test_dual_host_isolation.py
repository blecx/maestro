#!/usr/bin/env python3
from __future__ import annotations

import tempfile
from pathlib import Path

from _factorylib import build_runtime_env, resolve_factory_root


def main() -> None:
    factory_root = resolve_factory_root(__file__)
    with tempfile.TemporaryDirectory(prefix="sfvscode-a-") as tmp_a, tempfile.TemporaryDirectory(prefix="sfvscode-b-") as tmp_b:
        host_a = Path(tmp_a)
        host_b = Path(tmp_b)
        env_a = build_runtime_env(host_a, factory_root, "a")
        env_b = build_runtime_env(host_b, factory_root, "b")
        assert env_a.project_id != env_b.project_id
        assert env_a.values["COMPOSE_PROJECT_NAME"] != env_b.values["COMPOSE_PROJECT_NAME"]
        assert env_a.values["PORT_CONTEXT7"] != env_b.values["PORT_CONTEXT7"]
        print("Dual host isolation smoke test passed")


if __name__ == "__main__":
    main()
