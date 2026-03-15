import json
import subprocess
from pathlib import Path


def test_bootstrap_keeps_tooling_inside_hidden_tree(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-b", "main"], cwd=tmp_path, check=True, capture_output=True)
    factory_root = Path(__file__).resolve().parents[2]
    subprocess.run(["python3", str(factory_root / "scripts" / "bootstrap_host.py"), "--target", str(tmp_path), "--factory-root", str(factory_root)], check=True)
    assert (tmp_path / ".factory.lock.json").exists()
    lock = json.loads((tmp_path / ".factory.lock.json").read_text(encoding="utf-8"))
    assert lock["factoryRepo"] == "softwareFactoryVscode"
    assert lock["installPath"] == ".softwareFactoryVscode"
    assert not (tmp_path / ".vscode").exists()
