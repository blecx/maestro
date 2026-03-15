from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED = [
    ROOT / "README.md",
    ROOT / ".env.example",
    ROOT / ".vscode" / "settings.json",
    ROOT / ".vscode" / "tasks.json",
    ROOT / ".vscode" / "extensions.json",
    ROOT / "scripts" / "bootstrap_host.py",
    ROOT / "scripts" / "project_runtime_env.py",
    ROOT / "scripts" / "project_runtime_up.py",
    ROOT / "scripts" / "project_runtime_down.py",
    ROOT / "scripts" / "project_runtime_validate.py",
    ROOT / "manifests" / "extraction-manifest.json",
    ROOT / "manifests" / "upgrade-rules.json",
    ROOT / ".github" / "workflows" / "ci.yml",
    ROOT / ".github" / "ISSUE_TEMPLATE" / "feature_request.yml",
    ROOT / ".github" / "pull_request_template.md",
]


def test_required_files_exist() -> None:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED if not path.exists()]
    assert not missing, f"Missing required files: {missing}"
