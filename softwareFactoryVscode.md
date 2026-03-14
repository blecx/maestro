# softwareFactoryVscode

## Purpose

This document is the authoritative implementation specification for extracting the reusable Software Factory capabilities from the current `maestro` repository into a new standalone GitHub repository named **`softwareFactoryVscode`**.

The intent of this specification is that a follow-up implementation step can execute it end-to-end without needing to infer missing decisions.

The resulting repository must:

- be named **`softwareFactoryVscode`**,
- be fully self-contained,
- include all required runtime and development-time factory artefacts,
- include the companion validation specification `SoftwareFactoryVsocdeTestsuite.md`,
- include the VS Code workspace configuration required to make the host workspace behave like this repository,
- include all required MCP servers, Docker assets, bootstrap scripts, and documentation,
- avoid shipping Maestro-application-specific artefacts,
- support installation into a blank host repository,
- support safe enhancement, maintenance, and upgrades over time.

---

## Mandatory outcome

Create a standalone GitHub repository named:

- **`softwareFactoryVscode`**

This repo will be the canonical home of the reusable factory.

It must be consumable from a host project by cloning it before project start, preferably as a pinned nested repository at one of these paths:

- `.factory/softwareFactoryVscode`
- `tools/softwareFactoryVscode`

Preferred default:

- **`.factory/softwareFactoryVscode`**

The factory must not require any Maestro application code such as `apps/api/`, Maestro-specific frontend artefacts, or references to `maestro-Client`.

---

## Primary objectives

1. Extract all reusable Software Factory capabilities from `maestro`.
2. Keep runtime and meta/developer tooling strictly separated.
3. Provide a complete installation path for a fresh host repo.
4. Provide a complete update and maintenance model.
5. Remove all Maestro-project-specific naming, paths, defaults, and documentation from the extracted package.
6. Preserve per-project isolated Docker/MCP deployment.
7. Preserve or improve current architectural guards.

---

## Non-goals

The new `softwareFactoryVscode` repo must **not** include:

- `apps/api/` from Maestro,
- Maestro product-specific web UI or frontend delivery artefacts,
- `_external/maestro-Client` dependencies,
- Maestro issue queue conventions that are specific to the current backend/client split,
- any repo-specific allowlist hardcoded to `blecx/maestro`,
- any hidden dependency on parent directories outside the host repo,
- any requirement to fetch runtime code from the `maestro` repo after extraction.

---

## Current-state decision

### Readiness verdict

The current `maestro` repository is **not yet releasable as the final standalone package as-is**, but it is **sufficiently mature to serve as the source of extraction**.

### Current strengths to preserve

- existing installer path: `scripts/install_maestro_trunk.py`
- existing runtime scoping: `scripts/maestro_runtime_env.py`
- architectural separation intent in ADRs
- runtime/meta guard test: `tests/test_agent_boundaries.py`
- runtime packaging exclusion via `.dockerignore`
- existing MCP and Docker assets already present in repository

### Current blockers that must be fixed during extraction

- remaining `maestro` naming in docs, compose files, image names, networks, commands
- variable drift between `TARGET_WORKSPACE_PATH`, `PROJECT_WORKSPACE_DIR`, and `WORKSPACE_PATH`
- lingering references to `maestro-Client`
- lingering default repo references such as `YOUR_ORG/YOUR_REPO` and backend/client split assumptions
- runtime lifecycle code still using `/tmp/`
- installation story still oriented around trunk overlay rather than canonical standalone package consumption

---

## Target repository contract

## Repository identity

- **Repo name:** `softwareFactoryVscode`
- **Canonical branch:** `main`
- **Release versioning:** semantic versioning (`v1.0.0`, `v1.1.0`, `v2.0.0`)
- **Distribution model:** Git repository, preferably consumed as a Git submodule or pinned nested clone

## Consumption model

The host project must consume `softwareFactoryVscode` as a versioned dependency rather than copying ad hoc files manually.

Preferred modes, in order:

1. **Git submodule** at `.factory/softwareFactoryVscode`
2. **Pinned nested clone** at `.factory/softwareFactoryVscode`
3. **Generated bundle install** only if Git nesting is not allowed

Default recommendation:

- use a Git submodule for reproducible upgrades and rollback

---

## Architectural rules

The extracted factory must enforce these rules:

1. Runtime code must never depend on `.copilot/`, `.github/agents/`, or `.vscode/`.
2. Developer tooling must never become an accidental runtime dependency.
3. First-party runtime services must become self-contained where practical.
4. Opaque or third-party services may remain single-tenant but must run per host project instance.
5. Factory code and target project code must remain distinguishable at runtime.
6. The host repository must be mountable at `/target` inside containers.
7. Factory-owned runtime code should preferably live at `/factory` inside containers.
8. Bootstrap must be explicit, documented, testable, and reproducible.
9. No use of host-global `/tmp` for package-controlled staging; use workspace-local `.tmp/` in host or package-controlled data paths.
10. All default policies must be neutral and repo-agnostic.

---

## Repository structure for `softwareFactoryVscode`

Use the following top-level structure.

```text
softwareFactoryVscode/
├── SoftwareFactoryVsocdeTestsuite.md
├── .vscode/
│   ├── settings.json
│   ├── tasks.json
│   ├── extensions.json
│   └── extensions/
├── .copilot/
│   ├── config/
│   └── skills/
├── .github/
│   └── agents/
├── compose/
│   ├── docker-compose.factory.yml
│   ├── docker-compose.mcp-bash-gateway.yml
│   ├── docker-compose.mcp-devops.yml
│   ├── docker-compose.mcp-github-ops.yml
│   ├── docker-compose.mcp-offline-docs.yml
│   ├── docker-compose.repo-fundamentals.yml
│   └── docker-compose.context7.yml
├── configs/
│   ├── llm.default.json
│   ├── bash_gateway_policy.default.yml
│   └── runtime/
├── docker/
│   ├── approval-gate/
│   ├── agent-worker/
│   ├── context7/
│   ├── mcp-agent-bus/
│   ├── mcp-bash-gateway/
│   ├── mcp-devops-docker-compose/
│   ├── mcp-devops-test-runner/
│   ├── mcp-github-ops/
│   ├── mcp-memory/
│   ├── mcp-offline-docs/
│   ├── mcp-repo-fundamentals-filesystem/
│   ├── mcp-repo-fundamentals-git/
│   ├── mcp-repo-fundamentals-search/
│   └── mock-llm-gateway/
├── docs/
│   ├── INSTALL.md
│   ├── TESTING.md
│   ├── UPGRADE.md
│   ├── MAINTENANCE.md
│   ├── ARCHITECTURE.md
│   ├── EXTRACTION-SOURCE-MAP.md
│   └── ADR/
├── factory_runtime/
│   ├── agents/
│   ├── apps/
│   └── tests/
├── hooks/
├── manifests/
│   ├── extraction-manifest.json
│   ├── projection-manifest.json
│   └── upgrade-rules.json
├── scripts/
│   ├── bootstrap_host.py
│   ├── install_factory.py
│   ├── project_runtime_env.py
│   ├── project_runtime_up.py
│   ├── project_runtime_down.py
│   ├── project_runtime_validate.py
│   ├── project_upgrade.py
│   ├── project_projector.py
│   ├── check_boundaries.py
│   └── check_neutrality.py
├── templates/
│   ├── host/
│   └── docs/
├── .dockerignore
├── .env.example
├── Makefile
├── pyproject.toml or requirements.txt
└── README.md
```

Notes:

- `factory_runtime/` is the canonical package-owned runtime root.
- If preserving current folder names is required initially, a transition phase may temporarily keep `agents/` and `apps/` at top level, but the end-state should favor a clearer package-owned runtime boundary.
- Compose files should move under `compose/` for clarity.
- `.vscode/` is developer/workspace configuration only. It must never become a runtime dependency, but it must be present or projectable so the host workspace behaves like this one.

---

## Source extraction map from `maestro`

Extract and adapt the following from the current repo.

### Include from current repo

#### Developer/meta factory assets

- `.vscode/settings.json`
- `.vscode/tasks.json`
- `.vscode/extensions.json`
- `.vscode/extensions/**` only if a package-owned workspace extension state is intentionally required and documented
- `.copilot/config/**`
- `.copilot/skills/**`
- `.github/agents/**`
- selected `hooks/**`
- selected setup and projection scripts under `scripts/**`

#### Runtime assets

- required `agents/**` that belong to factory runtime orchestration
- required `apps/mcp/**`
- `apps/approval_gate/**`
- `apps/mock_llm_gateway/**` if needed for deterministic or local testing
- required Dockerfiles under `docker/**`
- compose definitions currently in root `docker-compose*.yml`
- runtime default configs under `configs/**`

#### Tests and validation

- `tests/test_agent_boundaries.py` or an evolved equivalent
- any tests needed to verify runtime/meta separation, runtime startup, and package neutrality

### Exclude from extraction

- `apps/api/**`
- Maestro product-specific templates, docs, or workflows unrelated to the factory
- frontend build and packaging assets tied to the Maestro application
- `_external/maestro-Client/**`
- project-specific issue queues or scripts that hardcode Maestro backend/client repo workflow
- archived or historical artefacts unless explicitly normalized and required

---

## Required neutrality cleanup

Before release, remove or neutralize all of the following categories.

### Naming cleanup

Replace package identity references from `maestro` to neutral or package-owned names where appropriate:

- image names
- network names
- compose project naming prefixes
- CLI help text
- README installation examples
- docs references

Allowed exceptions:

- historical migration notes that mention `maestro` as source only
- citations in source maps

### Repo/path cleanup

Remove or rewrite:

- references to `maestro-Client`
- references to `_external/maestro-Client`
- references to `blecx/maestro`
- references that assume sibling repos or parent directory conventions

### Default policy cleanup

Neutralize:

- `GITHUB_OPS_ALLOWED_REPOS`
- issue/pull-request repo defaults
- docs indexing assumptions
- backend/client split assumptions not universally valid

### Temporary path cleanup

Replace package-controlled `/tmp/` usage with one of:

- host-local `.tmp/softwareFactoryVscode/...`
- container-local `/factory/tmp/...` if ephemeral and internal to container only
- package data directories mounted from host-local `.tmp/softwareFactoryVscode/...`

Rule:

- host-visible, recoverable, or orchestrated temp/state files must not rely on host-global `/tmp`

### VS Code workspace parity cleanup

The extracted package must explicitly preserve the workspace-level VS Code behavior currently required in this repository, but in a neutralized and package-owned form.

This includes at minimum:

- workspace `python.defaultInterpreterPath`
- pytest workspace settings
- terminal temp-directory redirection to workspace-local `.tmp`
- `chat.tools.terminal.autoApprove` policy configuration
- `chat.tools.subagent.autoApprove` configuration
- `issueagent.customAgent` and related agent settings where still applicable
- MCP server wiring in workspace settings
- task definitions in `.vscode/tasks.json`
- extension recommendations in `.vscode/extensions.json`

The extracted package must also define an explicit extension support matrix to preserve the same seamless user experience and automation level.

At minimum, the package must classify extensions into these tiers:

- **Required external extensions**: needed for the intended developer workflow and automation UX
- **Required workspace-local extensions**: package-owned extensions shipped inside the repository if the workflow depends on them
- **Recommended extensions**: not mandatory, but strongly recommended for parity and productivity
- **Optional extensions**: nice-to-have enhancements that must not be required for correctness

The expected baseline matrix should include at least the following categories and default examples:

- **Copilot experience**
  - required external: `GitHub.copilot`, `GitHub.copilot-chat`
- **Python language support**
  - required external: `ms-python.python`, `ms-python.vscode-pylance`
- **JavaScript/TypeScript linting and formatting**
  - recommended external: `dbaeumer.vscode-eslint`, `esbenp.prettier-vscode`
- **GitHub and PR workflow support**
  - recommended external: `GitHub.vscode-pull-request-github`
- **Container/dev environment support**
  - recommended external: `ms-vscode-remote.remote-containers`
- **Docker workflow support**
  - recommended external: `ms-azuretools.vscode-docker`
- **Workspace-local issue workflow extension**
  - required workspace-local if the package continues to rely on `issueagent.customAgent` or equivalent chat participant routing

Context7 should be treated carefully:

- the default assumption should be that **Context7 is provided by the MCP server wiring**, not by a required VS Code extension
- if a Context7-related editor extension is later adopted, it must be documented as recommended or optional unless the workflow truly depends on it

### Concrete proposed extension matrix based on this repository

Use the following concrete recommendation as the default carry-forward matrix for `softwareFactoryVscode`.

#### Hard-required

These are required to preserve the intended automation and developer workflow baseline.

- `GitHub.copilot`
- `GitHub.copilot-chat`
- `ms-python.python`
- `ms-python.vscode-pylance`

#### Recommended

These are not strictly required for correctness, but they are strongly recommended to preserve the same seamless user experience and day-to-day productivity level as this repository.

- `dbaeumer.vscode-eslint`
- `esbenp.prettier-vscode`
- `GitHub.vscode-pull-request-github`
- `ms-vscode-remote.remote-containers`
- `ms-azuretools.vscode-docker`

#### Optional

These may improve workflow quality but must not be required for the factory to function correctly.

- any future Context7-related editor extension, if adopted later
- language-specific extensions for host-project technologies beyond the baseline Python/Copilot workflow
- additional formatter or editor productivity extensions that are user-preference driven rather than workflow-critical

#### Deprecated / not to carry over by default

These must not be copied forward in their current repo-specific form.

- the current Maestro-branded workspace-local extension under `.vscode/extensions/issueagent` in its existing identity (`publisher: maestro`, repository links to `blecx/maestro`, and Maestro-specific naming)
- any extension metadata or workspace-local extension source that still references `maestro`, `blecx/maestro`, or Maestro-specific issue workflow branding

If equivalent custom chat-participant functionality is still required after extraction, it must be reintroduced only as a **neutralized** workspace-local extension owned by `softwareFactoryVscode` with updated naming, repository metadata, settings contract, and documentation.

### Concrete proposed `.vscode/extensions.json` target example

Unless a future implementation chooses a different documented projection model, the package should use the following default target shape for `.vscode/extensions.json`.

This example intentionally distinguishes between broadly recommended marketplace extensions and extensions that are intentionally **not** carried over in their current Maestro-specific form.

```json
{
  "recommendations": [
    "GitHub.copilot",
    "GitHub.copilot-chat",
    "ms-python.python",
    "ms-python.vscode-pylance",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "GitHub.vscode-pull-request-github",
    "ms-vscode-remote.remote-containers",
    "ms-azuretools.vscode-docker"
  ],
  "unwantedRecommendations": ["maestro.issueagent"]
}
```

Notes for this example:

- `GitHub.copilot` and `GitHub.copilot-chat` are listed because the intended workflow and custom-agent experience depend on them.
- `ms-python.python` and `ms-python.vscode-pylance` are listed because the current automation and validation workflow is Python-centric.
- ESLint and Prettier are recommended to preserve code-quality ergonomics for JavaScript/TypeScript host projects, but they are not required for core factory correctness.
- GitHub PR, containers, and Docker support are recommended to preserve the current review and environment-management experience.
- `maestro.issueagent` is shown as unwanted in this example to make clear that the current Maestro-branded local extension must not be carried forward unchanged.
- If the extracted package later ships a neutralized replacement extension, replace `maestro.issueagent` with the new neutral extension ID and move it to the appropriate required or recommended category based on the final workflow contract.

These settings must be either:

- shipped directly as canonical workspace configuration, or
- generated/projected deterministically from package-owned source files such as `.copilot/config/**`

The end result must make a fresh host workspace behave like this repository without requiring undocumented manual VS Code setup.

---

## Required environment contract

All runtime components must standardize on these variables.

### Required variables

- `PROJECT_WORKSPACE_ID`
- `FACTORY_INSTANCE_ID`
- `COMPOSE_PROJECT_NAME`
- `TARGET_WORKSPACE_PATH`
- `FACTORY_AUDIT_DIR`
- `FACTORY_DATA_DIR`
- `FACTORY_CONFIG_DIR`

### Recommended variables

- `FACTORY_ROOT`
- `FACTORY_RUNTIME_ROOT`
- `HOST_FACTORY_DIR`
- `PORT_CONTEXT7`
- `PORT_BASH`
- `PORT_FS`
- `PORT_GIT`
- `PORT_SEARCH`
- `PORT_TEST`
- `PORT_COMPOSE`
- `PORT_DOCS`
- `PORT_GITHUB`
- `PORT_MOCK_LLM`
- `MEMORY_MCP_PORT`
- `AGENT_BUS_PORT`
- `APPROVAL_GATE_PORT`

### Variable unification rule

During extraction, replace all inconsistent mount/path variables with:

- **`TARGET_WORKSPACE_PATH`** for the host repository root mounted into containers

Deprecate and remove use of:

- `PROJECT_WORKSPACE_DIR`
- `WORKSPACE_PATH`

---

## Required runtime deployment model

### Compose scoping

Every compose-driven runtime deployment must be project-scoped.

Requirements:

- use `COMPOSE_PROJECT_NAME`
- avoid hardcoded `container_name`
- use project-scoped volumes and audit directories
- use deterministic per-project port assignment
- avoid exposing host ports for internal-only services when not needed

### Service classes

#### Class A — Opaque single-tenant

Run one isolated stack instance per host project.

#### Class B — First-party runtime services

Preferred end-state:

- baked runtime code under `/factory`
- mounted host repo under `/target`
- no dependency on package source being mounted from arbitrary host paths

#### Class C — Developer tooling

Never required for runtime startup.

### Context7 Docker/MCP artefact and setup contract

`softwareFactoryVscode` must explicitly include Context7 as a first-class factory artefact, because in this repository it is delivered via a Docker image and connected through MCP wiring.

The standalone package must include at minimum:

- the Context7 Docker image definition (currently represented by `docker/context7/Dockerfile`)
- the Context7 compose definition (currently represented by `docker-compose.context7.yml` or its future equivalent under `compose/`)
- the runtime environment variable contract for `PORT_CONTEXT7`
- support for the optional `CONTEXT7_API_KEY`
- `.vscode/settings.json` MCP server wiring for the local Context7 endpoint
- installation and verification documentation for bringing the Context7 service up locally

The default setup contract should be:

- build or start Context7 via the packaged compose stack
- expose the service on the package-managed local port for Context7
- configure VS Code MCP wiring to the local HTTP MCP endpoint
- treat `CONTEXT7_API_KEY` as optional unless a chosen runtime mode requires it

The installation docs must explicitly describe:

- where the Context7 Dockerfile lives
- how the Context7 service is started
- how `CONTEXT7_API_KEY` is supplied when available
- how to verify the Context7 MCP endpoint is reachable
- how the system should behave if the key is absent

---

## Required installation flow

The extracted package must support a clean installation into a brand-new host repo.

## Installation model

### Step 1 — Prepare host repository

The host repo is initialized normally by the user.

### Step 2 — Add factory

Preferred:

- add `softwareFactoryVscode` as a submodule under `.factory/softwareFactoryVscode`

Alternative:

- clone the repo at `.factory/softwareFactoryVscode`

### Step 3 — Bootstrap host

Run a package-owned bootstrap command that:

- validates the host repo is a Git repo
- creates required host-local directories under `.tmp/softwareFactoryVscode/`
- creates `.factory.lock.json`
- creates `.factory.env` from `.env.example` or equivalent
- projects selected configuration into host-visible locations if required
- projects or generates `.vscode/settings.json`, `.vscode/tasks.json`, and `.vscode/extensions.json` so the workspace behaves like this one
- verifies Docker and Python prerequisites

### Step 4 — Configure runtime env

Run a package-owned runtime env generator that writes:

- `.tmp/softwareFactoryVscode/runtime/<project-id>/.env.generated`

### Step 5 — Start factory services

Run the package-owned compose launcher.

This startup flow must explicitly include Context7 as part of the documented factory stack, either in the default compose launch path or in a clearly documented optional profile if the package chooses not to enable it by default.

### Step 6 — Validate installation

Run a package-owned validation command that verifies:

- env generation
- Docker compose startup
- health endpoints
- mounted `/target` visibility
- no missing config assets

---

## Required upgrade and maintenance model

This section is mandatory.

## Version lock

Each consuming host repo must contain:

- `.factory.lock.json`

This lock file must record:

- factory repo name
- factory version or pinned commit
- schema version
- enabled modules
- projected artefacts and versions
- last successful upgrade timestamp

### Example lock fields

```json
{
  "factoryRepo": "softwareFactoryVscode",
  "factoryVersion": "v1.0.0",
  "schemaVersion": 1,
  "installPath": ".factory/softwareFactoryVscode",
  "enabledModules": [
    "copilot-config",
    "github-agents",
    "mcp-runtime",
    "approval-gate"
  ],
  "projectionVersion": 1,
  "lastUpgrade": "2026-03-14T00:00:00Z"
}
```

## Override model

Host-specific customizations must live outside factory-owned canonical sources.

Create host-owned override locations such as:

- `.factory.overrides/copilot/`
- `.factory.overrides/github-agents/`
- `.factory.overrides/runtime/`
- `.factory.overrides/docs/`

Rules:

- do not edit canonical files under `.factory/softwareFactoryVscode` directly
- projection merges canonical defaults with host overrides deterministically
- upgrades must preserve overrides

## Upgrade command

Provide a package-owned upgrade command, for example:

- `scripts/project_upgrade.py`

The upgrade flow must:

1. detect current installed version
2. fetch or switch the target version
3. validate compatibility rules
4. regenerate projected artefacts
5. preserve host overrides
6. re-run validation checks
7. output a migration summary

## Release governance

The `softwareFactoryVscode` repo must maintain:

- release notes per version
- migration notes for breaking changes
- a compatibility matrix for bootstrap schema and projection schema
- CI checks validating fresh install and upgrade paths

---

## Required documentation set

The standalone repo must ship the following docs.

The validation contract in `SoftwareFactoryVsocdeTestsuite.md` is mandatory and must be included alongside the documents below.

### `SoftwareFactoryVsocdeTestsuite.md`

Must include:

- the complete validation strategy for `softwareFactoryVscode`
- automated test categories and acceptance criteria
- CI and release-gate expectations
- failure-mode coverage
- the canonical kickoff prompt for implementing the automated test suite

### `README.md`

Must include:

- what the repo is
- what it contains
- what it does not contain
- quick install
- quick start
- architecture overview
- link to install and upgrade docs
- note whether `.vscode` is shipped directly or projected/generated

### `docs/INSTALL.md`

Must include:

- prerequisites
- host repo preparation
- adding the factory repo
- bootstrap commands
- environment setup
- starting services
- validation steps
- troubleshooting
- how `.vscode/settings.json`, `.vscode/tasks.json`, and `.vscode/extensions.json` are created or updated
- how the Context7 Docker/MCP service is built, started, configured, and verified
- how `CONTEXT7_API_KEY` is supplied when available and how the package behaves when it is absent

### `docs/TESTING.md`

Must include:

- how to run the automated test suite locally
- test environment prerequisites
- how to run static, build, runtime, isolation, and upgrade checks separately
- where logs and diagnostics are collected
- how the test suite maps to `SoftwareFactoryVsocdeTestsuite.md`
- how to verify projected VS Code settings, tasks, MCP server wiring, and extension recommendations

### `docs/VSCODE-WORKSPACE.md`

Must include:

- the canonical workspace settings required for parity with this repository
- which parts are shipped directly versus projected/generated
- MCP server wiring expectations in `.vscode/settings.json`
- terminal auto-approve and subagent auto-approve policy expectations
- task definitions required in `.vscode/tasks.json`
- extension recommendations in `.vscode/extensions.json`
- the required/recommended/optional extension matrix with explicit VS Code extension IDs
- which extensions are external marketplace dependencies versus workspace-local bundled extensions
- whether the workspace-local `issueagent` extension remains part of the package and under what contract
- why Context7 is delivered primarily through MCP wiring rather than a mandatory editor extension
- any optional `.vscode/extensions/**` content and why it exists
- the concrete proposed extension matrix split into hard-required, recommended, optional, and deprecated/not-to-carry-over entries

### `docs/UPGRADE.md`

Must include:

- supported upgrade paths
- backup advice
- version lock behavior
- override preservation behavior
- rollback instructions

### `docs/MAINTENANCE.md`

Must include:

- how to add or replace MCP services
- how to change Docker images safely
- how to add config defaults
- how to add projection rules
- how to add neutrality checks

### `docs/ARCHITECTURE.md`

Must include:

- runtime/meta boundary
- `/factory` + `/target` model
- project-isolated compose model
- service classes
- security and policy assumptions
- the role of `.vscode/` as workspace configuration rather than runtime dependency

### `docs/EXTRACTION-SOURCE-MAP.md`

Must include:

- exact source paths in `maestro`
- exact target paths in `softwareFactoryVscode`
- whether file is copied, adapted, split, or excluded

---

## Required validation and CI

The standalone repo must implement the following checks.

All validation design and CI coverage must satisfy the requirements defined in `SoftwareFactoryVsocdeTestsuite.md`.

## Static checks

- boundary check: runtime must not reference `.copilot/` or `.github/`
- neutrality check: no forbidden `maestro`, `maestro-Client`, `_external/maestro-Client`, or `blecx/maestro` references outside migration docs/source maps
- variable-contract check: compose and scripts use the same canonical env names
- packaging check: `.dockerignore` and runtime builds exclude meta assets
- VS Code workspace parity check: required `.vscode` files, MCP wiring, task labels, and workspace settings are present and consistent with the documented contract

## Runtime checks

- fresh install into empty test repo succeeds
- runtime env generation succeeds
- compose stack starts successfully
- health endpoints respond
- `/target` mount is visible to runtime services
- two different host test repos can run stacks concurrently without conflicts

## Upgrade checks

- install v1
- add host override
- upgrade to newer version
- override is preserved
- validation still passes

---

## Required execution phases

Execute the work in the following phases.

## Phase 0 — Create the new repo scaffold

Deliver:

- GitHub repo `softwareFactoryVscode`
- initial README
- initial folder structure
- baseline CI

Acceptance:

- repository exists
- initial docs and manifests exist

## Phase 1 — Build the extraction manifest

Deliver:

- `manifests/extraction-manifest.json`
- `docs/EXTRACTION-SOURCE-MAP.md`

Acceptance:

- every included and excluded path from `maestro` is explicitly classified

## Phase 2 — Extract canonical assets

Deliver:

- copied/adapted factory assets from `maestro`
- cleaned structure in `softwareFactoryVscode`

Acceptance:

- repo builds without requiring the original `maestro` repo

## Phase 3 — Neutralize identity and defaults

Deliver:

- all Maestro-specific naming removed or rewritten
- repo-neutral defaults established

Acceptance:

- neutrality check passes

## Phase 4 — Unify runtime env contract

Deliver:

- canonical `TARGET_WORKSPACE_PATH` usage
- canonical project runtime env generator
- canonical compose naming and paths

Acceptance:

- no drift remains between scripts and compose files

## Phase 5 — Harden runtime packaging

Deliver:

- `/factory` + `/target` runtime split where feasible
- packaging boundary validation
- `.dockerignore` finalized

Acceptance:

- runtime can boot without developer/meta folders mounted

## Phase 6 — Create bootstrap and projection flow

Deliver:

- `scripts/install_factory.py`
- `scripts/bootstrap_host.py`
- `scripts/project_projector.py`

Acceptance:

- blank host repo can install and bootstrap in one documented flow

## Phase 7 — Create upgrade flow

Deliver:

- `.factory.lock.json` schema
- upgrade command
- override merge logic
- upgrade docs

Acceptance:

- versioned upgrade works and preserves overrides

## Phase 8 — Add clean-room validation

Deliver:

- fresh-install CI job
- dual-host concurrency CI job
- upgrade CI job

Acceptance:

- all jobs pass reliably

## Phase 9 — Final hardening

Deliver:

- documentation polish
- migration notes from `maestro`
- release `v1.0.0`

Acceptance:

- package is self-contained, documented, neutral, and reproducible

---

## Exact artefact requirements

The final `softwareFactoryVscode` repository must contain at minimum:

### Runtime services

- memory MCP
- agent bus MCP
- approval gate
- bash gateway MCP
- repo fundamentals MCPs
- devops MCPs
- offline docs MCP
- GitHub ops MCP
- Context7 MCP service delivered via Docker image and compose artefacts
- mock LLM gateway if required for local deterministic validation

### Runtime orchestration

- compose stack files
- runtime env generation
- startup/down scripts
- validation scripts
- per-project isolation logic

### Developer tooling

- VS Code workspace settings
- VS Code task definitions
- VS Code extension recommendations
- VS Code extension support matrix and installation guidance
- Copilot config
- GitHub agent wrappers
- installation helpers
- projection scripts
- repo setup scripts
- hooks if still part of the desired package behavior

### Documentation

- install
- testing
- VS Code workspace setup
- upgrade
- maintenance
- architecture
- source map
- troubleshooting
- test-suite contract (`SoftwareFactoryVsocdeTestsuite.md`)

---

## Explicit exclusions from the final package

The implementation must ensure the final repo does **not** contain any unavoidable dependency on:

- `apps/api/`
- Maestro-specific frontend build inputs
- `docker/web/Dockerfile` if it still assumes `_external/maestro-Client`
- `scripts` whose only purpose is Maestro-specific issue workflow management unless generalized
- historical knowledge artefacts with Maestro-specific operational assumptions unless archived and excluded from runtime/bootstrapping

---

## Required migration decisions

The follow-up implementation must explicitly decide, record, and implement each of the following:

1. Which current `agents/**` belong in package runtime versus archival or Maestro-specific logic.
2. Which current `scripts/**` become package public commands.
3. Whether `factory_runtime/` replaces current top-level `agents/` and `apps/` now or in a later compatibility phase.
4. Which MCP services remain first-party versus treated as opaque isolated services.
5. Whether projection writes directly into host `.copilot/` and `.github/agents/` or keeps them package-local with symlink/copy projection.
6. Whether `.vscode/settings.json`, `.vscode/tasks.json`, and `.vscode/extensions.json` are canonical files or generated projections.
7. Which VS Code extensions are required, recommended, optional, or workspace-local bundled for parity with this repository.
8. Whether a neutralized replacement for the current workspace-local `issueagent` extension is still necessary.
9. Whether the package publishes a Python CLI entrypoint in addition to scripts.

These decisions must be captured in docs and manifests, not left implicit.

---

## Required implementation checklist

The follow-up step must complete all items below.

- [ ] Create GitHub repo `softwareFactoryVscode`
- [ ] Add initial scaffold and docs
- [ ] Build extraction manifest from `maestro`
- [ ] Copy/adapt factory-relevant assets
- [ ] Remove Maestro-specific names and paths
- [ ] Remove `maestro-Client` coupling
- [ ] Remove `blecx/maestro` coupling
- [ ] Neutralize repo defaults and allowlists
- [ ] Replace host-global `/tmp` usage where package-controlled
- [ ] Unify runtime env variable contract
- [ ] Refactor compose files to use canonical variables and project scoping
- [ ] Introduce or finalize `/factory` + `/target` split
- [ ] Add install/bootstrap flow
- [ ] Add projection flow
- [ ] Add lock file and upgrade flow
- [ ] Add override model
- [ ] Add canonical or generated `.vscode` workspace settings, tasks, and extension recommendations
- [ ] Add explicit required/recommended/optional VS Code extension matrix and installation guidance
- [ ] Add Context7 Docker image, compose setup contract, and installation/verification guidance explicitly to the package
- [ ] Add fresh install validation
- [ ] Add concurrency validation
- [ ] Add upgrade validation
- [ ] Add `SoftwareFactoryVsocdeTestsuite.md` to the standalone repo and align CI to it
- [ ] Write release docs
- [ ] Publish first release

---

## Acceptance criteria for completion

This specification is considered successfully executed only when all of the following are true:

1. A new GitHub repository named `softwareFactoryVscode` exists.
2. It can be cloned into a host project before project work starts.
3. A blank host repo can install and start the full factory through a documented flow.
4. The package contains all required MCP servers and Docker setup.
5. The package includes complete installation documentation.
6. The package contains no required dependency on Maestro application artefacts.
7. No hidden Maestro-specific defaults remain in runtime behavior.
8. The package can be enhanced and upgraded safely via documented versioned workflows.
9. Two host projects can run isolated stacks concurrently.
10. CI proves fresh install, upgrade, and isolation behavior.

---

## Suggested first implementation order

If the next step needs an execution order, use this exact order:

1. Create `softwareFactoryVscode` repo scaffold.
2. Build extraction/source manifest.
3. Extract canonical files.
4. Remove Maestro-specific identity and repo coupling.
5. Unify env/compose contract.
6. Harden packaging boundaries.
7. Add bootstrap and projection.
8. Add upgrade/override model.
9. Add validation and CI.
10. Release `v1.0.0`.

---

## Final instruction to the next step

The next implementation step must treat this document as the complete execution contract.

It must not merely draft another plan.

It must:

- create the standalone repo structure,
- perform the extraction and cleanup,
- implement the install/bootstrap/upgrade flows,
- add the required docs and validation,
- and leave the result in a state that can be used as a self-contained Software Factory package for new host projects.

If any ambiguity remains during implementation, the default decision must favor:

- neutrality,
- self-containment,
- explicit versioning,
- host-project isolation,
- and separation of runtime from developer tooling.
