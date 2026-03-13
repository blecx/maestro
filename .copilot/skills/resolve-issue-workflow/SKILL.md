<skill>
<name>resolve-issue-workflow</name>
<description>Workflow or rule module extracted from .copilot/skills/resolve-issue-workflow/SKILL.md</description>
<file>
# Resolve Issue Workflow

## Role Contract

**issue implementation workflow authority** - Dictates how an issue becomes a PR, independent of underlying runtime execution engines. (Module)

Use this skill as the canonical implementation source for `resolve-issue`.

## Use When

- A specific issue number is provided for implementation.
- The user asks to pick the next issue and execute one issue-to-PR slice.

## Steps

1. Select issue (backend-first, lowest number) and confirm scope.
2. Write compact plan: goal, scope, AC, files, validation commands.
3. Apply UX delegation policy from `.copilot/skills/ux-delegation-policy/SKILL.md` and capture required consultation outcome.
4. Implement minimal code changes in a dedicated branch.
5. Run required validations for touched areas.
6. Commit with `Fixes #<issue>` and push.
7. Create PR using required template sections.
8. Address CI failures by root cause and re-validate.

## Required Planning Shape

- Goal
- Scope / non-goals
- Acceptance criteria
- Target files/modules
- Validation commands

Prefer tool-driven discovery over pasting large context into chat.

## Validation Baseline

- Backend: `black`, `flake8`, `pytest`
- Frontend: `npm run lint`, `npm run build`, tests if configured
- Include command outputs/evidence in PR body.

## Repo Rules

- Select backend/TUI/CLI issues before client/UX issues.
- Keep one issue per PR.
- Use `.tmp/`, never `/tmp`.
- Never touch `projectDocs/` or `configs/llm.json`.
- Apply the canonical UX delegation policy before finalizing UI/UX-impacting work.

## Guardrails

- Validate issue spec (strict sections + body-size limit) for roadmap specs.
- Keep scope to small CI-safe slices (single issue, minimal domains), no architecture regressions outside scope.

- Avoid unrelated refactors.
- Keep diffs reviewable and DDD-compliant.
- Use `.tmp/` for transient artifacts.
- Follow `.copilot/skills/ux-delegation-policy/SKILL.md` as the canonical delegation rule source.

## Completion Contract

Return a concise result that states:

- implemented issue,
- validation status,
- PR or blocking condition,
- any follow-up split/dependency if scope exceeded the slice.

</file>
</skill>