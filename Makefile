.PHONY: sync-maestro check-maestro-version install-drift-check uninstall-drift-check mcp-up mcp-down help init-env install-hooks

# Load .env if it exists so MAESTRO_VERSION can be set there
-include .env
MAESTRO_VERSION ?= main

help:
	@echo "Maestro Toolchain CLI"
	@echo "-----------------------"
	@echo "make sync-maestro          - Pull Maestro toolchain at MAESTRO_VERSION into your repo"
	@echo "make check-maestro-version   - Verify local copy matches MAESTRO_VERSION (manual)"
	@echo "make install-drift-check     - Install systemd user timer for weekly drift detection"
	@echo "make uninstall-drift-check   - Remove the drift-check systemd timer and service"
	@echo "make mcp-up                  - Start all Maestro Context (MCP) Docker servers locally"
	@echo "make mcp-down              - Stop all Maestro Context (MCP) Docker servers locally"
	@echo "make init-env              - Initialize .env from .env.maestro.example template"
	@echo "make install-hooks         - Install Maestro git hooks for AI complexity gates"
	@echo ""
	@echo "Current MAESTRO_VERSION: $(MAESTRO_VERSION)"

sync-maestro:
	@echo "🔄 Syncing Maestro toolchain (version: $(MAESTRO_VERSION)) into this repository..."
	@rm -rf /tmp/maestro-trunk
	@git clone --depth 1 --branch $(MAESTRO_VERSION) https://github.com/blecx/maestro.git /tmp/maestro-trunk 2>/dev/null || \
		(echo "⚠️  Branch/tag '$(MAESTRO_VERSION)' not found, falling back to main..." && \
		 git clone --depth 1 https://github.com/blecx/maestro.git /tmp/maestro-trunk)
	@rsync -av /tmp/maestro-trunk/agents/ ./agents/
	@rsync -av /tmp/maestro-trunk/apps/mcp/ ./apps/mcp/
	@rsync -av /tmp/maestro-trunk/.github/agents/ ./.github/agents/
	@rsync -av /tmp/maestro-trunk/.copilot/skills/ ./.copilot/skills/
	@cp /tmp/maestro-trunk/docker-compose*.yml ./
	@cp /tmp/maestro-trunk/Makefile ./Makefile
	@cp -n /tmp/maestro-trunk/.env.maestro.example ./.env.maestro.example || true
	@rsync -av /tmp/maestro-trunk/hooks/ ./hooks/
	@rsync -av /tmp/maestro-trunk/scripts/ ./scripts/
	@git -C /tmp/maestro-trunk rev-parse HEAD > .maestro-version
	@rm -rf /tmp/maestro-trunk
	@echo "✅ Maestro sync complete (pinned SHA written to .maestro-version)."
	@echo "   Run \"make init-env\" and \"make install-hooks\" if this is your first time."

check-maestro-version:
	@echo "🔍 Checking Maestro version drift..."
	@if [ ! -f .maestro-version ]; then \
		echo "⚠️  .maestro-version not found. Run 'make sync-maestro' first."; \
		exit 1; \
	fi
	@LOCAL_SHA=$$(cat .maestro-version); \
	REMOTE_SHA=$$(git ls-remote https://github.com/blecx/maestro.git refs/heads/$(MAESTRO_VERSION) | awk '{print $$1}'); \
	if [ "$$LOCAL_SHA" = "$$REMOTE_SHA" ]; then \
		echo "✅ Local Maestro ($$LOCAL_SHA) matches $(MAESTRO_VERSION) ($$REMOTE_SHA)."; \
	else \
		echo "⚠️  Drift detected!"; \
		echo "   Local : $$LOCAL_SHA"; \
		echo "   Remote: $$REMOTE_SHA ($(MAESTRO_VERSION))"; \
		echo "   Run 'make sync-maestro' to update."; \
		exit 1; \
	fi

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

install-drift-check:
	@echo "Installing Maestro drift-check systemd timer for workspace: $$(pwd)"
	@mkdir -p "$$HOME/.local/bin" "$$HOME/.config/systemd/user"
	@install -m 0755 scripts/check-maestro-drift.sh "$$HOME/.local/bin/check-maestro-drift"
	@printf 'MAESTRO_WORKSPACE=%s\nMAESTRO_VERSION=%s\n' "$$(pwd)" "$(MAESTRO_VERSION)" \
		> "$$HOME/.config/systemd/user/check-maestro-drift.env"
	@cp scripts/systemd/check-maestro-drift.service "$$HOME/.config/systemd/user/"
	@cp scripts/systemd/check-maestro-drift.timer    "$$HOME/.config/systemd/user/"
	@systemctl --user daemon-reload
	@systemctl --user enable --now check-maestro-drift.timer
	@echo "✅ Drift-check timer installed and enabled."
	@echo "   View status : systemctl --user status check-maestro-drift.timer"
	@echo "   Run manually: systemctl --user start check-maestro-drift.service"
	@echo "   Logs        : journalctl --user -u check-maestro-drift"

uninstall-drift-check:
	@echo "Removing Maestro drift-check systemd timer..."
	@systemctl --user disable --now check-maestro-drift.timer 2>/dev/null || true
	@rm -f "$$HOME/.config/systemd/user/check-maestro-drift.service" \
	       "$$HOME/.config/systemd/user/check-maestro-drift.timer" \
	       "$$HOME/.config/systemd/user/check-maestro-drift.env" \
	       "$$HOME/.local/bin/check-maestro-drift"
	@systemctl --user daemon-reload
	@echo "✅ Drift-check timer removed."
