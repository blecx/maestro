# Prompt 3 — Split approval tiers explicitly

## Objective

Design and implement explicit approval tiers for subagents and terminal commands so that “safe”, “trusted workflow”, and “low-friction” are meaningfully different and auditable.

## Why this prompt exists

The current safe profile is still too broad and mixes different trust boundaries together.

## Instructions

1. Separate the approval model into two axes:
   - subagent approval
   - terminal command approval
2. Define explicit profiles such as:
   - `safe`
   - `trusted-workflow`
   - `low-friction`
3. For each profile, document:
   - which subagents may auto-run
   - which command families may auto-run
   - what remains manual
4. Update `.copilot/config/` and any projection scripts or docs affected by the new model.
5. Ensure docs explain the trust tradeoffs in plain language.
6. Produce a matrix showing agents and commands by profile.

## Recommended default model

- `safe`: planning / issue drafting / verified closure only
- `trusted-workflow`: bounded implementation and merge workflows
- `low-friction`: operator-only high-trust mode

## Questions for the operator

1. Do you want `resolve-issue` and `pr-merge` in the default trusted profile or manual by default?
2. Should `tutorial` remain a single approval target, or be split into author vs audit?
3. Should `maestro-operator`, `workflow`, and continuation agents remain manual even in trusted workflow mode?

## Success criteria

- Approval profiles express real trust differences.
- Safe mode is no longer broad shell trust in disguise.
- The policy becomes explainable and enforceable.
