import json
from pathlib import Path

def test_settings_matrix_parity():
    """Ensure that .vscode/settings.json contains the mandated factory structure defaults."""
    settings_file = Path(".vscode/settings.json")
    if not settings_file.exists():
        return # Skip if not present in this checkout
        
    content = json.loads(settings_file.read_text(encoding="utf-8"))
    
    # Check that tool policies are configured
    assert "chat.tools.terminal.autoApprove" in content, "chat.tools.terminal.autoApprove must be projected"
    assert "chat.tools.subagent.autoApprove" in content, "chat.tools.subagent.autoApprove must be projected"
    
    # Check MCP servers
    mcp_config = content.get("mcp", {}).get("servers", {})
    required_servers = ["context7", "bashGateway", "git", "search", "filesystem", "dockerCompose", "testRunner", "offlineDocs", "githubOps"]
    
    for server in required_servers:
        assert server in mcp_config, f"Missing MCP server projection for: {server}"
