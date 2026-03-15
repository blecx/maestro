from pathlib import Path

from scripts._factorylib import build_runtime_env


def test_runtime_env_uses_canonical_keys(tmp_path: Path) -> None:
    runtime_env = build_runtime_env(tmp_path, tmp_path)
    for key in [
        "PROJECT_WORKSPACE_ID",
        "FACTORY_INSTANCE_ID",
        "COMPOSE_PROJECT_NAME",
        "TARGET_WORKSPACE_PATH",
        "FACTORY_AUDIT_DIR",
        "FACTORY_DATA_DIR",
        "FACTORY_CONFIG_DIR",
    ]:
        assert key in runtime_env.values
