# Prompt 4 — Reconcile managed keys in projection

## Objective

Make projection scripts reconcile managed settings keys instead of only merging additions, so stale approval residue and obsolete settings entries are removed deterministically.

## Why this prompt exists

Current projection behavior is additive. That allows stale managed keys such as stray approval entries to remain in `.vscode/settings.json` indefinitely.

## Instructions

1. Review projection scripts for:
   - merge-only behavior
   - drift detection scope
   - managed-key ownership boundaries
2. Define which settings keys are **owned** by projection scripts.
3. Update projection behavior so owned keys are reconciled to canonical state, not just merged.
4. Preserve non-owned local settings that are intentionally developer-specific.
5. Add a verification mode that reports:
   - extra owned keys
   - missing owned keys
   - mismatched owned values
6. Document the reconciliation behavior clearly in bootstrap and settings docs.

## Questions for the operator

1. Which keys should be treated as fully managed by projection?
   Suggested candidates:
   - `chat.tools.subagent.autoApprove`
   - `chat.tools.terminal.autoApprove`
   - `issueagent.customAgent`
   - `mcp`
2. Should projection remove unknown values inside owned blocks automatically, or only in a stricter `--reconcile` mode?
3. Do you want a “preview” mode that prints the keys that would be removed before applying changes?

## Success criteria

- Managed settings converge to canonical state.
- Stale approval residue no longer survives repeated projections.
- Non-owned local preferences remain untouched.
