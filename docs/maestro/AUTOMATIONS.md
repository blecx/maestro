# Automation Inventory

Canonical inventory of agents, custom agents, and automation entrypoints for this repository.

## 1) Runtime Agents (Python)

Primary source files:

- `agents/autonomous_workflow_agent.py`
- `agents/ralph_agent.py`
- `agents/workflow_agent.py`
- `agents/agent_registry.py`

Alias mapping in `agents/agent_registry.py`:

- `autonomous` -> `AutonomousWorkflowAgent`
- `default` -> `AutonomousWorkflowAgent`
- `ralph` -> `RalphAgent`
- `ralph-agent` -> `RalphAgent`
- `resolve-issue` -> `AutonomousWorkflowAgent`

Execution entrypoints:

- `./scripts/work-issue.py --issue <n> [--agent <alias>]`
- `scripts/agents/workflow` (wrapper to `agents/workflow_agent.py`)

## 2) Custom Chat Agents (`.github/agents/*.md`)

Authority + lifecycle agents:

- `resolve-issue.md`
- `pr-merge.md`
- `close-issue.md`
- `tutorial.md`

Converted wrappers for prompt workflows/runtime profiles:

- `create-issue.md`
- `Plan.md`
- `continue-backend.md`
- `continue-phase-2.md`
- `ralph-agent.md`
- `workflow.md`

## 3) Prompt Workflow Sources (`.github/prompts/agents/*.md`)

These are canonical workflow prompts that drive agent behavior:

- `create-issue.md`
- `Plan.md`
- `continue-backend.md`
- `continue-phase-2.md`
- `resolve-issue-dev.md`
- `ralph-agent.md`
- `pr-merge.md`
- `close-issue.md`
- `tutorial.md`

## 4) VS Code Agent/Automation Wiring

From `.vscode/settings.json`:

- `chat.tools.subagent.autoApprove` includes:
  - `create-issue`, `resolve-issue`, `close-issue`, `pr-merge`, `Plan`, `tutorial`
- `issueagent.customAgent`: `resolve-issue`

From `.vscode/tasks.json` (selected automation tasks):

(Tasks exist as convenience wrappers around the CLI workflows; the primary VS Code entrypoint is the chat participant `@resolve-issue /run`.)

- `📋 Select Next Issue` -> `next-issue`
- `📦 Select Next PR` -> `next-pr`
- `🔀 Merge PR` -> `scripts/prmerge`
- `🚀 Dev Stack: Supervised` -> `scripts/dev_stack_supervisor.py`

## 5) Scripted Workflow Automations

Core orchestration scripts:

- `scripts/work-issue.py`
- `scripts/prmerge`
- `scripts/close-issue.sh`
- `scripts/next-issue.py` (via `./next-issue`)
- `scripts/next-pr.py` (via `./next-pr`)
- `scripts/continue-phase-2.sh`
- `continue-backend` (root command)

## 6) CI/CD Automation

Main backend workflows in `.github/workflows/`:

- `ci.yml`
- `ci-backend.yml`
- `ci-web-ui.yml`
- `cd-backend.yml`
- `cd-smoke.yml`
- `rollback-backend.yml`
- `reusable-client-api-integration.yml`
- `reusable-ghcr-publish.yml`

## 7) Conversion Policy

When a new workflow prompt or runtime profile is added, do all of the following in the same change:

1. Add/update corresponding `.github/agents/*.md` wrapper.
2. Update `.github/agents/README.md`.
3. Update this inventory file.
4. Keep prompt logic canonical in `.github/prompts/agents/` and shared modules.
