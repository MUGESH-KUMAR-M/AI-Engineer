"""
Runtime LLM configuration — overrides .env from the settings UI.

Persisted to ``data/runtime_config.json`` (gitignored). API keys are
stored locally for development; use environment variables in production.
"""

import json
import logging
from pathlib import Path
from threading import Lock
from typing import Any

logger = logging.getLogger(__name__)

_CONFIG_PATH = Path("./data/runtime_config.json")
_lock = Lock()


def _default() -> dict[str, Any]:
    return {
        "provider": None,
        "model": None,
        "api_keys": {},
    }


def load() -> dict[str, Any]:
    with _lock:
        if not _CONFIG_PATH.exists():
            return _default()
        try:
            data = json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
            base = _default()
            base.update({k: v for k, v in data.items() if k in base})
            if isinstance(data.get("api_keys"), dict):
                base["api_keys"] = data["api_keys"]
            return base
        except Exception:
            logger.exception("Failed to load runtime config")
            return _default()


def save(data: dict[str, Any]) -> None:
    with _lock:
        _CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        _CONFIG_PATH.write_text(
            json.dumps(data, indent=2),
            encoding="utf-8",
        )


def mask_key(key: str) -> str:
    if not key or len(key) < 8:
        return "••••" if key else ""
    return f"••••{key[-4:]}"


def get_api_key(provider: str, env_key: str, runtime: dict[str, Any]) -> str:
    """Runtime key overrides environment."""
    runtime_keys = runtime.get("api_keys") or {}
    if runtime_keys.get(provider):
        return runtime_keys[provider]
    return env_key or ""


def update_config(
    provider: str | None = None,
    model: str | None = None,
    api_key: str | None = None,
    clear_api_key: bool = False,
) -> dict[str, Any]:
    """Merge updates and persist."""
    data = load()
    if provider is not None:
        data["provider"] = provider
    if model is not None:
        data["model"] = model
    if provider and api_key is not None and api_key.strip():
        data.setdefault("api_keys", {})[provider] = api_key.strip()
    if provider and clear_api_key:
        data.setdefault("api_keys", {}).pop(provider, None)
    save(data)
    return data
