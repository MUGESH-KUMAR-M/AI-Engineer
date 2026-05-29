"""
Application settings loaded from environment variables.

Uses pydantic-settings to provide validated, typed configuration
with automatic .env file loading.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application configuration.

    All values can be overridden via environment variables or a .env file
    located at the project root.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # API Keys
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    OLLAMA_API_URL: str = "http://localhost:11434"
    
    # Model Configuration
    CHROMA_PATH: str = "./data/chroma_db"
    TOP_K: int = 4
    MODEL_NAME: str = "gemini-2.0-flash"
    MODEL_PROVIDER: str = "gemini"  # Options: openai, anthropic, gemini, groq, ollama
    EMBEDDING_PROVIDER: str = "huggingface"  # Options: openai, huggingface (default: huggingface - no key needed)
    PDF_DIR: str = "./Docs"


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton of the application settings.

    Using ``lru_cache`` ensures the .env file is read only once per
    process lifetime.
    """
    return Settings()
