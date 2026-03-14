# Maestro Architectural Enhancement Plan: MCP & LLM Mocking

## 1. Executive Summary
This document outlines the architectural plan to introduce a Deterministic Mock LLM Gateway for local development and regression testing, alongside an overhaul of the Model Context Protocol (MCP) server topology. The goals are to prevent hard-crashes when API keys are missing, enable rigorous automated QA through preloaded Q&A prompt behaviors, and guarantee robust multi-project state persistence across host reboots.

---

## 2. Implementation Plan

### Phase 1: The Mock LLM Server (FastAPI / REST)
- Build a new lightweight REST service (`apps/mock_llm_gateway`).
- **OpenAI Proxy Endpoint (`/v1/chat/completions`)**: Receives requests, queries internal definitions, and returns pre-configured simulated LLM JSON responses.
- **Admin REST Interface (`/admin/mocks`)**: `POST` to upload exact prompt-to-response mappings, `GET` to view them, `DELETE` to flush state between CI test runs.

### Phase 2: LLM Factory Fallback Routing
- Update `agents/llm_client.py` and `agents/tooling/openai_images_client.py`.
- Intercept missing or blank `OPENAI_API_KEY` configurations.
- Transparently redirect `base_url` to the mock gateway with a dummy key (`"sk-dummy-test"`). No downstream orchestration logic requires changes.

### Phase 3: Dynamic Key Injection ("Hot-Swapping")
- Add an MCP tool / REST endpoint (`/admin/set-live-key`) attached to the agent bus.
- Patch LLM Client initialization to poll dynamic configuration overrides, switching from Mock to Live OpenAI endpoints seamlessly without docker restarts.

### Phase 4: CI / Regression Preloading
- Define a JSON schemas directory (`tests/mocks/`) representing expected Maestro action loops.
- Implement `scripts/preload-mocks.sh` to push expected interactions to the Mock Server before triggering integration tests.

---

## 3. Architecture Decision Records (ADRs)

### ADR-001: Deterministic Mock LLM Gateway for Q&A Regression
**Status:** Accepted
**Context:** Local development currently crashes without an `OPENAI_API_KEY`. Furthermore, testing autonomous orchestrator loops against live LLMs causes flaky CI pipelines due to intrinsic non-determinism.
**Decision:** We will proxy all LLM traffic through a standalone, OpenAI API-compatible local gateway (`apps/mock_llm_gateway`) when keys are missing. This gateway will serve deterministic, pre-loaded JSON responses based on prompt fingerprinting via an Admin REST API.
**Consequences:** 
- **Pros:** 100% deterministic CI testing; free local development without LLM expenses.
- **Cons:** Requires maintenance to keep the Mock Gateway's request/response schema parallel with OpenAI SDK updates.

### ADR-002: Instance-Dedicated MCP Server Architecture
**Status:** Accepted
**Context:** As Maestro scales, sharing a single global pool of MCP servers across multiple orchestrator instances causes context bleeding and race conditions. 
**Decision:** Each Maestro orchestrator instance will run its own dedicated, tightly-coupled set of MCP servers. Dependency wiring will be strictly encapsulated utilizing isolated Docker-Compose networks (`maestro_net_<instance_id>`).
**Consequences:**
- **Pros:** Zero cross-talk between agents. Independent crashing/scaling.
- **Cons:** Increased baseline memory footprint per Maestro instance on the host machine.

### ADR-003: State Persistence and Reboot Survivability
**Status:** Accepted
**Context:** Dedicated MCP servers maintain state (e.g., knowledge graphs, memory DBs) that currently risk data loss on system reboots or container teardowns.
**Decision:** We will strictly adopt named Docker volumes or persistent host bind-mounts for all persistent state. Specifically:
1. `mcp-memory` SQLite files will be bound to host-managed volumes (e.g., `/data/maestro/memory/<instance_id>`).
2. Vector indices and file-system mappings will be synchronized to disk continuously via WAL (Write-Ahead Logging) SQLite configurations.
**Consequences:**
- **Pros:** Full survivability across host reboots. Easy backup of instance states. 
- **Cons:** Necessitates robust file permission handling and cleanup processes for orphaned volumes.

### ADR-004: Multi-Project Automation and Isolation
**Status:** Accepted
**Context:** Maestro needs to handle multiple self-contained software projects. If an instance restarts, it must contextually restore its awareness of differing project definitions and boundaries.
**Decision:** All Maestro orchestration and MCP context will be strictly partitioned by `PROJECT_WORKSPACE_ID`. 
1. Database persistence layers (like the Agent Bus and Knowledge Graph) will enforce a strict multi-tenant schema partitioning data by project ID. 
2. File-system MCP servers will be strictly jailed `chroot`-style to the specific project's root directory string mapping.
**Consequences:**
- **Pros:** One Maestro cluster can orchestrate tasks across N projects seamlessly without cross-pollinating codebase knowledge. 
- **Cons:** Database queries become slightly more complex (requires `WHERE project = ?` appending on all MCP tools).