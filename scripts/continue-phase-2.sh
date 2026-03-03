#!/usr/bin/env bash
set -euo pipefail

MAX_ISSUES=25
ISSUE_OVERRIDE=""
DRY_RUN=0
NO_RECONCILE=0
MAX_ISSUES_CAP=25

# Token-budget safe defaults for model-constrained environments.
export WORK_ISSUE_COMPACT="${WORK_ISSUE_COMPACT:-1}"
export WORK_ISSUE_MAX_PROMPT_CHARS="${WORK_ISSUE_MAX_PROMPT_CHARS:-3200}"

usage() {
  cat <<'EOF'
Usage: ./scripts/continue-phase-2.sh [options]

Runs the /continue-phase-2 loop:
  next-issue -> work-issue -> prmerge

Options:
  --issue <n>           Run a single explicit issue.
  --max-issues <n>      Stop after n issues (default: 25).
  --dry-run             Select and print actions, do not execute work/merge.
  --no-reconcile        Pass --skip-reconcile to next-issue.
  -h, --help            Show this help.

Environment:
  PRMERGE_MAX_FILES, PRMERGE_MAX_LINES, PRMERGE_ALLOW_LARGE_SLICE,
  PRMERGE_ALLOW_UNAPPROVED
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
    --no-reconcile)
      NO_RECONCILE=1
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

if [[ "$MAX_ISSUES" -gt "$MAX_ISSUES_CAP" ]]; then
  echo "Requested --max-issues=$MAX_ISSUES exceeds default cap ($MAX_ISSUES_CAP)."
  if [[ "${CONTINUE_PHASE_ASSUME_YES:-}" == "1" ]]; then
    echo "CONTINUE_PHASE_ASSUME_YES=1: overriding baseline without prompt."
  elif [[ -t 0 ]]; then
    read -r -p "Override cap and continue? (y/N): " override_cap
    if [[ ! "$override_cap" =~ ^[Yy]$ ]]; then
      echo "Cancelled. Re-run with --max-issues <= $MAX_ISSUES_CAP or confirm override."
      exit 1
    fi
  else
    echo "Non-interactive stdin; cannot prompt for override confirmation." >&2
    echo "Re-run with --max-issues <= $MAX_ISSUES_CAP, or set CONTINUE_PHASE_ASSUME_YES=1 to override." >&2
    exit 1
  fi
fi

extract_issue_number() {
  local text="$1"
  local n
  n=$(echo "$text" | grep -oE 'Issue #[0-9]+' | head -1 | grep -oE '[0-9]+' || true)
  echo "$n"
}

count=0

while true; do
  if [[ -n "$ISSUE_OVERRIDE" ]]; then
    issue="$ISSUE_OVERRIDE"
    ISSUE_OVERRIDE=""
  else
    next_issue_cmd=("./next-issue")
    if [[ "$NO_RECONCILE" == "1" ]]; then
      next_issue_cmd+=("--skip-reconcile")
    fi

    set +e
    selection_output="$(${next_issue_cmd[@]} 2>&1)"
    selection_rc=$?
    set -e

    if [[ $selection_rc -ne 0 ]]; then
      echo "$selection_output"
      echo "No selectable issues or selection failed; stopping phase-2 loop."
      break
    fi

    issue=$(extract_issue_number "$selection_output")
    if [[ -z "$issue" ]]; then
      echo "$selection_output"
      echo "Could not parse issue number from next-issue output; stopping." >&2
      exit 2
    fi
  fi

  echo "============================================================"
  echo "/continue-phase-2 :: Processing Issue #$issue"
  echo "============================================================"

  if [[ "$DRY_RUN" == "1" ]]; then
    echo "[dry-run] Would run: ./scripts/work-issue.py --issue $issue"
    echo "[dry-run] Would run: PRMERGE_ASSUME_YES=1 ./scripts/prmerge $issue"
  else
    ./scripts/work-issue.py --issue "$issue"
    PRMERGE_ASSUME_YES=1 ./scripts/prmerge "$issue"
  fi

  count=$((count + 1))
  if [[ "$count" -ge "$MAX_ISSUES" ]]; then
    echo "Reached --max-issues=$MAX_ISSUES; stopping."
    break
  fi

done

echo "Phase-2 loop finished. Processed issues: $count"
