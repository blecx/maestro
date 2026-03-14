.PHONY: sync-maestro mcp-up mcp-down help init-env install-hooks

help:
	@echo "Maestro Toolchain CLI"
	@echo "-----------------------"
	@echo "make sync-maestro   - Pull the latest AI tooling from YOUR_ORG/YOUR_REPO trunk"
	@echo "make mcp-up         - Start all Maestro Context (MCP) Docker servers locally"
	@echo "make mcp-down       - Stop all Maestro Context (MCP) Docker servers locally"
	@echo "make init-env       - Initialize .env from .env.maestro.example template"
	@echo "make install-hooks  - Install Maestro git hooks for AI complexity gates"

sync-maestro:
	@echo "🔄 Syncing latest Maestro toolchain..."
	@python3 scripts/install_maestro_trunk.py .
	@echo "✅ Maestro sync complete. Run \"make init-env\" and \"make install-hooks\" if this is your first time."
mcp-up:
	@echo "🚀 MCP-UP Maestro MCP context servers in isolated runtime..."
	@ENV_FILE=$$(python3 scripts/maestro_runtime_env.py --target . --quiet) && \
	docker compose --env-file $$ENV_FILE \
	  -f docker-compose.maestro.yml \
	  -f docker-compose.mcp-bash-gateway.yml \
	  -f docker-compose.repo-fundamentals-mcp.yml \
	  -f docker-compose.mcp-github-ops.yml \
	  -f docker-compose.mcp-offline-docs.yml \
	  -f docker-compose.mcp-devops.yml \
	  up -d
	@echo "✅ MCP servers mcp-up complete."
mcp-down:
	@echo "🚀 MCP-DOWN Maestro MCP context servers in isolated runtime..."
	@ENV_FILE=$$(python3 scripts/maestro_runtime_env.py --target . --quiet) && \
	docker compose --env-file $$ENV_FILE \
	  -f docker-compose.maestro.yml \
	  -f docker-compose.mcp-bash-gateway.yml \
	  -f docker-compose.repo-fundamentals-mcp.yml \
	  -f docker-compose.mcp-github-ops.yml \
	  -f docker-compose.mcp-offline-docs.yml \
	  -f docker-compose.mcp-devops.yml \
	  down
	@echo "✅ MCP servers mcp-down complete."
init-env:
	@echo "Initializing .env from .env.maestro.example..."
	@if [ ! -f .env ]; then cp .env.maestro.example .env; echo "=> Created .env"; else echo "=> .env already exists"; fi

install-hooks:
	@echo "Installing Maestro git hooks..."
	@mkdir -p .git/hooks
	@cp hooks/pre-commit-maestro .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "=> Pre-commit hook installed successfully."
