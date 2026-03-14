# Software Factory Independence Plan

## 1. Goal

This plan defines how Maestro can be separated from any single host project and used as a reusable **Software Factory trunk** for bootstrapping and operating new projects.

The target outcome is:

- the Software Factory can be installed into another repository without hidden Maestro-specific assumptions,
- runtime services remain cleanly separated from developer/meta tooling,
- MCP and auxiliary Docker services can safely operate per project,
- third-party or opaque Docker images are handled through deployment isolation rather than risky internal rewrites.

This plan preserves the established separation of concern:

- **Software Factory / meta layer**: `.copilot/`, `.github/agents/`, `.vscode/`, projection scripts, bootstrap tooling
- **Maestro runtime layer**: `agents/`, `apps/mcp/`, runtime Dockerfiles, runtime orchestration
- **Target host project**: mounted or referenced as the project being served by the Software Factory

---

## 2. Architectural Position

### Accepted Constraint

Some Docker images are third-party, opaque, or otherwise not practical to retrofit for multi-project behavior.

### Decision

If a Docker image cannot be made safely multi-project aware, the architectural mitigation is:

- run a **dedicated instance per project**,
- isolate it with a **project-specific network**,
- isolate it with **project-specific volumes and audit paths**,
- isolate it with **project-specific container/service naming or compose project scoping**,
- isolate it with **project-specific host ports**, or avoid host port publishing entirely where possible.

This is acceptable because the host has sufficient resources and because deployment isolation is cleaner than violating separation of concern by teaching opaque images project awareness they do not support.

---

## 3. Proposed ADR

### ADR-010: Project-Isolated MCP Deployment for Opaque or Single-Tenant Services

**Status:** Proposed

**Context:**

Maestro depends on a set of Dockerized services, including first-party MCP servers and third-party or opaque runtime components. Some of these services cannot be safely or economically modified to support strict multi-project tenancy within a single process or container instance.

**Decision:**

1. Services that are **first-party and modifiable** should prefer explicit project scoping and self-contained images.
2. Services that are **third-party, opaque, or operationally too costly to modify** are treated as **single-tenant black boxes**.
3. Single-tenant services must run as **one isolated deployment instance per project/workspace**.
4. Isolation is enforced at the deployment boundary using `PROJECT_WORKSPACE_ID`, `MAESTRO_INSTANCE_ID`, dedicated Docker networks, dedicated volumes, dedicated audit directories, and dedicated port allocation or internal-only networking.

**Consequences:**

### Pros

- preserves separation of concern,
- avoids invasive modification of opaque services,
- reduces cross-project contamination risk,
- allows safe concurrent use across multiple repositories on the same host.

### Cons

- increases baseline resource usage,
- requires stronger runtime naming and lifecycle orchestration,
- increases bootstrap and operational complexity.

---

## 4. Core Principles

The following principles must remain true throughout implementation:

1. **Runtime code must never depend on `.copilot/` or `.github/`.**
2. **Editor projection configuration must never become runtime configuration by accident.**
3. **Factory code and target project files must be distinguishable at runtime.**
4. **Opaque services are isolated by deployment, not patched into fake multitenancy.**
5. **Bootstrap must be explicit, reproducible, and complete.**

---

## 5. Runtime Service Classes

To avoid ambiguity, all services should be assigned to one of three classes.

### Class A — Opaque Single-Tenant Services

Examples:

- third-party images,
- externally maintained services,
- services with fixed internal assumptions that are not worth rewriting.

**Policy:** Run one instance per project.

### Class B — First-Party Maestro Runtime Services

Examples:

- `mcp-memory`
- `mcp-agent-bus`
- repo fundamentals MCPs
- bash gateway MCP
- devops MCPs
- github ops MCP
- offline docs MCP

**Policy:** Prefer self-contained, project-aware services. If a service is not yet fully self-contained, it should still run per project until upgraded.

### Class C — Development and Meta Tooling

Examples:

- `.copilot/config`
- `.copilot/skills`
- `.github/agents`
- VS Code setup and projection scripts

**Policy:** Never used as runtime dependencies.

---

## 6. Mitigation Roadmap

## Phase 0 — Lock the Architecture

### Phase 0 objective

Freeze the deployment model before implementation changes begin.

### Phase 0 actions

- Create and adopt ADR-010.
- Update architecture documentation to distinguish:
  - modifiable project-aware services,
  - opaque per-project isolated services,
  - meta/development-only tooling.
- Define the official runtime contract for project identity:
  - `PROJECT_WORKSPACE_ID`
  - `MAESTRO_INSTANCE_ID`
  - target project root path

### Phase 0 acceptance criteria

- Every runtime component is classified into one of the three service classes.
- Documentation clearly describes why per-project isolated deployment is acceptable.
- Runtime/meta separation remains intact.

---

## Phase 1 — Make the Trunk Installable

### Phase 1 problem

The current bootstrap/sync path does not carry enough assets to make the Software Factory portable into another repository.

### Phase 1 objective

Provide one explicit, reproducible installer path that assembles all required runtime and meta assets.

### Phase 1 actions

- Replace or supersede the current sync flow with a dedicated installer, such as:
  - `scripts/install_maestro_trunk.py`, or
  - `scripts/sync_maestro_bundle.py`
- Ensure the installer copies or installs at least:
  - `agents/`
  - `apps/mcp/`
  - `docker/`
  - `scripts/`
  - `.copilot/skills/`
  - `.copilot/config/`
  - `.github/agents/`
  - `docker-compose*.yml`
  - `hooks/`
  - runtime starter config files
  - essential bootstrap documentation
- Stop using `/tmp/maestro-trunk` and move staging to workspace-local `.tmp/`.

### Phase 1 acceptance criteria

- A blank test repository can install the Software Factory in one explicit step.
- No copied compose file or setup script references a missing asset.
- The bootstrap process is workspace-local and policy-compliant.

---

## Phase 2 — Introduce a Project-Isolated Runtime Launcher

### Phase 2 problem

Several compose stacks still behave like singleton host-wide services due to fixed names and fixed ports.

### Phase 2 objective

Generate project-specific runtime identity, ports, and compose context so that each project runs its own isolated stack.

### Phase 2 actions

- Create a canonical launcher that computes runtime identity and generated environment files.
- Suggested artifacts:
  - `scripts/maestro_runtime_env.py`
  - `.tmp/maestro/runtime/<project-id>/.env.generated`
  - optional generated compose override files under `.tmp/maestro/runtime/<project-id>/`
- Derive and publish:
  - `PROJECT_WORKSPACE_ID`
  - `MAESTRO_INSTANCE_ID`
  - `COMPOSE_PROJECT_NAME`
  - project-specific data directories
  - project-specific audit directories
  - project-specific host port blocks
- Standardize one target mount variable, such as `TARGET_WORKSPACE_PATH`.
- Avoid host-port publishing for internal-only services when not needed.

### Phase 2 acceptance criteria

- Two different projects can run the full Maestro stack concurrently on one host.
- There are no container name conflicts.
- There are no host port conflicts.
- Audit and data paths are isolated per project.

---

## Phase 3 — Separate Factory Code from Target Project at Runtime

### Phase 3 problem

Some runtime containers currently depend on the mounted workspace for both their own server code and the target project content.

### Phase 3 objective

Strengthen separation of concern by separating factory code from target repository content inside containers.

### Phase 3 actions

- Adopt a two-root runtime model where practical:
  - `/factory` → Maestro runtime/tooling code baked into the image
  - `/target` → host project mounted at runtime
- For first-party services:
  - copy server code into the image,
  - copy required static policy/config assets into the image,
  - run the service from `/factory`,
  - access the host project only through `/target`.
- For opaque third-party images:
  - do not force self-containment if impossible,
  - instead run one isolated deployment per project.

### Phase 3 acceptance criteria

- First-party images can boot their service code without mounting the Maestro source tree.
- Target project access is explicit and separate from factory runtime code.
- Opaque services remain isolated per project without cross-project contamination.

---

## Phase 4 — Ship Real Default Runtime Config and Neutral Defaults

### Phase 4 problem

The trunk still has runtime references to missing config assets and some defaults remain Maestro-specific.

### Phase 4 objective

Provide complete, neutral runtime defaults so the Software Factory can bootstrap cleanly into a new project.

### Phase 4 actions

- Add and maintain required runtime defaults, including at least:
  - `configs/llm.default.json`
  - `configs/bash_gateway_policy.default.yml`
- Optionally separate runtime config ownership more explicitly, for example:
  - runtime config under `configs/runtime/`
  - editor/projection config under `.copilot/config/`
- Remove or neutralize repo-specific defaults such as:
  - default GitHub allowlists bound to `blecx/maestro`
  - project-specific docs indexing assumptions where inappropriate
- Prefer:
  - empty defaults,
  - auto-detection from current git remote,
  - or explicit installer-time prompts.

### Phase 4 acceptance criteria

- Runtime can start from a clean install without missing-file failures.
- A new host repository does not inherit Maestro-specific repo policy unintentionally.
- All required default runtime config assets exist in the trunk.

---

## Phase 5 — Enforce Runtime Packaging Boundaries

### Phase 5 problem

The code boundary between runtime and meta tooling exists, but packaging/build boundaries are not yet strictly enforced.

### Phase 5 objective

Ensure runtime images and runtime deployment artifacts do not accidentally include or depend on meta/development assets.

### Phase 5 actions

- Add a root `.dockerignore` to exclude at least:
  - `.github/`
  - `.copilot/`
  - `.vscode/`
  - `.tmp/`
  - `agents/training/`
  - `__pycache__/`
  - other development-only artifacts
- Add validation checks asserting that runtime build paths do not rely on:
  - `.copilot/`
  - `.github/agents/`
  - training artifacts
  - editor-only projection outputs

### Phase 5 acceptance criteria

- Runtime image builds do not package meta/development assets.
- Runtime services continue to function without access to `.copilot/` or `.github/`.
- Packaging behavior matches architectural boundary rules in practice.

---

## Phase 6 — Align Lifecycle Management with Project Isolation

### Phase 6 problem

Runtime code and deployment configuration are not yet fully aligned on project-specific scoping.

### Phase 6 objective

Make lifecycle operations strictly project-scoped.

### Phase 6 actions

- Ensure all compose-defined services receive and use:
  - `PROJECT_WORKSPACE_ID`
  - `MAESTRO_INSTANCE_ID`
  - target workspace path
  - project-specific audit and data locations
- Update bootloader logic to operate in terms of project-specific stacks rather than host-wide singleton assumptions.
- Ensure health checks, startup, teardown, snapshot, and restore logic are bound to the intended project stack.

### Phase 6 acceptance criteria

- Starting one project stack does not affect another.
- Reusing containers only occurs for the same project/instance identity.
- Lifecycle commands remain deterministic and project-scoped.

---

## Phase 7 — Quarantine Historical Contamination

### Phase 7 problem

Historical training and learning artifacts still contain legacy repository references that could reintroduce stale assumptions.

### Phase 7 objective

Ensure historical artifacts cannot affect bootstrap, packaging, or runtime behavior.

### Phase 7 actions

- Decide whether to:
  - archive them,
  - exclude them,
  - or normalize them if they remain operationally relevant.
- At minimum, ensure they are not part of:
  - bootstrap bundles,
  - runtime image contexts,
  - default operational validation,
  - runtime assumptions.

### Phase 7 acceptance criteria

- Legacy repository references do not affect current bootstrap or runtime behavior.
- Historical artifacts are clearly marked as archive-only, excluded, or normalized.

---

## 7. Recommended Implementation Order

To minimize architectural risk, implement in this sequence:

1. Write and adopt ADR-010.
2. Build the installer/bootstrap bundle.
3. Build the project-isolated runtime launcher.
4. Refactor compose files for per-project isolation.
5. Add required default runtime configs.
6. Make first-party images self-contained with a `/factory` + `/target` split.
7. Add `.dockerignore` and packaging validation.
8. Archive or exclude stale historical artifacts.

---

## 8. Suggested Issue Breakdown

### Issue A — ADR and Topology Contract

**Size:** S

Deliver:

- ADR-010
- documentation updates for isolated per-project deployment of opaque services

### Issue B — Bootstrap Installer

**Size:** M

Deliver:

- installer script
- manifest of required assets
- replacement of `/tmp` staging with `.tmp`

### Issue C — Runtime Environment Generator

**Size:** M

Deliver:

- generated per-project env
- deterministic project identity
- deterministic or reserved per-project port allocation

### Issue D — Compose Isolation Refactor

**Size:** M

Deliver:

- removal of fixed `container_name`
- parameterized ports
- consistent propagation of project identity variables

### Issue E — Runtime Default Config Assets

**Size:** S

Deliver:

- `configs/llm.default.json`
- `configs/bash_gateway_policy.default.yml`
- neutral bootstrap defaults

### Issue F — First-Party Image Self-Containment

**Size:** L (likely split by service domain)

Deliver:

- `/factory` and `/target` split
- Dockerfile updates per first-party service

### Issue G — Packaging Boundary Enforcement

**Size:** S

Deliver:

- `.dockerignore`
- validation checks for runtime build boundaries

### Issue H — Historical Artifact Quarantine

**Size:** S

Deliver:

- archive or exclusion policy
- docs describing what is operational vs. historical

---

## 9. Definition of Success

The Software Factory independence effort is successful when all of the following are true:

- Maestro can be installed into a new repository through one explicit, complete bootstrap path.
- Runtime services do not depend on `.copilot/` or `.github/`.
- First-party services are self-contained or explicitly isolated by design.
- Opaque services run safely as per-project isolated deployments.
- Multiple project stacks can run on the same host without naming, network, or state collisions.
- Runtime packaging excludes meta/development assets.
- No hidden Maestro-specific repo assumptions remain in defaults.

---

## 10. Summary

The correct architectural answer is not to force every image into shared multi-project behavior.

The correct answer is:

- preserve separation of concern,
- make bootstrap complete,
- isolate opaque services per project,
- make first-party services self-contained where practical,
- and enforce the runtime/meta boundary in code, packaging, and operations.

With these measures, the Software Factory can become a reusable trunk rather than a project-bound implementation detail.
