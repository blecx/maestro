# Extraction notes

This document summarizes the extraction posture for `softwareFactoryVscode`.

Preserved migration goal line (kept verbatim):

> Always keept the goal, that we like to move the software factory to a new project taking all of its capability, but nothing from maestor.

- Source repository: `maestro`
- Canonical target: standalone `softwareFactoryVscode`
- Runtime code retained under `factory_runtime/`
- Tool-owned workspace/governance files stay inside `.softwareFactoryVscode/`
- Host bootstrap creates only documented host-local artifacts such as `.factory.lock.json`, `.factory.env`, and `.tmp/softwareFactoryVscode/`
- Excluded artifacts include application-specific API/frontend delivery assets and all other non-reusable Maestro product concerns

See `docs/EXTRACTION-SOURCE-MAP.md`, `docs/ADR/0005-full-separation-from-host-project.md`, and `manifests/extraction-manifest.json` for the authoritative mapping.
