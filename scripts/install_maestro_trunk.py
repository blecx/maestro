#!/usr/bin/env python3
import os
import shutil
import argparse
from pathlib import Path

def copy_asset(src: Path, dest: Path) -> None:
    if not src.exists():
        print(f"Warning: Source {src} does not exist, skipping.")
        return
    
    if src.is_dir():
        shutil.copytree(src, dest, dirs_exist_ok=True)
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
    print(f"Copied {src} to {dest}")

def main():
    parser = argparse.ArgumentParser(description="Install Maestro Software Factory Trunk")
    parser.add_argument("target_repo", type=str, help="Path to the target repository")
    args = parser.parse_args()

    target_path = Path(args.target_repo).resolve()
    if not target_path.exists():
        print(f"Error: Target path {target_path} does not exist.")
        exit(1)

    print(f"Installing Maestro trunk into {target_path}...")
    
    components = [
        "agents", "apps", "docker", "scripts", 
        ".copilot/skills", ".copilot/config", ".github/agents",
        "hooks", "configs"
    ]
    
    files = [
        "docker-compose.context7.yml", "docker-compose.maestro.yml", 
        "docker-compose.mcp-bash-gateway.yml", "docker-compose.mcp-devops.yml",
        "docker-compose.mcp-github-ops.yml", "docker-compose.mcp-offline-docs.yml",
        "docker-compose.repo-fundamentals-mcp.yml", "Makefile", "requirements.txt",
        ".env.maestro.example", "setup.sh"
    ]

    source_path = Path(__file__).parent.parent.resolve()

    for component in components:
        src = source_path / component
        dest = target_path / component
        copy_asset(src, dest)

    for file in files:
        src = source_path / file
        dest = target_path / file
        copy_asset(src, dest)

    print(f"Successfully installed Maestro trunk to {target_path}")

if __name__ == "__main__":
    main()
