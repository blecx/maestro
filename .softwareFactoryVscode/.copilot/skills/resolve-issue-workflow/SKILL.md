<skill>
<name>resolve-issue-workflow</name>
<description>Neutral workflow for taking one issue-sized change from plan through validation.</description>
<file>
# Resolve Issue Workflow

## Instructions
1. Confirm goal, scope, acceptance criteria, and validation commands.
2. Keep changes focused to one issue-sized slice.
3. Prefer deterministic validation commands from `scripts/` and `tests/`.
4. Use `.tmp/` for temporary artifacts.
5. Before completion, capture which validations ran and whether follow-up work remains.

## Validation baseline
- `python scripts/check_neutrality.py`
- `python scripts/check_variable_contract.py`
- `python scripts/check_boundaries.py`
- `python scripts/check_vscode_workspace.py`
- `python -m pytest tests factory_runtime/tests -q --tb=short`
</file>
</skill>
