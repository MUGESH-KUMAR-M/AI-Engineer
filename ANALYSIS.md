# SWS AI RAG Chatbot — Technical Analysis

## System overview

```
User (React UI)
    → POST /api/chat
        → Embed question (HuggingFace all-MiniLM-L6-v2)
        → Retrieve top-K chunks (ChromaDB, L2 distance filter)
        → Build numbered context block
        → LLM generation (Ollama | OpenAI | Anthropic | Gemini | Groq)
    ← Answer + source filenames/pages
```

## Design decisions

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Vector DB | ChromaDB (local) | Zero ops, persistent, fast enough for ~10 PDFs |
| Embeddings | `all-MiniLM-L6-v2` | Free, local, 384-dim; good for short policy text |
| Chunking | 500 / 50 overlap | Matches assessment spec; ~1–2 paragraphs per chunk |
| Retrieval K | 4 | Balance of context vs. token limit |
| Default LLM | Ollama `phi3` | No API cost; works offline after model pull |
| Cloud LLMs | Runtime config | UI lets users paste keys without editing `.env` |

## Provider switching flow

1. User opens **Model** settings in the header.
2. Frontend calls `GET /api/providers` for catalog + active provider.
3. On save, `POST /api/providers/configure` writes `data/runtime_config.json`.
4. `get_effective_llm_config()` merges runtime + `.env` on every chat request.
5. Keys from UI override env vars for that provider only.

## Grounding & hallucination control

- System prompt restricts answers to provided context blocks.
- Each chunk is labeled with `[n] (Source: file.pdf, Page N)`.
- API returns structured `sources` for UI chips (independent of LLM prose).
- Distance threshold drops irrelevant chunks; fallback keeps top 2 if all filtered.

## Docker topology

| Service | Role | Port |
|---------|------|------|
| `backend` | FastAPI + RAG + Chroma | 8000 |
| `frontend` | Nginx serves React; proxies `/api` | 5173 → 80 |
| `ollama` (optional profile) | Local LLM | 11434 |

## Limitations

- Runtime API keys in JSON are for **development**; production should use secrets/env only.
- HuggingFace model downloads on first embed (cold start).
- Ollama `llama3` (8B) needs more RAM than `phi3` (3.8B).
- No conversation memory — each question is stateless RAG.

## Sample test queries

All should cite `Docs/` PDFs:

- Annual leave policy → `SWS-AI-leave-policy.pdf`
- Sick leave days → `SWS-AI-leave-policy.pdf`
- Resignation notice → `SWS-AI-resignation-policy.pdf`
- Password policy → `SWS-AI-it-security-policy.pdf`
- Health insurance → `SWS-AI-benefits-compensation.pdf`
