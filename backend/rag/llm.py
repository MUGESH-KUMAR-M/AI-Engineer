"""
LLM interaction layer supporting multiple providers.

Supports: Anthropic Claude, OpenAI, Google Gemini, Groq, and Ollama.
Builds a structured prompt from retrieved context chunks and calls
the selected LLM model to generate a grounded answer.
"""

import logging
from typing import Any

from backend.config.settings import get_settings

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
    """Format retrieved chunks into a numbered context block.

    Parameters
    ----------
    chunks:
        Each dict must have ``text`` and ``metadata`` keys.

    Returns
    -------
    str
        A human-readable, numbered context string.
    """
    lines: list[str] = []
    for idx, chunk in enumerate(chunks, start=1):
        meta = chunk["metadata"]
        filename = meta.get("source_filename", "unknown")
        page = meta.get("page_number", "?")
        lines.append(
            f"[{idx}] (Source: {filename}, Page {page})\n{chunk['text']}"
        )
    return "\n\n".join(lines)


def _ask_anthropic(question: str, context_text: str, settings) -> str:
    """Call Anthropic Claude API."""
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
    """Call OpenAI API."""
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
    """Call Google Gemini API."""
    import google.generativeai as genai
    
    genai.configure(api_key=settings.GOOGLE_API_KEY)
    model = genai.GenerativeModel(settings.MODEL_NAME)
    
    prompt = f"{_SYSTEM_PROMPT}\n\nContext:\n{context_text}\n\nQuestion: {question}"
    response = model.generate_content(prompt, stream=False)
    return response.text


def _ask_groq(question: str, context_text: str, settings) -> str:
    """Call Groq API."""
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
    """Resolve Ollama model tag (e.g. llama3 -> llama3:latest)."""
    name = settings.MODEL_NAME.replace("ollama-", "")
    if ":" not in name:
        name = f"{name}:latest"
    return name


def _ask_ollama(question: str, context_text: str, settings) -> str:
    """Call Ollama chat API (local LLM)."""
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
            "options": {
                "temperature": 0.1,
                "num_predict": 1024,
            },
        },
        timeout=settings.OLLAMA_TIMEOUT,
    )
    response.raise_for_status()
    data = response.json()
    return data.get("message", {}).get("content", "").strip()


def ask_llm(question: str, context_chunks: list[dict[str, Any]]) -> str:
    """Send the user question plus context to LLM and return the answer.

    Supports multiple LLM providers based on MODEL_PROVIDER setting.

    Parameters
    ----------
    question:
        The end-user's natural-language question.
    context_chunks:
        Retrieved document chunks from the vector store.

    Returns
    -------
    str
        The model's generated answer text.
    """
    settings = get_settings()
    context_text = _build_context_block(context_chunks)

    logger.debug(
        "Sending prompt to %s (provider: %s) …",
        settings.MODEL_NAME,
        settings.MODEL_PROVIDER,
    )

    try:
        if settings.MODEL_PROVIDER == "anthropic":
            answer = _ask_anthropic(question, context_text, settings)
        elif settings.MODEL_PROVIDER == "openai":
            answer = _ask_openai(question, context_text, settings)
        elif settings.MODEL_PROVIDER == "gemini":
            answer = _ask_gemini(question, context_text, settings)
        elif settings.MODEL_PROVIDER == "groq":
            answer = _ask_groq(question, context_text, settings)
        elif settings.MODEL_PROVIDER == "ollama":
            answer = _ask_ollama(question, context_text, settings)
        else:
            raise ValueError(f"Unknown provider: {settings.MODEL_PROVIDER}")

        logger.info("LLM responded (%d chars).", len(answer))
        return answer

    except Exception as e:
        logger.exception("LLM API call failed for provider %s", settings.MODEL_PROVIDER)
        raise
