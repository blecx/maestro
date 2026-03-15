# ADR 0003: Standalone bootstrap and self-contained installation

## Status

Accepted

## Context

A reusable software factory cannot depend on parent-directory assumptions, host-specific path traversals, or ad hoc file copying rules. Installation must be explicit, reproducible, and self-contained.

## Decision

`softwareFactoryVscode` uses a self-contained bootstrap model rooted in the hidden `.softwareFactoryVscode/` working tree plus documented host-local artifacts such as `.factory.lock.json`, `.factory.env`, and `.tmp/softwareFactoryVscode/`.

## Consequences

- Bootstrap defaults to the active host repository and does not require `../` traversal assumptions.
- Tool-owned workspace and governance files remain inside `.softwareFactoryVscode/`.
- Host-local generated state is limited to documented bootstrap artifacts.
- Reinstall and upgrade flows must remain idempotent and deterministic.
