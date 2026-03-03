#!/usr/bin/env bash
set -euo pipefail

MAX_ISSUES=25
ISSUE_OVERRIDE=""
DRY_RUN=0
MAX_ISSUES_CAP=25
NO_PUBLISH=0

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

mkdir -p "$ROOT_DIR/.tmp"
exec 9>"$ROOT_DIR/.tmp/continue-phase-3.lock"
if ! flock -n 9; then
  echo "Another continue-phase-3 loop is already running; stop it before starting a new one." >&2
  exit 3
fi
export WORK_ISSUE_COMPACT="${WORK_ISSUE_COMPACT:-1}"
export WORK_ISSUE_MAX_PROMPT_CHARS="${WORK_ISSUE_MAX_PROMPT_CHARS:-3200}"
export PYTHONUNBUFFERED="${PYTHONUNBUFFERED:-1}"
export LLM_CONFIG_PATH="${LLM_CONFIG_PATH:-configs/llm.workflow.json}"

# LLM-friendly defaults (GitHub Models can rate-limit aggressively; keep retries gentle).
export WORK_ISSUE_LLM_MAX_ATTEMPTS="${WORK_ISSUE_LLM_MAX_ATTEMPTS:-10}"
export WORK_ISSUE_LLM_BACKOFF_SECONDS="${WORK_ISSUE_LLM_BACKOFF_SECONDS:-60}"
export WORK_ISSUE_LLM_MAX_BACKOFF_SECONDS="${WORK_ISSUE_LLM_MAX_BACKOFF_SECONDS:-900}"
export WORK_ISSUE_LLM_BACKOFF_JITTER="${WORK_ISSUE_LLM_BACKOFF_JITTER:-0.20}"
export WORK_ISSUE_PLANNING_FALLBACK_MODEL="${WORK_ISSUE_PLANNING_FALLBACK_MODEL:-openai/gpt-4o-mini}"
export WORK_ISSUE_PLANNING_FALLBACK_AFTER_ATTEMPT="${WORK_ISSUE_PLANNING_FALLBACK_AFTER_ATTEMPT:-3}"
export WORK_ISSUE_PLANNING_FALLBACK_MAX_ATTEMPTS="${WORK_ISSUE_PLANNING_FALLBACK_MAX_ATTEMPTS:-6}"
export WORK_ISSUE_PLANNING_FALLBACK_PROMPT_CHARS="${WORK_ISSUE_PLANNING_FALLBACK_PROMPT_CHARS:-1400}"

# GitHub Models can enforce burst/secondary throttles even at low average RPS.
# Default to a conservative outbound LLM pace for this long-running loop.
export WORK_ISSUE_MAX_RPS="${WORK_ISSUE_MAX_RPS:-0.10}"
export WORK_ISSUE_RPS_JITTER="${WORK_ISSUE_RPS_JITTER:-0.25}"

# API-friendly pacing for gh CLI calls in this script.
GH_MIN_INTERVAL_SECONDS="${GH_MIN_INTERVAL_SECONDS:-1}"
__GH_LAST_CALL_TS=""

gh() {
  local min_interval
  min_interval="${GH_MIN_INTERVAL_SECONDS:-0}"

  if [[ -n "${__GH_LAST_CALL_TS}" && "${min_interval}" != "0" ]]; then
    local now elapsed
    now="$(date +%s)"
    elapsed="$(( now - __GH_LAST_CALL_TS ))"
    if [[ "$elapsed" -lt "$min_interval" ]]; then
      sleep "$(( min_interval - elapsed ))"
    fi
  fi

  command gh "$@"
  __GH_LAST_CALL_TS="$(date +%s)"
}

usage() {
  cat <<'EOF'
Usage: ./scripts/continue-phase-3.sh [options]

Runs the /continue-phase-3 loop (backend-first):
  publish step-3 backend issues -> select next open step:3 backend issue -> work-issue -> prmerge

Options:
  --issue <n>           Run a single explicit backend issue.
  --max-issues <n>      Stop after n issues (default: 25).
  --dry-run             Select and print actions, do not execute work/merge/publish.
  --no-publish          Do not auto-publish step-3 backend issues.
  -h, --help            Show this help.

Notes:
  - This loop is backend-first by design and uses `scripts/work-issue.py` + `scripts/prmerge`.
  - Client step-3 issues are intentionally not auto-processed by this script.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --issue)
      ISSUE_OVERRIDE="${2:-}"
      shift 2
      ;;
    --max-issues)
      MAX_ISSUES="${2:-0}"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --no-publish)
      NO_PUBLISH=1
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

if [[ "$MAX_ISSUES" -lt "$MAX_ISSUES_CAP" ]]; then
  echo "--max-issues values below $MAX_ISSUES_CAP are forbidden." >&2
  echo "Use --max-issues $MAX_ISSUES_CAP (default), or set a value above it and confirm override." >&2
  exit 1
fi

if [[ "$MAX_ISSUES" -gt "$MAX_ISSUES_CAP" ]]; then
  echo "Requested --max-issues=$MAX_ISSUES exceeds hard baseline ($MAX_ISSUES_CAP)."
  if [[ "${CONTINUE_PHASE_ASSUME_YES:-}" == "1" ]]; then
    echo "CONTINUE_PHASE_ASSUME_YES=1: overriding baseline without prompt."
  elif [[ -t 0 ]]; then
    read -r -p "Override baseline and continue with $MAX_ISSUES issues? (y/N): " override_cap
    if [[ ! "$override_cap" =~ ^[Yy]$ ]]; then
      echo "Cancelled. Re-run with --max-issues $MAX_ISSUES_CAP or confirm override."
      exit 1
    fi
  else
    echo "Non-interactive stdin; cannot prompt for override confirmation." >&2
    echo "Re-run with --max-issues $MAX_ISSUES_CAP, or set CONTINUE_PHASE_ASSUME_YES=1 to override." >&2
    exit 1
  fi
fi

publish_step3_backend_issues() {
  if [[ "$NO_PUBLISH" == "1" ]]; then
    return 0
  fi

  local cmd=(
    ./.venv/bin/python
    scripts/publish_issues.py
    --paths planning/issues/step-3.yml
    --repo blecx/AI-Agent-Framework
    --apply
  )

  if [[ "$DRY_RUN" == "1" ]]; then
    echo "[dry-run] Would run: ${cmd[*]}"
    return 0
  fi

  echo "Publishing Step-3 backend issue specs (idempotent map/create)..."
  "${cmd[@]}"
}

select_next_step3_backend_issue() {
  GH_PAGER=cat gh issue list \
    --repo blecx/AI-Agent-Framework \
    --state open \
    --label step:3 \
    --search "-label:\"status:blocked\"" \
    --limit 200 \
    --json number \
    --jq 'sort_by(.number) | .[0].number // empty'
}

label_split_children_step3() {
  local parent_issue
  parent_issue="$1"

  # Search for split children created by work-issue.py:
  # titles like: split(#<parent>): slice N - ...
  local search_query
  search_query="\"split(#${parent_issue}):\" in:title"

  local children
  children="$(GH_PAGER=cat gh issue list \
    --repo blecx/AI-Agent-Framework \
    --state open \
    --search "$search_query" \
    --limit 50 \
    --json number \
    --jq '.[].number' || true)"

  if [[ -z "$children" ]]; then
    echo "⚠ No split child issues found for #$parent_issue to label step:3."
    return 0
  fi

  echo "Labeling split child issues with step:3 (parent #$parent_issue)..."
  while IFS= read -r child; do
    [[ -z "$child" ]] && continue
    GH_PAGER=cat gh issue edit "$child" \
      --repo blecx/AI-Agent-Framework \
      --add-label step:3 >/dev/null
    echo "  - Labeled #$child (step:3)"
  done <<<"$children"
}

cd "$ROOT_DIR"

# Ensure .tmp exists for logs/locks.
mkdir -p .tmp

# Prevent multiple concurrent loops (avoids amplifying rate limits).
LOCK_DIR=".tmp/continue-phase-3.lockdir"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "❌ Another continue-phase-3 loop appears to be running (lock: $LOCK_DIR)."
  echo "   If this is stale, remove it: rm -rf $LOCK_DIR"
  exit 1
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

# Always log to a timestamped file.
LOG_FILE=".tmp/continue-phase-3-$(date -u +%Y%m%dT%H%M%SZ).log"
echo "📝 Logging to: $LOG_FILE"
exec > >(tee -a "$LOG_FILE") 2>&1

count=0
last_issue=""

while true; do
  issue=""

  if [[ -n "$ISSUE_OVERRIDE" ]]; then
    issue="$ISSUE_OVERRIDE"
    ISSUE_OVERRIDE=""
  else
    publish_step3_backend_issues
    issue="$(select_next_step3_backend_issue || true)"
  fi

  if [[ -z "$issue" ]]; then
    echo "No open backend step:3 issues available; stopping phase-3 loop."
    break
  fi

  if [[ "$DRY_RUN" == "1" && "$issue" == "$last_issue" ]]; then
    echo "Dry-run selected the same issue (#$issue) again; stopping to avoid duplicate preview output."
    break
  fi
  last_issue="$issue"

  echo "============================================================"
  echo "/continue-phase-3 :: Processing Backend Issue #$issue"
  echo "============================================================"

  if [[ "$DRY_RUN" == "1" ]]; then
    echo "[dry-run] Would run: ./scripts/work-issue.py --issue $issue"
    echo "[dry-run] Would run: PRMERGE_ASSUME_YES=1 ./scripts/prmerge $issue"
  else
    set +e
    ./scripts/work-issue.py --issue "$issue" --create-split-issues
    work_rc=$?
    set -e

    if [[ "$work_rc" -eq 2 ]]; then
      echo "✅ Planning guardrail split handled for #$issue."
      label_split_children_step3 "$issue"
      GH_PAGER=cat gh issue edit "$issue" \
        --repo blecx/AI-Agent-Framework \
        --remove-label step:3 >/dev/null || true
      echo "  - Removed step:3 from parent #$issue (will not be re-selected)."
      # Do not prmerge a split-only parent; continue to next issue.
      count=$((count + 1))
      continue
    fi

    if [[ "$work_rc" -ne 0 ]]; then
      echo "❌ work-issue failed for #$issue (exit=$work_rc); stopping phase-3 loop."
      exit "$work_rc"
    fi

    PRMERGE_ASSUME_YES=1 ./scripts/prmerge "$issue"
  fi

  count=$((count + 1))
  if [[ "$count" -ge "$MAX_ISSUES" ]]; then
    echo "Reached --max-issues=$MAX_ISSUES; stopping."
    if [[ "$MAX_ISSUES" -eq "$MAX_ISSUES_CAP" ]]; then
      echo "If more backend issues remain, re-run with --max-issues > $MAX_ISSUES_CAP and confirm override."
    fi
    break
  fi
done

echo "Phase-3 loop finished. Processed issues: $count"
