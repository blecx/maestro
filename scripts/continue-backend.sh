#!/usr/bin/env bash
set -euo pipefail

MAX_ISSUES=25
ISSUE_OVERRIDE=""
DRY_RUN=0
NO_PUBLISH=0
MAX_ISSUES_CAP=25

ROADMAP_PATHS=("planning/issues/step-4.yml")
ISSUE_LABEL="step:4"
BACKEND_REPO="blecx/AI-Agent-Framework"

export WORK_ISSUE_COMPACT="${WORK_ISSUE_COMPACT:-1}"
export WORK_ISSUE_MAX_PROMPT_CHARS="${WORK_ISSUE_MAX_PROMPT_CHARS:-1800}"
export LLM_CONFIG_PATH="${LLM_CONFIG_PATH:-configs/llm.workflow.json}"

# Throttling knobs (reduce GitHub Models request bursts).
export MODEL_RESOLVE_TTL_SECONDS="${MODEL_RESOLVE_TTL_SECONDS:-1800}"
export WORK_ISSUE_RATE_LIMIT_RETRIES="${WORK_ISSUE_RATE_LIMIT_RETRIES:-${WORK_ISSUE_RATE_LIMIT_ATTEMPTS:-4}}"
export WORK_ISSUE_RATE_LIMIT_DELAY="${WORK_ISSUE_RATE_LIMIT_DELAY:-${WORK_ISSUE_RATE_LIMIT_DELAY_SECONDS:-120}}"

# GitHub API pacing (gh CLI). Default is conservative to avoid secondary rate limits.
export GH_MIN_INTERVAL_SECONDS="${GH_MIN_INTERVAL_SECONDS:-3}"

__GH_LAST_CALL_TS=""
gh_slow() {
  local min_interval
  min_interval="${GH_MIN_INTERVAL_SECONDS:-0}"
  if [[ -n "${__GH_LAST_CALL_TS}" && "${min_interval}" != "0" ]]; then
    local now
    now="$(date +%s)"
    local elapsed
    elapsed=$((now - __GH_LAST_CALL_TS))
    if [[ "$elapsed" -lt "$min_interval" ]]; then
      sleep "$((min_interval - elapsed))"
    fi
  fi
  __GH_LAST_CALL_TS="$(date +%s)"
  command gh "$@"
}

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  cat <<'EOF'
Usage: ./scripts/continue-backend.sh [options]

Runs the backend-first roadmap loop:
  publish roadmap backend issues -> select scoped backend issue -> work-issue -> prmerge

Options:
  --issue <n>              Run a single explicit backend issue.
  --paths <glob> [...]     Roadmap spec paths (default: planning/issues/step-4.yml).
  --label <name>           Label used for scoped selection (default: step:4).
  --max-issues <n>         Stop after n issues (default: 25).
  --dry-run                Select and print actions, do not execute work/merge/publish.
  --no-publish             Do not auto-publish roadmap issues.
  -h, --help               Show this help.

Notes:
  - This command is backend-only and intended for roadmap-scoped issues.
  - Client work stays in its own loop.
EOF
}

ensure_roadmap_specs_present() {
  local p
  for p in "${ROADMAP_PATHS[@]}"; do
    if [[ "$p" == "planning/issues/step-4.yml" && ! -f "$p" ]]; then
      echo "Roadmap spec missing: $p; generating deterministically..."
      if [[ "$DRY_RUN" == "1" ]]; then
        echo "[dry-run] Would run: ./.venv/bin/python scripts/generate_step_4_roadmap.py --out $p"
      else
        ./.venv/bin/python scripts/generate_step_4_roadmap.py --out "$p"
      fi
    fi
  done
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
    --paths)
      ROADMAP_PATHS=()
      shift
      while [[ $# -gt 0 && ! "$1" =~ ^-- ]]; do
        ROADMAP_PATHS+=("$1")
        shift
      done
      if [[ ${#ROADMAP_PATHS[@]} -eq 0 ]]; then
        echo "--paths requires at least one glob" >&2
        exit 1
      fi
      ;;
    --label)
      require_option_value "--label" "${2:-}"
      ISSUE_LABEL="$2"
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

if [[ -n "$ISSUE_OVERRIDE" ]] && ! is_valid_issue_number "$ISSUE_OVERRIDE"; then
  echo "Invalid --issue value: $ISSUE_OVERRIDE" >&2
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

publish_backend_roadmap_issues() {
  if [[ "$NO_PUBLISH" == "1" ]]; then
    return 0
  fi

  ensure_backend_labels

  local cmd=(./.venv/bin/python scripts/publish_issues.py --repo "$BACKEND_REPO" --apply --paths)
  local p
  for p in "${ROADMAP_PATHS[@]}"; do
    cmd+=("$p")
  done

  if [[ "$DRY_RUN" == "1" ]]; then
    echo "[dry-run] Would run: ${cmd[*]}"
    return 0
  fi

  echo "Publishing backend roadmap issue specs (idempotent map/create)..."
  "${cmd[@]}"
}

ensure_backend_labels() {
  local labels
  labels="$(
    ./.venv/bin/python - "${ROADMAP_PATHS[@]}" <<'PY'
import sys
from pathlib import Path
import yaml

paths = [Path(p) for p in sys.argv[1:]]
labels = set()
for path in paths:
    if not path.exists():
        continue
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        continue
    entries = data.get("AI-Agent-Framework")
    if not isinstance(entries, list):
        continue
    for item in entries:
        if not isinstance(item, dict):
            continue
        for label in item.get("labels", []) or []:
            label_text = str(label).strip()
            if label_text:
                labels.add(label_text)

for label in sorted(labels):
    print(label)
PY
  )"

  if [[ -z "$labels" ]]; then
    return 0
  fi

  local existing
  existing="$(GH_PAGER=cat gh_slow label list --repo "$BACKEND_REPO" --limit 1000 --json name --jq '.[].name')"

  while IFS= read -r label; do
    [[ -z "$label" ]] && continue
    if ! grep -Fxq "$label" <<<"$existing"; then
      if [[ "$DRY_RUN" == "1" ]]; then
        echo "[dry-run] Would create label in $BACKEND_REPO: $label"
      else
        GH_PAGER=cat gh_slow label create "$label" --repo "$BACKEND_REPO" --color BFD4F2 --description "Roadmap scoped label" >/dev/null
        echo "Created missing backend label: $label"
      fi
    fi
  done <<<"$labels"
}

resolve_backend_models() {
  local cache_path
  cache_path=".tmp/llm.workflow.resolved.json"

  if [[ -f "$cache_path" && "${MODEL_RESOLVE_TTL_SECONDS:-0}" -gt 0 ]]; then
    local is_fresh
    is_fresh="$(./.venv/bin/python - <<'PY'
import os
import time
from pathlib import Path

ttl = int(os.environ.get("MODEL_RESOLVE_TTL_SECONDS", "0") or "0")
path = Path(".tmp/llm.workflow.resolved.json")
if ttl <= 0 or not path.exists():
    print("0")
else:
    age = time.time() - path.stat().st_mtime
    print("1" if age < ttl else "0")
PY
)"

    if [[ "$is_fresh" == "1" ]]; then
      export LLM_CONFIG_PATH="$cache_path"

      local planning_model
      local coding_model
      planning_model="$(./.venv/bin/python - <<'PY'
import json
from pathlib import Path
cfg = json.loads(Path(".tmp/llm.workflow.resolved.json").read_text(encoding="utf-8"))
print(cfg["roles"]["planning"]["model"])
PY
)"
      coding_model="$(./.venv/bin/python - <<'PY'
import json
from pathlib import Path
cfg = json.loads(Path(".tmp/llm.workflow.resolved.json").read_text(encoding="utf-8"))
print(cfg["roles"]["coding"]["model"])
PY
)"

      if [[ "$planning_model" != openai/gpt-5* ]]; then
        echo "⚠️  GPT-5 planning models unavailable on endpoint; using cached fallback planning model: $planning_model"
      fi
      echo "Model policy (cached): planning=$planning_model coding=$coding_model"
      return 0
    fi
  fi

  local resolved
  resolved="$(./.venv/bin/python - <<'PY'
import json
from pathlib import Path
from openai import OpenAI
from agents.llm_client import LLMClientFactory

api_key = LLMClientFactory.resolve_github_api_key("")
if not api_key:
    raise SystemExit("missing_api_key")

client = OpenAI(base_url="https://models.github.ai/inference", api_key=api_key)

planning_candidates = [
    "openai/gpt-5.2",
  "openai/gpt-5.2-codex",
    "openai/gpt-5.1-codex",
    "openai/gpt-4.1",
]
execution_candidates = [
  "openai/gpt-4o",
  "openai/gpt-4.1",
  "openai/gpt-4o-mini",
]

def first_available(candidates):
    rate_limited = False
    for model in candidates:
        try:
            client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "ok"}],
                max_tokens=1,
            )
            return model, rate_limited
        except Exception as exc:
            msg = str(exc).lower()
            if "too many requests" in msg or "ratelimit" in msg or "429" in msg:
                rate_limited = True
            continue
    return "", rate_limited

planning_model, planning_rl = first_available(planning_candidates)
coding_model, coding_rl = first_available(execution_candidates)

if not planning_model and planning_rl:
    planning_model = "openai/gpt-4.1"
if not coding_model and coding_rl:
    coding_model = "openai/gpt-4o"

if not planning_model:
    raise SystemExit("no_planning_model")
if not coding_model:
    raise SystemExit("no_execution_model")

base_cfg = LLMClientFactory.load_config()
cfg = {
    "timeout": int(base_cfg.get("timeout", 300)),
    "max_tokens": int(base_cfg.get("max_tokens", 8192)),
    "temperature": float(base_cfg.get("temperature", 0.2)),
    "api_key": base_cfg.get("api_key", "your-api-key-here"),
    "roles": {
        "planning": {
            "provider": "github",
            "base_url": "https://models.github.ai/inference",
            "api_key": base_cfg.get("api_key", "your-api-key-here"),
            "model": planning_model,
        },
        "coding": {
            "provider": "github",
            "base_url": "https://models.github.ai/inference",
            "api_key": base_cfg.get("api_key", "your-api-key-here"),
            "model": coding_model,
        },
        "review": {
            "provider": "github",
            "base_url": "https://models.github.ai/inference",
            "api_key": base_cfg.get("api_key", "your-api-key-here"),
            "model": coding_model,
        },
    },
}

tmp = Path(".tmp")
tmp.mkdir(parents=True, exist_ok=True)
out = tmp / "llm.workflow.resolved.json"
out.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")

print(json.dumps({"planning": planning_model, "coding": coding_model, "path": str(out)}))
PY
)"

  local planning_model
  local coding_model
  local resolved_path
  planning_model="$(echo "$resolved" | ./.venv/bin/python -c 'import json,sys; print(json.load(sys.stdin)["planning"])')"
  coding_model="$(echo "$resolved" | ./.venv/bin/python -c 'import json,sys; print(json.load(sys.stdin)["coding"])')"
  resolved_path="$(echo "$resolved" | ./.venv/bin/python -c 'import json,sys; print(json.load(sys.stdin)["path"])')"

  export LLM_CONFIG_PATH="$resolved_path"
  if [[ "$planning_model" != openai/gpt-5* ]]; then
    echo "⚠️  GPT-5 planning models unavailable on endpoint; using fallback planning model: $planning_model"
  fi
  echo "Model policy: planning=$planning_model coding=$coding_model"
}

validate_backend_issue_budget() {
  local cmd=(./.venv/bin/python scripts/check_issue_specs.py --no-legacy --strict-sections --max-body-chars 2600 --paths)
  local p
  for p in "${ROADMAP_PATHS[@]}"; do
    cmd+=("$p")
  done

  if [[ "$DRY_RUN" == "1" ]]; then
    echo "[dry-run] Would run: ${cmd[*]}"
    return 0
  fi

  "${cmd[@]}"
}

select_next_backend_issue() {
  local args=(
    issue list
    --repo "$BACKEND_REPO"
    --state open
    --limit 200
    --json number
    --jq 'sort_by(.number) | .[0].number // empty'
  )

  if [[ -n "$ISSUE_LABEL" ]]; then
    args=(
      issue list
      --repo "$BACKEND_REPO"
      --state open
      --label "$ISSUE_LABEL"
      --limit 200
      --json number
      --jq 'sort_by(.number) | .[0].number // empty'
    )
  fi

  GH_PAGER=cat gh_slow "${args[@]}"
}

run_work_issue_with_retry() {
  local issue="$1"
  local attempts="${WORK_ISSUE_RATE_LIMIT_RETRIES:-4}"
  local delay="${WORK_ISSUE_RATE_LIMIT_DELAY:-120}"
  local attempt=1

  while [[ "$attempt" -le "$attempts" ]]; do
    local log_file
    log_file=".tmp/work-issue-${issue}-attempt-${attempt}.log"

    set +e
    ./scripts/work-issue.py --issue "$issue" --create-split-issues 2>&1 | tee "$log_file"
    local rc=${PIPESTATUS[0]}
    set -e

    if [[ "$rc" -eq 2 ]]; then
      rm -f .tmp/work-issue-"$issue"-attempt-*.log || true
      echo "⏸️  Split issues created for #$issue. Pausing backend loop."
      return 2
    fi

    if [[ "$rc" -eq 0 ]]; then
      return 0
    fi

    if grep -qiE "Too many requests|RateLimit|429" "$log_file"; then
      if [[ "$attempt" -lt "$attempts" ]]; then
        echo "⚠️  Rate limit hit for issue #$issue (attempt $attempt/$attempts). Retrying in ${delay}s..."
        sleep "$delay"
        delay=$((delay * 2))
        attempt=$((attempt + 1))
        continue
      fi
    fi

    return "$rc"
  done

  return 1
}

cd "$ROOT_DIR"

ensure_roadmap_specs_present
resolve_backend_models
validate_backend_issue_budget

count=0
while true; do
  issue=""

  if [[ -n "$ISSUE_OVERRIDE" ]]; then
    issue="$ISSUE_OVERRIDE"
    ISSUE_OVERRIDE=""
  else
    publish_backend_roadmap_issues
    issue="$(select_next_backend_issue | tr -d '[:space:]' || true)"
  fi

  if [[ -z "$issue" ]]; then
    echo "No open scoped backend issues available; stopping backend loop."
    break
  fi

  if ! is_valid_issue_number "$issue"; then
    echo "Resolved issue id is invalid: '$issue'" >&2
    exit 1
  fi

  echo "============================================================"
  echo "/continue-backend :: Processing Backend Issue #$issue"
  echo "============================================================"

  if [[ "$DRY_RUN" == "1" ]]; then
    echo "[dry-run] Would run: ./scripts/work-issue.py --issue $issue --create-split-issues"
    echo "[dry-run] Would run: PRMERGE_ASSUME_YES=1 ./scripts/prmerge $issue"
  else
    set +e
    run_work_issue_with_retry "$issue"
    work_rc=$?
    set -e

    if [[ "$work_rc" -eq 2 ]]; then
      echo "Split operation completed for #$issue; stopping loop for manual review of new child issues."
      break
    fi
    if [[ "$work_rc" -ne 0 ]]; then
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

echo "Backend loop finished. Processed issues: $count"
