// src/lib/api.js
const BASE = import.meta.env.VITE_API_BASE || "";
console.log("API base:", BASE);

async function fetchJson(path, { method = "GET", token, body, form } = {}) {
    const url = `${BASE}${path}`;
    const headers = {};
    if (token) headers["Authorization"] = `Bearer ${token}`;
    if (!form) headers["Content-Type"] = "application/json";

    const res = await fetch(url, {
        method,
        headers,
        body: form ? body : body ? JSON.stringify(body) : undefined,
    });

    const ct = res.headers.get("content-type") || "";
    const txt = await res.text();

    if (!res.ok) {
        let data = null;
        try { if (ct.includes("application/json")) data = JSON.parse(txt); } catch {}
        const err = new Error(`HTTP ${res.status} ${res.statusText}`);
        err.status = res.status;
        err.body = data ?? txt;
        throw err;
    }
    try { return ct.includes("application/json") ? JSON.parse(txt) : txt; }
    catch { return txt; }
}

/* -------------------------------- Utilities -------------------------------- */
const qs = (obj = {}) =>
    Object.entries(obj)
        .filter(([, v]) => v !== undefined && v !== null && v !== "")
        .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
        .join("&");

/* ------------------------------ Public API --------------------------------- */
export const api = {
    /* ------------------ Auth ------------------ */
    login: (username, password) =>
        fetchJson("/auth/login", {
        method: "POST",
        form: true,
        body: new URLSearchParams({ username, password }),
        }),
    me: (t) => fetchJson("/users/me", { token: t }),

    /* -------------- Monitoring --------------- */
    listFiles:   (t)        => fetchJson("/monitoring/files", { token: t }),
    createFile:  (t, d)     => fetchJson("/monitoring/files", { method: "POST", token: t, body: d }),
    updateFile:  (t, id, d) => fetchJson(`/monitoring/files/${id}`, { method: "PUT", token: t, body: d }),
    deleteFile:  (t, id)    => fetchJson(`/monitoring/files/${id}`, { method: "DELETE", token: t }),
    scanNowFile: (t, id)    => fetchJson(`/monitoring/files/${id}/scan-now`, { method: "POST", token: t }),

    listFolders: (t)        => fetchJson("/monitoring/folders", { token: t }),
    createFolder:(t, d)     => fetchJson("/monitoring/folders", { method: "POST", token: t, body: d }),
    updateFolder:(t, id, d) => fetchJson(`/monitoring/folders/${id}`, { method: "PUT", token: t, body: d }),
    deleteFolder:(t, id)    => fetchJson(`/monitoring/folders/${id}`, { method: "DELETE", token: t }),
    scanNowFolder:(t, id)   => fetchJson(`/monitoring/folders/${id}/scan-now`, { method: "POST", token: t }),

    listIps:     (t)        => fetchJson("/monitoring/ips", { token: t }),
    createIp:    (t, d)     => fetchJson("/monitoring/ips", { method: "POST", token: t, body: d }),
    updateIp:    (t, id, d) => fetchJson(`/monitoring/ips/${id}`, { method: "PUT", token: t, body: d }),
    deleteIp:    (t, id)    => fetchJson(`/monitoring/ips/${id}`, { method: "DELETE", token: t }),
    scanNowIp:   (t, id)    => fetchJson(`/monitoring/ips/${id}/scan-now`, { method: "POST", token: t }),

    setFileFreq:   (t, id, frequency) => fetchJson(`/monitoring/files/${id}`,   { method: "PUT", token: t, body: { frequency } }),
    setFolderFreq: (t, id, frequency) => fetchJson(`/monitoring/folders/${id}`, { method: "PUT", token: t, body: { frequency } }),
    setIpFreq:     (t, id, frequency) => fetchJson(`/monitoring/ips/${id}`,     { method: "PUT", token: t, body: { frequency } }),

    /* ----------------- Metrics/Reports ---------------- */
    metrics: (t) => fetchJson("/metrics?limit_events=10", { token: t }),
    reports: (t) => fetchJson("/reports?limit_events=50", { token: t }),

    /* ---------------- Alerts & Activity (LOG FILE FIRST) --------------- */
    listHidsLog: async (t, { type = "activity", page = 1, limit = 10, level = "", contains = "" } = {}) => {
        try {
        const r = await fetchJson(`/logs/hids?${qs({ log_type: type, page, limit, level, contains })}`, { token: t });
        return { lines: r.lines, page_count: r.page_count, total: r.total };
        } catch (e) {
        // Fallback si l’endpoint n’existe pas encore
        if (e.status === 404) {
            if (type === "activity") {
            const a = await fetchJson(`/activity?${qs({ limit, offset: (page - 1) * limit })}`, { token: t });
            const items = a?.items || a || [];
            return { lines: items.map(x => ({ ts: x.ts, level: x.level || "INFO", source: x.kind || x.entity_type, msg: x.message || x.raw || "" })), page_count: 1, total: items.length };
            } else {
            const al = await fetchJson(`/alerts?${qs({ limit, offset: (page - 1) * limit })}`, { token: t });
            const items = al?.items || al || [];
            return { lines: items.map(x => ({ ts: x.ts, level: x.severity || "INFO", source: x.entity_type, msg: x.message || "" })), page_count: 1, total: items.length };
            }
        }
        throw e;
        }
    },
    clearHidsLog: (t, type) =>
        fetchJson("/logs/hids/clear", { method: "POST", token: t, body: { type } }),
    // purge avancée: type=activity|alerts, level=..., from=ISO, to=ISO
    purgeHidsLog: (t, { type, level, from, to }) =>
        fetchJson("/logs/hids/purge", { method: "POST", token: t, body: { type, level, from, to } }),

    // Compat list
    listAlerts: (t, { limit, offset, severity, entity_type } = {}) =>
        fetchJson(`/alerts?${qs({ limit, offset, severity, entity_type })}`, { token: t })
        .then((res) => Array.isArray(res) ? ({ items: res, total: res.length }) :
            ({ items: res.items || [], total: res.total ?? res.count ?? (res.items || []).length })),
    listActivity: (t, { limit, offset, kind, entity_type } = {}) =>
        fetchJson(`/activity?${qs({ limit, offset, kind, entity_type })}`, { token: t })
        .then((res) => Array.isArray(res) ? ({ items: res, total: res.length }) :
            ({ items: res.items || [], total: res.total ?? res.count ?? (res.items || []).length })),

    /* ---------------- Users (Settings) --------------- */
    listUsers:   (t)                 => fetchJson("/users", { token: t }),
    createUser:  (t, { username, email, password, is_admin }) =>
        fetchJson("/users", { method: "POST", token: t, body: { username, email, password, is_admin: !!is_admin } }),
//     updateUserPassword: (t, id, { password }) =>
//         fetchJson(`/users/${id}/password`, { method: "PUT", token: t, body: { password } }),
    updateUserPassword: (t, id, { password }) =>
    fetchJson(`/users/${id}/password`, {
        method: "PUT",
        token: t,
        body: { new_password: password }   // <-- attendu par l’API
    }),
    
    deleteUser:  (t, id)             => fetchJson(`/users/${id}`, { method: "DELETE", token: t }),

    /* ---------------- Engine all-in-one --------------- */
    engineState: (t)                 => fetchJson("/engine/state", { token: t }),
    startAll:    (t)                 => fetchJson("/engine/all/start", { method: "POST", token: t }),
    stopAll:     (t)                 => fetchJson("/engine/all/stop",  { method: "POST", token: t }),

    /* utilitaire */
    fetchJson,
};
export default api;
