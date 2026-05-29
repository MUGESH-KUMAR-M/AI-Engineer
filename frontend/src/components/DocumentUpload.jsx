import { useState } from 'react';
import './DocumentUpload.css';

export default function DocumentUpload({ onUploadSuccess }) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploadStats, setUploadStats] = useState(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const handleFileSelect = (e) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const handleFileUpload = async (file) => {
    if (!file.name.endsWith('.pdf')) {
      setError('❌ Only PDF files are supported');
      return;
    }

    if (file.size > 50 * 1024 * 1024) {
      setError('❌ File size exceeds 50MB limit');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Upload failed');
      }

      const data = await response.json();
      setUploadStats({
        filename: data.filename,
        pages: data.pages,
        chunks: data.chunks,
      });
      setError(null);
      onUploadSuccess(data);
    } catch (err) {
      setError(`❌ ${err.message || 'Upload failed'}`);
      console.error('Upload error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="document-upload">
      {uploadStats ? (
        <div className="upload-complete">
          <div className="success-check">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
              <polyline points="20 6 9 17 4 12" />
            </svg>
          </div>
          <h2>Upload Successful!</h2>
          <div className="stats">
            <p><strong>File:</strong> {uploadStats.filename}</p>
            <p><strong>Pages:</strong> {uploadStats.pages}</p>
            <p><strong>Chunks:</strong> {uploadStats.chunks}</p>
          </div>
          <p className="processing-note">📝 Document is being processed and will be available for queries shortly...</p>
          <button 
            className="upload-another-btn"
            onClick={() => setUploadStats(null)}
          >
            Upload Another Document
          </button>
        </div>
      ) : (
        <>
          <div
            className={`upload-area ${dragActive ? 'active' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <svg className="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>

            <h3>Upload Company Policy Document</h3>
            <p>Drag and drop your PDF here or click to browse</p>
            <p className="upload-hint">Maximum file size: 50MB</p>

            <input
              type="file"
              accept=".pdf"
              onChange={handleFileSelect}
              disabled={isLoading}
              style={{ display: 'none' }}
              id="file-input"
            />

            <label htmlFor="file-input" className="file-input-label">
              {isLoading ? '⏳ Uploading...' : '📁 Choose PDF File'}
            </label>
          </div>

          {error && <div className="upload-error">⚠️ {error}</div>}

          {isLoading && (
            <div className="upload-progress">
              <div className="spinner"></div>
              <p>Processing your document...</p>
              <p className="progress-hint">This may take a minute for larger files</p>
            </div>
          )}

          <div className="supported-types">
            <h4>Supported Documents:</h4>
            <ul>
              <li>📄 Company Policies</li>
              <li>📋 HR Guidelines</li>
              <li>🔒 Security Policies</li>
              <li>🎯 Standard Procedures</li>
              <li>📊 Reports & Guidelines</li>
            </ul>
          </div>
        </>
      )}
    </div>
  );
}
