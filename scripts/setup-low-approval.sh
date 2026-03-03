#!/bin/bash
# Configure VS Code command approval profiles in this workspace.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

mkdir -p "$ROOT_DIR/.tmp"

PROFILE="${1:-low-friction}"

if [[ "$PROFILE" == "--low-friction" || "$PROFILE" == "low-friction" ]]; then
	python3 "$SCRIPT_DIR/setup-vscode-autoapprove.py" --workspace-only --profile low-friction
	echo ""
	echo "✅ Low-approval HIGH-TRUST mode configured for workspace + client workspace."
	echo "⚠️  Risks: ultra-broad command approvals can hide dangerous commands."
else
	python3 "$SCRIPT_DIR/setup-vscode-autoapprove.py" --workspace-only --profile safe
	echo ""
	echo "✅ Safe approval profile configured for workspace + client workspace."
	echo "💡 To opt in to high-trust mode: $0 low-friction"
fi

echo ""
echo "📝 Reload VS Code: Ctrl+Shift+P -> Developer: Reload Window"
