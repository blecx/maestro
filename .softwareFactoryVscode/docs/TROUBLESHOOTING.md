# Troubleshooting

## Bootstrap fails: not a git repository

Initialize the host repository with Git first.

## Docker runtime does not start

Confirm Docker Desktop or Docker Engine is running and `docker compose version` succeeds.

## Context7 unreachable

- verify `.tmp/softwareFactoryVscode/runtime/<project-id>/.env.generated`
- verify `PORT_CONTEXT7`
- verify `compose/docker-compose.context7.yml` is included in the startup command

## VS Code files not updated

Rerun the bootstrap or upgrade projector:

- `python3 scripts/bootstrap_host.py --target <host> --factory-root <factory>`
- `python3 scripts/project_upgrade.py --target <host> --factory-root <factory>`
