#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

mkdir -p "${ROOT_DIR}/.tmp"

if [[ $# -eq 0 ]]; then
  echo "Usage: scripts/bash-gateway-exec.sh '<command>'"
  echo "   or: scripts/bash-gateway-exec.sh -- <command> [args...]"
  exit 2
fi

if [[ "${1}" == "--" ]]; then
  shift
fi

export TMPDIR="${TMPDIR:-${ROOT_DIR}/.tmp}"
export TMP="${TMP:-${ROOT_DIR}/.tmp}"
export TEMP="${TEMP:-${ROOT_DIR}/.tmp}"

if [[ $# -eq 1 ]]; then
  exec bash -lc "$1"
fi

exec bash -lc "$*"
