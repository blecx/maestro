# Prompt 6 — Clarify runtime roles

## Objective

Clarify the role boundaries between `workflow`, `maestro-operator`, `resolve-issue`, and runtime code under `agents/` so users and future maintainers do not confuse orchestration authority with CLI execution authority.

## Why this prompt exists

The runtime roles are close enough that users could invoke the wrong agent for the right problem.

## Instructions

1. Review wrappers, skills, and docs for:
   - `workflow`
   - `maestro-operator`
   - `resolve-issue`
   - runtime docs under `agents/` and `docs/maestro/agents/`
2. Define a one-sentence role contract for each:
   - `workflow`
   - repo-level runtime orchestration
   - `maestro-operator`
   - direct Maestro CLI bridge
   - `resolve-issue`
   - issue implementation workflow authority
3. Update docs and wrappers so these distinctions are explicit and repeated consistently.
4. Ensure runtime docs never imply they are the source of workflow policy.
5. Produce a role map table.

## Questions for the operator

1. Do you want `workflow` retained as a visible user-facing agent, or treated as an internal/runtime specialist?
2. Should `maestro-operator` remain a distinct user-facing agent, or be documented primarily as an expert / operator path?
3. Do you want runtime docs in `docs/maestro/agents/` to be considered archival, active runtime docs, or mixed?

## Success criteria

- Runtime roles are explicit and non-overlapping.
- Users can tell which agent to use for which class of task.
- Runtime execution no longer competes with workflow policy authority.
