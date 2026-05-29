import { useEffect, useState } from 'react';
import {
  X,
  Key,
  Check,
  Cpu,
  Cloud,
  Sparkles,
  Loader2,
} from 'lucide-react';
import { configureProvider, fetchProviders } from '../services/api';

const PROVIDER_ICONS = {
  ollama: Cpu,
  openai: Sparkles,
  anthropic: Cloud,
  gemini: Sparkles,
  groq: Cloud,
};

export default function SettingsPanel({ open, onClose, onConfigured }) {
  const [catalog, setCatalog] = useState(null);
  const [selectedProvider, setSelectedProvider] = useState('ollama');
  const [selectedModel, setSelectedModel] = useState('phi3');
  const [apiKey, setApiKey] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    if (!open) return;
    fetchProviders()
      .then((data) => {
        setCatalog(data);
        setSelectedProvider(data.active.provider);
        setSelectedModel(data.active.model);
        setApiKey('');
        setError('');
        setSuccess('');
      })
      .catch(() => setError('Could not load provider settings.'));
  }, [open]);

  const current = catalog?.providers?.find((p) => p.id === selectedProvider);

  const handleSave = async () => {
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      const result = await configureProvider({
        provider: selectedProvider,
        model: selectedModel,
        api_key: apiKey.trim() || undefined,
      });
      setSuccess(result.message);
      setApiKey('');
      onConfigured?.();
      const refreshed = await fetchProviders();
      setCatalog(refreshed);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  if (!open) return null;

  return (
    <div className="settings-overlay" onClick={onClose} role="presentation">
      <aside
        className="settings-panel"
        onClick={(e) => e.stopPropagation()}
        aria-label="AI model settings"
      >
        <div className="settings-header">
          <div>
            <h2>AI Model Settings</h2>
            <p>Default is Ollama (local). Paste an API key to use cloud models.</p>
          </div>
          <button type="button" className="icon-btn" onClick={onClose} aria-label="Close">
            <X size={20} />
          </button>
        </div>

        <div className="settings-body">
          {error && <div className="settings-alert error">{error}</div>}
          {success && <div className="settings-alert success">{success}</div>}

          <label className="settings-label">Provider</label>
          <div className="provider-grid">
            {catalog?.providers?.map((p) => {
              const Icon = PROVIDER_ICONS[p.id] || Cloud;
              const active = selectedProvider === p.id;
              return (
                <button
                  key={p.id}
                  type="button"
                  className={`provider-card ${active ? 'active' : ''}`}
                  onClick={() => {
                    setSelectedProvider(p.id);
                    setSelectedModel(p.default_model);
                    setApiKey('');
                  }}
                >
                  <Icon size={18} />
                  <span className="provider-name">{p.name}</span>
                  {p.requires_api_key && (
                    <span
                      className={`key-badge ${p.api_key_configured ? 'ok' : 'missing'}`}
                    >
                      {p.api_key_configured ? 'Key set' : 'Key needed'}
                    </span>
                  )}
                </button>
              );
            })}
          </div>

          {current && (
            <>
              <label className="settings-label" htmlFor="model-select">
                Model
              </label>
              <select
                id="model-select"
                className="settings-select"
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
              >
                {current.models.map((m) => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))}
              </select>

              {current.requires_api_key && (
                <>
                  <label className="settings-label" htmlFor="api-key">
                    API Key
                    {current.api_key_hint && (
                      <span className="key-hint"> Current: {current.api_key_hint}</span>
                    )}
                  </label>
                  <div className="api-key-row">
                    <Key size={16} className="key-icon" />
                    <input
                      id="api-key"
                      type="password"
                      className="settings-input"
                      placeholder={`Paste ${current.name} API key`}
                      value={apiKey}
                      onChange={(e) => setApiKey(e.target.value)}
                      autoComplete="off"
                    />
                  </div>
                  <p className="settings-hint">
                    Leave blank to keep the existing key. Keys are stored locally in{' '}
                    <code>data/runtime_config.json</code>.
                  </p>
                </>
              )}

              {selectedProvider === 'ollama' && (
                <p className="settings-hint">
                  Ensure Ollama is running: <code>ollama serve</code> and pull your model:{' '}
                  <code>ollama pull phi3</code>
                </p>
              )}
            </>
          )}
        </div>

        <div className="settings-footer">
          <button type="button" className="btn-secondary" onClick={onClose}>
            Cancel
          </button>
          <button
            type="button"
            className="btn-primary"
            onClick={handleSave}
            disabled={saving}
          >
            {saving ? (
              <>
                <Loader2 size={16} className="spin-inline" /> Saving…
              </>
            ) : (
              <>
                <Check size={16} /> Apply model
              </>
            )}
          </button>
        </div>
      </aside>
    </div>
  );
}
