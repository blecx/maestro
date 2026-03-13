# Rigid Copilot Review

## Purpose

This document captures a strict architectural and operational review of the repository's AI agent migration toward a `.copilot`-first ownership model. It focuses on seamless workflow execution, separation of concerns, approval governance, and residual migration risks.

## Executive Assessment

The move to `.copilot/` is directionally correct and mostly well-executed, but it is not yet fully seamless.

- **Architecture:** 7.5/10
- **Operational consistency:** 6.5/10
- **Approval / governance hygiene:** 5.5/10

### Short verdict

The ownership model is now much clearer, but several validators, approval behaviors, and stale authority references still behave like the previous model is partly authoritative. The migration is structurally good, but not yet hardened.

## What Is Solid

The following areas are strong and aligned:

- `.copilot/` is clearly declared canonical in:
  - `README.md`
  - `.copilot/README.md`
  - `docs/maestro/AUTOMATIONS.md`
  - `docs/maestro/AGENTS_README.md`
  - `docs/maestro/BOOTSTRAP.md`
- `.github/agents/*.md` are mostly thin wrappers, which is the correct pattern.
- `.copilot/config/` is split sensibly:
  - `vscode-agent-settings.json` for agent and MCP settings
  - `vscode-approval-profiles.json` for approval policy
- Workflow entrypoints are coherent:
  - `scripts/issue-pr-merge-cleanup-loop.sh`
  - `scripts/issue-loop-and-merge.sh`
  - `scripts/prmerge`
  - `.vscode/tasks.json`
- Runtime vs policy separation is documented correctly:
  - runtime in `agents/`
  - policy and behavior contracts in `.copilot/skills/`
  - discoverability in `.github/agents/`

This is the right layered design.

## Hard Failures

These are the main reasons the system is not yet seamless.

### 1. Some skills still point to the wrong authority

In `.copilot/skills/resolve-issue-workflow/SKILL.md` and `.copilot/skills/continue-phase-2-workflow/SKILL.md`, UX delegation still references `./ux/delegation-policy.md` instead of the canonical `.copilot/skills/ux-delegation-policy/SKILL.md`.

**Impact:** Medium-high  
**Why it matters:** A canonical skill must not point to a non-canonical authority path.

### 2. Approval validation is behind the new model

`scripts/check_subagent_autoapprove.py` still validates against an outdated hard-coded baseline and does not fully reflect the current `.copilot/config/vscode-agent-settings.json` model.

**Impact:** High  
**Why it matters:** Governance tooling that lags the architecture causes trust-by-accident instead of policy-by-design.

### 3. The approval projection script still behaves like a cross-workspace mutator

`scripts/setup-vscode-autoapprove.py` still defaults to touching global user settings and a sibling client workspace unless `--workspace-only` is passed.

**Impact:** High  
**Why it matters:** The docs now describe explicit local projection first, but the script still defaults to broader mutation.

### 4. Workspace settings show residue that projection did not reconcile

Current `.vscode/settings.json` contains stale approval residue such as `"/bash": true`, which is not part of the canonical approval profile.

**Impact:** Medium  
**Why it matters:** Projection is currently additive but not fully reconciliatory, so stale managed keys can survive indefinitely.

### 5. The “safe” terminal approval profile is still broad

The `safe` profile in `.copilot/config/vscode-approval-profiles.json` still approves broad regex-driven shell patterns, loop constructs, and many script paths.

**Impact:** High  
**Why it matters:** This behaves more like “trusted repo operator mode” than a strict safe profile.

## Separation-of-Concerns Review

## Clean separations

### `resolve-issue`

Correctly owns:

- issue-to-PR implementation flow
- planning shape
- validation expectations

This is acceptable.

### `pr-merge`

Correctly owns:

- merge readiness
- merge execution
- cleanup trigger

It correctly states that it should not fix implementation or failing CI. Good.

### `close-issue`

Correctly owns:

- verified close reasoning
- closure message traceability

This is narrower than `pr-merge`, which is good.

### `Plan`

Correctly owns:

- bounded planning
- issue slicing
- dependency mapping

This is clean.

### `workflow`

Correctly intends to own:

- runtime execution path only

This is the right intent.

### `maestro-operator`

Correctly intends to own:

- CLI invocation path for Maestro

Also clean in principle.

## Interference and overlap risks

### `pr-merge` vs `close-issue`

Current design is acceptable only if:

- `pr-merge` is the orchestrator
- `close-issue` is the closure policy authority

This should be stated more explicitly.

### `resolve-issue` vs `continue-backend` / `continue-phase-2`

These continuation agents should be loop orchestrators only. They should not introduce independent workflow law beyond:

- selection scope
- loop bounds
- stop conditions

At the moment, they still contain enough behavioral policy to drift away from `resolve-issue` and `pr-merge`.

### `workflow` vs `maestro-operator`

These are too close semantically.

- `workflow` should mean repo workflow runtime orchestration
- `maestro-operator` should mean direct operator control of the Maestro CLI

The distinction exists, but it is still thin.

### `ralph-agent` vs `resolve-issue`

`ralph-agent` should be treated as a strict overlay profile on top of `resolve-issue`, not as a competing issue-resolution authority.

### `tutorial` vs workflow / policy skills

`tutorial-writer-expert` is valuable, but it combines authoring and strict audit responsibilities that likely deserve separate risk / approval treatment.

## Skills Quality Review

## Strong skills

These are structurally strongest:

- `.copilot/skills/resolve-issue-workflow/SKILL.md`
- `.copilot/skills/pr-merge-workflow/SKILL.md`
- `.copilot/skills/close-issue-workflow/SKILL.md`
- `.copilot/skills/plan-workflow/SKILL.md`
- `.copilot/skills/workflow-runtime/SKILL.md`
- `.copilot/skills/maestro-operator-workflow/SKILL.md`

They have clear use conditions, steps, guardrails, and completion contracts.

## Medium quality / needs tightening

### `issue-creation-workflow`

Needs a stronger explicit boundary for:

- use when
- when not to use
- non-implementation guardrail

### `continue-backend-workflow`

Still reads partly like a legacy procedural module instead of a pure orchestration contract.

### `continue-phase-2-workflow`

Has the same issue as above and still contains stale UX authority references.

### `ralph-skills-review`

Useful, but this is a review matrix, not a standalone execution workflow. It should be treated as an overlay authority.

### `tutorial-writer-expert`

High-quality specialist guidance, but not shaped like the operational workflow baseline. That is acceptable as long as it stays isolated from general workflow approval defaults.

## Approval Guidance

## 1. Separate subagent approval from terminal approval

These are different decisions:

- **Subagent approval:** may this agent be invoked without asking?
- **Terminal approval:** once invoked, what commands may execute without asking?

They should not be treated as the same trust boundary.

## 2. Recommended subagent approval tiers

### Tier A — safe to auto-approve by default

- `Plan`
- `create-issue`
- `close-issue`
- `tutorial` only if split into audit vs author mode

### Tier B — auto-approve only in trusted workflow mode

- `resolve-issue`
- `pr-merge`
- `ralph-agent`

### Tier C — manual approval recommended

- `continue-backend`
- `continue-phase-2`
- `workflow`
- `maestro-operator`
- `tutorial` if not split by mode

## 3. Recommended terminal approval tiers

### Safe profile

Allow only deterministic, narrow commands:

- repo reads
- specific validation commands
- exact workflow scripts by name
- no generic broad shell regexes
- no blanket `bash` trust if avoidable

### Trusted workflow profile

Allow:

- exact repo scripts
- git commands
- test/build/lint commands
- avoid blanket catch-all command-line approvals

### Low-friction profile

Use only for deliberate operator workflows. It should never be the default.

## Concrete approval recommendation for this repo

### Auto-approve subagents in safe mode

- `Plan`
- `create-issue`
- `close-issue`

### Auto-approve subagents in trusted workflow mode

- `resolve-issue`
- `pr-merge`
- `ralph-agent`

### Keep manual

- `maestro-operator`
- `workflow`
- `continue-backend`
- `continue-phase-2`
- `tutorial` unless split by mode

## Specific Weak Points / SoC Violations

1. Canonical skills reference non-canonical UX authority paths.
2. Approval validator is not aligned with actual projected config.
3. Projection script defaults are broader than the stated policy model.
4. Projection is additive, not fully reconciliatory.
5. Continuation skills own too much policy.
6. Merge / close ownership is not explicit enough.
7. Runtime agent role distinction is too thin.

## Approval Status

### Approve now

- the ownership direction
- the wrapper pattern
- the `.copilot/config` split
- the task and loop wiring
- the general policy migration

### Approve with conditions

- `resolve-issue-workflow`
- `pr-merge-workflow`
- `close-issue-workflow`
- `plan-workflow`
- `maestro-operator-workflow`
- `workflow-runtime`

### Do not fully approve yet

- `continue-backend-workflow`
- `continue-phase-2-workflow`
- current approval-profile governance
- current validator alignment

## Strict Recommendation List

1. Fix stale authority references.
2. Make approval validation canonical.
3. Split approval tiers explicitly.
4. Make projection scripts reconcile managed keys.
5. Narrow continuation agents.
6. Clarify runtime roles.
7. Consider splitting tutorial authoring vs tutorial audit.

## Bottom Line

The migration is architecturally right but operationally not fully hardened.

The biggest remaining risks are:

- authority leakage
- approval drift
- validator lag
- agent role overlap at orchestration boundaries

If these are addressed in order, the `.copilot` migration can become genuinely seamless rather than merely well-documented.
