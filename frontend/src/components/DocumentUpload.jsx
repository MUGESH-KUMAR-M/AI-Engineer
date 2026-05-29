import { useState } from 'react';
import {
  CheckCircle2,
  FileText,
  Loader2,
  Upload,
  AlertTriangle,
} from 'lucide-react';
import { apiUrl } from '../services/api';
import './DocumentUpload.css';

export default function DocumentUpload({ onUploadSuccess }) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploadStats, setUploadStats] = useState(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') setDragActive(true);
    else if (e.type === 'dragleave') setDragActive(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files?.[0]) handleFileUpload(e.dataTransfer.files[0]);
  };

  const handleFileSelect = (e) => {
    if (e.target.files?.[0]) handleFileUpload(e.target.files[0]);
  };

  const handleFileUpload = async (file) => {
    if (!file.name.endsWith('.pdf')) {
      setError('Only PDF files are supported.');
      return;
    }
    if (file.size > 50 * 1024 * 1024) {
      setError('File size exceeds 50MB limit.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await fetch(apiUrl('/api/upload'), {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Upload failed');
      }
      const data = await response.json();
      setUploadStats({ filename: data.filename });
      onUploadSuccess(data);
    } catch (err) {
      setError(err.message || 'Upload failed');
    } finally {
      setIsLoading(false);
    }
  };

  if (uploadStats) {
    return (
      <div className="document-upload">
        <div className="upload-complete">
          <CheckCircle2 className="success-icon" size={48} />
          <h2>Upload successful</h2>
          <p className="upload-filename">{uploadStats.filename}</p>
          <p className="processing-note">
            Document is being chunked, embedded, and added to ChromaDB.
          </p>
          <button
            type="button"
            className="upload-another-btn"
            onClick={() => setUploadStats(null)}
          >
            Upload another PDF
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="document-upload">
      <div
        className={`upload-area ${dragActive ? 'active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <Upload className="upload-icon" size={40} strokeWidth={1.5} />
        <h3>Upload company policy PDF</h3>
        <p>Drag and drop or click to browse · Max 50MB</p>
        <input
          type="file"
          accept=".pdf"
          onChange={handleFileSelect}
          disabled={isLoading}
          id="file-input"
          hidden
        />
        <label htmlFor="file-input" className="file-input-label">
          {isLoading ? (
            <>
              <Loader2 size={16} className="spin-inline" /> Uploading…
            </>
          ) : (
            <>
              <FileText size={16} /> Choose PDF
            </>
          )}
        </label>
      </div>

      {error && (
        <div className="upload-error">
          <AlertTriangle size={18} />
          {error}
        </div>
      )}

      <div className="supported-types">
        <h4>Supported documents</h4>
        <ul>
          <li>HR & leave policies</li>
          <li>IT security & code of conduct</li>
          <li>Benefits, WFH & onboarding</li>
        </ul>
      </div>
    </div>
  );
}
