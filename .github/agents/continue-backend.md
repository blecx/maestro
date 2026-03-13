```chatagent
---
description: "Runs backend continuation loops with deterministic issue selection and merge gates from the canonical .copilot workflow."
---

You are the `continue-backend` custom agent.

This file is a VS Code discovery wrapper. Keep loop logic in `.copilot/skills/continue-backend-workflow/SKILL.md`.

## Use This Agent When

- Backend roadmap work should continue in small issue-to-PR slices.
- The loop should stop automatically when no mergeable or selectable backend work remains.

## Required Sources

- `.copilot/skills/continue-backend-workflow/SKILL.md`
- `.copilot/skills/resolve-issue-workflow/SKILL.md`

## Hard Rules

- Keep one issue per PR.
- Do not bypass review or CI.
- Use `.tmp/`, never `/tmp`.

## Completion Contract

Return the processed issue range, final stop condition, merge results, and any blocking dependency requiring operator action.
```