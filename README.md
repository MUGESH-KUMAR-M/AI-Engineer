# 🚀 SWS AI Assistant — Complete RAG Chatbot with Document Upload

A **production-ready Retrieval-Augmented Generation (RAG)** chatbot that lets employees ask natural-language questions about company policies and receive accurate, source-cited answers from internal PDF documents.

**Features:**
- ✅ 10 SWS AI company policy PDFs pre-ingested (HR, leave, IT security, etc.)
- ✅ **Document upload** - Add new PDFs dynamically without restarting
- ✅ **Multiple LLM support** - Gemini, Groq, Claude, OpenAI, Ollama
- ✅ **Local embeddings** - HuggingFace (no API key needed)
- ✅ **Production-ready** - Error handling, logging, async processing
- ✅ **Beautiful UI** - React 19 + Vite with glassmorphism design

---

## 🎯 Quick Start (Local Ollama Setup)

### Prerequisites
- **Python 3.11+**
- **Node.js 18+**
- **Ollama** installed with at least one local model (`phi3:latest` recommended)

### Project Setup

```bash
cd e:\AI-Engineer

# 1. (Optional) Create & activate venv
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install frontend dependencies
cd frontend
npm install
cd ..
```

**Done! 🎉** Upload PDFs, ask questions, get answers with sources!

---

## 📋 Current Configuration (Default)

- **Embeddings:** HuggingFace `sentence-transformers/all-MiniLM-L6-v2` (local, no API key)  
- **Vector DB:** ChromaDB (local, `data/chroma_db/`)  
- **LLM:** Ollama `phi3` via `MODEL_PROVIDER=ollama`  
- **PDF directory:** `./Docs` (10 SWS AI PDFs)

Key `.env` values (already set in this repo, but you can adjust):

```env
EMBEDDING_PROVIDER=huggingface
MODEL_PROVIDER=ollama
MODEL_NAME=phi3
OLLAMA_API_URL=http://localhost:11434
TOP_K=4
PDF_DIR=./Docs
```

---

## 📊 Project Structure

````
AI-Engineer/
├── .env.example              # Environment variable template
├── .gitignore                 # Git ignore rules
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── Docs/                      # 10 SWS AI company policy PDFs
│   ├── SWS-AI-benefits-compensation.pdf
│   ├── SWS-AI-code-of-conduct.pdf
│   ├── SWS-AI-company-overview.pdf
│   ├── SWS-AI-hr-policy.pdf
│   ├── SWS-AI-it-security-policy.pdf
│   ├── SWS-AI-leave-policy.pdf
│   ├── SWS-AI-onboarding-guide.pdf
│   ├── SWS-AI-performance-review.pdf
│   ├── SWS-AI-resignation-policy.pdf
│   └── SWS-AI-wfh-policy.pdf
├── backend/
│   ├── __init__.py
│   ├── main.py                # FastAPI app entry-point
│   ├── ingest.py              # Document ingestion script
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py        # Pydantic-settings configuration
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py         # Request/response Pydantic models
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── loader.py          # PDF text extraction (PyMuPDF)
│   │   ├── chunker.py         # Text chunking (LangChain)
│   │   ├── embedder.py        # OpenAI embeddings
│   │   ├── vector_store.py    # ChromaDB operations
│   │   ├── llm.py             # Anthropic Claude integration
│   │   └── pipeline.py        # End-to-end RAG orchestration
│   └── api/
│       ├── __init__.py
│       └── chat.py            # POST /api/chat endpoint
├── frontend/
│   ├── index.html             # HTML entry with Livvic font
│   ├── package.json           # Node dependencies
│   ├── vite.config.js         # Vite config with API proxy
│   └── src/
│       ├── main.jsx           # React entry
│       ├── App.jsx            # Main app component
│       ├── index.css          # Complete design system (950 lines)
│       ├── components/
│       │   ├── Header.jsx         # App header with status
│       │   ├── ChatWindow.jsx     # Message list + welcome screen
│       │   ├── ChatInput.jsx      # Auto-resizing textarea + send
│       │   ├── MessageBubble.jsx  # User/assistant message display
│       │   ├── SourceChips.jsx    # Source document badges
│       │   └── TypingIndicator.jsx# Animated typing dots
│       └── services/
│           └── api.js         # Fetch wrapper for /api/chat
└── data/
    └── chroma_db/             # ChromaDB persistent storage (auto-created)

````

---

## 🚀 Detailed Setup & Run Commands

### 1. Clone & backend setup

```bash
git clone <your-repo-url>
cd AI-Engineer

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Configure environment

```bash
# Copy the example env file
copy .env.example .env        # Windows
# cp .env.example .env        # macOS/Linux

# Default is local Ollama (no cloud keys required).
# Optional: set OpenAI / Groq / Anthropic / Gemini keys if you want to switch providers.
```

### 3. Ingest documents into Chroma

```bash
# This loads all 10 PDFs, chunks them, generates embeddings,
# and stores them in ChromaDB
python -m backend.ingest
```

You should see output like:
```
Step 1/4: Loading PDFs …
  → 42 raw page(s) loaded.
Step 2/4: Chunking documents …
  → 186 chunk(s) created.
Step 3/4: Generating embeddings …
  → 186 embedding(s) generated.
Step 4/4: Storing in ChromaDB …
  → 186 chunk(s) stored.
Ingestion complete ✓
```

### 4. Start the backend (FastAPI)

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8010
# API:       http://127.0.0.1:8010
# Health:    GET  /api/health
# Chat:      POST /api/chat
# Status:    GET  /api/status
# Ingest:    GET  /api/ingest-status
```

### 5. Start the frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
# UI: http://127.0.0.1:5173  (proxied to backend on :8010)
```

### 6. Open the App

Navigate to **http://localhost:5173** and start asking questions!

---

## 💬 Sample Queries

| Query | Expected Source |
|-------|---------------|
| "What is the annual leave policy at SWS AI?" | SWS-AI-leave-policy.pdf |
| "How many days of sick leave do employees get?" | SWS-AI-leave-policy.pdf |
| "What is the notice period for resignation?" | SWS-AI-resignation-policy.pdf |
| "What tools does SWS AI use for communication?" | SWS-AI-it-security-policy.pdf |
| "What is the password policy for company systems?" | SWS-AI-it-security-policy.pdf |
| "How are performance reviews conducted?" | SWS-AI-performance-review.pdf |
| "What are the WFH guidelines?" | SWS-AI-wfh-policy.pdf |
| "Does SWS AI offer health insurance?" | SWS-AI-benefits-compensation.pdf |

---

## 🔌 API Reference

### Health Check

```
GET /api/health
Response: { "status": "ok" }
```

### Chat

```
POST /api/chat
Content-Type: application/json

Request:  { "question": "What is the leave policy?" }
Response: {
  "answer": "According to the SWS AI Leave Policy...",
  "sources": [
    { "filename": "SWS-AI-leave-policy.pdf", "page": 2 },
    { "filename": "SWS-AI-hr-policy.pdf", "page": 5 }
  ]
}
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 19, Vite 6, Livvic font, white/blue UI |
| **Backend** | Python 3.11+, FastAPI |
| **Embeddings** | HuggingFace `all-MiniLM-L6-v2` (local) or OpenAI `text-embedding-3-small` |
| **Vector Store** | ChromaDB (persistent local) |
| **LLM (default)** | Ollama `phi3` (local, no API key) |
| **LLM (optional)** | Groq / OpenAI / Anthropic / Gemini via `.env` switches |
| **PDF Parsing** | PyMuPDF (fitz) |
| **Text Splitting** | LangChain `RecursiveCharacterTextSplitter` |

---

## 🏗️ Architecture Decisions

### Vector database: ChromaDB

Chroma was chosen for local, zero-ops persistence (`data/chroma_db/`). It needs no Docker or cloud account, fits a 3–4 hour assessment timeline, and exposes a simple upsert + cosine-similarity query API. Pinecone/FAISS are viable alternatives; Chroma keeps the prototype self-contained.

### Chunking: `RecursiveCharacterTextSplitter`

- **chunk_size=500**, **chunk_overlap=50** (per assessment spec)
- Splits on paragraph/sentence boundaries before hard-cutting, which keeps policy clauses intact
- Each chunk keeps `source_filename` + `page_number` for citation in the UI

### Embeddings: HuggingFace `all-MiniLM-L6-v2`

Runs locally with no API key (384-dim vectors, fast on CPU). OpenAI `text-embedding-3-small` is supported via `EMBEDDING_PROVIDER=openai` when higher quality is needed. **Important:** query and document embeddings must use the same model.

### Retrieval: top-k = 4

`TOP_K=4` balances context breadth vs. token limits. For narrow factual questions (e.g. sick leave days), rank-1 chunks are usually sufficient; for broad questions (e.g. WFH guidelines), 4 chunks pull related sections across pages.

Test retrieval without the LLM:

```bash
python scripts/test_retrieval.py "What is the leave policy?"
```

### Prompt design

The system prompt instructs the model to:

1. Answer **only** from numbered context blocks (filename + page per chunk)
2. Return exactly: *"I don't have that information in the company documents."* when context is insufficient
3. Cite which document the answer comes from

Context is formatted as `[1] (Source: file.pdf, Page N)\n<text>` so the model can attribute sources; the API also returns structured `sources` for the UI chips.

### LLM: Local Ollama (phi3) + pluggable providers

- **Default:** `MODEL_PROVIDER=ollama`, `MODEL_NAME=phi3` (runs fully local via Ollama)
- **Switching provider:** update `.env` to e.g.:
  - `MODEL_PROVIDER=groq`, `MODEL_NAME=llama-3.3-70b-versatile`, `GROQ_API_KEY=...`
  - `MODEL_PROVIDER=openai`, `MODEL_NAME=gpt-4.1-mini`, `OPENAI_API_KEY=...`
  - `MODEL_PROVIDER=anthropic`, `MODEL_NAME=claude-3.7-sonnet`, `ANTHROPIC_API_KEY=...`
- The RAG pipeline (`backend/rag/pipeline.py`) does not change when swapping LLMs.

---

## 🧩 Assumptions & Notes

- **Docs folder:** The 10 SWS AI PDFs live under `Docs/` and are treated as the single source of truth.
- **Grounded answers:** If relevant chunks are not found or are too far in vector space, the LLM is instructed to reply: *“I don't have that information in the company documents.”*
- **Local-first:** Default configuration assumes **no cloud API keys** and runs everything locally (HuggingFace embeddings + Ollama LLM + ChromaDB).
- **Ports:** Backend on `8010`, frontend on `5173`, with Vite dev proxy pointing `/api` to the backend.

---

## 📝 License

Built for the SWS AI Engineering Assessment.