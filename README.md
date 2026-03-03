# Maestro AI Framework

Maestro is a standalone, backend autonomous agent framework natively designed to operate within GitHub Copilot and VS Code environments. 
It utilizes a multi-model architecture alongside Model Context Protocol (MCP) servers to write code, conduct UI design constraints, execute testing pipelines autonomously, and commit to feature branches.

This repository serves as the **Toolchain Trunk**. It is meant to be merged/overlaid into any target repository (like the ISO 21500 ProjectBuilder) to immediately enable advanced Copilot execution rails.

## Architecture Documentation

All documentation regarding the AI operations, auto-approve VS Code settings, or custom agent lists previously stored at the root of target apps has been isolated here:
- [AUTOMATIONS.md](docs/maestro/AUTOMATIONS.md) - Full list of Python execution roots and triggers.
- [VSCode Settings Requirements](docs/maestro/VSCODE-GLOBAL-SETTINGS.md)
- [Prompts / Agents Overview](docs/maestro/AGENTS_README.md)

## How to Initialize this toolchain on a new Repo

1. Clone/Sync this trunk into your target directory.
2. Initialize the Python environment:
   ```bash
   ./setup-ai-pipeline.sh
   # (Note: Set up script is needed for root dependencies depending on your OS)
   ```
3. Boot the context logic using:
   ```bash
   docker compose -f docker-compose.mcp-memory-bus.yml up -d
   ```
4. Configure `.env` mapping variables like `CONTEXT7_API_KEY`.
