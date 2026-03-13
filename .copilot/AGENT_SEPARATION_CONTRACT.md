# Agent Separation of Concerns Contract

This document acts as a repository-local checklist enforcing what each agent, skill, and script class may and may not own. Its goal is to maintain architectural clarity and prevent logic duplication across the Maestro ecosystem.

## Ownership Classes

### 1. Canonical Workflow Skills (`.copilot/skills/`)
- **May own**: Core business logic for a specific task workflow (e.g., how a PR is merged, how an issue is resolved). Reusable execution checklists and prompts.
- **Must delegate**: User discovery/invocation patterns (to wrapper agents). Actual system execution (to scripts or MCP tools).
- **Must not redefine**: Global policy, repository rules, or hardcoded API credentials.

### 2. Policy / Authority Skills (`.copilot/skills/*-authority/`, `*-policy/`)
- **May own**: High-level repository constraints, UX standards, code conventions, and permission models.
- **Must delegate**: Workflow execution steps (to Canonical Workflow Skills).
- **Must not redefine**: Implementation details of specific workflows. Must remain declarative.

### 3. VS Code Discovery Wrappers (`.github/agents/`)
- **May own**: High-level intent, descriptions, and basic `@agent` invocation syntax for the VS Code UI.
- **Must delegate**: All workflow logic, execution steps, and constraints (to Canonical Workflow Skills in `.copilot/`).
- **Must not redefine**: Any business logic, step-by-step instructions, or policy. Must be "thin" wrappers.

### 4. Runtime / Operator Agents (`agents/` Python implementation)
- **May own**: The programmatic execution framework, LLM orchestration, internal state, and low-level parsing logic.
- **Must delegate**: High-level decision constraints and user prompts (to `.copilot/skills/`).
- **Must not redefine**: Workflow procedures or UI interaction patterns.

### 5. Orchestration / Continuation Agents (e.g., Supervisor / Workflow Routing)
- **May own**: Routing logic, status tracking across multiple sub-agents, and recovery/retry limits.
- **Must delegate**: The actual task execution (to standard Runtime Agents or Bash pipelines).
- **Must not redefine**: The underlying definition of what correct task execution looks like (to workflow skills).

### 6. Projection / Validation Scripts (`scripts/`)
- **May own**: The mechanical application of canonical config into local tools (e.g., updating `.vscode/settings.json`), bash automation, tests, CI hooks.
- **Must delegate**: The source of truth for the config (reading from `.copilot/config/`).
- **Must not redefine**: Policy rules or workflow logic.

## PR Review Checklist

For any PR touching agent architecture or skills:

- [ ] **No Fat Wrappers**: Do `.github/agents/*.md` files contain workflow logic? If yes, move logic to `.copilot/skills/` and make the wrapper thin.
- [ ] **Single Source of Truth**: Does the change duplicate policy or instructions already defined in an authority skill?
- [ ] **Projection Safety**: If a script updates `.vscode/` or local settings, is the baseline config pulled from `.copilot/`?
- [ ] **Infrastructure Boundaries**: Are Python agent changes (`agents/`) truly programmatic, or should they be conversational prompts located in `.copilot/`?
- [ ] **Separation of Concerns**: Does this change mix policy definition with execution routing?

**How to use:** When reviewing an agent or workflow PR, compare the changed files against these classes. Reject PRs that blur these lines (e.g., hardcoding security policy in a python script instead of an authority skill, or adding checklist logic to a `.github/agents` wrapper).
