# ADR 012: Explicit Two-Root Model for Docker Dependencies

**Status:** Accepted
**Date:** 2026-03-15

## Context

Prior to splitting the codebase, Dockerized MCP services and devops tools mounted the entire monolithic tree to access both their internal implementation code and the project's payload. This couples the execution context with the project payload context, causing cross-contamination risk, preventing independent scaling, and blocking the extraction of the Software Factory to its own generic trunk.

## Decision

The architectural contract for both Software Factory isolated tools and future tooling deployments will adhere to a **two-root model**:

- **`/factory` root**: The location within containers where the Software Factory component's code, models, static configuration, and runtime dependencies reside. This code is either baked into the image or explicitly mounted apart from the host project.
- **`/target` root**: The location mapped from the host environment to represent the target project under development (e.g., `maestro` or any generic repository).

Containers must restrict their tooling executions to operate exclusively on the `/target` namespace for business mutations, while maintaining their own lifecycles via the `/factory` namespace.

## Consequences

### Positive

- Complete logical decoupling: an MCP container doesn't accidentally run black/flake8 on its own backend code when instructed to "format the backend."
- Portability is guaranteed: `.dockerignore` files will rigorously separate tooling from the target application context.
- Secures container internals from recursive modifications by active LLM loops analyzing code.

### Negative

- Refactoring of paths required across all bash scripts and MCP servers to point to `/target`.
- Some volume mapping complexity in dynamic environment generation scripts (like `maestro_runtime_env.py` or bash gateways).
