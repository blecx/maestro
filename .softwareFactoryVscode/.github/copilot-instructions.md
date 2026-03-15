# Copilot Instructions for softwareFactoryVscode

## Overview

`softwareFactoryVscode` is a standalone software-factory package for bootstrapping host repositories from a hidden `.softwareFactoryVscode/` working tree and running isolated MCP/Docker services per host project.

## Core rules

- Keep runtime code under `factory_runtime/` independent from `.copilot/`, `.github/`, `.vscode/`, and docs.
- Treat the host repository as mounted at `/target` inside containers.
- Treat package-owned runtime code as baked into images under `/factory` where possible.
- Use only neutral defaults; never assume a specific backend/client split or sibling repository layout.
- Use `.tmp/softwareFactoryVscode/` for package-controlled host-visible state, never host-global `/tmp`.
- Keep tool-owned `.vscode/`, `.github/`, and `.copilot/` files inside the hidden factory tree; do not project them into host repositories.

## Validation baseline

Before considering a change complete, run the package checks relevant to your scope:

- `python scripts/check_neutrality.py`
- `python scripts/check_variable_contract.py`
- `python scripts/check_boundaries.py`
- `python scripts/check_vscode_workspace.py`
- `python -m pytest tests factory_runtime/tests -q --tb=short`

## Documentation contract

Keep these files aligned with implementation:

- `README.md`
- `docs/INSTALL.md`
- `docs/TESTING.md`
- `docs/VSCODE-WORKSPACE.md`
- `docs/UPGRADE.md`
- `docs/ARCHITECTURE.md`
- `SoftwareFactoryVsocdeTestsuite.md`
- `externalDevendenciesSoftwareFactory.md`

## Packaging guidance

- If a Dockerfile or compose file references paths outside `factory_runtime/`, verify that this is intentional and documented.
- Do not solve host-project problems by copying tool-owned configuration into the host repository unless a task explicitly changes the architecture.
- Keep GitHub workflow names stable once published because branch protection may depend on them.
