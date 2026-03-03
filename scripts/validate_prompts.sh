#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${ROOT_DIR}/.venv/bin/python"

if [[ ! -x "${PYTHON_BIN}" ]]; then
  PYTHON_BIN="python3"
fi

echo "[validate_prompts] Running strict prompt quality checks..."
"${PYTHON_BIN}" "${ROOT_DIR}/scripts/check_prompt_quality.py" --strict

echo "[validate_prompts] Running command contract checks..."
"${PYTHON_BIN}" "${ROOT_DIR}/scripts/check_command_contracts.py"

echo "[validate_prompts] Running Context7 guardrail checks..."
"${PYTHON_BIN}" "${ROOT_DIR}/scripts/check_context7_guardrails.py"

echo "[validate_prompts] Running prmerge policy checks..."
"${PYTHON_BIN}" "${ROOT_DIR}/scripts/check_prmerge_policy.py"

echo "[validate_prompts] Running continue-backend policy checks..."
"${PYTHON_BIN}" "${ROOT_DIR}/scripts/check_continue_backend_policy.py"
