# Maintenance

## Add or replace MCP services

- add runtime code under `factory_runtime/apps/mcp/`
- add Docker image under `docker/`
- add compose entry under `compose/`
- update `.vscode/settings.json` MCP wiring if the service is user-facing

## Change Docker images safely

- keep builds project-scoped
- avoid host-global mutable state
- verify `.dockerignore` still excludes meta assets

## Add config defaults

- put canonical defaults in `configs/`
- document them in `docs/INSTALL.md` or `docs/ARCHITECTURE.md`
- keep secrets out of committed defaults

## Add projection rules

- update `manifests/projection-manifest.json`
- update `scripts/project_projector.py`
- add or update tests under `tests/contracts` and `tests/integration`

## Add neutrality checks

- update `scripts/check_neutrality.py`
- extend forbidden tokens only when they are package-stable policies
