# Prompt 7 — Split tutorial authoring and audit responsibilities

## Objective

Evaluate whether the tutorial agent and tutorial skills should be split into separate authoring and audit tracks, with different approval and workflow expectations.

## Why this prompt exists

Tutorial authoring and strict tutorial auditing are different activities with different risk and trust profiles, but they currently share one specialist surface.

## Instructions

1. Review:
   - `.copilot/skills/tutorial-writer-expert/SKILL.md`
   - `.copilot/skills/tutorial-review-workflow/SKILL.md`
   - `.github/agents/tutorial.md`
2. Determine whether the current `tutorial` agent should remain unified or be split into:
   - `tutorial-author`
   - `tutorial-audit`
3. Compare the following concerns:
   - approval profile
   - execution style
   - evidence requirements
   - operator expectations
4. If a split is recommended, propose:
   - agent names
   - wrapper changes
   - skill ownership
   - approval defaults
5. If no split is recommended, document why and define explicit mode switching rules.

## Questions for the operator

1. Do you use the tutorial agent primarily for creation, for review, or for both equally?
2. Would you prefer separate user-facing commands for authoring and auditing?
3. Should strict audit mode be auto-approvable if it performs no writes?

## Success criteria

- Tutorial responsibilities are easier to approve safely.
- Audit and authoring concerns are no longer conflated.
- Approval policy can reflect actual risk rather than a blended average.
