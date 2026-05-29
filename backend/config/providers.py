"""
LLM provider catalog — models and metadata for the settings UI.
"""

from typing import TypedDict


class ProviderInfo(TypedDict):
    id: str
    name: str
    description: str
    requires_api_key: bool
    models: list[str]
    default_model: str


PROVIDERS: list[ProviderInfo] = [
    {
        "id": "ollama",
        "name": "Ollama",
        "description": "Local LLM — no API key required",
        "requires_api_key": False,
        "models": ["phi3", "llama3", "mistral", "gemma2"],
        "default_model": "phi3",
    },
    {
        "id": "openai",
        "name": "OpenAI",
        "description": "GPT-4o, GPT-4o mini, GPT-3.5",
        "requires_api_key": True,
        "models": ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
        "default_model": "gpt-4o-mini",
    },
    {
        "id": "anthropic",
        "name": "Anthropic",
        "description": "Claude Sonnet & Haiku",
        "requires_api_key": True,
        "models": [
            "claude-sonnet-4-20250514",
            "claude-3-5-haiku-20241022",
        ],
        "default_model": "claude-sonnet-4-20250514",
    },
    {
        "id": "gemini",
        "name": "Google Gemini",
        "description": "Gemini 2.0 Flash & Pro",
        "requires_api_key": True,
        "models": ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
        "default_model": "gemini-2.0-flash",
    },
    {
        "id": "groq",
        "name": "Groq",
        "description": "Fast cloud inference (Llama, Mixtral)",
        "requires_api_key": True,
        "models": [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
        ],
        "default_model": "llama-3.3-70b-versatile",
    },
]


def get_provider(provider_id: str) -> ProviderInfo | None:
    for p in PROVIDERS:
        if p["id"] == provider_id:
            return p
    return None
