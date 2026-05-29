import { Settings2, Sparkles } from 'lucide-react';

const PROVIDER_LABELS = {
  ollama: 'Ollama',
  openai: 'OpenAI',
  anthropic: 'Anthropic',
  gemini: 'Gemini',
  groq: 'Groq',
};

export default function Header({ systemStatus, onOpenSettings }) {
  const llm = systemStatus?.llm;
  const rag = systemStatus?.rag;

  const providerName = PROVIDER_LABELS[llm?.provider] || llm?.provider || '…';
  const isReady = llm?.ready && (rag?.chunks ?? 0) > 0;

  return (
    <header className="app-header">
      <div className="app-header-brand">
        <div className="brand-mark">
          <Sparkles size={20} strokeWidth={2.2} />
        </div>
        <div className="brand-copy">
          <h1>SWS AI Assistant</h1>
          <p>Company policy · RAG-powered answers</p>
        </div>
      </div>

      <div className="app-header-actions">
        {llm && (
          <div className={`model-pill ${isReady ? 'ready' : 'pending'}`}>
            <span className="model-pill-dot" />
            <span className="model-pill-text">
              {providerName} · {llm.model}
            </span>
          </div>
        )}

        <button
          type="button"
          className="settings-trigger"
          onClick={onOpenSettings}
          aria-label="Open model settings"
        >
          <Settings2 size={18} />
          <span>Model</span>
        </button>
      </div>
    </header>
  );
}
