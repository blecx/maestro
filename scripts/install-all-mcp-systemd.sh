#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

run_step() {
  local script_path="$1"
  echo "[install] ${script_path}"
  bash "${ROOT_DIR}/${script_path}"
}

run_step "scripts/install-context7-systemd.sh"
run_step "scripts/install-bash-gateway-mcp-systemd.sh"
run_step "scripts/install-repo-fundamentals-mcp-systemd.sh"
run_step "scripts/install-devops-mcp-systemd.sh"
run_step "scripts/install-offline-docs-mcp-systemd.sh"
run_step "scripts/install-github-ops-mcp-systemd.sh"

echo "[ok] All MCP systemd services installed and enabled"
