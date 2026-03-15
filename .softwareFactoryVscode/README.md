# softwareFactoryVscode

`softwareFactoryVscode` is a standalone, reusable Software Factory package extracted from `maestro` for host-project bootstrap, isolated MCP runtime orchestration, and VS Code workspace parity.

Preserved migration goal line (kept verbatim):

> Always keept the goal, that we like to move the software factory to a new project taking all of its capability, but nothing from maestor.

## What it contains

- project-scoped Docker/MCP runtime assets under `compose/`, `docker/`, and `factory_runtime/`
- package-owned bootstrap, projection, runtime, upgrade, and validation scripts under `scripts/`
- VS Code workspace configuration under `.vscode/`
- Copilot/agent metadata under `.copilot/` and `.github/agents/`
- test and validation contracts including `SoftwareFactoryVsocdeTestsuite.md`
- remote GitHub governance contract in `externalDevendenciesSoftwareFactory.md`

## What it does not contain

- source application API code from `apps/api/`
- source frontend delivery artifacts
- host-project-specific business logic
- any required dependency on a sibling client repository

## Quick install

1. Add this repository to your host repo at `.softwareFactoryVscode`.
2. Run `python3 .softwareFactoryVscode/scripts/bootstrap_host.py --target . --factory-root .softwareFactoryVscode`.
3. Generate runtime env with `python3 .softwareFactoryVscode/scripts/project_runtime_env.py --target .`.
4. Start the runtime with `python3 .softwareFactoryVscode/scripts/project_runtime_up.py --target . --build`.

The package remains self-contained in `.softwareFactoryVscode/`; its `.vscode/`, `.github/`, and `.copilot/` files are not projected into the host repository.

## Quick start

- Bootstrap host workspace: see `docs/INSTALL.md`
- Start/stop isolated runtime: see `docs/INSTALL.md` and `docs/ARCHITECTURE.md`
- Upgrade projected artifacts: see `docs/UPGRADE.md`
- Validate workspace/runtime: see `docs/TESTING.md`

## Architecture overview

The package keeps developer tooling and runtime concerns separated:

- runtime code lives under `factory_runtime/`
- host repositories mount at `/target`
- package runtime code mounts or builds under `/factory`
- VS Code workspace files remain package-owned inside `.softwareFactoryVscode/.vscode/` and are not projected into the host workspace by default

## Related docs

- `docs/INSTALL.md`
- `docs/TESTING.md`
- `docs/VSCODE-WORKSPACE.md`
- `docs/UPGRADE.md`
- `docs/MAINTENANCE.md`
- `docs/ARCHITECTURE.md`
- `docs/EXTRACTION-SOURCE-MAP.md`

## Workspace configuration model

This repository ships canonical `.vscode/settings.json`, `.vscode/tasks.json`, and `.vscode/extensions.json` templates for the hidden tool working tree itself. The bootstrap flow does not write these tool-owned files into the host workspace.
