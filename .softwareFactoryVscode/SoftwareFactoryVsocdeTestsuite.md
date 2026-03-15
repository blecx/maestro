# SoftwareFactoryVsocdeTestsuite

## Purpose

This document is the authoritative test-suite specification for the standalone GitHub repository **`softwareFactoryVscode`**.

It defines how the extracted Software Factory must be verified so that it is proven to work as designed, not merely assumed to work.

This specification is intended to be included in the future `softwareFactoryVscode` repository as a file with the exact name:

- **`SoftwareFactoryVsocdeTestsuite.md`**

The filename is intentionally preserved exactly as specified by the delivery contract.

---

## Relationship to `softwareFactoryVscode.md`

This document is a mandatory companion to `softwareFactoryVscode.md`.

Rules:

1. `softwareFactoryVscode.md` defines **what must be built**.
2. `SoftwareFactoryVsocdeTestsuite.md` defines **how correctness must be proven**.
3. The implementation is incomplete unless both documents are included in the resulting `softwareFactoryVscode` repository.
4. CI, validation scripts, and release gates must align with this document.

---

## Mandatory test objective

The test suite must prove all of the following:

1. The factory can be installed into a blank host repository.
2. The factory can bootstrap all required development and runtime artefacts.
3. The factory can start the required MCP/runtime services successfully.
4. Runtime/meta separation is preserved.
5. The package is neutral and contains no hidden Maestro-project coupling.
6. Per-project isolation works.
7. Upgrade and maintenance workflows work without breaking host customizations.
8. Failure conditions are detected clearly and safely.
9. The package is documented well enough that a clean-room user can follow the process.
10. The release can be trusted because the above checks are enforced automatically.

---

## Test philosophy

The validation model for `softwareFactoryVscode` must use multiple layers.

### Layer 1 — Static correctness

Validate structure, naming, references, manifests, docs, and boundaries without starting services.

### Layer 2 — Build correctness

Validate Docker builds, Python/package setup, generated config, and projection output.

### Layer 3 — Runtime correctness

Validate services actually start, respond, mount the target workspace correctly, and operate with correct isolation.

### Layer 4 — Lifecycle correctness

Validate install, bootstrap, up/down, restart, cleanup, snapshot, restore, and upgrade behavior.

### Layer 5 — Compatibility correctness

Validate upgrades, overrides, version lock handling, and multi-version migration.

### Layer 6 — Operational resilience

Validate failure modes, missing prerequisites, bad configuration, port conflicts, and partial startup behavior.

### Layer 7 — Human usability

Validate documentation accuracy and the operator prompt that starts the test run.

---

## Scope

The test suite must cover all major dimensions of the package.

### In scope

- repository structure
- extraction completeness
- packaging boundaries
- install/bootstrap flow
- projection flow
- VS Code workspace settings parity
- configuration defaults
- environment generation
- Docker compose behavior
- MCP service availability
- runtime/service health
- target workspace mounting
- isolation between two host repos
- upgrade flow
- override preservation
- CI/release gating
- documentation quality
- operator/test runner prompt quality

### Out of scope

- testing Maestro product-specific app behavior
- validating excluded Maestro application artefacts
- performance tuning beyond sanity-level acceptance
- SaaS-grade scale testing

---

## Required repository artefacts for testing

The future `softwareFactoryVscode` repo must include the following test-related artefacts.

### Test documents

- `SoftwareFactoryVsocdeTestsuite.md`
- `docs/TESTING.md`
- `docs/VSCODE-WORKSPACE.md`
- `docs/TROUBLESHOOTING.md`

### Test directories

- `tests/unit/`
- `tests/integration/`
- `tests/e2e/`
- `tests/fixtures/`
- `tests/contracts/`
- `tests/cleanroom/`

### Test support scripts

- `scripts/project_runtime_validate.py`
- `scripts/check_boundaries.py`
- `scripts/check_neutrality.py`
- `scripts/check_variable_contract.py`
- `scripts/check_vscode_workspace.py`
- `scripts/check_docs_accuracy.py`
- `scripts/test_fresh_install.py`
- `scripts/test_upgrade_path.py`
- `scripts/test_dual_host_isolation.py`
- `scripts/test_failure_modes.py`

### CI workflows

- `.github/workflows/ci-static.yml`
- `.github/workflows/ci-build.yml`
- `.github/workflows/ci-runtime.yml`
- `.github/workflows/ci-upgrade.yml`
- `.github/workflows/ci-release-gate.yml`

---

## Required test environments

The test plan must run in at least the following environments.

### Environment A — Local developer Linux

Purpose:

- baseline contributor workflow
- iterative debugging
- local reproduction of CI failures

### Environment B — Clean-room ephemeral Linux CI runner

Purpose:

- verify there are no hidden local assumptions
- verify documentation-driven install works from zero

### Environment C — Dual-workspace isolation environment

Purpose:

- verify two separate host repos can run the stack concurrently

### Environment D — Upgrade environment

Purpose:

- install older tagged version
- apply host overrides
- upgrade to a newer version
- validate preservation and compatibility

Optional but recommended later:

- macOS local developer environment
- rootless Docker environment
- limited-network environment for offline docs scenarios

---

## Test matrix

The suite must test the following scenario matrix.

| Scenario                                                  |    Install | Runtime | Upgrade | Isolation | Docs | Required |
| --------------------------------------------------------- | ---------: | ------: | ------: | --------: | ---: | -------: |
| Blank host repo, default config                           |        yes |     yes |      no |        no |  yes |      yes |
| Blank host repo, explicit config overrides                |        yes |     yes |      no |        no |  yes |      yes |
| Host repo with existing `.copilot/` and `.github/agents/` |        yes |     yes |      no |        no |  yes |      yes |
| Two host repos concurrently                               |        yes |     yes |      no |       yes |   no |      yes |
| Old version upgraded to new version                       |        yes |     yes |     yes |        no |  yes |      yes |
| Missing tokens / missing optional secrets                 |        yes | partial |      no |        no |  yes |      yes |
| Missing required runtime dependency                       | no/partial |      no |      no |        no |  yes |      yes |
| Bad override input                                        |        yes | partial |     yes |        no |  yes |      yes |
| Release candidate gate                                    |        yes |     yes |     yes |       yes |  yes |      yes |

---

## Test categories

## Category 1 — Repository structure and completeness

### Category 1 goal

Prove the standalone repo contains everything promised by `softwareFactoryVscode.md`.

### Category 1 required checks

- required folders exist
- required compose files exist
- required Dockerfiles exist
- the Context7 Dockerfile exists if Context7 is part of the package contract
- required scripts exist
- required docs exist
- required manifests exist
- required configs exist
- required `.vscode/settings.json`, `.vscode/tasks.json`, and `.vscode/extensions.json` exist or are explicitly generated by documented bootstrap flow
- `SoftwareFactoryVsocdeTestsuite.md` exists in repo root or documented canonical location

### Category 1 acceptance criteria

- no required path is missing
- extraction/source map and manifests agree with actual filesystem

---

## Category 2 — Neutrality and contamination checks

### Category 2 goal

Prove the package no longer depends on Maestro-specific identities or paths.

### Category 2 forbidden references

- `blecx/maestro`
- `maestro-Client`
- `_external/maestro-Client`
- Maestro-specific runtime repo assumptions
- hardcoded sibling repo layouts

### Category 2 required checks

- grep-based and semantic neutrality scan
- docs neutrality check
- compose neutrality check
- script neutrality check
- default config neutrality check
- package metadata neutrality check

### Category 2 acceptance criteria

- no forbidden references remain outside explicitly allowed migration/source-map files

---

## Category 3 — Runtime/meta boundary checks

### Category 3 goal

Prove runtime code cannot accidentally rely on meta tooling.

### Category 3 required checks

- runtime source does not import or reference `.copilot/`
- runtime source does not import or reference `.github/agents/`
- runtime images do not package `.copilot/`, `.github/`, `.vscode/`
- package-owned tests confirm the boundary continuously

### Category 3 acceptance criteria

- boundary checks pass in local and CI environments

---

## Category 4 — Variable contract checks

### Category 4 goal

Prove scripts, compose files, and docs all use one canonical environment contract.

### Category 4 required checks

- only canonical env variable names are used for workspace path handling
- deprecated names like `PROJECT_WORKSPACE_DIR` and `WORKSPACE_PATH` are absent or intentionally mapped with documented compatibility logic
- docs use the same names as scripts and compose files

### Category 4 acceptance criteria

 a clean host workspace can obtain the required `.vscode` behavior from the shipped `.softwareFactoryVscode/.vscode/` assets and documented host-local bootstrap outputs without undocumented manual setup

---

## Category 4b — VS Code workspace parity checks

### Category 4b goal

Prove the package reproduces the VS Code workspace behavior required for this factory to operate like the current repository.

### Category 4b required checks

- `.vscode/settings.json` exists or is generated deterministically
- `.vscode/tasks.json` exists or is generated deterministically
- `.vscode/extensions.json` exists or is generated deterministically
- workspace settings include the required Python interpreter and pytest configuration
- workspace settings redirect temp variables to workspace-local `.tmp` where required
- workspace settings define MCP server wiring consistently with the package runtime contract
- workspace settings define terminal auto-approve and subagent auto-approve behavior where required by the factory workflow
- task definitions include the required setup, runtime, validation, and maintenance tasks
- extension recommendations include all required or recommended extensions documented by the package
- extension recommendations distinguish required, recommended, and optional extension expectations in the documentation contract
- required external extension IDs for Copilot and Python language support are documented and validated
- recommended external extension IDs for linting, formatting, PR workflow, containers, and Docker support are documented and validated
- deprecated or not-to-carry-over extension entries are documented explicitly, including the current Maestro-branded `issueagent` form if it is not neutralized
- the concrete proposed `.vscode/extensions.json` target example is present in the documentation or an equivalent canonical payload is defined and validated
- if a workspace-local extension such as `issueagent` is part of the package contract, its source path, activation contract, and expected settings integration are validated
- Context7 behavior is validated against the documented rule that MCP wiring is primary and any editor extension is optional unless explicitly required
- `docs/VSCODE-WORKSPACE.md` matches the actual `.vscode` contract

### Category 4b acceptance criteria

- a clean host workspace can obtain the required `.vscode` behavior from the shipped `.softwareFactoryVscode/.vscode/` assets and documented host-local bootstrap outputs without undocumented manual setup

---

## Category 5 — Install and bootstrap checks

### Category 5 goal

Prove a new host repo can adopt the factory cleanly.

### Category 5 required scenarios

1. initialize an empty Git repo
2. add `softwareFactoryVscode` under `.softwareFactoryVscode`
3. run install/bootstrap command
4. create lock file and env files
5. keep tool-owned workspace/governance config inside the hidden tool tree
6. validate host repo remains usable

### Category 5 required checks

- bootstrap exits successfully
- `.factory.lock.json` is generated
- `.factory.env` or equivalent is generated
- host `.tmp/softwareFactoryVscode/` directories are created
- no tool-owned `.vscode/`, `.github/`, or `.copilot/` files are projected into the host repo by default
- hidden tool-owned workspace files remain inside `.softwareFactoryVscode/`
- re-running bootstrap is idempotent

### Category 5 acceptance criteria

- first run succeeds
- second run is safe and deterministic

---

## Category 6 — Configuration default checks

### Category 6 goal

Prove the package ships complete neutral defaults.

### Category 6 required checks

- `configs/llm.default.json` exists and is readable
- `configs/bash_gateway_policy.default.yml` exists and is readable
- default configs are neutral and do not silently bind to Maestro-specific repos
- Context7 configuration and `CONTEXT7_API_KEY` handling are documented and behave as specified
- missing optional secrets produce understandable warnings, not opaque crashes
- missing required settings are surfaced clearly

### Category 6 acceptance criteria

- clean install can reach a known-good baseline without missing-file failures

---

## Category 7 — Docker build checks

### Category 7 goal

Prove all required first-party images build successfully.

### Category 7 required checks

- each required Dockerfile builds in CI
- the Context7 Docker image builds successfully when Context7 is part of the package contract
- runtime images use only permitted build context inputs
- `.dockerignore` excludes meta/development artefacts correctly
- build failures give actionable diagnostics

### Category 7 acceptance criteria

- all required images build successfully in clean CI

---

## Category 8 — Runtime startup and health checks

### Category 8 goal

Prove the full runtime stack can start and respond.

### Category 8 required services

- memory MCP
- agent bus MCP
- approval gate
- bash gateway MCP
- repo fundamentals MCPs
- devops MCPs
- offline docs MCP
- GitHub ops MCP
- Context7 MCP service delivered through the packaged Docker image and compose artefacts
- mock LLM gateway if included in default or test profile

### Category 8 required checks

- runtime env generation succeeds
- compose startup succeeds
- health endpoints respond where applicable
- service logs do not contain startup-fatal errors
- Context7 service startup and MCP endpoint reachability are verified according to the documented setup contract
- target workspace is mounted and visible at `/target`
- package-owned runtime code is reachable at `/factory` where the split is implemented

### Category 8 acceptance criteria

- stack reaches healthy or expected-ready state within a documented timeout

---

## Category 9 — Host workspace interaction checks

### Category 9 goal

Prove the factory interacts with the host repo correctly and safely.

### Category 9 required checks

- host repo files are readable from `/target`
- factory actions do not mutate unrelated host files during bootstrap
- host-local data/audit directories are created under `.tmp/softwareFactoryVscode/`
- generated host-local artifacts are deterministic and tool-owned files remain in the hidden tree
- no hidden dependency on parent directories exists

### Category 9 acceptance criteria

- host workspace behavior matches documented ownership and mount rules

---

## Category 10 — Per-project isolation checks

### Category 10 goal

Prove two host repositories can run isolated stacks concurrently.

### Category 10 required scenario

- create host repo A
- create host repo B
- install the same factory version in both
- start both stacks concurrently
- inspect ports, volumes, networks, audit paths, and service health

### Category 10 required checks

- no container naming collisions
- no port collisions
- no network collisions
- no shared data contamination
- lifecycle operations in A do not affect B
- audit and state paths remain separated

### Category 10 acceptance criteria

- both host repos remain healthy and isolated concurrently

---

## Category 11 — Upgrade and override preservation checks

### Category 11 goal

Prove versioned maintenance works safely.

### Category 11 required scenario

1. install version N
2. create host overrides
3. start and validate stack
4. upgrade to version N+1
5. re-run projection and validation
6. verify overrides are preserved

### Category 11 required checks

- lock file version updates correctly
- compatibility rules are enforced
- overrides survive upgrade unchanged unless an explicit migration rule applies
- migration summary is generated
- rollback path is documented and testable

### Category 11 acceptance criteria

- upgrade succeeds without loss of host intent

---

## Category 12 — Failure mode checks

### Category 12 goal

Prove the factory fails safely and intelligibly.

### Category 12 required scenarios

- Docker unavailable
- Python unavailable or wrong version
- malformed env file
- port already occupied
- invalid override syntax
- broken compose file
- corrupted lock file
- partial install state

### Category 12 required checks

- errors are surfaced clearly
- partial installs can be retried safely
- no silent destructive cleanup occurs
- diagnostics point to remediation steps

### Category 12 acceptance criteria

- failure paths are actionable and non-destructive

---

## Category 13 — Documentation and prompt checks

### Category 13 goal

Prove a clean-room user can follow the docs and the startup prompt.

### Category 13 required checks

- README quick-start matches actual commands and file paths
- INSTALL guide matches actual bootstrap flow
- UPGRADE guide matches actual upgrade flow
- `VSCODE-WORKSPACE` guide states clearly that tool-owned workspace files stay inside `.softwareFactoryVscode/` and only documented host-local artifacts are generated
- `VSCODE-WORKSPACE` guide includes the explicit required/recommended/optional extension matrix with concrete extension IDs
- `VSCODE-WORKSPACE` guide includes a concrete `.vscode/extensions.json` target example or equivalent canonical extension payload
- INSTALL and VSCODE-WORKSPACE docs explain the Context7 Docker artefact, startup path, `CONTEXT7_API_KEY` handling, and MCP wiring expectations accurately
- TROUBLESHOOTING covers common failures verified by tests
- the operator prompt in this document accurately starts the validation flow

### Category 13 acceptance criteria

- a reviewer unfamiliar with the repo can follow the documented path without tribal knowledge

---

## Category 14 — Release gate checks

### Category 14 goal

Prove a release cannot ship unless core guarantees hold.

### Category 14 required checks

- static checks required before build checks
- build checks required before runtime checks
- runtime checks required before upgrade checks
- all mandatory jobs required for release tag or release PR

### Category 14 acceptance criteria

- no release is permitted while mandatory tests fail

---

## Test implementation requirements

The follow-up implementation must create a layered test suite.

## Unit tests

Purpose:

- validate deterministic helpers and contract logic

Examples:

- env generation logic
- path normalization logic
- lock file schema validation
- override merge logic
- neutrality scanner logic
- variable-contract scanner logic

## Integration tests

Purpose:

- validate cross-component behavior without requiring full dual-host scenarios

Examples:

- bootstrap + host-local artifact interactions
- compose env generation + config loading
- runtime validation scripts
- docs command extraction verification

## End-to-end tests

Purpose:

- validate true user journeys

Examples:

- blank repo install
- full stack startup
- dual-host isolation
- upgrade with overrides
- release-gate workflow

## Contract tests

Purpose:

- enforce static contracts described in `softwareFactoryVscode.md`

Examples:

- required file list
- forbidden reference list
- canonical env names
- documentation presence
- manifest completeness

---

## Required test fixtures

The future repo must define reusable fixtures for:

- blank Git host repo
- host repo with existing `.copilot/` config
- host repo with existing `.github/agents/`
- host repo with overrides
- host repo with intentionally broken config
- dual-host concurrent setup
- legacy-version install fixture for upgrade testing

Fixture rules:

- fixtures must be deterministic
- no hidden dependence on local parent directories
- no secrets committed in fixtures
- generated data must live under repo-local test temp directories

---

## Required scripts and commands to validate

At minimum, the suite must execute and validate behavior for:

- install command
- bootstrap command
- projection command
- runtime env generation command
- runtime up command
- runtime down command
- runtime validate command
- upgrade command
- neutrality check command
- boundary check command
- variable-contract check command

Each command must have:

- expected success conditions
- expected failure diagnostics
- idempotency expectations where applicable

---

## Required observability during tests

The test suite must collect enough diagnostics to debug failures quickly.

### Must collect on failure

- command exit code
- stdout/stderr
- relevant generated env files
- relevant logs from failed services
- compose ps/state snapshot
- host temp/audit directory listing
- diff of generated host-local artifacts when useful

### Must avoid

- leaking secrets in logs
- non-deterministic temporary storage outside declared test temp areas

---

## Performance and timing policy

This is not primarily a performance benchmark suite, but sanity thresholds are required.

### Required timing assertions

- bootstrap completes within a documented reasonable timeout on CI
- env generation completes quickly
- health checks become ready within documented service-specific timeouts
- upgrade does not hang indefinitely

The suite must fail on timeout with actionable diagnostics.

---

## Security and safety test requirements

The suite must verify that:

- meta tooling is not accidentally shipped inside runtime images
- package-controlled temp/state files are not routed to forbidden host-global locations
- overrides cannot silently rewrite factory-owned canonical source files
- generated files do not expose secrets unnecessarily
- docs do not instruct unsafe destructive defaults

---

## Required CI pipeline design

The future `softwareFactoryVscode` repo must implement at least the following pipeline stages.

## Stage 1 — Static

Runs:

- markdown/docs lint
- required file check
- neutrality check
- boundary check
- variable-contract check
- VS Code workspace parity check
- manifest validation

## Stage 2 — Build

Runs:

- Python environment setup
- image builds
- script smoke tests

## Stage 3 — Runtime smoke

Runs:

- blank repo install
- bootstrap
- env generation
- stack startup
- health validation
- stack teardown

## Stage 4 — Isolation

Runs:

- dual-host install
- dual-host startup
- collision/isolation verification
- dual-host teardown

## Stage 5 — Upgrade

Runs:

- install older tag
- add overrides
- upgrade to current ref
- validate preservation and migration

## Stage 6 — Release gate

Runs:

- aggregate success check
- block release if any mandatory prior stage fails

---

## Test-suite acceptance criteria

The `softwareFactoryVscode` implementation is not considered test-complete until all of the following are true:

1. All mandatory categories in this document have at least one automated check.
2. Blank repo install is validated automatically.
3. Dual-host isolation is validated automatically.
4. Upgrade with overrides is validated automatically.
5. Runtime/meta boundary is validated automatically.
6. Neutrality and contamination checks are validated automatically.
7. Documentation accuracy is validated at least in smoke form.
8. CI enforces mandatory release gates.
9. Failure diagnostics are sufficient for triage.
10. `SoftwareFactoryVsocdeTestsuite.md` is included in the standalone repo.

---

## Prompt to start implementing the test suite

Use the following prompt as the canonical kickoff prompt for the next step that must build the actual automated test suite in the standalone `softwareFactoryVscode` repository.

### Canonical kickoff prompt

```text
Implement the full automated validation suite for the standalone repository `softwareFactoryVscode` using `softwareFactoryVscode.md` and `SoftwareFactoryVsocdeTestsuite.md` as the execution contract.

You must not create a new plan-only document. You must create the real test assets.

Objectives:
1. Create all required test directories, fixtures, scripts, and CI workflows.
2. Implement static checks for neutrality, runtime/meta boundaries, variable contract consistency, required-file completeness, and documentation presence.
3. Implement static and integration checks for `.vscode/settings.json`, `.vscode/tasks.json`, `.vscode/extensions.json`, MCP server wiring, task labels, and workspace auto-approve policy configuration.
4. Implement validation for the documented extension support matrix, including required external extensions, recommended tooling extensions, and any workspace-local bundled extension such as `issueagent` if retained.
5. Implement validation for the packaged Context7 Docker artefact, including image build, compose startup, local MCP endpoint wiring, and `CONTEXT7_API_KEY` behavior.
6. Implement automated fresh-install tests that validate bootstrap into a blank host repo.
7. Implement automated runtime smoke tests that validate env generation, compose startup, health endpoints, `/target` visibility, and teardown.
8. Implement automated dual-host isolation tests proving two separate host repos can run concurrently without collisions or shared state contamination.
9. Implement automated upgrade tests proving version lock handling and host override preservation.
10. Implement failure-mode tests for missing prerequisites, bad config, malformed overrides, and occupied ports.
11. Implement documentation/testing smoke checks so that install, upgrade, and VS Code workspace docs match the actual commands, paths, projected settings, extension matrix, and Context7 setup contract.
12. Wire all mandatory tests into CI release gates.
13. Leave the repository in a state where the test suite can be executed repeatedly and deterministically.

Constraints:
- Preserve neutrality: no hidden Maestro-specific references outside explicitly allowed migration/source-map docs.
- Preserve the runtime/meta boundary.
- Use repo-local test temp paths, not host-global `/tmp` for orchestrated package test artefacts.
- Prefer deterministic fixtures and reproducible CI behavior.
- Collect actionable failure diagnostics.

Definition of done:
- All mandatory categories from `SoftwareFactoryVsocdeTestsuite.md` are implemented.
- CI contains separate static, build, runtime, isolation, and upgrade gates.
- Fresh install, isolation, and upgrade flows are automated.
- The resulting test suite proves the factory works as designed.
```

---

## Final instruction to the next step

The next implementation step must treat this document as binding.

It must not stop at writing a testing idea list.

It must create the actual automated test suite, scripts, fixtures, and CI wiring required to enforce the guarantees defined in this document.
