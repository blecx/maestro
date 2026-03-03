#!/usr/bin/env bash
# archive-goals.sh
# Archive "Goal" sections from markdown files in .tmp/ for AI-agent workflows.
#
# Usage:
#   bash scripts/archive-goals.sh
#   bash scripts/archive-goals.sh --move
#   bash scripts/archive-goals.sh --source .tmp --archive .tmp/archive

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="$REPO_ROOT/.tmp"
ARCHIVE_DIR="$REPO_ROOT/.tmp/archive"
MOVE_SOURCES=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --source)
      SOURCE_DIR="$REPO_ROOT/${2:-}"
      shift 2
      ;;
    --archive)
      ARCHIVE_DIR="$REPO_ROOT/${2:-}"
      shift 2
      ;;
    --move)
      MOVE_SOURCES=true
      shift
      ;;
    -h|--help)
      cat <<'EOF'
Archive "Goal" sections from .tmp markdown files.

Options:
  --source <path>   Source directory (default: .tmp)
  --archive <path>  Archive directory (default: .tmp/archive)
  --move            Move source files into archive snapshot after extraction
  -h, --help        Show help
EOF
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

if [[ ! -d "$SOURCE_DIR" ]]; then
  echo "Source directory not found: $SOURCE_DIR" >&2
  exit 1
fi

mkdir -p "$ARCHIVE_DIR"

TIMESTAMP="$(date -u +%Y%m%dT%H%M%S-%NZ)"
ARCHIVE_FILE="$ARCHIVE_DIR/goals-$TIMESTAMP.md"
MANIFEST_FILE="$ARCHIVE_DIR/goals-$TIMESTAMP.json"
SNAPSHOT_DIR="$ARCHIVE_DIR/snapshots/$TIMESTAMP"
mkdir -p "$SNAPSHOT_DIR"

# Match headings like:
#   ## Goal / Context
#   ## Goal / Problem Statement
#   ## Goal / Acceptance Criteria
GOAL_HEADING_REGEX='^##[[:space:]]+Goal([[:space:]]*/.*)?$'

files_scanned=0
files_with_goal=0

{
  echo "# Goal Archive"
  echo
  echo "- generated_at_utc: $TIMESTAMP"
  echo "- source_dir: $SOURCE_DIR"
  echo
} > "$ARCHIVE_FILE"

# shellcheck disable=SC2207
mapfile -t md_files < <(find "$SOURCE_DIR" -maxdepth 1 -type f -name '*.md' | sort)

if [[ ${#md_files[@]} -eq 0 ]]; then
  echo "No markdown files found in $SOURCE_DIR"
fi

for file in "${md_files[@]}"; do
  files_scanned=$((files_scanned + 1))

  # Extract one or more Goal sections; stop each section at next '## ' heading.
  extracted="$(awk -v re="$GOAL_HEADING_REGEX" '
    BEGIN { in_goal = 0; found = 0 }
    {
      if ($0 ~ re) {
        in_goal = 1
        found = 1
        print $0
        next
      }
      if (in_goal && $0 ~ /^##[[:space:]]+/) {
        in_goal = 0
      }
      if (in_goal) {
        print $0
      }
    }
    END {
      if (!found) {
        # print nothing
      }
    }
  ' "$file")"

  if [[ -n "$extracted" ]]; then
    files_with_goal=$((files_with_goal + 1))
    base="$(basename "$file")"

    {
      echo "## Source: $base"
      echo
      echo "$extracted"
      echo
      echo "---"
      echo
    } >> "$ARCHIVE_FILE"

    cp "$file" "$SNAPSHOT_DIR/$base"
  fi
done

if $MOVE_SOURCES; then
  for f in "$SNAPSHOT_DIR"/*.md; do
    [[ -e "$f" ]] || continue
    src_name="$(basename "$f")"
    if [[ -f "$SOURCE_DIR/$src_name" ]]; then
      mv "$SOURCE_DIR/$src_name" "$SNAPSHOT_DIR/$src_name"
    fi
  done
fi

cat > "$MANIFEST_FILE" <<EOF
{
  "generated_at_utc": "$TIMESTAMP",
  "source_dir": "${SOURCE_DIR#"$REPO_ROOT"/}",
  "archive_file": "${ARCHIVE_FILE#"$REPO_ROOT"/}",
  "snapshot_dir": "${SNAPSHOT_DIR#"$REPO_ROOT"/}",
  "files_scanned": $files_scanned,
  "files_with_goal": $files_with_goal,
  "move_sources": $MOVE_SOURCES
}
EOF

echo "Archived goals complete."
echo "  Markdown archive: ${ARCHIVE_FILE#"$REPO_ROOT"/}"
echo "  Manifest:         ${MANIFEST_FILE#"$REPO_ROOT"/}"
echo "  Snapshot dir:     ${SNAPSHOT_DIR#"$REPO_ROOT"/}"
echo "  Files scanned:    $files_scanned"
echo "  Files with goals: $files_with_goal"
