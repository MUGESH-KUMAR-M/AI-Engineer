"""
Effective LLM configuration — merges .env, runtime overrides, and keys.
"""

from dataclasses import dataclass
from backend.config.runtime_config import get_api_key, load
from backend.config.settings import Settings, get_settings


@dataclass(frozen=True)
class EffectiveLLMConfig:
    provider: str
    model: str
    openai_api_key: str
    anthropic_api_key: str
    google_api_key: str
    groq_api_key: str
    ollama_api_url: str
    ollama_timeout: int


def get_effective_llm_config() -> EffectiveLLMConfig:
    settings: Settings = get_settings()
    runtime = load()

    provider = runtime.get("provider") or settings.MODEL_PROVIDER
    model = runtime.get("model") or settings.MODEL_NAME

    return EffectiveLLMConfig(
        provider=provider,
        model=model,
        openai_api_key=get_api_key("openai", settings.OPENAI_API_KEY, runtime),
        anthropic_api_key=get_api_key(
            "anthropic", settings.ANTHROPIC_API_KEY, runtime
        ),
        google_api_key=get_api_key("gemini", settings.GOOGLE_API_KEY, runtime),
        groq_api_key=get_api_key("groq", settings.GROQ_API_KEY, runtime),
        ollama_api_url=settings.OLLAMA_API_URL,
        ollama_timeout=settings.OLLAMA_TIMEOUT,
    )


def clear_settings_cache() -> None:
    get_settings.cache_clear()
