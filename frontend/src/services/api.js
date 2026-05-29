const API_BASE =
  import.meta.env.VITE_API_BASE?.replace(/\/$/, '') || 'http://127.0.0.1:8010';

function apiUrl(path) {
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
