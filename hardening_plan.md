# Hardening Plan

## Purpose

This plan turns the rigid Copilot review into a concrete hardening program for the repository. It focuses on eliminating the four main remaining risks in the `.copilot` migration:

- authority leakage
- approval drift
- validator lag
- agent role overlap at orchestration boundaries

The goal is not merely to document the `.copilot`-first model, but to make it operationally authoritative, verifiable, and safe to use in seamless workflows.

## Problem Statement

The repository has already moved most workflow policy and agent configuration into `.copilot/`, but the migration is not yet fully hardened.

The main issues are:

1. Canonical skills still contain stale or non-canonical authority references.
2. Approval profiles are too broad and do not express clear trust tiers.
3. Validation logic still lags the new canonical `.copilot/config/` model.
4. Projection scripts reconcile incompletely, allowing stale managed settings to persist.
5. Some orchestration agents still carry too much workflow policy, increasing drift risk.
6. Runtime roles are not yet distinct enough for seamless human and agent usage.
7. The repository lacks an explicit local “agent separation contract” checklist to keep responsibilities stable over time.

## Hardening Goals

### Goal 1 — Reassert canonical authority

Make `.copilot/skills/` and `.copilot/config/` the only active workflow-policy authority, with all remaining authority references corrected or explicitly historical.

### Goal 2 — Tighten approval tiers

Separate subagent approval from terminal approval and define meaningful trust tiers that align with actual risk.

### Goal 3 — Make validation canonical

Update validators so they inspect the canonical config model rather than older hard-coded assumptions.

### Goal 4 — Reconcile managed projection state

Ensure projection scripts cleanly reconcile owned settings rather than only merging additions.

### Goal 5 — Reduce orchestration drift

Narrow orchestration and continuation agents so they delegate into canonical core skills instead of carrying competing workflow policy.

### Goal 6 — Clarify runtime and execution roles

Make `workflow`, `maestro-operator`, `resolve-issue`, and related runtime surfaces operationally distinct and clearly documented.

### Goal 7 — Establish a durable separation contract

Create a repository-local checklist that explains what each class of agent or skill may and may not own, so future migrations do not reintroduce role overlap.

## Execution Strategy

This hardening work should be executed as a sequence of bounded prompts, in order.

The order matters because later stages depend on earlier stages having established the correct authority and validation model.

## Ordered Hardening Sequence

### 1. Fix stale authority references

First, eliminate any remaining canonical-path leakage.

### 2. Tighten approval tiers

Second, redesign approval policy into explicit trust tiers.

### 3. Update validators

Third, align validators with the canonical configuration model.

### 4. Reconcile projection scripts

Fourth, make projection deterministic and able to remove stale managed keys.

### 5. Narrow orchestration boundaries

Fifth, reduce continuation and orchestration agents to orchestration-only responsibilities.

### 6. Clarify runtime roles

Sixth, make runtime and operator agents unambiguous in purpose.

### 7. Create an agent separation contract checklist

Finally, create a durable local checklist to keep the system hardened.

## Constraints

- Do not overwrite the existing review prompts.
- Keep `.copilot/` as the only canonical policy authority.
- Preserve runtime implementation code unless a prompt explicitly requires runtime changes.
- Prefer bounded, reviewable slices.
- Keep all transient artifacts in `.tmp/`.

## Expected Artifacts

This hardening program should produce or update:

- canonical skills under `.copilot/skills/`
- approval profile definitions under `.copilot/config/`
- validation and projection scripts under `scripts/`
- wrapper clarifications under `.github/agents/`
- documentation updates under `docs/maestro/`
- a repository-local agent separation contract checklist

## Success Criteria

The hardening pass is complete when all of the following are true:

- No canonical workflow skill points to a non-canonical authority path.
- Approval profiles express meaningful trust differences and are documented clearly.
- Validators inspect canonical config and no longer depend on stale hard-coded assumptions.
- Projection scripts can reconcile owned keys and remove stale managed residue.
- Continuation agents are orchestration-only and do not define competing workflow law.
- Runtime-facing agents have clear, non-overlapping roles.
- A repository-local agent separation contract checklist exists and is usable in future reviews.

## Final Outcome

When this plan is executed successfully, the repository will move from a mostly correct `.copilot` migration to an operationally hardened one:

- `.copilot` becomes truly authoritative
- approvals match actual risk
- validators and projections agree with policy
- orchestration layers stop drifting from core workflow logic
- runtime roles are clearer for both users and future maintainers
- separation of concerns is explicit and enforceable
