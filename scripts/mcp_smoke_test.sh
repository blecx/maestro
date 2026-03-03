#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

ok() {
  echo "[ok] $1"
}

fail() {
  echo "[fail] $1" >&2
  exit 1
}

check_systemd() {
  local unit="$1"
  local enabled
  local active
  enabled="$(sudo systemctl is-enabled "$unit" 2>/dev/null || true)"
  active="$(sudo systemctl is-active "$unit" 2>/dev/null || true)"

  [[ "$enabled" == "enabled" ]] || fail "$unit is not enabled (got: $enabled)"
  [[ "$active" == "active" ]] || fail "$unit is not active (got: $active)"
  ok "$unit enabled+active"
}

check_compose_service() {
  local project_name="$1"
  local compose_file="$2"
  local service="$3"

  local status
  status="$(docker compose --project-name "$project_name" -f "$compose_file" ps --status running --services 2>/dev/null | grep -E "^${service}$" || true)"
  [[ "$status" == "$service" ]] || fail "$service not running in $compose_file"
  ok "$service running in compose project $project_name"
}

check_endpoint_406() {
  local name="$1"
  local url="$2"
  local code
  code="$(curl -sS -o /dev/null -w "%{http_code}" "$url" || true)"
  [[ "$code" == "406" ]] || fail "$name endpoint expected HTTP 406, got $code"
  ok "$name endpoint reachable ($code)"
}

echo "[smoke] MCP services smoke test"

check_systemd "context7-mcp.service"
check_systemd "bash-gateway-mcp.service"
check_systemd "repo-fundamentals-mcp.service"
check_systemd "devops-mcp.service"
check_systemd "offline-docs-mcp.service"
check_systemd "github-ops-mcp.service"

check_compose_service "context7-mcp" "$ROOT_DIR/docker-compose.context7.yml" "context7"
check_compose_service "ai-agent-framework" "$ROOT_DIR/docker-compose.mcp-bash-gateway.yml" "bash-gateway-mcp"
check_compose_service "repo-fundamentals-mcp" "$ROOT_DIR/docker-compose.repo-fundamentals-mcp.yml" "git-mcp"
check_compose_service "repo-fundamentals-mcp" "$ROOT_DIR/docker-compose.repo-fundamentals-mcp.yml" "search-mcp"
check_compose_service "repo-fundamentals-mcp" "$ROOT_DIR/docker-compose.repo-fundamentals-mcp.yml" "filesystem-mcp"
check_compose_service "devops-mcp" "$ROOT_DIR/docker-compose.mcp-devops.yml" "docker-compose-mcp"
check_compose_service "devops-mcp" "$ROOT_DIR/docker-compose.mcp-devops.yml" "test-runner-mcp"
check_compose_service "offline-docs-mcp" "$ROOT_DIR/docker-compose.mcp-offline-docs.yml" "offline-docs-mcp"
check_compose_service "github-ops-mcp" "$ROOT_DIR/docker-compose.mcp-github-ops.yml" "github-ops-mcp"

check_endpoint_406 "Context7 MCP" "http://127.0.0.1:3010/mcp"
check_endpoint_406 "Bash Gateway MCP" "http://127.0.0.1:3011/mcp"
check_endpoint_406 "Git MCP" "http://127.0.0.1:3012/mcp"
check_endpoint_406 "Search MCP" "http://127.0.0.1:3013/mcp"
check_endpoint_406 "Filesystem MCP" "http://127.0.0.1:3014/mcp"
check_endpoint_406 "Docker Compose MCP" "http://127.0.0.1:3015/mcp"
check_endpoint_406 "Test Runner MCP" "http://127.0.0.1:3016/mcp"
check_endpoint_406 "Offline Docs MCP" "http://127.0.0.1:3017/mcp"
check_endpoint_406 "GitHub Ops MCP" "http://127.0.0.1:3018/mcp"

python3 "$ROOT_DIR/scripts/check_mcp_connections.py"

echo "[smoke] PASS"
