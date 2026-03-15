# Copilot Configuration Ownership

`.copilot/` is the canonical home for agent workflow logic, reusable skills, and local configuration sources that should not be authored directly in `.vscode/`.

## Ownership Model

- `skills/`: canonical workflow logic, policy modules, authorities, and reusable checklists.
- `config/`: machine-readable configuration sources used to generate or reconcile local editor settings.
  - `vscode-approval-profiles.json`: terminal approval profiles only.
  - `vscode-agent-settings.json`: explicit agent defaults, MCP wiring, and subagent policy.
- runtime-oriented skills such as `workflow-runtime` and the runtime-operator workflow also live here when the runtime wrapper should remain discoverable in VS Code but the behavior contract should still be canonicalized.

## Projection Layers

- `.github/agents/`: thin discovery wrappers so custom agents still show up in VS Code.
- `.vscode/`: editor-local runtime settings and optional convenience tasks only. Broad approval policy and hidden bootstrap behavior should not be authored here directly.
- `scripts/`: explicit setup or execution entrypoints that project canonical `.copilot` configuration into local tooling when needed.

## Current Transition Rule

When a workflow or policy is changed, update `.copilot/` first. Only then update any wrapper, script, or workspace projection that depends on it.

Explicit projection commands now include:

- `scripts/setup-vscode-autoapprove.py` for terminal approval profiles.
- `scripts/setup-vscode-agent-settings.py` for workspace agent defaults.

## Architectural Guidelines

For rules regarding separation of concerns across agents, workflow skills, scripts, and policy files, see the [Agent Separation of Concerns Contract](./AGENT_SEPARATION_CONTRACT.md). Review this checklist before submitting or approving PRs touching agent architecture.
