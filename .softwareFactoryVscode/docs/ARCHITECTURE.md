# Architecture

## ADR set

- `docs/ADR/0001-runtime-boundary.md` defines the runtime/workspace split.
- `docs/ADR/0002-agent-separation.md` defines the separation between software-factory tooling and product/runtime concerns.
- `docs/ADR/0003-standalone-bootstrap.md` defines self-contained bootstrap and install behavior.
- `docs/ADR/0004-project-isolated-mcp-deployment.md` defines per-project isolation for runtime services.
- `docs/ADR/0005-full-separation-from-host-project.md` defines the hidden-tree contract and the prohibition on host-domain contamination.

## Runtime/meta boundary

- runtime code lives under `factory_runtime/`
- meta/developer tooling lives under `.copilot/`, `.github/`, `.vscode/`, and docs
- runtime images must not depend on meta directories

## `/factory` + `/target` model

- package-owned runtime code is built or mounted at `/factory`
- host repository content is mounted at `/target`
- host-visible temp/state artifacts live under `.tmp/softwareFactoryVscode/`

## Project-isolated compose model

- each host repo gets a deterministic `COMPOSE_PROJECT_NAME`
- ports derive from `PROJECT_WORKSPACE_ID`
- audit/data/config directories are project-scoped

## Service classes

### Class A — opaque single-tenant

Third-party or opaque services run once per host project instance.

### Class B — first-party runtime services

These are shipped in `factory_runtime/` and built from this repository.

### Class C — developer tooling

These are not required for runtime startup.

## Security and policy assumptions

- no host-global `/tmp` for package-controlled state
- no runtime dependence on `.copilot/`, `.github/agents/`, or `.vscode/`
- neutral repo defaults by design

## Role of `.vscode/`

`.vscode/` is part of the developer/workspace contract only. It stays inside `.softwareFactoryVscode/.vscode/` so a host workspace can opt into the factory tooling without treating tool-owned files as part of the host-product domain. It is never a runtime dependency.
