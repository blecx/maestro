# Hardening Prompt 2 — Tighten approval tiers

## Objective

Redesign approval policy so it uses explicit, auditable trust tiers for both subagent invocation and terminal execution.

## Why this prompt comes second

Once authority is clean, the next priority is to ensure trust policy reflects real risk. The current “safe” model is still too broad.

## Scope

In scope:

- `.copilot/config/vscode-approval-profiles.json`
- `.copilot/config/vscode-agent-settings.json`
- projection docs and approval docs
- related validation expectations

Out of scope:

- unrelated runtime behavior changes
- broad workflow rewrites unrelated to approval policy

## Instructions

1. Separate approval policy into two axes:
   - subagent approval
   - terminal approval
2. Define explicit tiers, for example:
   - `safe`
   - `trusted-workflow`
   - `low-friction`
3. For each tier, document:
   - which subagents are auto-approved
   - which terminal commands are auto-approved
   - which operations remain manual
4. Remove or reduce overly broad “safe” approvals where practical.
5. Update any related docs to explain the trust tradeoffs clearly.
6. Produce a profile matrix.

## Questions for the operator

1. Should `resolve-issue` and `pr-merge` be auto-approved only in trusted mode, or always require manual confirmation?
2. Should continuation agents remain manual in all profiles?
3. Should `tutorial` stay unified, or do you want different approval treatment for authoring vs auditing?

## Success criteria

- Trust tiers are explicit and meaningfully different.
- Safe mode is truly conservative.
- Subagent and terminal approval are no longer conflated.
