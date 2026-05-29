"""
Provider configuration API — list models and switch LLM at runtime.
"""

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.config.llm_config import clear_settings_cache, get_effective_llm_config
from backend.config.providers import PROVIDERS, get_provider
from backend.config.runtime_config import load, mask_key, update_config
from backend.config.settings import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()

_KEY_FIELDS = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GOOGLE_API_KEY",
    "groq": "GROQ_API_KEY",
}


class ConfigureProviderRequest(BaseModel):
    provider: str = Field(..., description="Provider id: ollama, openai, anthropic, gemini, groq")
    model: str = Field(..., description="Model name for the provider")
    api_key: str | None = Field(
        default=None,
        description="Optional API key (saved locally). Omit to keep existing.",
    )


def _key_configured(provider_id: str, settings, runtime: dict) -> tuple[bool, str]:
    if provider_id == "ollama":
        return True, ""
    env_val = getattr(settings, _KEY_FIELDS.get(provider_id, ""), "") or ""
    runtime_val = (runtime.get("api_keys") or {}).get(provider_id, "")
    key = runtime_val or env_val
    return bool(key), mask_key(key)


@router.get("/api/providers")
async def list_providers() -> dict:
    """Return provider catalog and active selection."""
    settings = get_settings()
    runtime = load()
    effective = get_effective_llm_config()

    providers_out = []
    for p in PROVIDERS:
        configured, masked = _key_configured(p["id"], settings, runtime)
        providers_out.append(
            {
                **p,
                "api_key_configured": configured if p["requires_api_key"] else True,
                "api_key_hint": masked,
            }
        )

    return {
        "providers": providers_out,
        "active": {
            "provider": effective.provider,
            "model": effective.model,
        },
    }


@router.post("/api/providers/configure")
async def configure_provider(body: ConfigureProviderRequest) -> dict:
    """Switch LLM provider/model and optionally save an API key."""
    info = get_provider(body.provider)
    if not info:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {body.provider}")

    if body.model not in info["models"]:
        raise HTTPException(
            status_code=400,
            detail=f"Model '{body.model}' is not available for {body.provider}.",
        )

    settings = get_settings()
    runtime = load()

    if info["requires_api_key"]:
        new_key = body.api_key.strip() if body.api_key else None
        existing = (runtime.get("api_keys") or {}).get(body.provider) or getattr(
            settings, _KEY_FIELDS.get(body.provider, ""), ""
        )
        if not new_key and not existing:
            raise HTTPException(
                status_code=400,
                detail=f"API key required for {info['name']}. Paste your key or set it in .env.",
            )

    update_config(
        provider=body.provider,
        model=body.model,
        api_key=body.api_key,
    )
    clear_settings_cache()
    effective = get_effective_llm_config()

    logger.info(
        "LLM configured — provider=%s model=%s",
        effective.provider,
        effective.model,
    )

    return {
        "message": f"Now using {info['name']} ({effective.model})",
        "active": {
            "provider": effective.provider,
            "model": effective.model,
        },
    }
