# AI Agents

This directory contains the Python runtimes and adapters used for issue-resolution workflows.

## Current Runtime Model

The active execution path is:

1. `scripts/work-issue.py`
2. `agents/agent_registry.py`
3. `agents/maestro_adapter.py` for the default `autonomous` and `default` aliases

Ralph remains an alternate strict profile via `agents/ralph_agent.py`.

Canonical workflow policy does not live here. The source of truth for workflow behavior lives under `.copilot/skills/`, while `.github/agents/` remains the VS Code discovery layer.

## Key Files

- `agent_registry.py` - resolves runtime aliases such as `autonomous`, `default`, and `ralph`
- `maestro_adapter.py` - default issue runner used by `scripts/work-issue.py`
- `maestro.py` - Maestro orchestrator
- `maestro_cli.py` - direct CLI for Maestro runs
- `ralph_agent.py` - strict profile overlay
- `workflow_agent.py` - legacy workflow compatibility runner
- `workflow_phase_services.py` - workflow phase helpers
- `workflow_side_effect_adapters.py` - workflow side-effect boundaries
- `tools.py` - shared tool functions
- `knowledge/` - runtime knowledge base artifacts

## Profiles

### Default Issue Runner

Use the main issue runner for standard implementation work:

```bash
source .venv/bin/activate
./scripts/work-issue.py --issue 26
```

The `autonomous` alias currently resolves to `MaestroAdapter`.

### Ralph

Use Ralph for stricter review-gated execution:

```bash
./scripts/work-issue.py --issue 26 --agent ralph
```

VS Code chat entrypoint:

```text
@ralph /run
```

### Maestro CLI

Use the direct Maestro CLI when the task explicitly calls for Maestro orchestration rather than the standard `work-issue` flow:

```bash
.venv/bin/python -m agents.maestro_cli --issue 26 --repo blecx/AI-Agent-Framework
```

## Workflow Compatibility Path

`workflow_agent.py` is retained for scripted workflow compatibility and historical reference.
It is not the canonical workflow-policy source.

If you need that path explicitly:

```bash
./scripts/agents/workflow --issue 26 --dry-run
```

## Knowledge And Support Modules

These modules support the active runtimes:

- `command_cache.py`
- `time_estimator.py`
- `coverage_analyzer.py`
- `commit_strategy.py`
- `learning_scorer.py`
- `llm_client.py`

Knowledge base outputs are stored under `agents/knowledge/`.

## Current Documentation

- [docs/maestro/AUTOMATIONS.md](../docs/maestro/AUTOMATIONS.md)
- [docs/maestro/BOOTSTRAP.md](../docs/maestro/BOOTSTRAP.md)
- [docs/maestro/AGENTS_README.md](../docs/maestro/AGENTS_README.md)
- [docs/maestro/agents/MAESTRO-DESIGN.md](../docs/maestro/agents/MAESTRO-DESIGN.md)

## Development Notes

- Prefer `.copilot/skills/` for workflow-policy changes.
- Keep `.github/agents/` thin and discoverability-focused.
- Treat runtime changes in this directory as implementation work, not policy authoring.
- Use `.tmp/`, never `/tmp`, for transient artifacts managed by tooling.
