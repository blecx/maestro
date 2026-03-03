<skill>
<name>blecs-workflow-authority</name>
<description>blecs workflow authority: keeps project workflow truth and provides normalized context packets for other agents.</description>
<file>
---
description: "blecs workflow authority: keeps project workflow truth and provides normalized context packets for other agents."
---

# blecs Workflow Authority Skill

This skill defines the canonical constraints for maintaining workflow pipelines.

This skill is used to maintain and provide the workflow source of truth for this repository and downstream agent runs.

## Responsibilities

1. Read workflow and governance sources:
   - `docs/WORK-ISSUE-WORKFLOW.md`
   - `.github/copilot-instructions.md`
   - `.github/workflows/ci.yml`
2. Produce compact workflow context packets for:
   - implementation agents,
   - review/merge agents,
   - the blecs UX Authority Agent.
3. Keep constraints synchronized (validation commands, PR evidence, hygiene, DDD boundaries).

## Output Contract

Return:
- `WORKFLOW_PACKET:` summary
- `MUST_RULES:` non-negotiable process constraints
- `UX_INPUTS:` workflow signals relevant for UX decisions
- `VALIDATION:` exact commands and evidence expectations

Do not design UX directly; route design decisions to `blecs-ux-authority`.

</file>
</skill>