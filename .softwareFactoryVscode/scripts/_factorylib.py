from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

FACTORY_NAME = "softwareFactoryVscode"
SCHEMA_VERSION = 1
PROJECTION_VERSION = 1
DEFAULT_INSTALL_PATH = f".{FACTORY_NAME}"
REQUIRED_ENV_VARS = [
    "PROJECT_WORKSPACE_ID",
    "FACTORY_INSTANCE_ID",
    "COMPOSE_PROJECT_NAME",
    "TARGET_WORKSPACE_PATH",
    "FACTORY_AUDIT_DIR",
    "FACTORY_DATA_DIR",
    "FACTORY_CONFIG_DIR",
]
OPTIONAL_ENV_VARS = [
    "FACTORY_ROOT",
    "FACTORY_RUNTIME_ROOT",
    "HOST_FACTORY_DIR",
    "PORT_CONTEXT7",
    "PORT_BASH",
    "PORT_FS",
    "PORT_GIT",
    "PORT_SEARCH",
    "PORT_TEST",
    "PORT_COMPOSE",
    "PORT_DOCS",
    "PORT_GITHUB",
    "PORT_MOCK_LLM",
    "MEMORY_MCP_PORT",
    "AGENT_BUS_PORT",
    "APPROVAL_GATE_PORT",
]
COMPOSE_FILES = [
    "compose/docker-compose.factory.yml",
    "compose/docker-compose.context7.yml",
    "compose/docker-compose.mcp-bash-gateway.yml",
    "compose/docker-compose.repo-fundamentals.yml",
    "compose/docker-compose.mcp-devops.yml",
    "compose/docker-compose.mcp-offline-docs.yml",
    "compose/docker-compose.mcp-github-ops.yml",
]
@dataclass(frozen=True)
class RuntimeEnv:
    values: dict[str, str]
    project_id: str
    env_file: Path


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def compute_project_id(target_path: Path) -> str:
    digest = hashlib.sha256(str(target_path.resolve()).encode("utf-8")).hexdigest()
    return digest[:10]


def resolve_factory_root(script_file: str | Path) -> Path:
    return Path(script_file).resolve().parent.parent


def ensure_git_repo(target_repo: Path) -> None:
    if not (target_repo / ".git").exists():
        raise SystemExit(f"Target is not a git repository: {target_repo}")


def ensure_host_layout(target_repo: Path) -> dict[str, Path]:
    base = target_repo / ".tmp" / FACTORY_NAME
    runtime = base / "runtime"
    audit = base / "audit"
    data = base / "data"
    config = base / "config"
    for path in (base, runtime, audit, data, config):
        path.mkdir(parents=True, exist_ok=True)
    return {
        "base": base,
        "runtime": runtime,
        "audit": audit,
        "data": data,
        "config": config,
    }


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def merge_json(base: object, override: object) -> object:
    if isinstance(base, dict) and isinstance(override, dict):
        merged = dict(base)
        for key, value in override.items():
            merged[key] = merge_json(merged.get(key), value) if key in merged else value
        return merged
    if isinstance(base, list) and isinstance(override, list):
        return override
    return override


def project_file(source: Path, destination: Path, *, merge_json_payload: bool = False) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if merge_json_payload and destination.exists():
        merged = merge_json(
            json.loads(source.read_text(encoding="utf-8")),
            json.loads(destination.read_text(encoding="utf-8")),
        )
        destination.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")
        return
    shutil.copy2(source, destination)


def build_runtime_env(target_repo: Path, factory_root: Path, instance_id: str = "default") -> RuntimeEnv:
    layout = ensure_host_layout(target_repo)
    project_id = compute_project_id(target_repo)
    runtime_dir = layout["runtime"] / project_id
    runtime_dir.mkdir(parents=True, exist_ok=True)
    env_file = runtime_dir / ".env.generated"
    ports_base = (int(project_id[:6], 16) % 10000) + 20000
    values = {
        "PROJECT_WORKSPACE_ID": project_id,
        "FACTORY_INSTANCE_ID": instance_id,
        "COMPOSE_PROJECT_NAME": f"software-factory-{project_id}-{instance_id}",
        "TARGET_WORKSPACE_PATH": str(target_repo.resolve()),
        "FACTORY_AUDIT_DIR": str((layout["audit"] / project_id).resolve()),
        "FACTORY_DATA_DIR": str((layout["data"] / project_id).resolve()),
        "FACTORY_CONFIG_DIR": str((layout["config"] / project_id).resolve()),
        "FACTORY_ROOT": str(factory_root.resolve()),
        "FACTORY_RUNTIME_ROOT": str((factory_root / "factory_runtime").resolve()),
        "HOST_FACTORY_DIR": str((target_repo / DEFAULT_INSTALL_PATH).resolve()),
        "PORT_CONTEXT7": str(ports_base + 10),
        "PORT_BASH": str(ports_base + 11),
        "PORT_GIT": str(ports_base + 12),
        "PORT_SEARCH": str(ports_base + 13),
        "PORT_FS": str(ports_base + 14),
        "PORT_COMPOSE": str(ports_base + 15),
        "PORT_TEST": str(ports_base + 16),
        "PORT_DOCS": str(ports_base + 17),
        "PORT_GITHUB": str(ports_base + 18),
        "PORT_MOCK_LLM": str(ports_base + 19),
        "MEMORY_MCP_PORT": str(ports_base + 20),
        "AGENT_BUS_PORT": str(ports_base + 21),
        "APPROVAL_GATE_PORT": str(ports_base + 22),
    }
    for key in ("FACTORY_AUDIT_DIR", "FACTORY_DATA_DIR", "FACTORY_CONFIG_DIR"):
        Path(values[key]).mkdir(parents=True, exist_ok=True)
    for extra_path in (
        Path(values["FACTORY_DATA_DIR"]) / "memory",
        Path(values["FACTORY_DATA_DIR"]) / "agent-bus",
        Path(values["FACTORY_DATA_DIR"]) / "offline-docs",
        Path(values["FACTORY_AUDIT_DIR"]) / "bash-gateway",
        Path(values["FACTORY_AUDIT_DIR"]) / "docker-compose",
        Path(values["FACTORY_AUDIT_DIR"]) / "test-runner",
        Path(values["FACTORY_AUDIT_DIR"]) / "github-ops",
    ):
        extra_path.mkdir(parents=True, exist_ok=True)
    env_file.write_text("".join(f"{k}={v}\n" for k, v in values.items()), encoding="utf-8")
    return RuntimeEnv(values=values, project_id=project_id, env_file=env_file)


def write_lock_file(target_repo: Path, *, install_path: str = DEFAULT_INSTALL_PATH) -> Path:
    payload = {
        "factoryRepo": FACTORY_NAME,
        "factoryVersion": "v0.1.0-local",
        "schemaVersion": SCHEMA_VERSION,
        "installPath": install_path,
        "enabledModules": [
            "mcp-runtime",
            "approval-gate",
            "self-contained-tooling",
        ],
        "projectionVersion": PROJECTION_VERSION,
        "lastUpgrade": utc_now(),
    }
    lock_file = target_repo / ".factory.lock.json"
    write_json(lock_file, payload)
    return lock_file


def ensure_factory_env(target_repo: Path, factory_root: Path) -> Path:
    example = factory_root / ".env.example"
    target = target_repo / ".factory.env"
    if not target.exists():
        shutil.copy2(example, target)
    return target


def run(cmd: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=check)


def compose_command(factory_root: Path, env_file: Path) -> list[str]:
    cmd = ["docker", "compose", "--env-file", str(env_file)]
    for compose_file in COMPOSE_FILES:
        cmd.extend(["-f", str(factory_root / compose_file)])
    return cmd


def verified_python() -> str:
    return os.environ.get("PYTHON", "python3")


def parse_env_file(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key] = value
    return data


def find_forbidden_tokens(root: Path, tokens: Iterable[str], *, allow_paths: set[str]) -> list[str]:
    violations: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if relative in allow_paths or any(relative.startswith(prefix.rstrip("*").rstrip("/")) for prefix in allow_paths if prefix.endswith("*")):
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            continue
        for token in tokens:
            if token in content:
                violations.append(f"{relative}: contains '{token}'")
                break
    return violations
