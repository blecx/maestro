# Maestro Freeing & Separation of Concerns Plan

## 1. Executive Summary

Maestro was successfully extracted from its parent repository (`AI-Agent-Framework`) but still carries legacy dependencies, environment variables, and conceptual overlaps. This document analyzes the current architectural breakage regarding agent definitions and lays out a rigid plan to transform Maestro into a fully standalone, properly scoped project. 

Central to this plan is resolving the "split brain" architecture where development-time agents and runtime application agents are bleeding their definitions, prompts, and skills into one another.

## 2. Conceptual Nomenclature & Separation of Concerns

To permanently fix the architectural decay, we must establish a rigid separation between two distinct classes of agents:

- **Software Factory Agents:**
  These are the developer-facing SDLC (Software Development Life Cycle) tools. They live exclusively in the repository's meta-directories (`.vscode/`, `.github/agents/`, `.copilot/skills/`). Their sole purpose is to help the human development team write code, merge PRs, plan issues, and build the Maestro software.
- **Maestro Agents:**
  These constitute the actual product/runtime. They include the autonomous orchestrators (e.g., Planner, Coder, Ralph) and orchestrate the MCP servers. They live exclusively in `agents/` and `apps/mcp/`. They run on Python, utilize their own distinct prompt files, knowledge stores, and skills, and fulfill end-user workloads.

**The Current Problem:** Maestro Agents currently try to inherit or read prompt schemas from the Software Factory Agent layer, or rely on hard-coded legacy paths pointing to `AI-Agent-Framework`. This is a strict architectural anti-pattern.

## 3. Implementation Phases (Completed)

### Phase 1: Decoupling from AI-Agent-Framework (The Standalone Step)

- **Objective:** Sever all remaining hardcoded ties to the parent repository.
- **Action items:**
  - Full codebase audit (`grep -ri "AI-Agent-Framework"`) to remove legacy repository URLs, Docker context assumptions, and hardcoded `blecx/AI-Agent-Framework` test defaults.
  - Fix default environment variables in `.env.maestro.example` and `docker-compose.maestro.yml` so that `AGENT_REPO` maps dynamically to the runtime workspace, not the old repo.
  - Review and clean up `scripts/` that assume a monorepo file structure traversing outside the current directory (`../AI-Agent-Framework/`).

### Phase 2: Resolving the Agent Typology Fracture

- **Objective:** Untangle the Software Factory Agents from the Maestro Agents.
- **Action items:**
  - Audit `.copilot/skills/` and `.github/agents/` to ensure they ONLY contain instructions for GitHub Copilot Workspace interactions.
  - Move any runtime application prompts, system instructions, or internal skills meant for `MaestroOrchestrator` execution out of the `.github`/`.copilot` directories and into a dedicated `agents/prompts/` and `agents/tooling/` structure.
  - Refactor `agents/llm_client.py` and associated Python routers to strictly load prompts from the `agents` local scoped directories. The runtime application must never read a `.md` file from `.github/` or `.copilot/`.

### Phase 3: Consolidation and Documentation

- **Objective:** Finalize the boundaries so future development does not break the rules.
- **Action items:**
  - Update standard operating procedures (`README.md`, `docs/development.md`) confirming the exact locations for adding Software Factory skills versus Maestro runtime prompts.
  - Write test cases asserting that `agents/` modules do not import or statistically read from the meta-directories.

## 4. Architecture Decision Records (ADRs)

### ADR-005: Strict Boundary for Agent Separation of Concerns

**Status:** Accepted

**Context:** The project utilizes AI both as a development tool (Copilot) and as the delivered product itself (Maestro). Commingling prompt files or logic limits portability, confuses LLM context generation, and creates circular dependencies.

**Decision:** We mandate a rigid physical filesystem boundary separating Software Factory Agents from Maestro Agents. 

**Consequences:**
- Software Factory Agents (`.github/agents`, `.copilot/skills`, `.vscode`) are strictly for human developer velocity. They do not ship with the runtime Docker containers or exist in the production environment.
- Maestro Agents (`agents/`, `apps/`) are the product. They must be completely self-contained. The production Dockerfile will utilize `.dockerignore` to explicitly exclude `.github/` and `.copilot/` to physically prevent runtime dependence on developer tools.

### ADR-006: Standalone Repository Configuration and Bootstrapping

**Status:** Accepted

**Context:** Scripts and Docker configurations carry legacy mappings indicating they still belong to the broader `AI-Agent-Framework` ecosystem, blocking drop-in deployments.

**Decision:** Maestro will adopt a 100% self-referential initialization sequence. Environment variables dictating project scope will default strictly to the active git repository context traversing `.` rather than hardcoded parent strings. 

**Consequences:**
- Requires rewriting test-fixtures that point to `../AI-Agent-Framework` to instead point to localized mocked project directories. 
- Guarantees immediate out-of-the-box working states for any new developer cloning the `maestro` repo.