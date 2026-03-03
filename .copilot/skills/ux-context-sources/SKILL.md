<skill>
<name>ux-context-sources</name>
<description>Workflow or rule module extracted from .copilot/skills/ux-context-sources/SKILL.md</description>
<file>
# UX Skill: Context Sources

Derive product intent from:

- `README.md`
- `docs/development.md`
- `docs/WORK-ISSUE-WORKFLOW.md`
- active UI code under `../AI-Agent-Framework-Client/client/`

Always summarize inferred intent before proposing navigation/layout changes.

Source precedence for conflicts:
1. Implemented runtime/CI behavior
2. Active code paths and tests
3. Current workflow documentation
4. Historical planning notes

Confidence rule:
- If confidence is low due to missing evidence, record it as a requirement gap.

</file>
</skill>