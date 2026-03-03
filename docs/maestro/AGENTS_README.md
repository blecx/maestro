# Custom Agent Registry

This directory contains repository custom agents (`*.md`) discoverable by Copilot Chat. 
These files have been consolidated from legacy duplicate folders to serve as the single source of truth for all workflows.

## Available Agents

- **[resolve-issue.md](./resolve-issue.md)** - Issue → PR agent with plan-first execution and validation gates.
- **[pr-merge.md](./pr-merge.md)** - Merge PRs safely with CI checks and issue closure workflow.
- **[close-issue.md](./close-issue.md)** - Close issues with template-backed, traceable resolution comments.
- **[tutorial.md](./tutorial.md)** - Create Markdown-only tutorials with strict visual evidence, feature-gap reporting, and duplicate-content audits.
- **[create-issue.md](./create-issue.md)** - Create template-compliant issues only (no implementation), with clear acceptance criteria and validation steps.
- **[Plan.md](./Plan.md)** - Produce compact, actionable implementation plans with bounded discovery and issue sizing.
- **[continue-backend.md](./continue-backend.md)** - Run backend-only continuation loops with guarded PR/merge flow.
- **[continue-phase-2.md](./continue-phase-2.md)** - Run phase-2 continuation loops with review-before-merge policy.
- **[ralph-agent.md](./ralph-agent.md)** - Execute strict spec-kit style issue resolution with specialist review gates.
- **[workflow.md](./workflow.md)** - Legacy workflow-agent wrapper profile for scripted batch runs.
- **[maestro-operator.md](./maestro-operator.md)** - Bridge agent that executes the underlying Python autonomous 'Maestro' workflow.

## Legacy Sub-Agents functioning as Pseudo-Skills (Soon to be moved to `.copilot/skills`)

## Automation Inventory

- **[AUTOMATIONS.md](./AUTOMATIONS.md)** is documentation (an inventory), not a selectable Copilot custom agent. 

## Spec Kit-Compatible Command Prompts

- Core Spec Kit workflow command prompts: [`./speckit/`](./speckit/)
- blecs namespace command extensions: [`./blecs/`](./blecs/)

These directories hold slash-command style prompt files and are intentionally separated from `*.md` custom agent definitions.

## Auto-Approve Wiring

Subagents mapped in `.vscode/settings.json` under `chat.tools.subagent.autoApprove` will use the agent name omitting the `.md` extension.
