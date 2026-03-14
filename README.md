# Maestro AI Framework

Maestro is a standalone backend agent framework designed to operate within GitHub Copilot and VS Code environments.
It uses a multi-model architecture alongside Model Context Protocol (MCP) servers to write code, enforce workflow constraints, execute testing pipelines, and operate against feature branches.

This repository serves as the **Toolchain Trunk**. It is meant to be merged/overlaid into any target repository to immediately enable advanced Copilot execution rails.

---

## 🚀 Quick Setup (For New Host Projects)

When integrating Maestro into a new project, follow these steps to securely sync the files without polluting your app's core architecture.

### 1. Initial Sync

To pull the Maestro toolchain directly into your existing app repository, run the makefile sync operation.
*(You only need to copy the Makefile manually during the first initialization)*:

```bash
wget https://raw.githubusercontent.com/blecx/maestro/main/Makefile -O Makefile.maestro
make -f Makefile.maestro sync-maestro
```

### 2. Environment Setup

The AI architecture runs locally via Python and Docker. Generate the python environment for the agent runner:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r agents/requirements.txt  # Or similar dependency root
```

*Note: Ensure your `.env` contains the required keys for MCP tools (e.g. `CONTEXT7_API_KEY`).*

### 3. Start MCP Context Servers

Maestro agents are blind without Context Gateways (MCPs). Start the dockerized MCP suite using the automated `Makefile`:

```bash
make mcp-up
```

*(To stop them later, run `make mcp-down`)*.

---

## Architecture Documentation

The repository now uses a `.copilot`-first ownership model for workflow logic and agent configuration, with `.github/agents` kept as thin discovery wrappers for VS Code.

Primary docs:

- **[Automation Architecture](docs/maestro/AUTOMATIONS.md)** - ownership model, canonical sources, wrappers, and runtime entrypoints.
- **[Fresh Clone Bootstrap](docs/maestro/BOOTSTRAP.md)** - explicit setup and projection steps for a new workspace.
- **[VS Code Settings Guidance](docs/maestro/VSCODE-GLOBAL-SETTINGS.md)** - projection-first guidance for workspace and optional user settings.
- **[Agents Overview](docs/maestro/AGENTS_README.md)** - current Copilot custom-agent registry and wrapper model.

---

## Agent Typology

Maestro enforces a strict boundary between development-time aids and runtime applications:

- **Software Factory Agents** (residing in `.github/`, `.copilot/`) assist developers in building the app.
- **Maestro Agents** (residing in `agents/`, `apps/`) are the runtime orchestrators that serve the end user.

Please ensure prompts for Maestro Agents are placed in `agents/prompts/` and never commingled with developer tooling.
