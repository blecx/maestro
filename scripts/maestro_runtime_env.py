#!/usr/bin/env python3
import os
import hashlib
import json
import argparse
from pathlib import Path

def generate_project_id(target_path: Path) -> str:
    path_str = str(target_path.resolve())
    return hashlib.md5(path_str.encode()).hexdigest()[:8]

def get_instance_id() -> str:
    return os.environ.get("MAESTRO_INSTANCE_ID", "default")

def main():
    parser = argparse.ArgumentParser(description="Generate Maestro isolated runtime environment")
    parser.add_argument("--target", type=str, default=".", help="Path to the target repository")
    parser.add_argument("--quiet", action="store_true", help="Only output the env file path")
    args = parser.parse_args()

    target_path = Path(args.target).resolve()
    if not target_path.exists():
        if not args.quiet: print(f"Error: Target path {target_path} does not exist.")
        exit(1)

    project_id = generate_project_id(target_path)
    instance_id = get_instance_id()
    project_name = f"maestro-{project_id}-{instance_id}"

    runtime_dir = target_path / ".tmp" / "maestro" / "runtime" / project_id
    runtime_dir.mkdir(parents=True, exist_ok=True)
    
    env_file = runtime_dir / ".env.generated"
    
    ports_base = int(project_id, 16) % 10000 + 10000 # Generate deterministic base port between 10000 and 19999
    
    env_vars = {
        "PROJECT_WORKSPACE_ID": project_id,
        "MAESTRO_INSTANCE_ID": instance_id,
        "COMPOSE_PROJECT_NAME": project_name,
        "TARGET_WORKSPACE_PATH": str(target_path),
        "MAESTRO_AUDIT_DIR": str(target_path / ".tmp" / "maestro" / "audit" / project_id),
        "MAESTRO_DATA_DIR": str(target_path / ".tmp" / "maestro" / "data" / project_id),
        
        # Specific ports mapped in compose files
        "PORT_CONTEXT7": str(ports_base + 10),
        "PORT_BASH": str(ports_base + 11),
        "PORT_FS": str(ports_base + 12),
        "PORT_GIT": str(ports_base + 13),
        "PORT_SEARCH": str(ports_base + 14),
        "PORT_TEST": str(ports_base + 15),
        "PORT_COMPOSE": str(ports_base + 16),
        "PORT_DOCS": str(ports_base + 17),
        "PORT_GITHUB": str(ports_base + 18),
        "PORT_TUI": str(ports_base + 19),
        "MEMORY_MCP_PORT": str(ports_base + 20),
        "AGENT_BUS_PORT": str(ports_base + 21),
        "APPROVAL_GATE_PORT": str(ports_base + 22)
    }

    # Ensure directories exist
    Path(env_vars["MAESTRO_AUDIT_DIR"]).mkdir(parents=True, exist_ok=True)
    Path(env_vars["MAESTRO_DATA_DIR"]).mkdir(parents=True, exist_ok=True)

    with open(env_file, 'w') as f:
        for k, v in env_vars.items():
            f.write(f"{k}={v}\n")
            
    if args.quiet:
        print(str(env_file))
    else:
        print(f"Generated environment for project {project_id} at {env_file}")
        print("Environment variables:")
        for k, v in env_vars.items():
            print(f"  {k}={v}")

if __name__ == "__main__":
    main()
