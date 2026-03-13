# VS Code Global Settings Guidance

This repository no longer treats VS Code user settings as the primary source of truth for agent workflow policy.

Canonical sources now live under `.copilot/config/`:

- `.copilot/config/vscode-approval-profiles.json`
- `.copilot/config/vscode-agent-settings.json`

Use workspace-local projection first. Only add user-level settings when you intentionally want personal defaults across multiple repositories.

## Preferred Setup

For a fresh clone of this repository, run the explicit workspace projections instead of pasting large JSON blocks into VS Code user settings:

```bash
bash scripts/setup-low-approval.sh safe
/usr/local/bin/python3.12 scripts/setup-vscode-agent-settings.py
```

Optional workspace variants:

- `bash scripts/setup-low-approval.sh low-friction`
- VS Code tasks:
  - `⚙️ Configure Approval Profile (Safe)`
  - `⚙️ Configure Approval Profile (Low-Friction)`
  - `⚙️ Configure Workspace Agent Settings`

## What Belongs In User Settings

User settings should remain personal and editor-generic.
Good candidates:

- UI/editor preferences
- font, theme, layout, telemetry choices
- non-repository-specific Copilot preferences you want everywhere

Do not treat user settings as the authoritative place for this repository's:

- subagent allowlists,
- MCP server registry,
- repo-specific terminal approval patterns,
- issue/workflow routing defaults.

Those belong in `.copilot/config/` and are projected into `.vscode/settings.json` when needed.

## If You Want Personal Global Defaults

Keep them minimal and non-authoritative. A reasonable example is:

```json
{
  "chat.checkpoints.showFileChanges": true,
  "chat.customAgentInSubagent.enabled": true
}
```

If a global default conflicts with this repository's projected workspace settings, the workspace setting should win.

## Verification

Check workspace projections explicitly:

```bash
python3 scripts/setup-vscode-autoapprove.py --check --profile safe
/usr/local/bin/python3.12 scripts/setup-vscode-agent-settings.py --check
```

If drift is reported, re-run the corresponding projection command or task.

## Related Docs

- `docs/maestro/BOOTSTRAP.md`
- `docs/maestro/AUTOMATIONS.md`
- `.copilot/README.md`

## Migration Note

Older guidance in this repository recommended copying a large repo-specific JSON block into VS Code user settings.
That model is deprecated because it duplicated policy, hid source-of-truth ownership, and made fresh-clone behavior harder to reason about.
