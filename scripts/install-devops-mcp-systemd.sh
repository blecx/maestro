#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="${ROOT_DIR}/docker-compose.mcp-devops.yml"
PROJECT_NAME="devops-mcp"
UNIT_NAME="devops-mcp.service"
UNIT_PATH="/etc/systemd/system/${UNIT_NAME}"
ENV_FILE="/etc/default/devops-mcp"
DOCKER_BIN="$(command -v docker || true)"
SYSTEMCTL_BIN="$(command -v systemctl || true)"
SUDO_BIN="$(command -v sudo || true)"

if [[ -z "${DOCKER_BIN}" ]]; then
  echo "docker command not found. Install Docker first."
  exit 1
fi

if [[ -z "${SYSTEMCTL_BIN}" ]]; then
  echo "systemctl not found. This script requires systemd."
  exit 1
fi

if [[ -z "${SUDO_BIN}" ]]; then
  echo "sudo command not found. This script requires sudo for unit installation."
  exit 1
fi

if [[ ! -d /run/systemd/system ]]; then
  echo "systemd does not appear to be active on this host."
  exit 1
fi

if [[ ! -f "${COMPOSE_FILE}" ]]; then
  echo "Compose file not found: ${COMPOSE_FILE}"
  exit 1
fi

if ! "${DOCKER_BIN}" compose version >/dev/null 2>&1; then
  echo "docker compose plugin not found. Install Docker Compose v2 support."
  exit 1
fi

if [[ ! -f "${ENV_FILE}" ]]; then
  sudo tee "${ENV_FILE}" >/dev/null <<'EOF'
# Optional overrides for DevOps MCP service
# DOCKER_COMPOSE_MCP_TARGETS=main=docker-compose.yml,context7=docker-compose.context7.yml,bash_gateway=docker-compose.mcp-bash-gateway.yml,repo_fundamentals=docker-compose.repo-fundamentals-mcp.yml,devops_mcp=docker-compose.mcp-devops.yml
# TEST_RUNNER_PYTHON=python3
EOF
  sudo chmod 0600 "${ENV_FILE}"
  echo "Created ${ENV_FILE} template."
fi

sudo tee "${UNIT_PATH}" >/dev/null <<EOF
[Unit]
Description=DevOps MCP Docker Service
After=docker.service network-online.target
Wants=network-online.target
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
EnvironmentFile=-${ENV_FILE}
WorkingDirectory=${ROOT_DIR}
ExecStart=${DOCKER_BIN} compose --project-name ${PROJECT_NAME} -f ${COMPOSE_FILE} up -d --build --remove-orphans
ExecStop=${DOCKER_BIN} compose --project-name ${PROJECT_NAME} -f ${COMPOSE_FILE} down --remove-orphans
ExecReload=${DOCKER_BIN} compose --project-name ${PROJECT_NAME} -f ${COMPOSE_FILE} up -d --build --remove-orphans
TimeoutStartSec=900
TimeoutStopSec=180
UMask=0077
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
EOF

sudo chmod 0644 "${UNIT_PATH}"
sudo systemctl daemon-reload
sudo systemctl enable --now "${UNIT_NAME}"

echo "Installed and started ${UNIT_NAME}."
echo "Environment file: ${ENV_FILE}"
echo "Check status with: sudo systemctl status ${UNIT_NAME}"
echo "Enabled: $(sudo systemctl is-enabled "${UNIT_NAME}")"
echo "Active: $(sudo systemctl is-active "${UNIT_NAME}")"
