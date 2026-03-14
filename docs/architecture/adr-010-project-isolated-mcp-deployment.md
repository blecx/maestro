# ADR-010: Project-Isolated MCP Deployment for Opaque or Single-Tenant Services

**Status:** Proposed

**Context:** Maestro runs a mixed set of Dockerized dependencies, including first-party MCP services and third-party or otherwise opaque images. Some services can be improved to support explicit project-aware behavior, but others cannot be safely or economically retrofitted for strict multi-project use within a shared container instance.

This creates a design tension:

- ADR-004 requires strong project isolation across multiple software projects.
- ADR-005 requires a strict boundary between Software Factory tooling and Maestro runtime concerns.
- Some runtime dependencies remain effectively single-tenant by design or by practical constraint.

Attempting to force all services into shared multi-project tenancy would either:

1. require invasive rewrites of opaque services,
2. blur separation of concern by embedding host-project-specific behavior into the wrong layer, or
3. increase operational fragility through partial and unsafe tenancy hacks.

The host environment is assumed to have sufficient resources to run dedicated per-project instances where needed.

**Decision:** Maestro will support two deployment modes for runtime services:

1. **Project-aware first-party services** should prefer explicit project scoping and self-contained runtime packaging.
2. **Opaque, third-party, or operationally expensive-to-modify services** will be treated as single-tenant services and deployed as one isolated instance per project/workspace.

For services in the second category, isolation will be enforced at the deployment boundary using:

- `PROJECT_WORKSPACE_ID`
- `MAESTRO_INSTANCE_ID`
- project-scoped Docker Compose naming
- dedicated Docker networks
- dedicated volumes or bind-mounted state locations
- dedicated audit/output directories
- dedicated host-port allocation, or no host-port publishing when not required

This decision preserves separation of concern:

- Software Factory and editor/project meta tooling remain in `.copilot/`, `.github/agents/`, `.vscode/`, and explicit setup/projection scripts.
- Maestro runtime logic remains in `agents/`, `apps/mcp/`, runtime compose files, and runtime Docker images.
- Target host projects remain mounted or referenced as external workspaces served by the runtime, not mixed into Software Factory ownership.

**Consequences:**

- **Pros:**
  - Preserves ADR-005 separation of concern while still enabling multi-project operation.
  - Avoids invasive modification of third-party or opaque images.
  - Reduces risk of cross-project state leakage.
  - Provides a practical path to run multiple project stacks concurrently on the same host.
  - Keeps first-party services free to evolve toward stronger self-containment over time.

- **Cons:**
  - Increases resource usage because some services will run once per project.
  - Requires stronger lifecycle orchestration around project identity, naming, ports, and cleanup.
  - Increases bootstrap complexity because runtime environments must be generated or parameterized consistently.
  - Can create more Docker objects on the host, requiring disciplined teardown and audit hygiene.

**Implementation Notes:**

- Compose definitions should avoid fixed singleton assumptions such as hard-coded `container_name` values when project concurrency is required.
- Runtime launchers should generate or compute project-scoped environment values and port assignments.
- First-party services should move toward a clearer `/factory` and `/target` separation where runtime code is baked into images and host project files are mounted separately.
- Opaque services do not need to become internally multi-tenant as long as per-project deployment isolation is enforced.

**Validation Expectations:**

- Two independent project stacks can run concurrently on one host without network, port, or state collisions.
- Runtime/meta boundary tests continue to pass.
- Lifecycle commands only affect the intended project stack.
- No runtime service depends on `.copilot/` or `.github/` paths.
