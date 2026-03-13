# Continue Phase-2 Workflow

Use this module when running `/continue-phase-2`.

Entry command:

- `./continue-phase-2`

Limit policy:

- Default `max-issues` per run is `25`.
- Values above `25` require explicit runtime confirmation.

## Loop

1. **Select:** run `./next-issue` and capture selected issue.
2. **Implement:** strictly delegate to canonical `resolve-issue-workflow` for all implementation, slice sizing, validations, and rules.
3. **Merge:** strictly delegate to canonical `pr-merge-workflow` for all gate checks and merge logic.
4. **Record:** append notes/artifacts and continue to next issue.

## Stop Conditions

- No selectable issues available.
- Blocking dependency unresolved.
- Repeated CI failure requiring human decision.
