import subprocess
from pathlib import Path


def test_bootstrap_does_not_project_vscode_overrides(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-b", "main"], cwd=tmp_path, check=True, capture_output=True)
    factory_root = Path(__file__).resolve().parents[2]

    subprocess.run(
        [
            "python3",
            str(factory_root / "scripts" / "bootstrap_host.py"),
            "--target",
            str(tmp_path),
            "--factory-root",
            str(factory_root),
        ],
        check=True,
    )

    assert not (tmp_path / ".vscode").exists()
    assert not (tmp_path / ".factory.overrides").exists()
