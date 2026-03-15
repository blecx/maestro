# Extraction Source Map

| Source path in `maestro` | Target path in `softwareFactoryVscode` | Action |
| --- | --- | --- |
| `.vscode/settings.json` | `.vscode/settings.json` | adapted |
| `.vscode/tasks.json` | `.vscode/tasks.json` | adapted |
| `.vscode/extensions.json` | `.vscode/extensions.json` | adapted |
| `.copilot/` | `.copilot/` | copied (transition phase) |
| `.github/agents/` | `.github/agents/` | copied (transition phase) |
| `configs/` | `configs/` | adapted |
| `docker/context7/` | `docker/context7/` | copied |
| `docker/mcp-*/` | `docker/mcp-*/` | copied |
| `apps/mcp/**` | `factory_runtime/apps/mcp/**` | copied |
| `apps/approval_gate/**` | `factory_runtime/apps/approval_gate/**` | copied |
| `apps/mock_llm_gateway/**` | `factory_runtime/apps/mock_llm_gateway/**` | copied |
| `agents/**` | `factory_runtime/agents/**` | copied (compatibility phase) |
| `tests/test_agent_boundaries.py` | `factory_runtime/tests/test_agent_boundaries.py` | copied |
| `apps/api/**` | excluded | excluded |
| Maestro frontend artifacts | excluded | excluded |
| `_external/maestro-Client/**` | excluded | excluded |

## Notes

- The current extraction keeps some compatibility-era runtime layout under `factory_runtime/agents/` and `factory_runtime/apps/` while enforcing package boundaries via scripts and docs.
- Neutrality exceptions are limited to source-map and migration-style documents such as this one and the companion validation specs.
