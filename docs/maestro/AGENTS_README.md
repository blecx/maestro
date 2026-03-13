# Custom Agent Registry

This directory contains repository custom agents (`*.md`) discoverable by Copilot Chat.
These files are the VS Code discovery layer, not the canonical home for workflow logic.

Canonical workflow logic, reusable policies, and approval-profile sources live under `.copilot/`.
Use `.github/agents/*.md` as thin wrappers that point to the relevant `.copilot/skills/*/SKILL.md` source.

## Available Agents

- **[resolve-issue.md](./resolve-issue.md)** - Issue → PR agent with plan-first execution and validation gates.
- **[pr-merge.md](./pr-merge.md)** - Merge PRs safely with CI checks and issue closure workflow.
- **[close-issue.md](./close-issue.md)** - Close issues with template-backed, traceable resolution comments.
- **[create-issue.md](./create-issue.md)** - Create template-compliant issues only (no implementation), with clear acceptance criteria and validation steps.
- **[Plan.md](./Plan.md)** - Produce compact, actionable implementation plans with bounded discovery and issue sizing.

## Runtime Agents

- `workflow` and `maestro-operator` now also use canonical `.copilot/skills/` modules while remaining thin VS Code discovery wrappers.

## Automation Inventory

- **[AUTOMATIONS.md](./AUTOMATIONS.md)** is documentation (an inventory), not a selectable Copilot custom agent.

## Spec Kit-Compatible Command Prompts

- Core Spec Kit workflow command prompts: [`./speckit/`](./speckit/)
- blecs namespace command extensions: [`./blecs/`](./blecs/)

These directories hold slash-command style prompt files and are intentionally separated from `*.md` custom agent definitions.

## Auto-Approve Wiring

Subagents mapped in `.vscode/settings.json` under `chat.tools.subagent.autoApprove` will use the agent name omitting the `.md` extension.
Approval profiles should be authored in `.copilot/config/` and only projected into `.vscode/` when explicitly configured.
