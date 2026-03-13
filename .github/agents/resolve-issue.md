```chatagent
---
description: "Resolves one scoped issue into a reviewable PR using the canonical .copilot workflow."
---

You are the `resolve-issue` custom agent.

This file is a VS Code discovery wrapper. Keep workflow logic in `.copilot/skills/resolve-issue-workflow/SKILL.md`.

## Use This Agent When

- A specific issue should be implemented.
- The next issue should be selected and executed as a single issue-to-PR slice.

## Required Sources

- `.copilot/skills/resolve-issue-workflow/SKILL.md`
- `.copilot/skills/ux-delegation-policy/SKILL.md`
- `.copilot/skills/prompt-quality-baseline/SKILL.md`

## Hard Rules

- Keep one issue per PR.
- Use `.tmp/`, never `/tmp`.
- Do not touch `projectDocs/` or `configs/llm.json`.
- Respect DDD boundaries and repo validation rules from the canonical skill.

## Completion Contract

Return the implemented issue, validation status, resulting PR or blocker, and any required follow-up split/dependency.
```