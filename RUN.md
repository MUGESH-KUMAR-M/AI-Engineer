# 🚀 Quick Run Commands

## Backend Setup (Run Once)
```bash
cd e:\AI-Engineer
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m backend.ingest
```

## Choose Your LLM Provider

### ⭐ Option 1: Gemini (Easiest - Free Tier Available)
```bash
# .env
GOOGLE_API_KEY=your-key-from-makersuite.google.com
MODEL_PROVIDER=gemini
MODEL_NAME=gemini-2.0-flash
```

### ⚡ Option 2: Groq (Fastest)
```bash
# .env
GROQ_API_KEY=your-key-from-console.groq.com
MODEL_PROVIDER=groq
MODEL_NAME=mixtral-8x7b-32768
```

### 💻 Option 3: Ollama (Local - No API Key)
```bash
# In terminal 1: ollama serve
# In terminal 2: ollama pull llama2

# .env
OLLAMA_API_URL=http://localhost:11434
MODEL_PROVIDER=ollama
MODEL_NAME=ollama-llama2
```

### 🤖 Option 4: Claude (Anthropic)
```bash
# .env
ANTHROPIC_API_KEY=your-key-from-console.anthropic.com
MODEL_PROVIDER=anthropic
MODEL_NAME=claude-sonnet-4-20250514
```

### 🔵 Option 5: GPT-4 (OpenAI)
```bash
# .env
OPENAI_API_KEY=your-key-from-platform.openai.com
MODEL_PROVIDER=openai
MODEL_NAME=gpt-4o
```

## Run Application

**Terminal 1 - Backend:**
```bash
cd e:\AI-Engineer
.\venv\Scripts\Activate.ps1
uvicorn backend.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd e:\AI-Engineer\frontend
npm run dev
```

**Open Browser:**
```
http://localhost:5173
```

## Test Questions
- "What is the annual leave policy at SWS AI?"
- "How many days of sick leave do employees get?"
- "What is the notice period for resignation?"
- "What tools does SWS AI use for communication?"
- "What is the password policy for company systems?"
- "How are performance reviews conducted?"
- "What are the WFH guidelines?"
- "Does SWS AI offer health insurance?"

---

## API Endpoint
```bash
POST http://localhost:8000/api/chat

Request:
{
  "question": "What is the leave policy?"
}

Response:
{
  "answer": "...",
  "sources": [
    {"filename": "SWS-AI-leave-policy.pdf", "page": 1}
  ]
}
```

For detailed setup, see [SETUP.md](./SETUP.md)
