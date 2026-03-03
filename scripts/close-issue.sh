#!/usr/bin/env bash
set -euo pipefail

# GitHub API pacing for gh CLI calls in this script.
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
  cat <<'USAGE'
close-issue.sh - Close a GitHub issue using a repo-managed message template.

Usage:
  ./scripts/close-issue.sh --issue <number> [--pr <number>] [--template <name>] [--merge-commit <sha>] [--data <json>] [--reason <completed|not_planned>] [--dry-run]

Options:
  --issue         Issue number to close (required)
  --pr            PR number that delivered the fix (optional, but recommended)
  --template      One of: generic, feature, bugfix, docs, infrastructure (default: generic)
  --merge-commit  Merge commit SHA (optional; auto-detected from PR if available)
  --data          Path to JSON file with additional template variables (optional)
  --reason        Close reason for GitHub (default: completed)
  --dry-run       Print the rendered message and exit without closing
  --allow-placeholders  Allow placeholder/default template text (not recommended)

Template variables:
  Templates live under scripts/templates/issue-close/*.md.j2.
  You can supply extra variables via --data.

Examples:
  # Print message only
  ./scripts/close-issue.sh --issue 42 --pr 43 --template infrastructure --dry-run

  # Close issue with a custom filled message
  mkdir -p .tmp
  cat > .tmp/close.json <<'JSON'
  {
    "summary": "- Added init-only dry-run and plan-only modes",
    "how_to_validate": "- ./scripts/work-issue.py --issue 42 --dry-run\n- ./scripts/work-issue.py --issue 42 --plan-only",
    "notes": "- Requires reachable LLM base_url for --plan-only"
  }
JSON
  ./scripts/close-issue.sh --issue 42 --pr 43 --template infrastructure --data .tmp/close.json
USAGE
}

issue=""
pr=""
template="generic"
merge_commit=""
data_json=""
reason="completed"
dry_run=0
allow_placeholders=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    --issue)
      issue="${2:-}"; shift 2
      ;;
    --pr)
      pr="${2:-}"; shift 2
      ;;
    --template)
      template="${2:-}"; shift 2
      ;;
    --merge-commit)
      merge_commit="${2:-}"; shift 2
      ;;
    --data)
      data_json="${2:-}"; shift 2
      ;;
    --reason)
      reason="${2:-}"; shift 2
      ;;
    --dry-run)
      dry_run=1; shift 1
      ;;
    --allow-placeholders)
      allow_placeholders=1; shift 1
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 2
      ;;
  esac
done

if [[ -z "$issue" ]]; then
  echo "--issue is required" >&2
  usage
  exit 2
fi

case "$template" in
  generic|feature|bugfix|docs|infrastructure) ;;
  *)
    echo "Invalid --template: $template" >&2
    exit 2
    ;;
esac

template_path="scripts/templates/issue-close/${template}.md.j2"
if [[ ! -f "$template_path" ]]; then
  echo "Template not found: $template_path" >&2
  exit 2
fi

if [[ -n "$data_json" && ! -f "$data_json" ]]; then
  echo "--data file not found: $data_json" >&2
  exit 2
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI is required (https://cli.github.com)" >&2
  exit 2
fi

# Prefer venv python when available
py="python3"
if [[ -x ".venv/bin/python" ]]; then
  py=".venv/bin/python"
fi

# Gather issue metadata
issue_json="$({
  gh issue view "$issue" --json number,title,url,state -q '{"issue_number":.number,"issue_title":.title,"issue_url":.url,"issue_state":.state}'
} 2>/dev/null || true)"

if [[ -z "$issue_json" ]]; then
  echo "Could not fetch issue #$issue (check repo/auth)." >&2
  exit 2
fi

pr_json="{}"
if [[ -n "$pr" ]]; then
  pr_json="$({
    gh pr view "$pr" --json number,title,url,state,mergedAt,mergeCommit -q '{"pr_number":.number,"pr_title":.title,"pr_url":.url,"pr_state":.state,"pr_merged_at":(.mergedAt // ""),"merge_commit":(.mergeCommit.oid // "")}'
  } 2>/dev/null || true)"
fi

# Render the message with Jinja2
mkdir -p .tmp
msg_file=".tmp/close-issue-${issue}-$$.md"
trap 'rm -f "$msg_file"' EXIT

"$py" - "$template_path" "$issue_json" "$pr_json" "$data_json" "$merge_commit" >"$msg_file" <<'PY'
import json
import sys
from pathlib import Path

from jinja2 import Environment

template_path = Path(sys.argv[1])
issue_json = sys.argv[2]
pr_json = sys.argv[3]
data_path = sys.argv[4]
merge_commit_override = sys.argv[5]

ctx = {}
ctx.update(json.loads(issue_json))
ctx.update(json.loads(pr_json))

# Allow explicit merge commit override
if merge_commit_override:
    ctx["merge_commit"] = merge_commit_override

# Merge additional template variables
if data_path:
    extra = json.loads(Path(data_path).read_text())
    if isinstance(extra, dict):
        ctx.update(extra)

env = Environment(autoescape=False)
tmpl = env.from_string(template_path.read_text())
out = tmpl.render(**ctx)

# Ensure trailing newline (GitHub comment readability)
print(out.rstrip() + "\n")
PY

if [[ "$allow_placeholders" -ne 1 ]]; then
  # Guardrail: prevent accidentally closing issues with placeholder/default template text.
  # This mirrors the repo's general quality bar (no placeholder evidence in PRs).
  placeholders=(
    "- (add summary of changes)"
    "- (add validation commands / steps)"
    "- (add any caveats, follow-ups, or next steps)"
    "- (describe what users can do now)"
    "- (paste checklist / key criteria and mark done)"
    "- (key files, main decisions, constraints)"
    "- (commands run / expected results)"
    "- (follow-ups, related issues, rollout notes)"
    "- (short description of the bug as reported)"
    "- (why it happened)"
    "- (what changed to resolve it)"
    "- (tests run / manual steps)"
    "- (prevention, monitoring, related cleanup)"
    "- (what was added/updated and where)"
    "- (list key docs/files)"
    "- (build/lint checks if relevant)"
    "- (anything reviewers/users should know)"
    "- (what infrastructure/tooling was added/changed)"
    "- (what this unblocks / improves)"
    "- (commands run / verification steps)"
    "- (rollout notes, next steps, related issues)"
  )

  found=0
  for needle in "${placeholders[@]}"; do
    if grep -qF -- "$needle" "$msg_file"; then
      if [[ "$found" -eq 0 ]]; then
        echo "ERROR: rendered close message still contains placeholder template text." >&2
        echo "Fill the template variables via --data (JSON) or override fields explicitly." >&2
        echo "If you really want to bypass this guard, pass --allow-placeholders." >&2
        echo >&2
        echo "Placeholders found:" >&2
      fi
      echo "- $needle" >&2
      found=1
    fi
  done

  if [[ "$found" -eq 1 ]]; then
    exit 2
  fi
fi

if [[ "$dry_run" -eq 1 ]]; then
  cat "$msg_file"
  exit 0
fi

# Close the issue with the rendered comment.
# Note: gh will refuse if you lack permissions.
gh issue close "$issue" --reason "$reason" -c "$(cat "$msg_file")"

echo "Closed issue #$issue using template '$template'."
