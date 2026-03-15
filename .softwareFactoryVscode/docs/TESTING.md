# Testing

## Local test suite

Run the contract and smoke checks locally:

- `python3 scripts/check_boundaries.py`
- `python3 scripts/check_neutrality.py`
- `python3 scripts/check_variable_contract.py`
- `python3 scripts/check_vscode_workspace.py`
- `python3 scripts/check_docs_accuracy.py`
- `python3 scripts/test_fresh_install.py`
- `python3 scripts/test_dual_host_isolation.py`
- `python3 scripts/test_upgrade_path.py`
- `python3 scripts/test_failure_modes.py`
- `pytest tests/contracts tests/unit tests/integration -q`

## Prerequisites

- Python 3.10+
- Git
- Docker for runtime checks

## Split checks

### Static

- `check_boundaries.py`
- `check_neutrality.py`
- `check_variable_contract.py`
- `check_vscode_workspace.py`
- `check_docs_accuracy.py`

### Build/runtime

- `test_fresh_install.py`
- `project_runtime_validate.py`

### Isolation

- `test_dual_host_isolation.py`

### Upgrade

- `test_upgrade_path.py`

## Logs and diagnostics

Runtime artifacts and diagnostics are written under `.tmp/softwareFactoryVscode/` in the host repository.

## Relationship to `SoftwareFactoryVsocdeTestsuite.md`

This document maps the executable checks to the validation contract defined in `SoftwareFactoryVsocdeTestsuite.md`.

## VS Code parity verification

Use `check_vscode_workspace.py` to verify:

- projected settings
- task labels
- MCP wiring
- extension recommendations and unwanted recommendations
