import { useState, useCallback, useEffect } from 'react';
import { MessageSquare, Upload } from 'lucide-react';
import Header from './components/Header';
import SettingsPanel from './components/SettingsPanel';
import ChatWindow from './components/ChatWindow';
import ChatInput from './components/ChatInput';
import DocumentUpload from './components/DocumentUpload';
import { sendMessage, fetchSystemStatus, fetchIngestStatus } from './services/api';

const LOADING_STAGES = ['embed', 'search', 'generate'];

export default function App() {
  const [activeTab, setActiveTab] = useState('chat');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStage, setLoadingStage] = useState('search');
  const [systemStatus, setSystemStatus] = useState(null);
  const [ingestionStats, setIngestionStats] = useState(null);
  const [uploadedDocs, setUploadedDocs] = useState([]);
  const [settingsOpen, setSettingsOpen] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        const [status, ingest] = await Promise.all([
          fetchSystemStatus(),
          fetchIngestStatus(),
        ]);
        setSystemStatus(status);
        setIngestionStats(ingest);
      } catch {
        /* retry on interval */
      }
    };
    load();
    const interval = setInterval(load, 4000);
    return () => clearInterval(interval);
  }, []);

  const handleSend = useCallback(async (text) => {
    const userMessage = {
      role: 'user',
      content: text,
      timestamp: Date.now(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setLoadingStage('embed');

    const stageTimers = [
      setTimeout(() => setLoadingStage('search'), 400),
      setTimeout(() => setLoadingStage('generate'), 1800),
    ];

    try {
      const data = await sendMessage(text);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.answer,
          sources: data.sources || [],
          timestamp: Date.now(),
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content:
            error.message ||
            'Unable to reach the assistant. Ensure Ollama is running and documents are ingested.',
          sources: [],
          timestamp: Date.now(),
          isError: true,
        },
      ]);
    } finally {
      stageTimers.forEach(clearTimeout);
      setIsLoading(false);
      setLoadingStage('search');
    }
  }, []);

  const handleSuggestionClick = useCallback(
    (text) => handleSend(text),
    [handleSend]
  );

  const handleUploadSuccess = (data) => {
    setUploadedDocs((prev) => [...prev, { ...data, timestamp: Date.now() }]);
    setMessages((prev) => [
      ...prev,
      {
        role: 'assistant',
        content: `Document "${data.filename}" uploaded and indexed into the knowledge base.`,
        sources: [],
        timestamp: Date.now(),
        isSystem: true,
      },
    ]);
    setTimeout(() => setActiveTab('chat'), 1500);
  };

  return (
    <div className="app-container">
      <Header
        systemStatus={systemStatus}
        onOpenSettings={() => setSettingsOpen(true)}
      />
      <SettingsPanel
        open={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        onConfigured={async () => {
          try {
            const status = await fetchSystemStatus();
            setSystemStatus(status);
          } catch {
            /* ignore */
          }
        }}
      />

      <nav className="tab-navigation" aria-label="Main navigation">
        <button
          type="button"
          className={`tab-button ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => setActiveTab('chat')}
        >
          <MessageSquare size={18} />
          <span>Chat</span>
          {ingestionStats?.total_chunks > 0 && (
            <span className="tab-badge">{ingestionStats.total_chunks}</span>
          )}
        </button>
        <button
          type="button"
          className={`tab-button ${activeTab === 'upload' ? 'active' : ''}`}
          onClick={() => setActiveTab('upload')}
        >
          <Upload size={18} />
          <span>Upload PDF</span>
          {uploadedDocs.length > 0 && (
            <span className="tab-badge accent">{uploadedDocs.length}</span>
          )}
        </button>
      </nav>

      <main className="tab-content">
        {activeTab === 'chat' ? (
          <>
            <ChatWindow
              messages={messages}
              isLoading={isLoading}
              loadingStage={loadingStage}
              onSuggestionClick={handleSuggestionClick}
            />
            <ChatInput onSend={handleSend} disabled={isLoading} />
          </>
        ) : (
          <div className="upload-tab">
            <DocumentUpload
              onUploadSuccess={handleUploadSuccess}
              ingestionStats={ingestionStats}
            />
          </div>
        )}
      </main>
    </div>
  );
}
