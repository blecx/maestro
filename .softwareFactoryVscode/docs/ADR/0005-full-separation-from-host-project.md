# ADR 0005: Full separation from the host project

## Status

Accepted

## Context

The software factory was originally extracted from `maestro`, but an extracted tool must not continue to leak source-project identity, workspace ownership, or governance files into the host project it serves. Without an explicit separation rule, the host repository becomes contaminated by tool-owned metadata and Copilot/editor context can mix the factory domain with the host-product domain.

Preserved migration goal line (kept verbatim):

> Always keept the goal, that we like to move the software factory to a new project taking all of its capability, but nothing from maestor.

## Decision

`softwareFactoryVscode` must remain fully separated from the host project.

## Consequences

- The factory lives in the hidden `.softwareFactoryVscode/` working tree by default.
- Tool-owned `.vscode/`, `.github/`, and `.copilot/` content stays inside that hidden tree and is not projected into the host repository by default.
- Host repositories only receive documented host-local bootstrap artifacts such as `.factory.lock.json`, `.factory.env`, and `.tmp/softwareFactoryVscode/`.
- Copilot, search, and maintenance workflows for the host project should ignore `.softwareFactoryVscode/` unless the operator explicitly chooses to work on the factory itself.
- The source repository used for extraction, including `maestro`, must not define the runtime identity of the extracted factory.
- The extraction target is to preserve all reusable software-factory capability while carrying nothing from `maestro` except documented source provenance.
- Documentation, tests, manifests, and upgrade logic must preserve this separation as a release-blocking contract.
