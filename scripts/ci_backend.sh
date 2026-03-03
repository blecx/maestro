#!/usr/bin/env bash
# Local CI simulation script - runs all CI gates before pushing
# Usage: ./scripts/ci_backend.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "=================================================="
echo "🔍 Backend CI Quality Gates - Local Simulation"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

GATES_PASSED=0
GATES_FAILED=0

run_gate() {
    local gate_num=$1
    local gate_name=$2
    shift 2
    local gate_cmd="$@"
    
    echo "Gate $gate_num: $gate_name"
    echo "----------------------------------------"
    
    if eval "$gate_cmd"; then
        echo -e "${GREEN}✅ Gate $gate_num PASSED${NC}"
        ((GATES_PASSED++))
    else
        echo -e "${RED}❌ Gate $gate_num FAILED${NC}"
        ((GATES_FAILED++))
    fi
    
    echo ""
}

# Ensure projectDocs exists
mkdir -p projectDocs

# Gate 1: All Tests Pass
run_gate 1 "All Tests Pass" "pytest tests/ -v --tb=short -q"

# Gate 2: Coverage Threshold
run_gate 2 "Coverage Threshold (80%+)" "
    pip install -q pytest-cov > /dev/null 2>&1 &&
    bash scripts/run_pytest_coverage.sh --ci -q &&
    python scripts/coverage_diff.py origin/main HEAD
"

# Gate 3: Missing Tests Detection
run_gate 3 "Missing Tests Detection" "
    # Gate intent: prevent adding new modules without tests.
    # Only enforce for *added* Python files; edits to existing modules shouldn't fail this gate.
    CHANGED_FILES=\$(git diff --name-only --diff-filter=A origin/main...HEAD | grep '^apps/.*\.py$' || true)
    
    if [ -z \"\$CHANGED_FILES\" ]; then
        echo '✅ No new Python files added in apps/'
        exit 0
    fi
    
    MISSING_TESTS=\"\"
    for file in \$CHANGED_FILES; do
        if [[ \"\$file\" == *\"__init__.py\" ]]; then
            continue
        fi
        
        if [[ \"\$file\" == apps/api/* ]]; then
            module_path=\"\${file#apps/api/}\"
            test_file=\"tests/unit/test_\${module_path}\"
        elif [[ \"\$file\" == apps/tui/* ]]; then
            module_path=\"\${file#apps/tui/}\"
            test_file=\"tests/unit/test_\${module_path}\"
        else
            continue
        fi
        
        if [ ! -f \"\$test_file\" ]; then
            MISSING_TESTS=\"\$MISSING_TESTS\n  - \$file (expected: \$test_file)\"
        fi
    done
    
    if [ -n \"\$MISSING_TESTS\" ]; then
        echo '❌ Missing test files:'
        echo -e \"\$MISSING_TESTS\"
        exit 1
    fi
    
    echo '✅ All new/changed code has corresponding test files'
"

# Gate 4: Documentation Sync
run_gate 4 "Documentation Sync" "python scripts/check_test_docs.py"

# Gate 5: OpenAPI Spec Validation
run_gate 5 "OpenAPI Spec Validation" "
    cd apps/api &&
    python -c '
import sys
sys.path.insert(0, \".\")
from main import app
import json

spec = app.openapi()

# Check for required fields
assert \"openapi\" in spec, \"Missing openapi version\"
assert \"info\" in spec, \"Missing info section\"
assert \"paths\" in spec, \"Missing paths section\"

# Check all endpoints have descriptions
missing_desc = []
for path, methods in spec[\"paths\"].items():
    for method, details in methods.items():
        if \"summary\" not in details and \"description\" not in details:
            missing_desc.append(f\"{method.upper()} {path}\")

if missing_desc:
    print(\"❌ Endpoints missing descriptions:\")
    for endpoint in missing_desc:
        print(f\"  - {endpoint}\")
    sys.exit(1)

print(f\"✅ OpenAPI spec valid ({len(spec[\\\"paths\\\"])} endpoints documented)\")
'
"

# Gate 6: Linting
run_gate 6 "Linting (black + flake8)" "
    CI_DIFF_ONLY=true CI_DIFF_RANGE=origin/main...HEAD bash scripts/quality/gate6_lint.sh
"

# Gate 7: Security Scanning
run_gate 7 "Security Scanning (bandit + safety)" "
    pip install -q bandit safety > /dev/null 2>&1 &&
    CI_DIFF_ONLY=true CI_DIFF_RANGE=origin/main...HEAD bash scripts/quality/gate7_security.sh
"

# Gate 8: Test Execution Time
run_gate 8 "Test Execution Time (<10min)" "
    START_TIME=\$(date +%s)
    pytest tests/ -v --tb=short -q > /dev/null 2>&1
    END_TIME=\$(date +%s)
    DURATION=\$((END_TIME - START_TIME))
    
    echo \"Test suite completed in \${DURATION}s\"
    
    if [ \$DURATION -gt 600 ]; then
        echo '❌ Test suite exceeded 10 minute limit'
        exit 1
    fi
    
    echo \"✅ Test suite within time limit (\${DURATION}s / 600s)\"
"

# Gate 9: Flaky Test Detection (warning only)
echo "Gate 9: Flaky Test Detection"
echo "----------------------------------------"
echo "⏭️  Skipping in local simulation (too time-consuming)"
echo -e "${YELLOW}⚠️  Gate 9 SKIPPED (runs in CI only)${NC}"
echo ""

# Summary
echo "=================================================="
echo "CI Gates Summary"
echo "=================================================="
echo -e "${GREEN}Passed: $GATES_PASSED${NC}"
echo -e "${RED}Failed: $GATES_FAILED${NC}"
echo ""

if [ $GATES_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All gates passed! Ready to push.${NC}"
    exit 0
else
    echo -e "${RED}❌ Some gates failed. Fix issues before pushing.${NC}"
    exit 1
fi
