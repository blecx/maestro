# ADR 0002: Agent and tooling separation

## Status

Accepted

## Context

`softwareFactoryVscode` exists to provide developer tooling, bootstrap automation, and runtime orchestration for host repositories. The host product domain and the factory tool domain must stay distinct or the resulting workspace becomes non-portable, harder to reason about, and easier to break accidentally.

## Decision

`softwareFactoryVscode` treats software-factory tooling as a separate concern from any host-product runtime or business domain.

## Consequences

- Tooling assets live inside the hidden `.softwareFactoryVscode/` tree.
- Product/runtime code for a host project must not depend on `.github/`, `.copilot/`, or `.vscode/` assets owned by the factory.
- The factory may guide, inspect, and orchestrate a host project, but it does not become part of the host project's product domain.
- Runtime packaging and tests must keep enforcing the runtime/meta boundary.
