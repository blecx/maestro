# VS Code Workspace

## Canonical workspace contract

The package ships canonical workspace JSON templates for the tool working tree itself.

Canonical sources:

- `.vscode/settings.json`
- `.vscode/tasks.json`
- `.vscode/extensions.json`

Isolation rules:

- these files stay inside `.softwareFactoryVscode/.vscode/`
- bootstrap does not write them into the host repository
- host-project `.vscode/` remains owned by the host repository

## MCP wiring expectations

`.vscode/settings.json` defines local MCP endpoints for:

- Context7
- bash gateway
- git
- search
- filesystem
- docker compose
- test runner
- offline docs
- github ops

## Auto-approve policy expectations

The workspace contract preserves:

- terminal auto-approve rules for low-risk development commands
- subagent auto-approve for selected workflows

## Required task definitions

`.vscode/tasks.json` includes at minimum:

- `⚙️ Factory: Bootstrap Host`
- `🧬 Factory: Generate Runtime Env`
- `🚀 Factory: Runtime Up`
- `🛑 Factory: Runtime Down`
- `✅ Factory: Validate Runtime`

## Extension recommendations

### Hard-required external extensions

- `GitHub.copilot`
- `GitHub.copilot-chat`
- `ms-python.python`
- `ms-python.vscode-pylance`

### Recommended external extensions

- `dbaeumer.vscode-eslint`
- `esbenp.prettier-vscode`
- `GitHub.vscode-pull-request-github`
- `ms-vscode-remote.remote-containers`
- `ms-azuretools.vscode-docker`

### Optional extensions

- future Context7 editor-side extension, if adopted later
- language-specific extensions for host-project stacks
- user-preference productivity tools

### Deprecated / not carried over by default

- workspace-local `issueagent` extensions from the source repository

The package does not ship a replacement workspace-local `issueagent` extension. If one is introduced later, it must use a package-owned identity and be documented explicitly.

## External vs workspace-local extensions

This package currently depends on external marketplace extensions only. It does **not** ship a replacement workspace-local `issueagent` extension.

## Why Context7 is MCP-first

Context7 is delivered primarily through MCP wiring because the runtime contract depends on a project-scoped local service. An editor extension may be added later, but it is optional unless a future workflow explicitly requires it.

## Concrete `.vscode/extensions.json` shape

```json
{
  "recommendations": [
    "GitHub.copilot",
    "GitHub.copilot-chat",
    "ms-python.python",
    "ms-python.vscode-pylance",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "GitHub.vscode-pull-request-github",
    "ms-vscode-remote.remote-containers",
    "ms-azuretools.vscode-docker"
  ]
}
```
