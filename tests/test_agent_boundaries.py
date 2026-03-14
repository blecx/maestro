import pytest
import os
from pathlib import Path

def test_no_meta_dir_access():
    """Ensure that code in agents/ does not reference .github/ or .copilot/"""
    agents_dir = Path("agents")
    violations = []
    
    for root, _, files in os.walk(agents_dir):
        for file in files:
            if not file.endswith(".py"):
                continue
            filepath = Path(root) / file
            if "__pycache__" in str(filepath):
                continue
                
            content = filepath.read_text(encoding="utf-8")
            if ".github/" in content or ".copilot/" in content:
                violations.append(str(filepath))
                
    assert not violations, f"Architectural violation: .github/ or .copilot/ referenced in {violations}"
