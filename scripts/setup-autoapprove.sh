#!/bin/bash
# Quick wrapper to setup VS Code auto-approve settings

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔧 Setting up VS Code auto-approve for Copilot..."
echo ""

# Run the Python script
python3 "$SCRIPT_DIR/setup-vscode-autoapprove.py" "$@"

echo ""
echo "🎯 To apply changes immediately:"
echo "   1. Press Ctrl+Shift+P"
echo "   2. Type: Developer: Reload Window"
echo "   3. Press Enter"
echo ""
echo "💡 Or restart VS Code"
