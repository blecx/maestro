# Prompt 5 — Narrow continuation agents

## Objective

Refactor continuation workflows so `continue-backend` and `continue-phase-2` act as orchestration shells only, delegating implementation semantics to `resolve-issue` and merge semantics to `pr-merge`.

## Why this prompt exists

Current continuation skills still contain enough behavioral policy to drift away from canonical implementation and merge workflows.

## Instructions

1. Review:
   - `.copilot/skills/continue-backend-workflow/SKILL.md`
   - `.copilot/skills/continue-phase-2-workflow/SKILL.md`
   - related wrappers and loop scripts
2. Identify policy that should belong instead to:
   - `resolve-issue-workflow`
   - `pr-merge-workflow`
   - `ux-delegation-policy`
3. Reduce continuation skills to:
   - scope selection
   - loop bounds
   - stop conditions
   - orchestration-specific reporting
4. Keep them explicit about delegation to canonical implementation and merge authorities.
5. Document the narrowed responsibilities.

## Questions for the operator

1. Should continuation agents be permitted to carry any domain-specific policy beyond issue selection and loop stops?
2. Do you want `continue-phase-2` to retain any UX-specific gating language locally, or only delegate that to the UX authority and core workflows?
3. Should continuation agents stay auto-approvable at all after narrowing, or remain manual orchestrators?

## Success criteria

- Continuation agents are orchestration layers, not competing workflow authorities.
- Canonical implementation and merge semantics live only in the core skills.
- Drift risk between loop agents and core agents is reduced.
