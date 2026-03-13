# Automation Architecture

Current source-of-truth inventory for agentic workflows, editor projections, and runtime automation in this repository.

## Ownership Model

The repository now uses an explicit layered model.

1. `.copilot/`
   Canonical home for workflow logic, reusable skills, policy modules, and machine-readable configuration sources.
2. `.github/agents/`
   Thin VS Code discovery wrappers so custom agents show up in Copilot Chat.
3. `.vscode/`
   Editor-local runtime settings and convenience tasks only. It should not be the canonical home for workflow policy.
4. `scripts/`
   Explicit setup and execution entrypoints that project canonical `.copilot` configuration into local tooling when needed.
5. `agents/`
   Python runtime adapters for CLI and autonomous execution paths.

## Canonical Sources

### Workflow Logic

- `.copilot/skills/resolve-issue-workflow/SKILL.md`
- `.copilot/skills/pr-merge-workflow/SKILL.md`
- `.copilot/skills/issue-creation-workflow/SKILL.md`
- `.copilot/skills/continue-backend-workflow/SKILL.md`
- `.copilot/skills/continue-phase-2-workflow/SKILL.md`
- `.copilot/skills/tutorial-writer-expert/SKILL.md`
- `.copilot/skills/ralph-skills-review/SKILL.md`
- `.copilot/skills/plan-workflow/SKILL.md`
- `.copilot/skills/close-issue-workflow/SKILL.md`
- `.copilot/skills/workflow-runtime/SKILL.md`
- `.copilot/skills/maestro-operator-workflow/SKILL.md`

### Policy and Configuration

- `.copilot/skills/ux-delegation-policy/SKILL.md`
- `.copilot/config/vscode-approval-profiles.json`
- `.copilot/config/vscode-agent-settings.json`

## VS Code Discovery Wrappers

These files should remain thin and point back to `.copilot`:

- `.github/agents/resolve-issue.md`
- `.github/agents/pr-merge.md`
- `.github/agents/create-issue.md`
- `.github/agents/continue-backend.md`
- `.github/agents/continue-phase-2.md`
- `.github/agents/tutorial.md`
- `.github/agents/ralph-agent.md`
- `.github/agents/Plan.md`
- `.github/agents/close-issue.md`
- `.github/agents/maestro-operator.md`
- `.github/agents/workflow.md`

## Explicit Projection Scripts

Use these scripts instead of hidden editor mutation.

- `scripts/setup-vscode-autoapprove.py`
  Projects terminal approval profiles from `.copilot/config/vscode-approval-profiles.json`.
- `scripts/setup-vscode-agent-settings.py`
  Projects explicit agent defaults and MCP wiring from `.copilot/config/vscode-agent-settings.json`.
- `scripts/setup-low-approval.sh`
  Convenience shell wrapper around the approval profile script.

## Workspace Settings Scope

Committed `.vscode/settings.json` should contain only editor-local baseline settings and the projected values that a developer explicitly chooses to apply. It is no longer the authority for:

- agent selection,
- subagent auto-approve policy,
- MCP server registry,
- broad approval profile definitions.

## Runtime Automation

### Python Runtime Agents

- `agents/agent_registry.py`
- `agents/maestro_adapter.py`
- `agents/ralph_agent.py`
- `agents/workflow_agent.py`

### CLI and Loop Entrypoints

- `scripts/work-issue.py`
- `scripts/prmerge`
- `scripts/close-issue.sh`
- `scripts/next-issue.py`
- `scripts/next-pr.py`
- `scripts/continue-backend.sh`
- `scripts/continue-phase-2.sh`

These remain supported execution adapters, but they are not the source of truth for workflow intent.

## Fresh Clone Bootstrap

For the explicit developer bootstrap flow, use:

- `docs/maestro/BOOTSTRAP.md`

That document is the operational guide for a fresh clone and should be kept in sync with the projection scripts and tasks.

## Deprecated Assumptions Removed

The following are no longer valid assumptions and should not be reintroduced:

- `.github/prompts/agents/` as the canonical workflow source.
- `agents/autonomous_workflow_agent.py` as the runtime default.
- hidden folder-open setup that silently enables low-friction approvals.
- `.vscode/` as the canonical home for agent policy.
- `docs/maestro/APPROVAL_PROFILES.md` - Explicit guide to trust boundaries and profile selection.
