import { Cpu, Database, Sparkles } from 'lucide-react';

export default function Header({ systemStatus }) {
  const rag = systemStatus?.rag;
  const llm = systemStatus?.llm;
  const ollama = systemStatus?.ollama;

  const isOnline =
    systemStatus?.status === 'ok' ||
    (rag?.chunks > 0 && llm?.ready);

  const statusLabel = isOnline
    ? llm?.provider === 'ollama'
      ? `Ollama · ${llm?.model || 'local'}`
      : 'Online'
    : 'Connecting…';

  return (
    <header className="header">
      <div className="header-logo">
        <Sparkles size={22} strokeWidth={2} />
      </div>
      <div className="header-text">
        <div className="header-title">SWS AI Assistant</div>
        <div className="header-subtitle">RAG-Powered Company Policy Chatbot</div>
      </div>

      <div className="header-metrics">
        {rag && (
          <div className="header-metric" title="Indexed document chunks">
            <Database size={14} />
            <span>{rag.chunks} chunks</span>
          </div>
        )}
        {llm?.provider === 'ollama' && (
          <div
            className={`header-metric ${ollama?.model_ready ? 'ready' : 'warn'}`}
            title="Local LLM via Ollama"
          >
            <Cpu size={14} />
            <span>{ollama?.model_ready ? 'Ollama' : 'Ollama starting'}</span>
          </div>
        )}
      </div>

      <div className={`header-status ${isOnline ? 'online' : 'offline'}`}>
        <div className="header-status-dot" />
        <span className="header-status-text">{statusLabel}</span>
      </div>
    </header>
  );
}
