"""Load and validate external APIs config. No secrets in file - only env var names."""
import os
import re
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Default config path (project root / config / apis.yaml)
_DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "config" / "apis.yaml"


def _resolve_env(value: str) -> str:
    """Replace ${VAR_NAME} with os.environ value."""
    if not isinstance(value, str):
        return value
    pattern = re.compile(r"\$\{([^}]+)\}")
    return pattern.sub(lambda m: os.getenv(m.group(1), ""), value)


def load_config(config_path: Path | None = None) -> list[dict[str, Any]]:
    """
    Load apis.yaml and resolve base_url from env. Returns list of API configs.
    Skips APIs whose base_url_env is missing or empty in env.
    """
    path = config_path or Path(os.getenv("APIS_CONFIG_PATH", str(_DEFAULT_CONFIG_PATH)))
    if not path.exists():
        logger.debug("External APIs config not found: %s", path)
        return []

    try:
        import yaml
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        logger.exception("Failed to load APIs config %s: %s", path, e)
        return []

    apis = data.get("apis") or []
    resolved = []
    for api in apis:
        if not isinstance(api, dict):
            continue
        base_url_env = (api.get("base_url_env") or "").strip()
        if not base_url_env:
            logger.warning("API %s has no base_url_env, skipping", api.get("id"))
            continue
        base_url = (os.getenv(base_url_env) or "").strip().rstrip("/")
        if not base_url:
            logger.debug("API %s: %s not set, skipping", api.get("id"), base_url_env)
            continue
        api = {**api, "base_url": base_url}
        resolved.append(api)
    return resolved
