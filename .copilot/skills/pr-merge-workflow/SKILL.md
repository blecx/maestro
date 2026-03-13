<skill>
<name>pr-merge-workflow</name>
<description>Workflow or rule module extracted from .copilot/skills/pr-merge-workflow/SKILL.md</description>
<file>
# PR Merge Workflow (Module)

Use this skill as the canonical implementation source for `pr-merge`.

## Use When

- A PR is ready or nearly ready and needs merge validation.
- An issue number needs to be resolved through PR discovery and merge.

## Steps

1. Verify PR is open, mergeable, and not draft.
2. Confirm required checks are green (or only pre-existing failures).
3. Merge with squash and delete branch.
4. Comment and close linked issue (if needed).
5. Clean `.tmp` files for this issue/PR.
6. Sync local `main` and verify final state.

## Required Checks

- Choose the correct repo and validation gate before merge.
- Require real validation evidence in the PR body.
- For UI/UX-affecting changes, require recorded UX authority resolution.
- Capture merge metrics when tooling supports it.

## Guardrails

- If `prmerge` reports no PR found for the issue, treat that as a complete answer (nothing to merge). Do not prompt for a manual PR number.
- Mandatory PR review before merge.

- Do not fix failing code/tests in this workflow.
- Delegate implementation changes to `resolve-issue`.
- Document any admin override rationale.
- Never use `/tmp`; use `.tmp/`.
- Never merge with failing CI.

</file>
</skill>