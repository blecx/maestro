# Hardening Prompt 5 — Narrow orchestration boundaries

## Objective

Reduce continuation and orchestration agents to orchestration-only responsibilities so they delegate into canonical implementation and merge workflows instead of carrying competing workflow law.

## Why this prompt comes fifth

Core policy, validation, and projection should be stable before orchestration layers are simplified to depend on them.

## Scope

In scope:

- `.copilot/skills/continue-backend-workflow/SKILL.md`
- `.copilot/skills/continue-phase-2-workflow/SKILL.md`
- related wrappers and loop docs

Out of scope:

- changing issue selection order unless required by scope clarification
- unrelated runtime implementation changes

## Instructions

1. Identify policy in continuation skills that should instead belong to:
   - `resolve-issue-workflow`
   - `pr-merge-workflow`
   - `ux-delegation-policy`
2. Reduce continuation skills to:
   - selection scope
   - loop bounds
   - stop conditions
   - orchestration-specific reporting
3. Ensure they explicitly delegate implementation and merge semantics to canonical core skills.
4. Update any affected docs.
5. Summarize the boundary changes.

## Questions for the operator

1. Should continuation agents be purely orchestrators, with no domain-specific workflow law at all?
2. Should they remain manually approved even after narrowing?
3. Do you want loop-specific reporting templates retained locally?

## Success criteria

- Continuation agents no longer behave like competing workflow authorities.
- Delegation boundaries are explicit.
- Drift risk between orchestration and core workflows is reduced.
