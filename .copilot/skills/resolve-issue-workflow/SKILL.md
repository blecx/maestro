<skill>
<name>resolve-issue-workflow</name>
<description>Workflow or rule module extracted from .copilot/skills/resolve-issue-workflow/SKILL.md</description>
<file>
# Resolve Issue Workflow (Module)

## Steps

1. Select issue (backend-first, lowest number) and confirm scope.
2. Write compact plan: goal, scope, AC, files, validation commands.
3. Apply UX delegation policy from `./ux/delegation-policy.md` and capture required consultation outcome.
4. Implement minimal code changes in a dedicated branch.
5. Run required validations for touched areas.
6. Commit with `Fixes #<issue>` and push.
7. Create PR using required template sections.
8. Address CI failures by root cause and re-validate.

## Validation Baseline

- Backend: `black`, `flake8`, `pytest`
- Frontend: `npm run lint`, `npm run build`, tests if configured
- Include command outputs/evidence in PR body.

## Guardrails

- Avoid unrelated refactors.
- Keep diffs reviewable and DDD-compliant.
- Use `.tmp/` for transient artifacts.
- Follow `./ux/delegation-policy.md` as the canonical delegation rule source.

</file>
</skill>