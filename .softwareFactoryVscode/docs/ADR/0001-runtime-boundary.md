# ADR 0001: Runtime and workspace boundary

## Status
Accepted

## Decision
`softwareFactoryVscode` keeps runtime code under `factory_runtime/` and workspace/developer assets under `.vscode/`, `.copilot/`, `.github/`, and `docs/`.

## Consequences

- Runtime images must build from package-owned sources under `factory_runtime/`.
- Tool-owned `.vscode/`, `.copilot/`, and `.github/` assets remain inside the hidden `.softwareFactoryVscode/` working tree.
- Host repositories do not receive projected tool-owned workspace or governance artifacts.
- Host-visible temporary state uses `.tmp/softwareFactoryVscode/`.
