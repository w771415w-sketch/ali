let API = (import.meta.env?.VITE_ALI_BACKEND_URL || 'http://127.0.0.1:8765');
async function apiBase() {
  if (window.electronAPI) {
    try {
      const url = await window.electronAPI.getBackendUrl();
      if (url) { API = url; }
    } catch (e) {
    }
  } else {
  }
  return API;
}

async function request(path, options = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), options.timeout ?? 20000);
  try {
    const base = await apiBase();
    const url = `${base}${path}`;
    const response = await fetch(url, {
      ...options,
      headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
      signal: controller.signal,
    });
    const type = response.headers.get('content-type') || '';
    const body = type.includes('application/json') ? await response.json() : await response.text();
    if (!response.ok) {
      throw new Error(typeof body === 'string' ? body : (body.error || `HTTP ${response.status}`));
    }
    return body;
  } catch (error) {
    if (error?.name === 'AbortError') throw new Error('انتهت مهلة الاتصال بـ ALI Runtime.');
    throw error;
  } finally {
    clearTimeout(timeout);
  }
}

async function streamChat(messages, project_dir, model_version = '', onEvent, conversation_id = '', compute_mode = 'auto', externalSignal = null) {
  const controller = externalSignal ? null : new AbortController();
  const signal = externalSignal || controller.signal;
  const timeout = setTimeout(() => controller?.abort(), 10 * 60 * 1000);
  try {
    const base = await apiBase();
    const response = await fetch(`${base}/api/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'text/event-stream' },
      body: JSON.stringify({ messages, project_dir, model_version, conversation_id, compute_mode }),
      signal,
    });
    if (!response.ok || !response.body) {
      const body = await response.text();
      throw new Error(body || `HTTP ${response.status}`);
    }
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const frames = buffer.split('\n\n');
      buffer = frames.pop() || '';
      for (const frame of frames) {
        const line = frame.split('\n').find((x) => x.startsWith('data:'));
        if (!line) continue;
        const raw = line.slice(5).trim();
        if (!raw) continue;
        try { onEvent?.(JSON.parse(raw)); } catch (_) { /* ignore malformed frame */ }
      }
    }
    if (buffer.trim()) {
      const line = buffer.split('\n').find((x) => x.startsWith('data:'));
      if (line) {
        try { onEvent?.(JSON.parse(line.slice(5).trim())); } catch (_) { /* ignore */ }
      }
    }
  } catch (error) {
    if (error?.name === 'AbortError') { const e = new Error('تم إيقاف إنشاء الإجابة.'); e.code = 'ABORTED'; throw e; }
    throw error;
  } finally {
    clearTimeout(timeout);
  }
}

export const api = {
  status: () => request('/api/status', { timeout: 8000 }),
  hardware: () => request('/api/hardware', { timeout: 8000 }),
  chat: (messages, project_dir, model_version = '', conversation_id = '', compute_mode = 'auto') => request('/api/chat', {
    method: 'POST', body: JSON.stringify({ messages, project_dir, model_version, conversation_id, compute_mode }), timeout: 120000,
  }),
  streamChat,
  feedback: (payload) => request('/api/chat/feedback', { method: 'POST', body: JSON.stringify(payload) }),
  correct: (payload) => request('/api/learning/correct', { method: 'POST', body: JSON.stringify(payload) }),
  learningErrors: (limit=100) => request(`/api/learning/errors?limit=${limit}`),
  lineage: () => request('/api/training/lineage'),
  files: (path = '') => request(`/api/files?path=${encodeURIComponent(path)}`),
  readFile: (path) => request(`/api/file?path=${encodeURIComponent(path)}`),
  writeFile: (path, content) => request('/api/file', { method: 'POST', body: JSON.stringify({ path, content }) }),
  createFile: (path, content = '') => request('/api/file', { method: 'POST', body: JSON.stringify({ path, content, create: true }) }),
  deleteFile: (path) => request('/api/file/delete', { method: 'POST', body: JSON.stringify({ path }) }),
  git: () => request('/api/git'),
  models: () => request('/api/models'),
  selectModel: (version, compute_mode='auto') => request('/api/models/select', { method: 'POST', body: JSON.stringify({ version, compute_mode }), timeout: 120000 }),
  promoteModel: (version) => request('/api/models/promote', { method: 'POST', body: JSON.stringify({ version }), timeout: 120000 }),
  memory: (query = '', type = '') => request(`/api/memory?query=${encodeURIComponent(query)}&type=${encodeURIComponent(type)}`),
  saveMemory: (payload) => request('/api/memory', { method: 'POST', body: JSON.stringify(payload) }),
  deleteMemory: (id) => request('/api/memory/delete', { method: 'POST', body: JSON.stringify({ id }) }),
  search: (query) => request(`/api/search?q=${encodeURIComponent(query)}`),
  webSearch: (query) => request('/api/web/search', { method: 'POST', body: JSON.stringify({ query }), timeout: 30000 }),
  settings: () => request('/api/settings', { timeout: 8000 }),
  saveSettings: (settings) => request('/api/settings', { method: 'POST', body: JSON.stringify(settings) }),
  doctor: () => request('/api/doctor', { timeout: 15000 }),
  workspace: (path) => request('/api/workspace', { method: 'POST', body: JSON.stringify({ path }) }),
  training: () => request('/api/training/status', { timeout: 10000 }),
  trainingIngest: (paths) => request('/api/training/ingest', { method: 'POST', body: JSON.stringify({ paths }), timeout: 120000 }),
  trainingStart: (promote = true, compute_mode='auto') => request('/api/training/start', { method: 'POST', body: JSON.stringify({ promote, compute_mode }), timeout: 10000 }),
  trainingCancel: () => request('/api/training/cancel', { method: 'POST', body: JSON.stringify({}), timeout: 10000 }),
  trainingEvents: (runId = '', limit = 100) => request(`/api/training/events?run_id=${encodeURIComponent(runId)}&limit=${limit}`),
  conversations: () => request('/api/conversations?limit=100'),
  conversation: (id) => request(`/api/conversations/detail?id=${encodeURIComponent(id)}`),
  createConversation: (title='محادثة جديدة') => request('/api/conversations', { method: 'POST', body: JSON.stringify({ title }) }),
  renameConversation: (id,title) => request('/api/conversations/rename', { method: 'POST', body: JSON.stringify({ id, title }) }),
  deleteConversation: (id) => request('/api/conversations/delete', { method: 'POST', body: JSON.stringify({ id }) }),
  clearConversation: (id) => request('/api/conversations/clear', { method: 'POST', body: JSON.stringify({ id }) }),
};

export const msg = (e) => e instanceof Error ? e.message : String(e);
