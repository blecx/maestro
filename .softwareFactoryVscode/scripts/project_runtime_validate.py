#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from _factorylib import REQUIRED_ENV_VARS, build_runtime_env, parse_env_file, resolve_factory_root


HEALTH_ENDPOINTS = {
    "context7": "/mcp",
    "approval_gate": "/health",
}


def check_http(url: str) -> bool:
    try:
        with urlopen(url, timeout=2) as response:
            return response.status < 500
    except URLError:
        return False
    except Exception:
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate softwareFactoryVscode runtime wiring")
    parser.add_argument("--target", default=".", help="Host repository root")
    parser.add_argument("--instance-id", default="default", help="Factory instance suffix")
    args = parser.parse_args()

    target_repo = Path(args.target).resolve()
    runtime_env = build_runtime_env(target_repo, resolve_factory_root(__file__), args.instance_id)
    values = parse_env_file(runtime_env.env_file)

    missing = [key for key in REQUIRED_ENV_VARS if key not in values]
    if missing:
        raise SystemExit(f"Missing runtime env keys: {missing}")

    result = {
        "env_file": str(runtime_env.env_file),
        "project_id": runtime_env.project_id,
        "checks": {
            "target_workspace_exists": target_repo.exists(),
            "factory_tmp_exists": (target_repo / ".tmp" / "softwareFactoryVscode").exists(),
            "context7_reachable": check_http(f"http://127.0.0.1:{values['PORT_CONTEXT7']}{HEALTH_ENDPOINTS['context7']}"),
            "approval_gate_reachable": check_http(f"http://127.0.0.1:{values['APPROVAL_GATE_PORT']}{HEALTH_ENDPOINTS['approval_gate']}"),
        },
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
