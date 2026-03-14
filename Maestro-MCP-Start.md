# Maestro MCP Lifecycle & Initialization Plan

## 1. Executive Summary
Maestro's orchestration relies heavily on an interconnected mesh of Model Context Protocol (MCP) servers (memory DBs, repo filesystem searchers, bash gateways). Rebooting the host machine or restarting the Maestro worker requires a rigid safety protocol to ensure that inherited Docker containers aren't stale, broken, or misaligned with the current project's configuration before proceeding. Additionally, local state (such as knowledge bases) must be cleanly persisted and verified on boot.

This document establishes the architecture for the **Maestro Pre-Flight Bootloader**, which will automatically verify, recycle, reconstruct, and snapshot MCP dependencies at the top and tail of the application's lifecycle.

---

## 2. Boot & Teardown Architecture Sequences

### Phase 1: Pre-Flight MCP Validation (Start / Boot Time)
The `agents.maestro_cli` command will be updated to execute an initialization routine BEFORE attempting to poll its queues or connect to external LLMs.

**The Verification Checklist:**
1. **Network Discovery:** Sweep the local Docker daemon for running containers matching the active `MAESTRO_INSTANCE_ID` pattern.
2. **Version Pinning Analysis:** Identify if running MCP containers match the image hashes or compose configurations declared in the active project directory.
   - *If Match:* Reuse the containers to eliminate boot-time latency.
   - *If Mismatch (Stale/Broken):* Issue a kill SIGTERM, prune them, and force a fresh `docker compose up`.
3. **Health-Check Handshake:** Send mock HTTP/JSON RPC payloads to each respective MCP port. Do not pass green until an `HTTP 200 / "status":"ok"` is explicitly received.

### Phase 2: Data Hydration & Integrity Check
1. **SQLite & Vector Integrity Check:** If an inherited container is determined as reused, trigger an intra-MCP verification command to confirm its `.db` files aren't corrupted or locked.
2. **Data Hydration (The Sync Hook):** Before the main Agent loop takes over, invoke a `memory_sync_startup` module. This module scans the current `AGENT_WORKSPACE` for localized `.tmp/maestro_snapshots` and forces the MCP servers to ingest them. If the orchestrator detects an empty memory layout but sees local workspace snapshot binaries, it performs a restore operation.

### Phase 3: Defensive Teardown & Checkpointing
1. **Graceful SIGINT Trapping:** Catch `Ctrl+C` or Docker `SIGTERM` signals in the main python orchestrator string. 
2. **Snapshot Dump:** Prior to halting processes, issue a command to `mcp-memory` and `mcp-agent-bus` to export a differential backup or `.sql` dump into `.tmp/maestro_snapshots/`.
3. **Orphan Sweeping (Optional):** Provide an explicit CLI flag `--kill-mcps-on-exit` forcing the teardown of the MCP Docker network as the process terminates.

---

## 3. Architecture Decision Records (ADRs)

### ADR-007: Container Lifecycle Verification ("Pre-Flight Bootloader")
**Status:** Accepted
**Context:** When a user or pipeline triggers Maestro, standard Docker startup scripts blindly attempt connection assuming MCP ports are up, leading to fatal race conditions or communicating with broken containers from past un-graceful shutdowns.
**Decision:** We introduce a mandatory synchronous connection handshake script embedded directly into the orchestrator startup process that verifies docker hashes, intercepts hanging containers, and validates port liveliness. Broken instances will be aggressively pruned and spun up from scratch.
**Consequences:**
- **Pros:** 100% guarantee that Maestro will never crash due to mysterious backend connectivity problems; heavily reduces manual debugging.
- **Cons:** Nominal ~1.5s latency addition to tool execution or node boot sequences while network handshakes complete.

### ADR-008: Automated State Snapshotting & Hydration
**Status:** Accepted
**Context:** Restarting machine hosts often leaves runtime databases out of sync with external file systems or abruptly flushes transient context needed across multi-step automation jobs.
**Decision:** We will establish a localized snapshot mechanism residing under `.tmp/maestro_snapshots/`. 
- On orchestrator shutdown: State is dumped via an explicit snapshot command API route exposing the databases.
- On orchestrator boot: A hydration module checks for existing snapshots for the given `PROJECT_WORKSPACE_ID` and restores if the active memory buffer is empty.
**Consequences:**
- **Pros:** Total protection of context logic across unexpected developer laptop power cycles or container crashes.
- **Cons:** Demands synchronous blocking rules to capture the snapshot cleanly when a user signals an interrupt before killing the python node process.

### ADR-009: Strict Opt-In Orphan Control Policy
**Status:** Accepted
**Context:** Maestro creates multiple background dockers. Allowing them to run invisibly consumes host memory, but aggressively tearing them down defeats the purpose of caching system memory and "always-on" agent buses.
**Decision:** 
By default, the bootloader will *reuse* valid containers across separate application runs to keep orchestration exceptionally fast. To forcefully purge and rebuild the mesh, users/systems must pass an explicit `--force-rebuild-mcps` or trigger the teardown hooks via `--kill-mcps-on-exit`.
**Consequences:** 
- **Pros:** Optimizes response speed heavily for continuous development workflows. Maintains the "Agent as a background daemon" paradigm naturally.