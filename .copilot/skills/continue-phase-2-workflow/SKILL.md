<skill>
<name>continue-phase-2-workflow</name>
<description>Workflow or rule module extracted from .copilot/skills/continue-phase-2-workflow/SKILL.md</description>
<file>
# Continue Phase-2 Workflow

Use this module when running `/continue-phase-2`.

Entry command:

- `./continue-phase-2`

Limit policy:

- Default `max-issues` per run is `25`.
- Values above `25` require explicit runtime confirmation.

## Loop

1. **Issue selection:** run `./next-issue` and capture selected issue.
2. **Slice sizing:** keep scope to a small CI-safe slice (single issue, minimal touched domains).
3. **Implement:** run `./scripts/work-issue.py --issue <n>` (or `--plan-only` when needed).
4. **Validate:** run required checks for changed areas before PR merge.
5. **Review gate:** ensure PR reviewed and approved before merge.
6. **Merge gate:** merge with `./scripts/prmerge <issue>` after CI pass.

Merge rule:

- If `prmerge` reports no PR found for the issue, treat that as a complete answer (nothing to merge). Do not prompt for a manual PR number; stop or continue to the next issue.
7. **Record:** append notes/artifacts and continue to next issue.

## Quality Gates

- Apply canonical UX delegation policy from `./ux/delegation-policy.md`.
- Mandatory PR review before merge.
- CI must pass for merge path.
- PR merge slice limits enforced by `scripts/prmerge` policy defaults.
- No architecture regressions outside issue scope.

## Stop Conditions

- No selectable issues available.
- Blocking dependency unresolved.
- Repeated CI failure requiring human decision.

</file>
</skill>