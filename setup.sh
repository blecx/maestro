#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
venv_dir="${repo_root}/.venv"

requested_python="${PYTHON_BIN:-/usr/local/bin/python3.12}"

if [[ "${requested_python}" = /* ]]; then
  if [[ ! -x "${requested_python}" ]]; then
    echo "Python 3.12 executable not found at ${requested_python}" >&2
    exit 1
  fi
  python_cmd=("${requested_python}")
else
  if ! command -v "${requested_python}" >/dev/null 2>&1; then
    echo "Python executable '${requested_python}' was not found" >&2
    exit 1
  fi
  python_cmd=("$(command -v "${requested_python}")")
fi

"${python_cmd[@]}" - <<'PY'
import sys

if sys.version_info[:2] != (3, 12):
    raise SystemExit(
        f"Expected Python 3.12, found {sys.version.split()[0]} at {sys.executable}"
    )
PY

echo "Using Python: $("${python_cmd[@]}" -c 'import sys; print(sys.executable)')"
echo "Python version: $("${python_cmd[@]}" -c 'import sys; print(sys.version.split()[0])')"

if [[ ! -d "${venv_dir}" ]]; then
  echo "Creating virtual environment in ${venv_dir}"
  "${python_cmd[@]}" -m venv "${venv_dir}"
else
  echo "Reusing existing virtual environment in ${venv_dir}"
fi

"${venv_dir}/bin/python" -m pip install --upgrade pip setuptools wheel

requirements_file="${repo_root}/requirements.txt"
compat_requirements_file="${repo_root}/agents/requirements.txt"

if [[ -f "${requirements_file}" ]]; then
  echo "Installing dependencies from ${requirements_file}"
  "${venv_dir}/bin/pip" install -r "${requirements_file}"
elif [[ -f "${compat_requirements_file}" ]]; then
  echo "Installing dependencies from ${compat_requirements_file}"
  "${venv_dir}/bin/pip" install -r "${compat_requirements_file}"
else
  echo "No requirements file found; created the virtual environment only"
fi

echo
echo "Bootstrap complete"
echo "Activate with: source .venv/bin/activate"
echo "Interpreter: ${venv_dir}/bin/python"