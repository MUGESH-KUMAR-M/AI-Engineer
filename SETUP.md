# RAG Chatbot - Complete Setup & Run Guide

## 🚀 Quick Start (Choose One)

### Option 1: Using Gemini (Google) - Recommended for Quick Setup ✅

```bash
# 1. Get API Key
# Visit: https://makersuite.google.com/app/apikeys
# Copy your API key

# 2. Update .env
# Edit .env and set:
# GOOGLE_API_KEY=your-gemini-api-key
# MODEL_PROVIDER=gemini
# MODEL_NAME=gemini-2.0-flash

# 3. Install & Run
cd e:\AI-Engineer
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 4. Ingest Documents (First Time Only)
python -m backend.ingest

# 5. Start Backend
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# 6. In another terminal, start Frontend
cd frontend
npm run dev
```

### Option 2: Using Groq (Fastest) ⚡

```bash
# 1. Get API Key
# Visit: https://console.groq.com/keys
# Copy your API key

# 2. Update .env
# GROQ_API_KEY=your-groq-key
# MODEL_PROVIDER=groq
# MODEL_NAME=mixtral-8x7b-32768

# 3-6. Follow same steps as Option 1 above
```

### Option 3: Using Ollama (Local Model) 💻

```bash
# 1. Install Ollama
# Visit: https://ollama.ai
# Download and install

# 2. Start Ollama Server
ollama serve

# 3. In another terminal, pull a model
ollama pull llama2

# 4. Update .env
# OLLAMA_API_URL=http://localhost:11434
# MODEL_PROVIDER=ollama
# MODEL_NAME=ollama-llama2

# 5-6. Follow same steps as Option 1 above
```

### Option 4: Using Claude (Anthropic)

```bash
# 1. Get API Key: https://console.anthropic.com/
# ANTHROPIC_API_KEY=your-anthropic-key
# MODEL_PROVIDER=anthropic
# MODEL_NAME=claude-sonnet-4-20250514

# 5-6. Follow same steps as Option 1 above
```

### Option 5: Using OpenAI (GPT-4)

```bash
# 1. Get API Key: https://platform.openai.com/api-keys
# OPENAI_API_KEY=your-openai-key
# MODEL_PROVIDER=openai
# MODEL_NAME=gpt-4o

# 5-6. Follow same steps as Option 1 above
```

---

## 📋 Detailed Setup Instructions

### Step 1: Install Python & Node.js
- Python 3.9+: https://python.org
- Node.js 16+: https://nodejs.org

### Step 2: Create Project Folder
```bash
cd e:\AI-Engineer
```

### Step 3: Set Up Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1
# (If error: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser)

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Configure .env File
Create `.env` in project root with:
```
# Choose ONE provider:

# --- OPTION A: Gemini (Recommended) ---
GOOGLE_API_KEY=your-key-here
MODEL_PROVIDER=gemini
MODEL_NAME=gemini-2.0-flash

# --- OPTION B: Groq ---
GROQ_API_KEY=your-key-here
MODEL_PROVIDER=groq
MODEL_NAME=mixtral-8x7b-32768

# --- OPTION C: Ollama (Local) ---
OLLAMA_API_URL=http://localhost:11434
MODEL_PROVIDER=ollama
MODEL_NAME=ollama-llama2

# --- OPTION D: Anthropic ---
ANTHROPIC_API_KEY=your-key-here
MODEL_PROVIDER=anthropic
MODEL_NAME=claude-sonnet-4-20250514

# --- OPTION E: OpenAI ---
OPENAI_API_KEY=your-key-here
MODEL_PROVIDER=openai
MODEL_NAME=gpt-4o

# Common Settings (same for all)
CHROMA_PATH=./data/chroma_db
TOP_K=4
PDF_DIR=./Docs
```

### Step 5: Ingest Documents (First Time Only)
```bash
python -m backend.ingest
# Output: Will process all 10 PDFs and create vector embeddings
```

### Step 6: Start Backend API
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Backend will be available at:
# - API: http://localhost:8000
# - Docs: http://localhost:8000/docs
```

### Step 7: Start Frontend (New Terminal)
```bash
cd frontend
npm install  # (First time only)
npm run dev

# Frontend will be available at:
# - UI: http://localhost:5173
```

### Step 8: Test the Chatbot
Open browser to http://localhost:5173 and try:
- "What is the annual leave policy?"
- "How many days of sick leave do employees get?"
- "What is the notice period for resignation?"
- "What is the password policy?"
- "What are the WFH guidelines?"

---

## 🔑 Getting API Keys

### Gemini (Google)
1. Go to: https://makersuite.google.com/app/apikeys
2. Create new API key
3. Copy and paste into .env

### Groq
1. Go to: https://console.groq.com/keys
2. Create new API key
3. Copy and paste into .env

### Anthropic (Claude)
1. Go to: https://console.anthropic.com/
2. Create new API key
3. Copy and paste into .env

### OpenAI (GPT-4)
1. Go to: https://platform.openai.com/api-keys
2. Create new API key
3. Copy and paste into .env

### Ollama (Local - No Key Needed)
1. Download from: https://ollama.ai
2. Install and run: `ollama serve`
3. In another terminal: `ollama pull llama2`
4. No API key required!

---

## 🧪 Testing

### Test Backend API Directly
```bash
curl -X POST http://localhost:8000/api/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"question\": \"What is the leave policy?\"}"
```

### Expected Response
```json
{
  "answer": "According to SWS AI HR policy, employees are entitled to...",
  "sources": [
    {"filename": "SWS-AI-leave-policy.pdf", "page": 1},
    {"filename": "SWS-AI-hr-policy.pdf", "page": 3}
  ]
}
```

---

## 📁 Project Structure After Setup
```
AI-Engineer/
├── venv/                    # Virtual environment (created)
├── data/
│   └── chroma_db/          # Vector database (created by ingest)
├── .env                    # Configuration (create this!)
├── requirements.txt        # Python dependencies
├── README.md
├── backend/
│   ├── main.py            # FastAPI app
│   ├── ingest.py          # Ingestion script
│   ├── config/
│   │   └── settings.py    # Configuration loader
│   ├── api/
│   │   └── chat.py        # Chat endpoint
│   ├── models/
│   │   └── schemas.py     # Request/response models
│   └── rag/
│       ├── loader.py      # PDF loader
│       ├── chunker.py     # Text chunking
│       ├── embedder.py    # Embedding generation
│       ├── vector_store.py # ChromaDB wrapper
│       ├── llm.py         # LLM providers (UPDATED)
│       └── pipeline.py    # RAG pipeline
├── frontend/              # React UI
│   ├── src/
│   ├── public/
│   └── package.json
└── Docs/                  # PDF files (10 SWS AI documents)
```

---

## ⚙️ Environment Variables Reference

| Variable | Options | Description |
|----------|---------|-------------|
| `MODEL_PROVIDER` | `gemini`, `groq`, `ollama`, `anthropic`, `openai` | Which LLM to use |
| `MODEL_NAME` | See table below | Specific model version |
| `GOOGLE_API_KEY` | Your key | Required for Gemini |
| `GROQ_API_KEY` | Your key | Required for Groq |
| `ANTHROPIC_API_KEY` | Your key | Required for Claude |
| `OPENAI_API_KEY` | Your key | Required for GPT |
| `OLLAMA_API_URL` | `http://localhost:11434` | Ollama server URL |
| `CHROMA_PATH` | `./data/chroma_db` | Vector DB location |
| `TOP_K` | `3-5` | Documents to retrieve |
| `PDF_DIR` | `./Docs` | PDF directory |

### Supported Models

| Provider | MODEL_NAME | Speed | Cost |
|----------|-----------|-------|------|
| Gemini | `gemini-2.0-flash` | Fast | Free tier |
| Groq | `mixtral-8x7b-32768` | Very Fast | Free tier |
| Ollama | `ollama-llama2` | Depends on HW | Free |
| Anthropic | `claude-sonnet-4-20250514` | Medium | Paid |
| OpenAI | `gpt-4o` | Medium | Paid |

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Activate venv: `.\venv\Scripts\Activate.ps1` |
| `API Key Error` | Check .env file has correct key |
| `No PDFs found` | Ensure PDFs are in `./Docs` folder |
| `Port 8000 in use` | Change port: `uvicorn backend.main:app --port 8001` |
| `Chroma error` | Delete `data/chroma_db` folder and re-ingest |
| `Ollama won't connect` | Ensure Ollama is running: `ollama serve` |

---

## ✅ Verification Checklist

- [ ] Python 3.9+ installed
- [ ] Node.js 16+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] .env file created with API key
- [ ] PDFs in `./Docs` folder (10 files)
- [ ] Documents ingested (`python -m backend.ingest`)
- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] Chat UI loads at http://localhost:5173
- [ ] Can send message and get response

---

## 🚀 Next Steps

1. **Test Queries**: Try the sample questions above
2. **GitHub**: Push to your GitHub repo
3. **Deploy**: See [DEPLOYMENT.md](../DEPLOYMENT.md) for production setup
4. **Customize**: Modify chunking strategy in `backend/rag/chunker.py`

---

**Project Ready! Your RAG chatbot is now fully functional with multiple LLM options.** 🎉
