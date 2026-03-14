# ADR-005: Strict Boundary for Agent Separation of Concerns

**Status:** Accepted

**Context:** The project utilizes AI both as a development tool (Copilot) and as the delivered product itself (Maestro). Commingling prompt files or logic limits portability, confuses LLM context generation, and creates circular dependencies.

**Decision:** We mandate a rigid physical filesystem boundary separating Software Factory Agents from Maestro Agents. 

**Consequences:**
- Software Factory Agents (`.github/agents`, `.copilot/skills`, `.vscode`) are strictly for human developer velocity. They do not ship with the runtime Docker containers or exist in the production environment.
- Maestro Agents (`agents/`, `apps/`) are the product. They must be completely self-contained. The production Dockerfile will utilize `.dockerignore` to explicitly exclude `.github/` and `.copilot/` to physically prevent runtime dependence on developer tools.
