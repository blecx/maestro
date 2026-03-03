# Token-Budgeted Issue Template

Use this template when planning issues for autonomous execution on constrained model endpoints.

## Scope Rules

- One issue = one PR.
- Prefer `S` or `M` sized slices.
- Keep changed-file set explicit and small.

## Prompt Budget Guidance

- Keep planning context packet under ~3000-3500 chars.
- Keep review/fix notes under ~3000-3500 chars.
- Avoid embedding full docs; reference file paths and fetch targeted sections.

## Canonical Body Addendum

Add this section to issue bodies when relevant:

```markdown
## Token Budget Constraints
- [ ] Planning packet stays within compact context budget.
- [ ] Review/fix loop uses truncated notes when needed.
- [ ] Validation commands are explicit and runnable.
```

## Validation Checklist

- `./scripts/validate_prompts.sh`
- `python scripts/check_command_contracts.py`
- `python scripts/check_issue_specs.py --paths "planning/issues/*.yml" --no-legacy --strict-sections`
