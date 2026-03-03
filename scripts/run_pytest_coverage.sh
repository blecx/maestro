#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

export PYTHONPATH="$PROJECT_ROOT/apps/api:$PROJECT_ROOT/apps/tui:$PROJECT_ROOT${PYTHONPATH:+:$PYTHONPATH}"

LOCK_DIR=".tmp/coverage"
LOCK_FILE="$LOCK_DIR/pytest-cov.lock"
mkdir -p "$LOCK_DIR"

if ! command -v flock >/dev/null 2>&1; then
    echo "❌ flock is required for deterministic coverage execution" >&2
    exit 2
fi

MODE="full"
USER_ARGS=()

print_help() {
    cat <<'EOF'
Usage: bash scripts/run_pytest_coverage.sh [mode] [pytest_args...]

Modes:
    --full           Run full tests/ with coverage (default)
    --ci             Alias for --full (explicit CI intent)
    --local-stable   Run deterministic core suites (unit/integration/agents/ci)
  --help           Show this help message

Examples:
  bash scripts/run_pytest_coverage.sh --ci -q
  bash scripts/run_pytest_coverage.sh --local-stable -q
  bash scripts/run_pytest_coverage.sh --full -k "health"
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --full)
            MODE="full"
            shift
            ;;
        --ci)
            MODE="ci"
            shift
            ;;
        --local-stable)
            MODE="local-stable"
            shift
            ;;
        --help|-h)
            print_help
            exit 0
            ;;
        *)
            USER_ARGS+=("$1")
            shift
            ;;
    esac
done

PYTHON_BIN="python"
if [ -x "$PROJECT_ROOT/.venv/bin/python" ]; then
    PYTHON_BIN="$PROJECT_ROOT/.venv/bin/python"
fi

SHIM_DIR="$LOCK_DIR/bin"
mkdir -p "$SHIM_DIR"
cat > "$SHIM_DIR/python" <<EOF
#!/usr/bin/env bash
exec "$PYTHON_BIN" "\$@"
EOF
chmod +x "$SHIM_DIR/python"
export PATH="$SHIM_DIR:$PATH"

echo "🔒 Acquiring coverage lock: $LOCK_FILE"
exec 9>"$LOCK_FILE"
flock 9

echo "🧹 Cleaning stale coverage shards"
rm -f .coverage .coverage.*

export COVERAGE_FILE="$LOCK_DIR/.coverage"

echo "🧪 Running pytest with coverage"
echo "🐍 Using interpreter: $PYTHON_BIN"
echo "🧭 Mode: $MODE"

PYTEST_ARGS=(tests/ --cov=apps/api --cov=apps/tui --cov-report=term-missing --cov-report=json)

if [[ "$MODE" == "local-stable" ]]; then
    PYTEST_ARGS=(
        tests/unit/
        tests/integration/
        tests/agents/
        tests/ci/
        --cov=apps/api
        --cov=apps/tui
        --cov-report=term-missing
        --cov-report=json
    )
fi

PYTEST_ARGS+=("${USER_ARGS[@]}")

"$PYTHON_BIN" -m pytest "${PYTEST_ARGS[@]}"

echo "✅ Coverage run completed (coverage.json updated)"