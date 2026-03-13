# Copilot Approval Profiles

## Objective

These profiles dictate the auto-approval boundaries for subagents and terminal commands. Our architecture ensures that "safe", "trusted workflow", and "low-friction" are meaningfully apart.

## The Model

The model defines two distinct lines of trust:

1. **Subagent Approval**: Which custom agents (`@agent-name`) may start without confirmation.
2. **Terminal Command Approval**: What shell commands those agents (or the default Copilot agent) may execute without prompting.

### Profiles

#### 1. `safe`

- **Goal:** Maximum human control. Only harmless reads, isolated validation, and non-mutating planning agents are auto-approved.
- **Subagents Approved:** `Plan`, `create-issue`, `close-issue`
- **Commands Approved:** Pure read-only commands (`cat`, `rg`, `fd`, `ls`), focused scripts (`validate_issue_specs.sh`), and standard test targets (`pytest`, `npm run lint`).
- **When to use:** When evaluating new workflows, onboarding, or enforcing strict manual oversight.

#### 2. `trusted-workflow` (Default)

- **Goal:** Uninterrupted typical implementation loops, while retaining manual gates for broadly destructive generic shell patterns.
- **Commands Approved:** `safe` + structured git operations (`git add`, `git commit`, `git push`), build target workflows, and repo operators.
- **When to use:** Daily development cycle. Allows the primary PR workflow loop to run, but keeps experimental/continuation agents heavily audited.

#### 3. `low-friction`

- **Goal:** Near-zero prompt friction for authorized operators. Maximum trust is placed in the agent ecosystem.
- **Subagents Approved:** All (`maestro-operator`, `workflow`, `continue-*`, `tutorial`)
- **Commands Approved:** Very broad regexes allowing almost any shell command, `/tmp` manipulations, loops, and pipeline chaining.
- **When to use:** By repository maintainers when driving massive refactoring or high-throughput autonomous execution runs.

## Applying Profiles

```bash
# Setup safe (maximum gates)
./scripts/setup-low-approval.sh safe

# Setup trusted workflow (default for active dev)
./scripts/setup-low-approval.sh trusted-workflow

# Setup low-friction (full autonomy)
./scripts/setup-low-approval.sh low-friction
```

## Validation

You can validate workspace drift against the chosen profile using:

```bash
python3 scripts/validate_workspace_settings.py --profile safe
```

## Canonical Source

The exact approvals rule-set lives natively in:
`.copilot/config/vscode-approval-profiles.json`. They are projected forcefully into the workspace `settings.json` and cleanly discard outdated residues.

## Profile Matrix

| Category / Profile                                             | `safe`   | `trusted-workflow` | `low-friction` |
| -------------------------------------------------------------- | -------- | ------------------ | -------------- |
| **Subagents: Non-mutating** (`Plan`, `create`, `close`)        | **Auto** | **Auto**           | **Auto**       |
| **Subagents: Workflow Loops** (`resolve`, `pr-merge`, `ralph`) | Man      | **Auto**           | **Auto**       |
| **Subagents: Operators** (`maestro`, `workflow`, `continue-*`) | Man      | Man                | **Auto**       |
| **Cmds: Read Only** (`rg`, `cat`, `ls`)                        | **Auto** | **Auto**           | **Auto**       |
| **Cmds: Validation Scripts** (`check_*.py`, `validate_*.sh`)   | **Auto** | **Auto**           | **Auto**       |
| **Cmds: Git Core** (`add`, `commit`, `push`, `pull`, `diff`)   | Man      | **Auto**           | **Auto**       |
| **Cmds: System Execution** (`python`, `npm`, `docker`)         | Man      | **Auto**           | **Auto**       |
| **Cmds: Wildcard Shell Regex** (`.*`, `while/for loops`)       | Man      | Man                | **Auto**       |
