.PHONY: sync-maestro mcp-up mcp-down help init-env install-hooks

help:
	@echo "Maestro Toolchain CLI"
	@echo "-----------------------"
	@echo "make sync-maestro   - Pull the latest AI tooling from blecx/maestro trunk"
	@echo "make mcp-up         - Start all Maestro Context (MCP) Docker servers locally"
	@echo "make mcp-down       - Stop all Maestro Context (MCP) Docker servers locally"
	@echo "make init-env       - Initialize .env from .env.maestro.example template"
	@echo "make install-hooks  - Install Maestro git hooks for AI complexity gates"

sync-maestro:
	@echo "🔄 Syncing latest Maestro toolchain into your current repository..."
	@rm -rf /tmp/maestro-trunk
	@git clone --depth 1 https://github.com/blecx/maestro.git /tmp/maestro-trunk
	@rsync -av /tmp/maestro-trunk/agents/ ./agents/
	@rsync -av /tmp/maestro-trunk/apps/mcp/ ./apps/mcp/
	@rsync -av /tmp/maestro-trunk/.github/agents/ ./.github/agents/
	@rsync -av /tmp/maestro-trunk/.copilot/skills/ ./.copilot/skills/
	@rsync -av /tmp/maestro-trunk/docs/maestro/ ./docs/maestro/
	@cp /tmp/maestro-trunk/docker-compose*.yml ./
	@cp /tmp/maestro-trunk/Makefile ./Makefile
	@cp -n /tmp/maestro-trunk/.env.maestro.example ./.env.maestro.example || true
	@cp -R /tmp/maestro-trunk/hooks ./hooks
	@rm -rf /tmp/maestro-trunk
	@echo "✅ Maestro sync complete. Run \"make init-env\" and \"make install-hooks\" if this is your first time."

mcp-up:
	@echo "🚀 Starting Maestro MCP context servers..."
	docker compose -f docker-compose.maestro.yml up -d
	docker compose -f docker-compose.mcp-bash-gateway.yml up -d
	docker compose -f docker-compose.repo-fundamentals-mcp.yml up -d
	docker compose -f docker-compose.mcp-github-ops.yml up -d
	docker compose -f docker-compose.mcp-offline-docs.yml up -d
	docker compose -f docker-compose.mcp-devops.yml up -d
	@echo "✅ MCP servers are running."

mcp-down:
	@echo "🛑 Stopping Maestro MCP context servers..."
	docker compose -f docker-compose.maestro.yml down
	docker compose -f docker-compose.mcp-bash-gateway.yml down
	docker compose -f docker-compose.repo-fundamentals-mcp.yml down
	docker compose -f docker-compose.mcp-github-ops.yml down
	docker compose -f docker-compose.mcp-offline-docs.yml down
	docker compose -f docker-compose.mcp-devops.yml down
	@echo "✅ MCP servers stopped."

init-env:
	@echo "Initializing .env from .env.maestro.example..."
	@if [ ! -f .env ]; then cp .env.maestro.example .env; echo "=> Created .env"; else echo "=> .env already exists"; fi

install-hooks:
	@echo "Installing Maestro git hooks..."
	@mkdir -p .git/hooks
	@cp hooks/pre-commit-maestro .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "=> Pre-commit hook installed successfully."
