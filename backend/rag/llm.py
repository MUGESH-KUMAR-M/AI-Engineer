"""
LLM interaction layer supporting multiple providers.

Supports: Anthropic Claude, OpenAI, Google Gemini, Groq, and Ollama.
Uses effective config from .env + runtime UI overrides.
"""

import logging
from types import SimpleNamespace
from typing import Any

from backend.config.llm_config import EffectiveLLMConfig, get_effective_llm_config

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are the SWS AI company policy assistant. "
    "Rules:\n"
    "1. Answer ONLY from the Context sections below — never invent facts.\n"
    "2. If the answer is not in the context, respond exactly: "
    "I don't have that information in the company documents.\n"
    "3. Be concise, professional, and cite the source document name.\n"
    "4. Use bullet points for lists when helpful."
)


def _build_context_block(chunks: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for idx, chunk in enumerate(chunks, start=1):
        meta = chunk["metadata"]
        filename = meta.get("source_filename", "unknown")
        page = meta.get("page_number", "?")
        lines.append(
            f"[{idx}] (Source: {filename}, Page {page})\n{chunk['text']}"
        )
    return "\n\n".join(lines)


def _as_settings(cfg: EffectiveLLMConfig) -> SimpleNamespace:
    """Adapt EffectiveLLMConfig for provider helpers."""
    return SimpleNamespace(
        MODEL_NAME=cfg.model,
        MODEL_PROVIDER=cfg.provider,
        OPENAI_API_KEY=cfg.openai_api_key,
        ANTHROPIC_API_KEY=cfg.anthropic_api_key,
        GOOGLE_API_KEY=cfg.google_api_key,
        GROQ_API_KEY=cfg.groq_api_key,
        OLLAMA_API_URL=cfg.ollama_api_url,
        OLLAMA_TIMEOUT=cfg.ollama_timeout,
    )


def _ask_anthropic(question: str, context_text: str, settings) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    user_message = f"Context:\n{context_text}\n\nQuestion: {question}"
    response = client.messages.create(
        model=settings.MODEL_NAME,
        max_tokens=1024,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text


def _ask_openai(question: str, context_text: str, settings) -> str:
    import openai

    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    user_message = f"Context:\n{context_text}\n\nQuestion: {question}"
    response = client.chat.completions.create(
        model=settings.MODEL_NAME,
        max_tokens=1024,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content


def _ask_gemini(question: str, context_text: str, settings) -> str:
    import google.generativeai as genai

    genai.configure(api_key=settings.GOOGLE_API_KEY)
    model = genai.GenerativeModel(settings.MODEL_NAME)
    prompt = f"{_SYSTEM_PROMPT}\n\nContext:\n{context_text}\n\nQuestion: {question}"
    response = model.generate_content(prompt, stream=False)
    return response.text


def _ask_groq(question: str, context_text: str, settings) -> str:
    from groq import Groq

    client = Groq(api_key=settings.GROQ_API_KEY)
    user_message = f"Context:\n{context_text}\n\nQuestion: {question}"
    response = client.chat.completions.create(
        model=settings.MODEL_NAME,
        max_tokens=1024,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content


def _ollama_model_name(settings) -> str:
    name = settings.MODEL_NAME.replace("ollama-", "")
    if ":" not in name:
        name = f"{name}:latest"
    return name


def _ask_ollama(question: str, context_text: str, settings) -> str:
    import requests

    model = _ollama_model_name(settings)
    user_message = f"Context:\n{context_text}\n\nQuestion: {question}"
    response = requests.post(
        f"{settings.OLLAMA_API_URL.rstrip('/')}/api/chat",
        json={
            "model": model,
            "stream": False,
            "messages": [
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            "options": {"temperature": 0.1, "num_predict": 1024},
        },
        timeout=settings.OLLAMA_TIMEOUT,
    )
    response.raise_for_status()
    return response.json().get("message", {}).get("content", "").strip()


def _call_provider(cfg: EffectiveLLMConfig, question: str, context_text: str) -> str:
    settings = _as_settings(cfg)
    provider = cfg.provider

    if provider == "anthropic":
        return _ask_anthropic(question, context_text, settings)
    if provider == "openai":
        return _ask_openai(question, context_text, settings)
    if provider == "gemini":
        return _ask_gemini(question, context_text, settings)
    if provider == "groq":
        return _ask_groq(question, context_text, settings)
    if provider == "ollama":
        return _ask_ollama(question, context_text, settings)
    raise ValueError(f"Unknown provider: {provider}")


def ask_llm(question: str, context_chunks: list[dict[str, Any]]) -> str:
    cfg = get_effective_llm_config()
    context_text = _build_context_block(context_chunks)

    logger.info(
        "LLM request — provider=%s model=%s",
        cfg.provider,
        cfg.model,
    )

    try:
        answer = _call_provider(cfg, question, context_text)
        logger.info("LLM responded (%d chars).", len(answer))
        return answer
    except Exception as primary_error:
        if cfg.provider != "groq" and cfg.groq_api_key:
            logger.warning(
                "Provider %s failed (%s). Trying Groq fallback.",
                cfg.provider,
                primary_error,
            )
            fallback = EffectiveLLMConfig(
                provider="groq",
                model="llama-3.3-70b-versatile",
                openai_api_key=cfg.openai_api_key,
                anthropic_api_key=cfg.anthropic_api_key,
                google_api_key=cfg.google_api_key,
                groq_api_key=cfg.groq_api_key,
                ollama_api_url=cfg.ollama_api_url,
                ollama_timeout=cfg.ollama_timeout,
            )
            answer = _call_provider(fallback, question, context_text)
            logger.info("Groq fallback succeeded (%d chars).", len(answer))
            return answer
        logger.exception("LLM failed for provider %s", cfg.provider)
        raise
