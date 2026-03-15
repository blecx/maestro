#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    settings = json.loads((ROOT / ".vscode" / "settings.json").read_text(encoding="utf-8"))
    tasks = json.loads((ROOT / ".vscode" / "tasks.json").read_text(encoding="utf-8"))
    extensions = json.loads((ROOT / ".vscode" / "extensions.json").read_text(encoding="utf-8"))

    required_settings = [
        "python.defaultInterpreterPath",
        "python.testing.pytestEnabled",
        "terminal.integrated.env.linux",
        "chat.tools.terminal.autoApprove",
        "chat.tools.subagent.autoApprove",
        "mcp",
    ]
    missing = [key for key in required_settings if key not in settings]
    if missing:
        raise SystemExit(f"Missing settings keys: {missing}")

    task_labels = {task.get("label") for task in tasks.get("tasks", [])}
    required_tasks = {
        "⚙️ Factory: Bootstrap Host",
        "🧬 Factory: Generate Runtime Env",
        "🚀 Factory: Runtime Up",
        "🛑 Factory: Runtime Down",
        "✅ Factory: Validate Runtime",
    }
    task_missing = sorted(required_tasks - task_labels)
    if task_missing:
        raise SystemExit(f"Missing task labels: {task_missing}")

    recommendations = set(extensions.get("recommendations", []))
    for ext in ["GitHub.copilot", "GitHub.copilot-chat", "ms-python.python", "ms-python.vscode-pylance"]:
        if ext not in recommendations:
            raise SystemExit(f"Missing required extension recommendation: {ext}")
    unwanted = set(extensions.get("unwantedRecommendations", []))
    if any(item.startswith("maestro.") for item in unwanted):
        raise SystemExit("Legacy maestro-branded extensions must not be projected into the package workspace")

    print("VS Code workspace check passed")


if __name__ == "__main__":
    main()
