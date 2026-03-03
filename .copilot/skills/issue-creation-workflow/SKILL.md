<skill>
<name>issue-creation-workflow</name>
<description>Workflow or rule module extracted from .copilot/skills/issue-creation-workflow/SKILL.md</description>
<file>
# Issue Creation Workflow (Module)

## Steps

1. Search for duplicates and related issues.
2. Select repository (backend/client) and estimate size (S/M/L).
3. Draft issue body using feature template sections.
4. Add testable acceptance criteria and validation commands.
5. Add cross-repo impact and dependencies.
6. Save draft under `.tmp/`, review, then create issue.

## Required Sections

- Goal / Problem Statement
- Scope (In / Out / Dependencies)
- Acceptance Criteria
- API Contract (if applicable)
- Technical Approach
- Testing Requirements
- Documentation Updates

## Quality Checks

- Criteria are specific and measurable.
- No unresolved placeholders remain.
- Repo constraints included (`projectDocs/`, `configs/llm.json`).
- Cross-repo link exists when downstream work is needed.

</file>
</skill>