import { useState, useCallback, useEffect } from 'react';
import Header from './components/Header';
import ChatWindow from './components/ChatWindow';
import ChatInput from './components/ChatInput';
import DocumentUpload from './components/DocumentUpload';
import './App.css';
import { sendMessage } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('chat');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(null);
  const [documentCount, setDocumentCount] = useState(0);
  const [ingestionStats, setIngestionStats] = useState(null);
  const [uploadedDocs, setUploadedDocs] = useState([]);

  // Fetch ingestion status periodically
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch('/api/ingest-status');
        if (response.ok) {
          const data = await response.json();
          setIngestionStats(data);
        }
      } catch (error) {
        console.log('Could not fetch status');
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleSend = useCallback(
    async (text) => {
      // Add user message
      const userMessage = {
        role: 'user',
        content: text,
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);

      try {
        const data = await sendMessage(text);
        const assistantMessage = {
          role: 'assistant',
          content: data.answer,
          sources: data.sources || [],
          timestamp: Date.now(),
        };
        setMessages((prev) => [...prev, assistantMessage]);
      } catch (error) {
        const errorMessage = {
          role: 'assistant',
          content:
            'Sorry, I encountered an error while processing your request. Please try again.',
          sources: [],
          timestamp: Date.now(),
          isError: true,
        };
        setMessages((prev) => [...prev, errorMessage]);
        console.error('Chat error:', error);
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const handleSuggestionClick = useCallback(
    (text) => {
      handleSend(text);
    },
    [handleSend]
  );

  const handleUploadSuccess = (data) => {
    setUploadSuccess(data);
    setDocumentCount((prev) => prev + 1);
    setUploadedDocs((prev) => [...prev, { ...data, timestamp: Date.now() }]);

    const systemMessage = {
      role: 'assistant',
      content: `✓ Document "${data.filename}" uploaded! Processing in background...`,
      sources: [],
      timestamp: Date.now(),
      isSystem: true,
    };
    setMessages((prev) => [...prev, systemMessage]);

    setTimeout(() => {
      setActiveTab('chat');
      setUploadSuccess(null);
    }, 2000);
  };

  return (
    <div className="app-container">
      <Header />
      
      {/* Tab Navigation */}
      <div className="tab-navigation">
        <button
          className={`tab-button ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => setActiveTab('chat')}
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
          Chat with AI
          {ingestionStats && (
            <span className="badge">{ingestionStats.total_chunks}</span>
          )}
        </button>
        
        <button
          className={`tab-button ${activeTab === 'upload' ? 'active' : ''}`}
          onClick={() => setActiveTab('upload')}
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="17 8 12 3 7 8" />
            <line x1="12" y1="3" x2="12" y2="15" />
          </svg>
          Upload Documents
          {documentCount > 0 && <span className="badge">{documentCount}</span>}
        </button>
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {activeTab === 'chat' ? (
          <>
            <ChatWindow
              messages={messages}
              isLoading={isLoading}
              onSuggestionClick={handleSuggestionClick}
            />
            <ChatInput onSend={handleSend} disabled={isLoading} />
          </>
        ) : (
          <div className="upload-tab">
            <DocumentUpload onUploadSuccess={handleUploadSuccess} />

            {uploadedDocs.length > 0 && (
              <div className="uploaded-documents-section">
                <h3>📚 Recent Uploads</h3>
                <ul className="docs-list">
                  {uploadedDocs.map((doc, idx) => (
                    <li key={idx} className="doc-item">
                      <span className="doc-icon">📄</span>
                      <span className="doc-name">{doc.filename}</span>
                      <span className="doc-status">✓ Processing</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {ingestionStats && (
              <div className="stats-section">
                <h3>📊 Knowledge Base Stats</h3>
                <div className="stats-grid">
                  <div className="stat-box">
                    <span className="stat-number">{ingestionStats.total_chunks}</span>
                    <span className="stat-label">Document Chunks</span>
                  </div>
                  <div className="stat-box">
                    <span className="stat-icon-large">💾</span>
                    <span className="stat-label">Vector Database</span>
                  </div>
                </div>
              </div>
            )}

            {uploadSuccess && (
              <div className="upload-success-banner">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="20 6 9 17 4 12" />
                </svg>
                <span>Document received! Processing...</span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
