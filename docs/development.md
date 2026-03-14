For AI and Autonomous agent setup documentation and integrations, refer to [Maestro Toolchain Setup](https://github.com/blecx/maestro).

## Agent Typology and Separation of Concerns

Maestro distinguishes between two distinct classes of agents:

1. **Software Factory Agents:**
   - **Purpose**: Developer-facing SDLC assistants (e.g., GitHub Copilot).
   - **Location**: `.vscode/`, `.github/agents/`, `.copilot/skills/`.
   - **Environment**: Only active during development.

2. **Maestro Agents:**
   - **Purpose**: Runtime autonomous orchestrators (e.g., Planner, Coder, Ralph).
   - **Location**: `agents/` and `apps/mcp/` (prompts belong in `agents/prompts/` and `agents/tooling/`).
   - **Environment**: Shipped with the Maestro product.

**Architectural Rule:** Maestro runtime applications must *never* read from or depend on Software Factory Agent folders (`.github` or `.copilot`). See ADR-005 for more details.
