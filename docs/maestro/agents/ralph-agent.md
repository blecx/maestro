# Ralph Agent

Ralph is a strict issue-resolution profile built for high-confidence delivery in VS Code and CLI workflows.

## What Ralph Adds

- Spec-Kit style execution loop (analyze, plan, implement, validate, review, handoff)
- Skill-based acceptance criteria
- Specialist reviewer gates (architecture, quality, security, UX when applicable)
- Bounded review iteration loop (max 5)

## Usage

### VS Code Chat

- `@ralph /run`

### CLI

- `./scripts/work-issue.py --issue 26 --agent ralph`

## Prompt Source of Truth

- Agent prompt: `.github/agents/ralph-agent.md`
- Skills/review matrix: `.copilot/skills/ralph-skills-review/SKILL.md`

## Acceptance Model

Ralph passes only when all required skill criteria and reviewer gates pass for the issue scope. Otherwise it returns explicit change tasks and iterates until pass or budget exhaustion.
