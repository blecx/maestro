import json
from pathlib import Path

def test_extensions_matrix_parity():
    """Ensure that .vscode/extensions.json follows the mandated factory structure."""
    ext_file = Path(".vscode/extensions.json")
    if not ext_file.exists():
        return # Skip if not present in this checkout, although it should be
        
    content = json.loads(ext_file.read_text(encoding="utf-8"))
    
    recommendations = content.get("recommendations", [])
    unwanted = content.get("unwantedRecommendations", [])
    
    # Hard-required and recommended
    expected_recommendations = [
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
    
    for req in expected_recommendations:
        assert req in recommendations, f"Missing required extension recommendation: {req}"
        
    # Maestro issueagent MUST be expelled
    assert "maestro.issueagent" not in recommendations, "maestro.issueagent must NOT be recommended in the standalone factory"
    assert "maestro.issueagent" in unwanted, "maestro.issueagent MUST be in unwantedRecommendations to neutralize blecx/maestro"
