# Hardening Prompt 6 — Clarify runtime roles

## Objective

Clarify and document the boundaries between workflow authority agents and runtime/operator agents so their roles are operationally distinct.

## Why this prompt comes sixth

After orchestration boundaries are narrowed, runtime role clarity can be expressed without competing with unresolved policy ownership.

## Scope

In scope:

- `.github/agents/workflow.md`
- `.github/agents/maestro-operator.md`
- `.github/agents/resolve-issue.md`
- runtime docs under `agents/` and `docs/maestro/agents/`
- related canonical skills

Out of scope:

- broad runtime implementation rewrites unless explicitly necessary

## Instructions

1. Define a one-sentence role contract for:
   - `workflow`
   - `maestro-operator`
   - `resolve-issue`
   - runtime code under `agents/`
2. Update wrappers, skills, and docs to repeat those distinctions consistently.
3. Ensure runtime docs never imply they are the source of workflow policy.
4. Produce a role map table.

## Questions for the operator

1. Should `workflow` remain user-facing or be treated mainly as a specialist runtime path?
2. Should `maestro-operator` remain prominently user-facing or be reserved for explicit operator use?
3. Are runtime docs to be treated as active, archival, or mixed?

## Success criteria

- Runtime and workflow roles are non-overlapping.
- Users can tell which agent to use for which task.
- Runtime surfaces no longer compete with workflow policy authority.
