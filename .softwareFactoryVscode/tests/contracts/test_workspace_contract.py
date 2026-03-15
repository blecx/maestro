import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_workspace_contract() -> None:
    settings = json.loads((ROOT / ".vscode" / "settings.json").read_text(encoding="utf-8"))
    assert settings["terminal.integrated.env.linux"]["TMPDIR"] == "${workspaceFolder}/.tmp"
    assert "mcp" in settings

    extensions = json.loads((ROOT / ".vscode" / "extensions.json").read_text(encoding="utf-8"))
    assert "GitHub.copilot" in extensions["recommendations"]
    assert not extensions.get("unwantedRecommendations")
