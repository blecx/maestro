.PHONY: help bootstrap runtime-env runtime-up runtime-down validate install-hooks

help:
	@echo "softwareFactoryVscode commands"
	@echo "------------------------------"
	@echo "make bootstrap     - Bootstrap the current host repository"
	@echo "make runtime-env   - Generate isolated runtime environment"
	@echo "make runtime-up    - Start factory runtime services"
	@echo "make runtime-down  - Stop factory runtime services"
	@echo "make validate      - Run package validation checks"
	@echo "make install-hooks - Install package pre-commit hook"

bootstrap:
	@python3 scripts/bootstrap_host.py --target . --factory-root .

runtime-env:
	@python3 scripts/project_runtime_env.py --target .

runtime-up:
	@python3 scripts/project_runtime_up.py --target . --build

runtime-down:
	@python3 scripts/project_runtime_down.py --target .

validate:
	@python3 scripts/check_neutrality.py
	@python3 scripts/check_variable_contract.py
	@python3 scripts/check_boundaries.py
	@python3 scripts/check_vscode_workspace.py
	@python3 scripts/check_docs_accuracy.py

install-hooks:
	@echo "Installing package pre-commit hook..."
	@mkdir -p .git/hooks
	@cp hooks/pre-commit-factory .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "=> Pre-commit hook installed successfully."
