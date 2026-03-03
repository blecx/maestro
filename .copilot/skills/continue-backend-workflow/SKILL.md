<skill>
<name>continue-backend-workflow</name>
<description>Workflow or rule module extracted from .copilot/skills/continue-backend-workflow/SKILL.md</description>
<file>
# Continue Backend Workflow

Use this module when running `/continue-backend`.

Entry command:

- `./continue-backend`

Limit policy:

- Default `max-issues` per run is `25`.
- Values below `25` are forbidden.
- Values above `25` require explicit runtime override confirmation.

## Loop

1. **Model policy:** resolve planning/execution models and enforce token-budget mode.
2. **Issue spec validation:** check strict sections + body-size limit for roadmap specs.
3. **Publish:** run deterministic issue publishing for backend roadmap entries.
4. **Select:** pick next scoped backend issue (label-filtered by default).
5. **Implement:** run `./scripts/work-issue.py --issue <n>` with retry/backoff.
6. **Merge:** run `./scripts/prmerge <n>` after required checks.

Merge rule:

- If `prmerge` reports no PR found for the issue, treat that as a complete answer (nothing to merge). Do not prompt for a manual PR number; stop or continue to the next issue.
7. **Record:** persist outcomes and continue.

## Quality Gates

- Mandatory PR review before merge.
- CI pass required for merge path.
- Prompt and policy validators must pass.
- Keep one issue per PR and scope small.

## Stop Conditions

- No scoped backend issues available.
- Blocking dependency unresolved.
- Repeated API rate limiting requiring operator pause.

</file>
</skill>