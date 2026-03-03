#!/usr/bin/env bash
set -euo pipefail

MAX_ISSUES=25
ISSUE_OVERRIDE=""
DRY_RUN=0
SKIP_RECONCILE=0
NO_SPLIT_ISSUES=0

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

mkdir -p .tmp
exec 9>"$ROOT_DIR/.tmp/issue-pr-merge-cleanup.lock"
if ! flock -n 9; then
  echo "Another issue/pr/merge/cleanup loop is already running; stop it first." >&2
  exit 3
fi

usage() {
  cat <<'EOF'
Usage: ./scripts/issue-pr-merge-cleanup-loop.sh [options]

Loop workflow:
  select issue -> work-issue -> prmerge -> mandatory .tmp cleanup verify

Options:
  --issue <n>         Run one explicit issue first.
  --max-issues <n>    Stop after n issues (default: 25).
  --dry-run           Print actions only; do not execute.
  --skip-reconcile    Pass --skip-reconcile to next-issue.py selection.
  --no-split-issues   Do not pass --create-split-issues to work-issue.py.
  -h, --help          Show this help.

Cleanup policy (after successful merge):
  rm -f .tmp/pr-body-<issue>.md .tmp/issue-<issue>-*.md
  ls -la .tmp/*<issue>* 2>/dev/null || echo "✓ Cleanup verified"
EOF
}

require_option_value() {
  local option="$1"
  local value="${2:-}"
  if [[ -z "$value" || "$value" =~ ^-- ]]; then
    echo "$option requires a value" >&2
    exit 1
  fi
}

is_valid_issue_number() {
  local value="$1"
  [[ "$value" =~ ^[1-9][0-9]*$ ]]
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --issue)
      require_option_value "--issue" "${2:-}"
      ISSUE_OVERRIDE="$2"
      shift 2
      ;;
    --max-issues)
      require_option_value "--max-issues" "${2:-}"
      MAX_ISSUES="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --skip-reconcile)
      SKIP_RECONCILE=1
      shift
      ;;
    --no-split-issues)
      NO_SPLIT_ISSUES=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if ! [[ "$MAX_ISSUES" =~ ^[0-9]+$ ]]; then
  echo "Invalid --max-issues value: $MAX_ISSUES" >&2
  exit 1
fi

if [[ -n "$ISSUE_OVERRIDE" ]] && ! is_valid_issue_number "$ISSUE_OVERRIDE"; then
  echo "Invalid --issue value: $ISSUE_OVERRIDE" >&2
  exit 1
fi

select_next_issue() {
  local next_cmd=(./scripts/next-issue.py)
  if [[ "$SKIP_RECONCILE" == "1" ]]; then
    next_cmd+=(--skip-reconcile)
  fi

  if [[ "$DRY_RUN" == "1" ]]; then
    echo "[dry-run] Would run: ${next_cmd[*]}"
    echo "[dry-run] Using sample selected issue: 99999"
    return 0
  fi

  local output
  if ! output="$(${next_cmd[@]})"; then
    echo "$output"
    return 1
  fi

  echo "$output"

  local selected
  selected="$(printf '%s\n' "$output" | sed -n 's/.*Selected Issue: #\([0-9][0-9]*\).*/\1/p' | head -n1)"
  if [[ -z "$selected" ]]; then
    echo "Failed to parse selected issue number from next-issue output." >&2
    return 1
  fi

  printf '%s' "$selected"
}

run_work_issue() {
  local issue="$1"
  local cmd=(./scripts/work-issue.py --issue "$issue")
  if [[ "$NO_SPLIT_ISSUES" != "1" ]]; then
    cmd+=(--create-split-issues)
  fi

  if [[ "$DRY_RUN" == "1" ]]; then
    echo "[dry-run] Would run: ${cmd[*]}"
    return 0
  fi

  set +e
  "${cmd[@]}"
  local rc=$?
  set -e
  return "$rc"
}

run_prmerge() {
  local issue="$1"
  if [[ "$DRY_RUN" == "1" ]]; then
    echo "[dry-run] Would run: ./scripts/prmerge $issue"
    return 0
  fi
  ./scripts/prmerge "$issue"
}

cleanup_issue_tmp() {
  local issue="$1"
  if [[ "$DRY_RUN" == "1" ]]; then
    echo "[dry-run] Would run: rm -f .tmp/pr-body-$issue.md .tmp/issue-$issue-*.md"
    echo "[dry-run] Would run: ls -la .tmp/*$issue* 2>/dev/null || echo \"✓ Cleanup verified\""
    return 0
  fi

  rm -f ".tmp/pr-body-${issue}.md" .tmp/issue-"${issue}"-*.md
  ls -la .tmp/*"${issue}"* 2>/dev/null || echo "✓ Cleanup verified"
}

count=0
while [[ "$count" -lt "$MAX_ISSUES" ]]; do
  issue=""
  if [[ -n "$ISSUE_OVERRIDE" ]]; then
    issue="$ISSUE_OVERRIDE"
    ISSUE_OVERRIDE=""
  else
    echo "Selecting next issue..."
    if [[ "$DRY_RUN" == "1" ]]; then
      select_next_issue
      issue="99999"
    else
      selection_output="$(select_next_issue)"
      issue="$(printf '%s\n' "$selection_output" | tail -n1)"
      printf '%s\n' "$selection_output" | sed '$d'
    fi
  fi

  if [[ -z "$issue" ]]; then
    echo "No issue selected; stopping loop."
    exit 1
  fi

  echo
  echo "========================================="
  echo "Loop item $((count + 1))/$MAX_ISSUES -> issue #$issue"
  echo "========================================="

  work_rc=0
  run_work_issue "$issue" || work_rc=$?

  if [[ "$work_rc" -eq 2 ]]; then
    echo "Issue #$issue triggered split-issues flow (exit=2). Skipping prmerge for parent issue."
    cleanup_issue_tmp "$issue"
    count=$((count + 1))
    continue
  fi

  if [[ "$work_rc" -ne 0 ]]; then
    echo "work-issue failed for #$issue (exit=$work_rc); stopping loop."
    exit "$work_rc"
  fi

  run_prmerge "$issue"
  cleanup_issue_tmp "$issue"

  count=$((count + 1))
done

echo "Loop complete: processed $count issue(s)."
