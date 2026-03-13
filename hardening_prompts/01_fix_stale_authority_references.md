# Hardening Prompt 1 — Fix stale authority references

## Objective

Audit and correct any remaining authority references that still point outside the canonical `.copilot` workflow and policy surfaces, unless they are explicitly historical.

## Why this prompt comes first

All later hardening work depends on a correct source-of-truth map. If canonical skills still point to non-canonical paths, approval and validation work will continue to drift.

## Scope

In scope:

- `.copilot/skills/**/SKILL.md`
- `.github/agents/*.md`
- `docs/**`
- `scripts/**`
- other active workflow-policy documentation

Out of scope:

- deleting archival docs just because they mention legacy paths
- rewriting runtime implementation unless authority references are actively wrong

## Instructions

1. Search for references to:
   - `./ux/delegation-policy.md`
   - `.github/prompts/agents`
   - `autonomous_workflow_agent.py`
   - any other path that incorrectly claims current workflow authority
2. Classify every match as one of:
   - **canonical bug**
   - **historical and acceptable**
   - **runtime-valid reference**
3. Fix all canonical bugs.
4. Mark intentionally historical references clearly where needed.
5. Produce a summary of:
   - files changed
   - references intentionally preserved
   - rationale for each preserved legacy reference

## Questions for the operator

1. Should every non-`.copilot` workflow authority reference be treated as a defect unless explicitly marked historical?
2. Should legacy runtime references remain in archival docs if they are clearly labeled historical?
3. Do you want an aggressive cleanup or a minimal correction pass?

## Success criteria

- Active workflow authority points only to canonical `.copilot` sources.
- Historical references no longer masquerade as current policy.
- The authority map is stable for later hardening steps.
