# ADR 011: Physical Repository Separation for Maestro and Software Factory

**Status:** Accepted
**Date:** 2026-03-15

## Context

Historically, the `maestro` repository housed both the core application (Maestro: an ISO 21500 Project Management AI Agent) and the toolkit used to build it (Software Factory: AI coding agents, workflow scripts, MCP servers, and `.copilot` policies).

This lack of separation mixes distinct domains:
- The **Target Application Domain** (`apps/api`, `maestro-client`, PM pipelines).
- The **Meta-Tooling Domain** (`agents/`, `.copilot`, `.github/agents`, `apps/mcp/`, `docker/mcp-*`).

Having both in a single repository leads to confusion over build dependencies, leaky boundaries in Docker contexts, and editor configurations applying to incorrect runtime components.

## Decision

We will completely separate the Software Factory from the Maestro application into distinct Git repositories.
1. `maestro` (and `maestro-client`): Contains *only* the domain and application code for the ISO 21500 tool.
2. `software-factory` (name TBD): Contains all toolchains, MCP servers, autonomous agent logic, and Copilot extensions.

The Software Factory will operate on `maestro` purely 'from the outside-in', attaching to it as a target host project.

## Consequences

### Positive

- Strict enforcement of separation of concerns; the application cannot accidentally depend on the meta-tooling.
- Simplified CI/CD: Maestro's pipelines will test and build Maestro; Software Factory pipelines will maintain MCPs and AI toolchains.
- Independent versioning of AI tools from the business application.
- The Software Factory becomes a reusable asset capable of orchestrating new/other projects beyond just `maestro`.

### Negative

- Requires orchestration logic to clone and attach the Software Factory to a target repository locally and in CI.
- Developer setup now spans a toolset repo and application repo (manageable via VS Code Workspaces or initialization scripts).
