#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="/etc/default/bash-gateway-mcp"
UNIT_NAME="bash-gateway-mcp.service"
POLICY_PATH="/workspace/configs/bash_gateway_policy.max_allowance.yml"
POLICY_FILE_HOST="${ROOT_DIR}/configs/bash_gateway_policy.max_allowance.yml"
VSCODE_SETUP="${ROOT_DIR}/scripts/setup-vscode-autoapprove.py"
AUDIT_DIR_HOST="${ROOT_DIR}/.tmp/agent-script-runs"

info() { printf "ℹ %s\n" "$*"; }
ok() { printf "✅ %s\n" "$*"; }
warn() { printf "⚠️  %s\n" "$*"; }
err() { printf "❌ %s\n" "$*"; }

require_file() {
  local path="$1"
  if [[ ! -f "$path" ]]; then
    err "Missing required file: $path"
    exit 1
  fi
}

append_or_replace_env_var() {
  local key="$1"
  local value="$2"
  local file="$3"

  if grep -qE "^${key}=" "$file"; then
    sed -i "s|^${key}=.*|${key}=${value}|" "$file"
  else
    printf "%s=%s\n" "$key" "$value" >>"$file"
  fi
}

configure_vscode_low_friction() {
  info "Configuring VS Code Copilot terminal approvals (low-friction profile)..."
  python3 "$VSCODE_SETUP" --profile low-friction
  ok "VS Code settings updated (global + backend workspace + client workspace)."
}

configure_workspace_tmp() {
  info "Ensuring workspace temp directory exists..."
  mkdir -p "${ROOT_DIR}/.tmp"
  ok "Workspace temp directory ready: ${ROOT_DIR}/.tmp"
}

configure_audit_dir_permissions() {
  info "Ensuring bash gateway audit dir is writable for local user + service..."
  mkdir -p "${AUDIT_DIR_HOST}"

  if command -v sudo >/dev/null 2>&1; then
    local owner_user owner_group
    owner_user="${SUDO_USER:-$USER}"
    owner_group="$(id -gn "${owner_user}")"
    sudo mkdir -p "${AUDIT_DIR_HOST}"
    sudo chown "${owner_user}:${owner_group}" "${AUDIT_DIR_HOST}"
    sudo chmod 0775 "${AUDIT_DIR_HOST}"
  else
    chmod 0775 "${AUDIT_DIR_HOST}" || true
  fi

  ok "Audit dir ready: ${AUDIT_DIR_HOST}"
}

configure_bash_gateway_policy() {
  require_file "$POLICY_FILE_HOST"

  if ! command -v sudo >/dev/null 2>&1; then
    warn "sudo not found. Skipping systemd MCP service reconfiguration."
    warn "Manual step: set BASH_GATEWAY_POLICY_PATH=${POLICY_PATH} for bash-gateway-mcp service."
    return 0
  fi

  if [[ ! -f "$ENV_FILE" ]]; then
    info "Creating ${ENV_FILE} ..."
    sudo install -m 600 /dev/null "$ENV_FILE"
  fi

  info "Setting Bash Gateway MCP policy path override to max allowance..."
  sudo bash -lc "$(cat <<'EOS'
set -euo pipefail
FILE="$1"
KEY="$2"
VAL="$3"
if grep -qE "^${KEY}=" "$FILE"; then
  sed -i "s|^${KEY}=.*|${KEY}=${VAL}|" "$FILE"
else
  printf "%s=%s\n" "$KEY" "$VAL" >>"$FILE"
fi
EOS
)" _ "$ENV_FILE" "BASH_GATEWAY_POLICY_PATH" "$POLICY_PATH"

  if command -v systemctl >/dev/null 2>&1 && systemctl status "$UNIT_NAME" >/dev/null 2>&1; then
    info "Restarting ${UNIT_NAME} to apply policy..."
    sudo systemctl restart "$UNIT_NAME"
    sudo systemctl is-active "$UNIT_NAME" >/dev/null
    ok "${UNIT_NAME} is active with updated environment override."
  elif command -v systemctl >/dev/null 2>&1 && systemctl is-enabled "$UNIT_NAME" >/dev/null 2>&1; then
    info "Restarting enabled unit ${UNIT_NAME} to apply policy..."
    sudo systemctl restart "$UNIT_NAME"
    sudo systemctl is-active "$UNIT_NAME" >/dev/null
    ok "${UNIT_NAME} is active with updated environment override."
  else
    warn "${UNIT_NAME} not installed."
    warn "Start/install with: ./scripts/install-bash-gateway-mcp-systemd.sh"
  fi
}

review_configuration() {
  info "Reviewing resulting configuration (sanity checks)..."

  local backend_settings="${ROOT_DIR}/.vscode/settings.json"
  local client_settings="${ROOT_DIR}/../AI-Agent-Framework-Client/.vscode/settings.json"

  require_file "$backend_settings"
  require_file "$client_settings"

  python3 - <<PY
import json
from pathlib import Path

backend = json.loads(Path("${backend_settings}").read_text())
client = json.loads(Path("${client_settings}").read_text())

def assert_key(obj, path, expected=None):
    cur = obj
    for p in path:
        if p not in cur:
            raise SystemExit(f"Missing key: {'.'.join(path)}")
        cur = cur[p]
    if expected is not None and cur != expected:
        raise SystemExit(f"Unexpected value for {'.'.join(path)}: {cur!r} != {expected!r}")

assert_key(backend, ["chat.tools.terminal.autoApprove", "/^\\s*.+$/", "approve"], True)
assert_key(client, ["chat.tools.terminal.autoApprove", "/^\\s*.+$/", "approve"], True)
assert_key(backend, ["terminal.integrated.env.linux", "TMPDIR"], "\${workspaceFolder}/.tmp")
assert_key(client, ["terminal.integrated.env.linux", "TMPDIR"], "\${workspaceFolder}/.tmp")

print("OK: VS Code low-friction keys + TMPDIR settings present in both workspaces.")
PY

  if [[ -f "$ENV_FILE" ]] && command -v sudo >/dev/null 2>&1 && sudo grep -q "^BASH_GATEWAY_POLICY_PATH=${POLICY_PATH}$" "$ENV_FILE"; then
    ok "Bash gateway env file points to max-allowance policy."
  else
    warn "Bash gateway env file not updated or unavailable; MCP service may still use default policy."
  fi

  if command -v docker >/dev/null 2>&1; then
    local container_policy
    container_policy="$(docker inspect --format '{{range .Config.Env}}{{println .}}{{end}}' bash-gateway-mcp 2>/dev/null | grep '^BASH_GATEWAY_POLICY_PATH=' || true)"
    if [[ "$container_policy" == "BASH_GATEWAY_POLICY_PATH=${POLICY_PATH}" ]]; then
      ok "Running container uses max-allowance bash gateway policy."
    elif [[ -n "$container_policy" ]]; then
      warn "Running container policy is '${container_policy#BASH_GATEWAY_POLICY_PATH=}' (expected ${POLICY_PATH})."
      warn "If just updated compose/env, restart service: sudo systemctl restart ${UNIT_NAME}"
    else
      warn "Could not read running container policy env (container may be restarting or absent)."
    fi
  fi

  if [[ -d "${AUDIT_DIR_HOST}" ]]; then
    local mode owner
    mode="$(stat -c '%a' "${AUDIT_DIR_HOST}" 2>/dev/null || echo "unknown")"
    owner="$(stat -c '%U:%G' "${AUDIT_DIR_HOST}" 2>/dev/null || echo "unknown")"
    info "Audit dir permissions: ${owner} ${mode}"
  fi

  ok "Review completed: script changes map to real config paths and active keys."
}

main() {
  require_file "$VSCODE_SETUP"
  require_file "$POLICY_FILE_HOST"

  info "Applying maximal allowance profile for VS Code + MCP bash gateway."
  configure_workspace_tmp
  configure_audit_dir_permissions
  configure_vscode_low_friction
  configure_bash_gateway_policy
  review_configuration

  echo
  ok "Configuration complete."
  info "Reload VS Code window: Ctrl+Shift+P -> Developer: Reload Window"
  info "For MCP calls, use bash gateway profile 'max' with script_path 'scripts/bash-gateway-exec.sh'"
}

main "$@"
