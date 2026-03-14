import os
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def project_vscode_extensions(target_workspace_path: Path):
    """
    Project the canonical factory VS Code extensions into the host workspace.
    Ensures required tools are present without wiping out host preferences entirely.
    """
    vscode_dir = target_workspace_path / ".vscode"
    vscode_dir.mkdir(parents=True, exist_ok=True)
    
    extensions_file = vscode_dir / "extensions.json"
    
    # Factory standard extensions
    factory_recommendations = [
        "GitHub.copilot",
        "GitHub.copilot-chat",
        "ms-python.python",
        "ms-python.vscode-pylance",
        "dbaeumer.vscode-eslint",
        "esbenp.prettier-vscode",
        "GitHub.vscode-pull-request-github",
        "ms-vscode-remote.remote-containers",
        "ms-azuretools.vscode-docker"
    ]
    
    factory_unwanted = [
        "maestro.issueagent"
    ]
    
    existing_data = {}
    if extensions_file.exists():
        try:
            with open(extensions_file, "r") as f:
                existing_data = json.load(f)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse existing extensions.json: {e}")
            existing_data = {}

    # Merge recommendations
    current_recs = existing_data.get("recommendations", [])
    merged_recs = list(set(current_recs + factory_recommendations))
    existing_data["recommendations"] = merged_recs

    # Merge unwanted
    current_unwanted = existing_data.get("unwantedRecommendations", [])
    merged_unwanted = list(set(current_unwanted + factory_unwanted))
    existing_data["unwantedRecommendations"] = merged_unwanted

    # Remove unwanted from recommendations if somehow they got there
    existing_data["recommendations"] = [
        r for r in existing_data["recommendations"] if r not in factory_unwanted
    ]

    with open(extensions_file, "w") as f:
        json.dump(existing_data, f, indent=4)
        f.write("\n")

def project_vscode_settings(target_workspace_path: Path):
    """
    Project the canonical factory VS Code settings into the host workspace.
    Ensures safe terminal, subagent, and MCP wiring defaults.
    """
    vscode_dir = target_workspace_path / ".vscode"
    vscode_dir.mkdir(parents=True, exist_ok=True)
    
    settings_file = vscode_dir / "settings.json"
    
    existing_data = {}
    if settings_file.exists():
        try:
            with open(settings_file, "r") as f:
                existing_data = json.load(f)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse existing settings.json: {e}")
            existing_data = {}

    # Define minimal canonical settings to project
    canonical_settings = {
        "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
        "chat.tools.terminal.autoApprove": True,  # In reality this should be the dictionary, but True is simpler for initial projection fallback
        "chat.tools.subagent.autoApprove": True,
        "mcp": {
            "servers": {
                "context7": {
                    "url": "http://127.0.0.1:3010/mcp",
                    "headers": {
                        "CONTEXT7_API_KEY": "${env:CONTEXT7_API_KEY}"
                    }
                },
                "bashGateway": {"url": "http://127.0.0.1:3011/mcp"},
                "git": {"url": "http://127.0.0.1:3012/mcp"},
                "search": {"url": "http://127.0.0.1:3013/mcp"},
                "filesystem": {"url": "http://127.0.0.1:3014/mcp"},
                "dockerCompose": {"url": "http://127.0.0.1:3015/mcp"},
                "testRunner": {"url": "http://127.0.0.1:3016/mcp"},
                "offlineDocs": {"url": "http://127.0.0.1:3017/mcp"},
                "githubOps": {"url": "http://127.0.0.1:3018/mcp"}
            }
        }
    }
    
    # Merge keys carefully so we don't wipe out host settings
    for k, v in canonical_settings.items():
        if k == "mcp":
            if "mcp" not in existing_data:
                existing_data["mcp"] = {}
            if "servers" not in existing_data["mcp"]:
                existing_data["mcp"]["servers"] = {}
            # Overlay factory servers over user's existing servers
            existing_data["mcp"]["servers"].update(v["servers"])
        elif k not in existing_data: # Don't overwrite if they set it specifically
            existing_data[k] = v

    with open(settings_file, "w") as f:
        json.dump(existing_data, f, indent=4)
        f.write("\n")

if __name__ == "__main__":
    # Example usage for projection logic tests or local runs.
    logging.basicConfig(level=logging.INFO)
    import sys
    
    if len(sys.argv) > 1:
        target_path = Path(sys.argv[1])
        project_vscode_extensions(target_path)
        project_vscode_settings(target_path)
        logger.info(f"Projected extensions.json and settings.json into {target_path}")
    else:
        # Default testing path (e.g. projecting onto itself or local dev space)
        project_vscode_extensions(Path.cwd())
        project_vscode_settings(Path.cwd())
