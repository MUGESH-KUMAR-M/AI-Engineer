import { useCallback, useRef, useState } from 'react';
import {
  CheckCircle2,
  FileText,
  Loader2,
  Upload,
  AlertTriangle,
  Files,
  X,
  Zap,
  HardDrive,
  Trash2,
} from 'lucide-react';
import { uploadBulk, uploadSingle } from '../services/api';
import './DocumentUpload.css';

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function DocumentUpload({ onUploadSuccess, ingestionStats }) {
  const [mode, setMode] = useState('single');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [result, setResult] = useState(null);
  const [pendingFiles, setPendingFiles] = useState([]);
  const singleInputRef = useRef(null);
  const bulkInputRef = useRef(null);

  const validatePdf = (file) => {
    if (!file.name.toLowerCase().endsWith('.pdf')) return 'Only PDF files are supported.';
    if (file.size > 50 * 1024 * 1024) return `${file.name} exceeds 50MB.`;
    return null;
  };

  const addPendingFiles = (fileList) => {
    const incoming = Array.from(fileList);
    const errors = [];
    const valid = [];

    for (const file of incoming) {
      const err = validatePdf(file);
      if (err) errors.push(err);
      else valid.push(file);
    }

    if (errors.length) setError(errors[0]);
    else setError(null);

    if (mode === 'single') {
      if (valid.length > 0) setPendingFiles([valid[0]]);
      return;
    }

    setPendingFiles((prev) => {
      const names = new Set(prev.map((f) => f.name));
      const merged = [...prev];
      for (const f of valid) {
        if (!names.has(f.name)) merged.push(f);
      }
      if (merged.length > 20) {
        setError('Maximum 20 PDFs per bulk upload.');
        return merged.slice(0, 20);
      }
      return merged;
    });
  };

  const removePending = (index) => {
    setPendingFiles((prev) => prev.filter((_, i) => i !== index));
    setError(null);
  };

  const clearPending = () => {
    setPendingFiles([]);
    setError(null);
  };

  const runUpload = async () => {
    if (pendingFiles.length === 0) {
      setError('Select at least one PDF to upload.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      if (mode === 'single' && pendingFiles.length === 1) {
        const data = await uploadSingle(pendingFiles[0]);
        setResult({ type: 'single', data });
        setPendingFiles([]);
        onUploadSuccess?.(data);
      } else {
        const data = await uploadBulk(pendingFiles);
        setResult({ type: 'bulk', data });
        setPendingFiles([]);
        onUploadSuccess?.({ filename: `${data.accepted} files`, bulk: true });
      }
    } catch (err) {
      setError(err.message || 'Upload failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') setDragActive(true);
    else if (e.type === 'dragleave') setDragActive(false);
  };

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault();
      e.stopPropagation();
      setDragActive(false);
      if (e.dataTransfer.files?.length) addPendingFiles(e.dataTransfer.files);
    },
    [mode]
  );

  const switchMode = (next) => {
    setMode(next);
    setPendingFiles([]);
    setError(null);
    setResult(null);
  };

  if (result) {
    return (
      <div className="document-upload">
        <div className="upload-success-card">
          <div className="success-icon-wrap">
            <CheckCircle2 size={40} strokeWidth={2} />
          </div>
          <h2>Upload complete</h2>
          <p className="success-subtitle">
            {result.type === 'bulk'
              ? `${result.data.accepted} document(s) queued for batch indexing`
              : 'Your document is being processed'}
          </p>

          {result.type === 'single' ? (
            <div className="success-file-chip">
              <FileText size={18} />
              <span>{result.data.filename}</span>
            </div>
          ) : (
            <ul className="success-file-list">
              {result.data.files?.map((f, i) => (
                <li key={i}>
                  <FileText size={16} />
                  <span>{f.filename}</span>
                  <span className="file-status-tag">Queued</span>
                </li>
              ))}
            </ul>
          )}

          <p className="success-hint">
            {result.type === 'bulk' ? (
              <>
                <Zap size={14} /> Batch mode: extract → embed → ChromaDB in one optimized pass
              </>
            ) : (
              <>Chunking, embedding, and indexing into the knowledge base…</>
            )}
          </p>

          <button type="button" className="btn-upload-primary" onClick={() => setResult(null)}>
            Upload more documents
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="document-upload">
      <div className="upload-page-header">
        <div>
          <h2 className="upload-page-title">Document upload</h2>
          <p className="upload-page-desc">
            Add company policy PDFs to the RAG knowledge base
          </p>
        </div>
        {ingestionStats && (
          <div className="upload-kb-stat">
            <HardDrive size={18} />
            <div>
              <span className="upload-kb-value">{ingestionStats.total_chunks}</span>
              <span className="upload-kb-label">chunks indexed</span>
            </div>
          </div>
        )}
      </div>

      <div className="upload-mode-switch">
        <button
          type="button"
          className={`mode-card ${mode === 'single' ? 'active' : ''}`}
          onClick={() => switchMode('single')}
        >
          <div className="mode-card-icon single">
            <FileText size={22} />
          </div>
          <div className="mode-card-text">
            <strong>Single upload</strong>
            <span>One PDF at a time</span>
          </div>
        </button>
        <button
          type="button"
          className={`mode-card ${mode === 'bulk' ? 'active' : ''}`}
          onClick={() => switchMode('bulk')}
        >
          <div className="mode-card-icon bulk">
            <Files size={22} />
          </div>
          <div className="mode-card-text">
            <strong>Bulk upload</strong>
            <span>Up to 20 PDFs · batch optimized</span>
          </div>
        </button>
      </div>

      <div
        className={`drop-zone ${dragActive ? 'drag-active' : ''} ${isLoading ? 'disabled' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => !isLoading && (mode === 'single' ? singleInputRef : bulkInputRef).current?.click()}
        onKeyDown={(e) => e.key === 'Enter' && singleInputRef.current?.click()}
        role="button"
        tabIndex={0}
      >
        <div className="drop-zone-inner">
          <div className="drop-icon-ring">
            {isLoading ? (
              <Loader2 size={32} className="spin" />
            ) : (
              <Upload size={32} strokeWidth={1.5} />
            )}
          </div>
          <h3>
            {isLoading
              ? 'Uploading…'
              : mode === 'bulk'
                ? 'Drop multiple PDFs here'
                : 'Drop your PDF here'}
          </h3>
          <p>or click to browse · PDF only · max 50MB per file</p>
          {mode === 'bulk' && (
            <span className="drop-badge">
              <Zap size={12} /> Optimized batch indexing
            </span>
          )}
        </div>

        <input
          ref={singleInputRef}
          id="pdf-single-input"
          type="file"
          accept=".pdf,application/pdf"
          hidden
          disabled={isLoading}
          onChange={(e) => {
            if (e.target.files?.length) addPendingFiles(e.target.files);
            e.target.value = '';
          }}
        />
        <input
          ref={bulkInputRef}
          id="pdf-bulk-input"
          type="file"
          accept=".pdf,application/pdf"
          multiple
          hidden
          disabled={isLoading}
          onChange={(e) => {
            if (e.target.files?.length) addPendingFiles(e.target.files);
            e.target.value = '';
          }}
        />
      </div>

      {error && (
        <div className="upload-alert error">
          <AlertTriangle size={18} />
          <span>{error}</span>
        </div>
      )}

      {pendingFiles.length > 0 && (
        <div className="pending-panel">
          <div className="pending-header">
            <h4>
              {mode === 'single' ? 'Selected file' : `${pendingFiles.length} file(s) ready`}
            </h4>
            <button type="button" className="btn-text" onClick={clearPending} disabled={isLoading}>
              <Trash2 size={14} /> Clear all
            </button>
          </div>
          <ul className="pending-list">
            {pendingFiles.map((file, index) => (
              <li key={`${file.name}-${index}`}>
                <FileText size={18} className="pending-file-icon" />
                <div className="pending-file-info">
                  <span className="pending-name">{file.name}</span>
                  <span className="pending-size">{formatSize(file.size)}</span>
                </div>
                <button
                  type="button"
                  className="btn-icon-remove"
                  onClick={(e) => {
                    e.stopPropagation();
                    removePending(index);
                  }}
                  disabled={isLoading}
                  aria-label={`Remove ${file.name}`}
                >
                  <X size={16} />
                </button>
              </li>
            ))}
          </ul>
          <button
            type="button"
            className="btn-upload-primary full-width"
            onClick={(e) => {
              e.stopPropagation();
              runUpload();
            }}
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <Loader2 size={18} className="spin" /> Uploading…
              </>
            ) : mode === 'bulk' ? (
              <>
                <Files size={18} /> Upload {pendingFiles.length} PDF
                {pendingFiles.length > 1 ? 's' : ''} (batch)
              </>
            ) : (
              <>
                <Upload size={18} /> Upload & index document
              </>
            )}
          </button>
        </div>
      )}

      <div className="upload-info-grid">
        <div className="info-card">
          <h5>Single upload</h5>
          <p>Best for one new policy. Processed in the background immediately after upload.</p>
        </div>
        <div className="info-card highlight">
          <h5>
            <Zap size={14} /> Bulk upload
          </h5>
          <p>
            All PDFs are extracted, embedded in batches, and stored in ChromaDB in a single pass —
            faster than uploading files one by one.
          </p>
        </div>
      </div>
    </div>
  );
}
