<skill>
<name>tutorial-review-workflow</name>
<description>Workflow or rule module extracted from .copilot/skills/tutorial-review-workflow/SKILL.md</description>
<file>
# Tutorial Review Workflow (Module)

## Steps

1. Build source-of-truth map from code/routes/commands.
2. Audit tutorial docs for accuracy and stale instructions.
3. Flag duplication and select canonical references.
4. Identify coverage gaps and undocumented artifacts.
5. Produce qualified findings with severity and evidence.
6. Group fixes into plan/issue batches.

## Qualified Findings Fields

- ID, category, severity
- location and evidence
- user impact
- proposed fix
- workflow target

## Guardrails

- Final narrative output stays in Markdown.
- Keep UX and TUI paths separate.
- Do not invent unsupported product behavior.

</file>
</skill>