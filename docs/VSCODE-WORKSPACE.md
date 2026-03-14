# VS Code Workspace Configuration

This document defines the canonical VS Code workspace configuration required to preserve the intended developer, automation, and AI Copilot workflow within host repositories.

## Purpose

To ensure seamless integration with the Software Factory, we specify an explicit VS Code extension matrix and standard workspace settings that project into host repositories. This ensures tool parity, AI agent usability, and codebase consistency.

## 1. VS Code Extension Matrix

### Hard-Required Extensions

These are essential for core factory functionality, AI workflows, and proper interpretation of repository directives:

* **GitHub.copilot** - Base completion and Copilot AI infrastructure.
* **GitHub.copilot-chat** - Chat participant infrastructure, vital for routing to custom agents and workflows.
* **ms-python.python** - Required to properly load Python-based orchestration hooks and validation boundaries.
* **ms-python.vscode-pylance** - High-performance language server required for type-checking and AI grounding context.

### Recommended Extensions

Not strictly required to boot the application stack, but strongly recommended to preserve full developer ergonomics and the automation-centric workflow:

* **ms-vscode-remote.remote-containers** - Provides native dev-container experiences for sandbox testing.
* **ms-azuretools.vscode-docker** - Critical for viewing, starting, and inspecting internal Docker networks for the MCP services.
* **GitHub.vscode-pull-request-github** - Supports the highly recommended "Plan → Issues → PRs" branching model natively within VS Code.
* **dbaeumer.vscode-eslint** & **esbenp.prettier-vscode** - Recommended for host repositories utilizing TypeScript/JavaScript.

### Optional Extensions

These extensions can enhance the environment further but hold no hard significance to factory automation:

* Formatter plugins (e.g., `tamasfe.even-better-toml`).
* Any explicitly future-adopted Context7 editor sidecar extensions (Context7 is primarily delivered via direct MCP network wiring, rather than a mandatory extension UI mapping).

### Deprecated / Unwanted Extensions

* **maestro.issueagent** - This legacy workspace-local extension is explicitly not carried over to ensure package neutrality from `blecx/maestro`. It is projected into `unwantedRecommendations`. If equivalent participant functionality is reintroduced later, an entirely new normalized extension mapping will supersede this.

## 2. Setting up the Environment

The factory projection mechanism handles inserting these extensions into the target host repository automatically.

During `scripts/bootstrap_host.py` execution, the target workspace `.vscode/extensions.json` is generated/modified to reflect exactly what is mandated above.

## 3. Terminal & Subagent Policies

To ensure seamless continuous AI operations and autonomous deployments, standard policies are projected into the `.vscode/settings.json`:

* The workspace should set `"chat.tools.terminal.autoApprove": true` to allow continuous CLI execution for verified orchestration commands if standard within the factory node.
* The workspace should set `"chat.tools.subagent.autoApprove": true` carefully following container constraints.
* MCP Server wiring configurations must bridge the local container network without hardcoding absolute paths.
