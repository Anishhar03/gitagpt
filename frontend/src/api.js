const ORIGIN = (import.meta.env.VITE_API_ORIGIN || 'http://localhost:8000').replace(/\/$/, '');
const BASE = `${ORIGIN}/api/v1`;


export class ApiError extends Error {
  constructor(message, status = 0) {
    super(message);
    this.status = status;
  }
}


async function request(path, { token, body, headers, ...options } = {}) {
  let response;
  try {
    response = await fetch(`${BASE}${path}`, {
      ...options,
      headers: {
        ...(body instanceof FormData ? {} : { 'Content-Type': 'application/json' }),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...headers,
      },
      body: body instanceof FormData ? body : body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    throw new ApiError('The Gita GPT service is unreachable. Check the running services.');
  }
  if (response.status === 204) return null;
  const payload = await response.json().catch(() => null);
  if (!response.ok) throw new ApiError(payload?.detail || 'The request could not be completed.', response.status);
  return payload;
}


export const api = {
  origin: ORIGIN,
  config: () => request('/config'),
  devLogin: (body) => request('/auth/dev', { method: 'POST', body }),
  googleLogin: (credential) => request('/auth/google', { method: 'POST', body: { credential } }),
  me: (token) => request('/auth/me', { token }),
  conversations: (token) => request('/conversations', { token }),
  conversation: (token, id) => request(`/conversations/${id}`, { token }),
  createConversation: (token, body) => request('/conversations', { token, method: 'POST', body }),
  archiveConversation: (token, id) => request(`/conversations/${id}`, { token, method: 'DELETE' }),
  ask: (token, id, question) => request(`/conversations/${id}/messages`, {
    token, method: 'POST', body: { question },
  }),
  feedback: (token, messageId, rating) => request(`/conversations/messages/${messageId}/feedback`, {
    token, method: 'POST', body: { rating },
  }),
  documents: (token) => request('/knowledge/documents', { token }),
  uploadDocument: (token, form) => request('/knowledge/documents', { token, method: 'POST', body: form }),
  deleteDocument: (token, id) => request(`/knowledge/documents/${id}`, { token, method: 'DELETE' }),
  daily: (token) => request('/knowledge/daily', { token }),
  bookmarks: (token) => request('/knowledge/bookmarks', { token }),
  bookmark: (token, chunkId) => request('/knowledge/bookmarks', {
    token, method: 'POST', body: { chunk_id: chunkId, note: '' },
  }),
  removeBookmark: (token, id) => request(`/knowledge/bookmarks/${id}`, { token, method: 'DELETE' }),
  exportConversation: async (token, id) => {
    const response = await fetch(`${BASE}/conversations/${id}/export`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok) throw new ApiError('Could not export this conversation.', response.status);
    return response.blob();
  },
};
