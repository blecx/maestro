# Fresh Clone Bootstrap

This document defines the explicit setup path for a fresh clone of the Maestro repository.

## Goal

Start from a clean checkout, configure only the settings you actually want, and avoid hidden workspace mutation.

## 1. Base Environment

From the repository root:

```bash
./setup.sh
source .venv/bin/activate
mkdir -p .tmp
```

Use the workspace Python interpreter after setup:

- `.venv/bin/python`

## 2. Choose Your VS Code Projection Level

The repository now separates two concerns:

- terminal approval profile,
- workspace agent defaults and MCP wiring.

Nothing should auto-enable high-trust mode on folder open.

### Safe Approval Profile

Apply the safe terminal approval profile:

```bash
.venv/bin/python scripts/setup-vscode-autoapprove.py --workspace-only --profile trusted-workflow
```

Equivalent VS Code task:

- `⚙️ Configure Approval Profile (Safe)`

### Low-Friction Approval Profile

Apply only when you explicitly want broad command approvals:

```bash
bash scripts/setup-low-approval.sh low-friction
```

Equivalent VS Code task:

- `⚙️ Configure Approval Profile (Low-Friction)`

### Workspace Agent Settings

Apply agent defaults, subagent auto-approve values, and MCP wiring from the canonical `.copilot` config:

```bash
.venv/bin/python scripts/setup-vscode-agent-settings.py
```

Equivalent VS Code task:

- `⚙️ Configure Workspace Agent Settings`

## 3. Verify Local Projection

Check terminal approval profile drift:

```bash
.venv/bin/python scripts/setup-vscode-autoapprove.py --check --workspace-only --profile trusted-workflow
```

Check workspace agent setting drift:

```bash
.venv/bin/python scripts/setup-vscode-agent-settings.py --check
```

## 4. Optional Runtime Startup

If you want the local stack running:

- use `🚀 Dev Stack: Supervised`, or
- start targeted tasks such as backend or frontend only.

These are runtime conveniences, not configuration authority.

## 5. What Lives Where

- `.copilot/`
  Canonical workflow logic and configuration sources.
- `.github/agents/`
  VS Code discovery wrappers only.
- `.vscode/`
  Local editor settings and tasks.
- `scripts/`
  Explicit projection and execution entrypoints.

## 6. Recommended First-Use Sequence

For most developers:

1. Run `./setup.sh`.
2. Apply `⚙️ Configure Approval Profile (Safe)`.
3. Apply `⚙️ Configure Workspace Agent Settings`.
4. Reload VS Code.
5. Verify drift with the two `--check` commands above.

Only opt into low-friction approvals if you understand the trust tradeoff.

## 7. Recovery

If workspace settings drift or you want to reapply the canonical projection:

```bash
.venv/bin/python scripts/setup-vscode-autoapprove.py --workspace-only --profile trusted-workflow
.venv/bin/python scripts/setup-vscode-agent-settings.py
```

If you need to audit the architecture or source-of-truth map, see:

- `docs/maestro/AUTOMATIONS.md`

## Projection and Reconciliation

VS Code settings are managed through strict **reconciliation**, not merely additive merging.

- The root keys configured by the projection scripts (e.g. `mcp`, `chat.tools.subagent.autoApprove`, `chat.tools.terminal.autoApprove`, `issueagent.customAgent`) are treated as **fully owned** by the canonical config.
- Any manual modifications or unknown sub-keys within these owned hierarchies in `.vscode/settings.json` will be automatically **removed** when projection scripts run.
- Non-owned settings paths remain untouched, allowing safe management of developer-specific local preferences alongside canonical team policies.
