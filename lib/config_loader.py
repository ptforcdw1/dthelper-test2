"""Load YAML configs. Centralized so paths aren't duplicated across scripts."""
import os
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent


def _load(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_global() -> dict:
    cfg = _load(REPO / "config" / "global.yaml")
    tenant_env = cfg["dynatrace"]["tenant_url_env"]
    tenant = os.environ.get(tenant_env)
    if not tenant:
        raise RuntimeError(f"env var {tenant_env} not set")
    cfg["dynatrace"]["tenant_url"] = tenant
    return cfg


def load_naming() -> dict:
    return _load(REPO / "config" / "naming-convention.yaml")


def load_app_env(app: str, env: str) -> dict:
    path = REPO / "config" / "apps" / app / f"{env}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Missing app/env config: {path}")
    return _load(path)
