# ADR 0004: Project-isolated MCP deployment

## Status

Accepted

## Context

The software factory runs runtime services for host repositories, including first-party and opaque dependencies. Some services cannot be made safely multi-tenant inside one shared process or container without excessive coupling or risk.

## Decision

Runtime services may use per-project isolated deployment when shared tenancy would violate separation of concerns or operational safety.

## Consequences

- Project identity is enforced through generated runtime metadata such as `PROJECT_WORKSPACE_ID`, `COMPOSE_PROJECT_NAME`, and project-scoped data paths.
- Opaque or third-party services can run one isolated instance per host project.
- Factory-owned runtime code remains separate from host-project content through the `/factory` and `/target` model where implemented.
- Runtime isolation must not require projecting tool-owned `.vscode/`, `.github/`, or `.copilot/` files into the host repository.
