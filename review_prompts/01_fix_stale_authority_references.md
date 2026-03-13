# Prompt 1 — Fix stale authority references

## Objective

Audit all `.copilot/skills/**/SKILL.md`, `.github/agents/*.md`, `docs/**`, and `scripts/**` files for references that still point to pre-migration or non-canonical workflow authority paths, then replace or explicitly classify them as historical.

## Why this prompt exists

Canonical skills currently still reference a non-canonical UX delegation path in some places. This breaks the `.copilot`-first ownership model.

## Instructions

1. Search for references to:
   - `./ux/delegation-policy.md`
   - `.github/prompts/agents`
   - `autonomous_workflow_agent.py`
2. Classify every match into one of these buckets:
   - **canonical bug** — must be updated now
   - **historical reference** — may stay, but must be clearly labeled historical
   - **runtime implementation reference** — valid if it describes active runtime behavior
3. Update all canonical workflow and wrapper files so they point to the correct canonical authority under `.copilot/skills/`.
4. Do not rewrite historical documents unless they are pretending to be current authority.
5. Produce a short report with:
   - changed files
   - matches left intentionally unchanged
   - rationale for every remaining match

## Questions for the operator

Answer these before execution if there is ambiguity:

1. Do you want **all** historical references normalized, or only those that currently pretend to be active authority?
2. Should explicit references to legacy runtime files remain in archival docs when clearly labeled as historical?
3. Do you want the review to treat every non-`.copilot` workflow authority reference as a defect unless explicitly documented as archival?

## Success criteria

- No canonical workflow skill points to a non-canonical authority path.
- Remaining legacy references are explicitly historical or runtime-valid.
- The result strengthens `.copilot` as the only workflow authority.
