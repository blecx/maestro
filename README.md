# Maestro AI Framework

Maestro is a standalone, backend autonomous agent framework natively designed to operate within GitHub Copilot and VS Code environments. 
It utilizes a multi-model architecture alongside Model Context Protocol (MCP) servers to write code, conduct UI design constraints, execute testing pipelines autonomously, and commit to feature branches.

This repository serves as the **Toolchain Trunk**. It is meant to be merged/overlaid into any target repository to immediately enable advanced Copilot execution rails.

---

## 🚀 Quick Setup (For New Host Projects)

When integrating Maestro into a new project, follow these steps to securely sync the files without polluting your app's core architecture.

### 1. Initial Sync
To pull the Maestro toolchain directly into your existing app repository, simply run the makefile sync operation. 
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

All documentation regarding the AI operations, auto-approve VS Code settings, or custom agent lists previously stored at the root of target apps has been isolated here:
- **[AUTOMATIONS.md](docs/maestro/AUTOMATIONS.md)** - Full list of Python execution roots and triggers.
- **[VSCode Settings Requirements](docs/maestro/VSCODE-GLOBAL-SETTINGS.md)** - Explains how `chat.tools.subagent.autoApprove` handles the workflow.
- **[Prompts / Agents Overview](docs/maestro/AGENTS_README.md)** - List of Copilot Custom Agents.
