#!/usr/bin/env bash
# check-maestro-drift.sh — Compare local .maestro-version SHA to blecx/maestro remote.
# Designed to run as a systemd service. Exits 0 cleanly when offline so the timer
# does not accumulate failures; Persistent=true on the timer ensures it retries.
set -euo pipefail

WORKSPACE="${MAESTRO_WORKSPACE:-$PWD}"
VERSION_FILE="${WORKSPACE}/.maestro-version"
MAESTRO_VERSION="${MAESTRO_VERSION:-main}"
GITHUB_ENDPOINT="https://github.com"
MAESTRO_REMOTE="https://github.com/blecx/maestro.git"

log() { echo "[check-maestro-drift] $*"; }

# ── Network check ─────────────────────────────────────────────────────────────
# Exit 0 (not a failure) when GitHub is unreachable; the timer will retry next
# time the systemd monotonic clock fires (Persistent=true covers resume-from-sleep).
if ! curl -sf --max-time 8 --head "$GITHUB_ENDPOINT" > /dev/null 2>&1; then
    log "No network access to GitHub — skipping drift check (will retry on next timer fire)."
    exit 0
fi

# ── Version file check ────────────────────────────────────────────────────────
if [ ! -f "$VERSION_FILE" ]; then
    log "WARNING: $VERSION_FILE not found. Run 'make sync-maestro' in $WORKSPACE."
    # Non-fatal: do not exit 1 here — user may not have run sync-maestro yet.
    exit 0
fi

LOCAL_SHA=$(cat "$VERSION_FILE")

# ── Remote SHA lookup ─────────────────────────────────────────────────────────
REMOTE_SHA=$(git ls-remote "$MAESTRO_REMOTE" "refs/heads/${MAESTRO_VERSION}" 2>/dev/null | awk '{print $1}')

if [ -z "$REMOTE_SHA" ]; then
    log "Could not resolve remote SHA for branch '${MAESTRO_VERSION}' — skipping."
    exit 0
fi

# ── Drift evaluation ──────────────────────────────────────────────────────────
if [ "$LOCAL_SHA" = "$REMOTE_SHA" ]; then
    log "✅ Maestro is current (SHA: ${LOCAL_SHA})"
    exit 0
fi

log "⚠️  Drift detected!"
log "  Workspace : $WORKSPACE"
log "  Branch    : $MAESTRO_VERSION"
log "  Local SHA : $LOCAL_SHA"
log "  Remote SHA: $REMOTE_SHA"
log "  Action    : cd $WORKSPACE && make sync-maestro"

# Desktop notification (best-effort — no failure if not available)
if command -v notify-send > /dev/null 2>&1; then
    notify-send --urgency=normal --app-name="Maestro" \
        "Maestro toolchain drift detected" \
        "Run 'make sync-maestro' in $(basename "$WORKSPACE")"
fi

# systemd journal entry
logger -t check-maestro-drift \
    "Drift: local=$LOCAL_SHA remote=$REMOTE_SHA branch=$MAESTRO_VERSION workspace=$WORKSPACE"

# Exit 1 so systemd records the unit as failed and shows it in status output.
# The timer itself is not affected — it will fire again next week.
exit 1
