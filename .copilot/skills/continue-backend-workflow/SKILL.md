# Continue Backend Workflow

Use this module when running `/continue-backend`.

Entry command:

- `./continue-backend`

Limit policy:

- Default `max-issues` per run is `25`.
- Values below `25` are forbidden.
- Values above `25` require explicit runtime override confirmation.

## Loop

1. **Select:** pick next scoped backend issue (label-filtered by default).
2. **Implement:** strictly delegate to canonical `resolve-issue-workflow` for all implementation, validations, and rules.
3. **Merge:** strictly delegate to canonical `pr-merge-workflow` for all gate checks and merge logic.
4. **Record:** persist outcomes and continue.

## Stop Conditions

- No scoped backend issues available.
- Blocking dependency unresolved.
- Repeated API rate limiting requiring operator pause.
