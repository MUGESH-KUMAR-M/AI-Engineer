const API_BASE =
  import.meta.env.VITE_API_BASE?.replace(/\/$/, '') || 'http://127.0.0.1:8010';

export function apiUrl(path) {
  return `${API_BASE}${path.startsWith('/') ? path : `/${path}`}`;
}

export async function sendMessage(question) {
  const response = await fetch(apiUrl('/api/chat'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to get response from the assistant');
  }
  return response.json();
}

export async function fetchSystemStatus() {
  const response = await fetch(apiUrl('/api/status'));
  if (!response.ok) {
    throw new Error('Status unavailable');
  }
  return response.json();
}

export async function fetchIngestStatus() {
  const response = await fetch(apiUrl('/api/ingest-status'));
  if (!response.ok) {
    throw new Error('Ingest status unavailable');
  }
  return response.json();
}

export async function fetchProviders() {
  const response = await fetch(apiUrl('/api/providers'));
  if (!response.ok) {
    throw new Error('Could not load providers');
  }
  return response.json();
}

/** Upload one or more PDFs — always POST /api/upload with field name ``file`` */
export async function uploadFiles(files) {
  const list = Array.isArray(files) ? files : [files];
  const formData = new FormData();
  for (const f of list) {
    formData.append('file', f);
  }

  let response = await fetch(apiUrl('/api/upload'), {
    method: 'POST',
    body: formData,
  });

  // Fallback: try legacy bulk path if unified route missing (old server)
  if (response.status === 404 && list.length > 1) {
    const bulkForm = new FormData();
    for (const f of list) {
      bulkForm.append('files', f);
    }
    response = await fetch(apiUrl('/api/upload/bulk'), {
      method: 'POST',
      body: bulkForm,
    });
  }

  // Old backend: single-file handler only — upload one at a time
  if (!response.ok && list.length > 1 && (response.status === 422 || response.status === 400)) {
    const results = [];
    for (const f of list) {
      const single = new FormData();
      single.append('file', f);
      const r = await fetch(apiUrl('/api/upload'), { method: 'POST', body: single });
      if (!r.ok) {
        const err = await r.json().catch(() => ({}));
        throw new Error(err.detail || `Upload failed for ${f.name}`);
      }
      results.push(await r.json());
    }
    return {
      accepted: results.length,
      files: list.map((f) => ({ filename: f.name, status: 'queued' })),
      message: `${results.length} file(s) queued (sequential upload).`,
    };
  }

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    const detail = err.detail;
    const msg = Array.isArray(detail)
      ? detail.map((d) => d.msg || d).join(', ')
      : detail || 'Upload failed';
    throw new Error(msg);
  }

  const data = await response.json();

  // Normalize bulk shape for UI
  if (list.length > 1 && !data.files) {
    return {
      accepted: data.accepted || list.length,
      files: list.map((f) => ({ filename: f.name, status: 'queued' })),
      message: data.message,
    };
  }

  return data;
}

export async function uploadSingle(file) {
  return uploadFiles([file]);
}

export async function uploadBulk(files) {
  const data = await uploadFiles(files);
  return {
    accepted: data.accepted || files.length,
    files: data.files || files.map((f) => ({ filename: f.name, status: 'queued' })),
    message: data.message,
  };
}

export async function configureProvider({ provider, model, api_key }) {
  const response = await fetch(apiUrl('/api/providers/configure'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ provider, model, api_key }),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to save provider settings');
  }
  return response.json();
}
