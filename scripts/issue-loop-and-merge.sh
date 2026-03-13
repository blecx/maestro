#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v jq >/dev/null 2>&1; then
  echo "❌ jq is required for parsing next-pr JSON output."
  exit 1
fi

echo "🔁 Starting issue/PR merge loop..."
merged_count=0

while true; do
  pr_json="$(./scripts/next-pr.py --json)"

  candidate_count="$(jq -r '(.recommended // []) | length' <<<"$pr_json")"
  if [[ "$candidate_count" -eq 0 ]]; then
    candidate_count="$(jq -r '(.candidates // []) | length' <<<"$pr_json")"
  fi

  if [[ "$candidate_count" -eq 0 ]]; then
    echo "ℹ No PR candidates available."
    break
  fi

  pr_number="$({
    jq -r '(.recommended[0].number // empty)' <<<"$pr_json"
    jq -r '(.candidates[0].number // empty)' <<<"$pr_json"
  } | awk 'NF {print; exit}')"

  if [[ -z "$pr_number" ]]; then
    echo "❌ Could not determine PR number from next-pr output:"
    echo "$pr_json"
    exit 2
  fi

  echo "🚀 Merging PR #$pr_number ..."
  scripts/prmerge --pr "$pr_number"
  merged_count=$((merged_count + 1))
done

echo "🧹 Cleaning temporary issue/PR artifacts..."
rm -f .tmp/pr-body-*.md .tmp/issue-*-*.md

if ls -la .tmp/pr-body-*.md .tmp/issue-*-*.md >/dev/null 2>&1; then
  echo "⚠ Some temp files still remain in .tmp"
else
  echo "✅ Cleanup verified"
fi

echo "✅ Loop complete. Merged PR runs: $merged_count"
