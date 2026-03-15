# Install

## Prerequisites

- Git repository already initialized for the host project
- Python 3.10+
- Docker with `docker compose`
- VS Code with the extensions documented in `docs/VSCODE-WORKSPACE.md`

## Host repo preparation

Preferred layout:

- host repo root
- nested factory repo at `.softwareFactoryVscode`

## Add the factory repo

Preferred:

- add as a Git submodule at `.softwareFactoryVscode`

Alternative:

- clone or copy the repo into `.softwareFactoryVscode`

## Bootstrap commands

Run from the host repo root:

- `python3 .softwareFactoryVscode/scripts/bootstrap_host.py --target . --factory-root .softwareFactoryVscode`
- `python3 .softwareFactoryVscode/scripts/project_runtime_env.py --target .`

## Environment setup

Bootstrap creates:

- `.factory.lock.json`
- `.factory.env`
- `.tmp/softwareFactoryVscode/`
- no projected tool-owned `.vscode/`, `.github/`, or `.copilot/` files in the host repo
- hidden tool working tree remains at `.softwareFactoryVscode/`

The runtime env generator writes:

- `.tmp/softwareFactoryVscode/runtime/<project-id>/.env.generated`

## Starting services

Start the full packaged stack:

- `python3 .softwareFactoryVscode/scripts/project_runtime_up.py --target . --build`

Stop the stack:

- `python3 .softwareFactoryVscode/scripts/project_runtime_down.py --target .`

## Validation steps

- `python3 .softwareFactoryVscode/scripts/project_runtime_validate.py --target .`
- `python3 .softwareFactoryVscode/scripts/check_vscode_workspace.py`
- `python3 .softwareFactoryVscode/scripts/check_neutrality.py`

## How tool-owned workspace files are isolated

The factory package keeps its own `.vscode/`, `.copilot/`, and `.github/` files inside `.softwareFactoryVscode/`.

Bootstrap does not project these tool-owned files into the host workspace. Host-project VS Code, GitHub, and Copilot configuration remains owned by the host repository.

## Context7 setup

Context7 is delivered primarily as a Docker/MCP service, not as a mandatory VS Code extension.

- Dockerfile: `docker/context7/Dockerfile`
- Compose file: `compose/docker-compose.context7.yml`
- Port env var: `PORT_CONTEXT7`
- Optional key: `CONTEXT7_API_KEY`

Supply `CONTEXT7_API_KEY` in `.factory.env` or the shell environment when available. If it is absent, Context7 should still start in local mode where supported by the image, and the rest of the factory remains usable.

## Troubleshooting

- If bootstrap says the target is not a git repo, initialize the host with `git init` first.
- If Docker is missing, install Docker and confirm `docker compose version` works.
- If Context7 is unreachable, confirm the generated runtime env contains `PORT_CONTEXT7` and the service is running.
- If projected VS Code files are stale, rerun `scripts/project_upgrade.py`.
