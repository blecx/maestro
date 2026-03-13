# Hardening Prompt 4 — Reconcile projection scripts

## Objective

Upgrade projection scripts so they reconcile owned settings keys instead of merely merging additions, preventing stale managed state from lingering.

## Why this prompt comes fourth

Once policy and validation are canonical, projections must converge the workspace to that state cleanly.

## Scope

In scope:

- `scripts/setup-vscode-autoapprove.py`
- `scripts/setup-vscode-agent-settings.py`
- related docs and drift checks
- owned settings blocks in `.vscode/settings.json`

Out of scope:

- unrelated VS Code preferences that are intentionally developer-specific

## Instructions

1. Define which settings keys are fully managed by projection.
2. Update projection behavior so managed keys are reconciled, not only merged.
3. Preserve non-managed user preferences.
4. Add or document preview / check behavior for removals.
5. Ensure the docs match the new projection semantics.
6. Summarize what is now managed and how drift is handled.

## Questions for the operator

1. Which settings blocks should be fully managed?
2. Should unknown keys in managed blocks be removed automatically or only in a stricter reconcile mode?
3. Do you want a dry-run output that lists keys to be removed before applying changes?

## Success criteria

- Projection converges owned keys to canonical state.
- Stale managed residue is removed deterministically.
- Non-owned preferences remain intact.
