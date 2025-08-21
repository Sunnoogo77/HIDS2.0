const BASE = import.meta.env.VITE_API_BASE;

export async function fetchJson(path, { method='GET', token, body, form } = {}) {
    const url = `${BASE}${path}`;
    const headers = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;
    if (!form) headers['Content-Type'] = 'application/json';
    const res = await fetch(url, {
        method,
        headers,
        body: form ? body : (body ? JSON.stringify(body) : undefined),
    });
    if (!res.ok) {
        const txt = await res.text().catch(()=> '');
        throw new Error(`HTTP ${res.status} ${res.statusText} — ${txt}`);
    }
    const ct = res.headers.get('content-type') || '';
    return ct.includes('application/json') ? res.json() : res.text();
}

export const api = {
    login: (username, password) =>
        fetchJson('/auth/login', {
        method: 'POST',
        form: true,
        body: new URLSearchParams({ username, password }),
    }),

    me: (token) => fetchJson('/users/me', { token }), // si tu ajoutes l’endpoint plus tard

  // monitoring
    listFiles: (token) => fetchJson('/monitoring/files', { token }),
    createFile: (token, data) => fetchJson('/monitoring/files', { method:'POST', token, body:data }),
    updateFile: (token, id, data) => fetchJson(`/monitoring/files/${id}`, { method:'PUT', token, body:data }),
    deleteFile: (token, id) => fetchJson(`/monitoring/files/${id}`, { method:'DELETE', token }),

    listFolders: (token) => fetchJson('/monitoring/folders', { token }),
    createFolder: (token, data) => fetchJson('/monitoring/folders', { method:'POST', token, body:data }),
    updateFolder: (token, id, data) => fetchJson(`/monitoring/folders/${id}`, { method:'PUT', token, body:data }),
    deleteFolder: (token, id) => fetchJson(`/monitoring/folders/${id}`, { method:'DELETE', token }),

    listIps: (token) => fetchJson('/monitoring/ips', { token }),
    createIp: (token, data) => fetchJson('/monitoring/ips', { method:'POST', token, body:data }),
    updateIp: (token, id, data) => fetchJson(`/monitoring/ips/${id}`, { method:'PUT', token, body:data }),
    deleteIp: (token, id) => fetchJson(`/monitoring/ips/${id}`, { method:'DELETE', token }),

    scanNowFile: (token, id) => fetchJson(`/monitoring/files/${id}/scan-now`, { method:'POST', token }),
    scanNowFolder: (token, id) => fetchJson(`/monitoring/folders/${id}/scan-now`, { method:'POST', token }),
    scanNowIp: (token, id) => fetchJson(`/monitoring/ips/${id}/scan-now`, { method:'POST', token }),

    metrics: (token) => fetchJson('/metrics?limit_events=10', { token }),
    reports: (token) => fetchJson('/reports?limit_events=50', { token }),
    activity: (token, limit=200) => fetchJson(`/activity?limit=${limit}`, { token }),
    users: (token) => fetchJson('/users', { token }) // admin-only
};
