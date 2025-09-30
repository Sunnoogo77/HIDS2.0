// Fichier : src/pages/Settings.jsx

import { useEffect, useMemo, useState } from "react";
import { useAuth } from "../context/AuthProvider";
import { api } from "../lib/api";
import { Pencil, Trash2, Check, X, Play, Pause, Square } from "lucide-react";

/* ---------- UI helpers ---------- */
const Badge = ({ children, tone = "muted" }) => {
    const map = {
        ok: "bg-emerald-500/20 text-emerald-300",
        warn: "bg-amber-500/20 text-amber-300",
        danger: "bg-red-500/20 text-red-300",
        muted: "bg-white/5 text-muted",
        info: "bg-sky-500/20 text-sky-300",
        role: "bg-purple-500/20 text-purple-300",
    };
    return (
        <span className={`px-2 py-0.5 rounded-full text-xs border border-white/10 ${map[tone]}`}>
        {children}
        </span>
    );
};

const IconButton = ({ title, onClick, children, disabled=false }) => (
    <button
        className="p-2 rounded-md border border-white/10 bg-panel2 hover:bg-panel transition disabled:opacity-50 disabled:cursor-not-allowed"
        title={title}
        aria-label={title}
        onClick={onClick}
        disabled={disabled}
    >
        {children}
    </button>
);

/* ---------- Modal: Add / Edit password ---------- */
function UserModal({ open, mode, user, onClose, onSave, disabled }) {
    const [username, setUsername] = useState(user?.username || "");
    const [email, setEmail] = useState(user?.email || "");
    const [isAdmin, setIsAdmin] = useState(!!user?.is_admin);
    const [password, setPassword] = useState("");
    const [confirm, setConfirm] = useState("");

    useEffect(() => {
        if (open) {
        setUsername(user?.username || "");
        setEmail(user?.email || "");
        setIsAdmin(!!user?.is_admin);
        setPassword("");
        setConfirm("");
        }
    }, [open, user]);

    if (!open) return null;

    const canSave =
        !disabled &&
        ((mode === "add" && username && email && password && password === confirm) ||
        (mode === "edit" && password && password === confirm));

    const submit = () => {
        if (!canSave) return;
        if (mode === "add") onSave({ username, email, password, is_admin: isAdmin });
        else onSave({ password });
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
        <div className="absolute inset-0 bg-black/60" onClick={onClose} />
        <div className="relative z-10 w-[460px] rounded-xl bg-panel p-4 border border-white/10 shadow-lg">
            <div className="text-lg font-medium mb-4">
            {mode === "add" ? "Add user" : `Change password — ${user?.username}`}
            </div>

            {disabled && (
            <div className="mb-3 px-3 py-2 rounded-md bg-red-500/20 text-red-300">
                Admin required to perform this action.
            </div>
            )}

            <div className="grid gap-3">
            {mode === "add" && (
                <>
                <div className="grid gap-1.5">
                    <label className="text-xs text-muted">Username</label>
                    <input
                    className="bg-panel2 border border-white/10 rounded-md px-3 py-2 disabled:opacity-50"
                    value={username}
                    onChange={e=>setUsername(e.target.value)}
                    placeholder="jdoe"
                    disabled={disabled}
                    />
                </div>
                <div className="grid gap-1.5">
                    <label className="text-xs text-muted">Email</label>
                    <input
                    type="email"
                    className="bg-panel2 border border-white/10 rounded-md px-3 py-2 disabled:opacity-50"
                    value={email}
                    onChange={e=>setEmail(e.target.value)}
                    placeholder="jdoe@example.com"
                    disabled={disabled}
                    />
                </div>
                </>
            )}

            <div className="grid gap-1.5">
                <label className="text-xs text-muted">New password</label>
                <input
                type="password"
                className="bg-panel2 border border-white/10 rounded-md px-3 py-2 disabled:opacity-50"
                value={password}
                onChange={e=>setPassword(e.target.value)}
                placeholder="********"
                disabled={disabled}
                />
            </div>
            <div className="grid gap-1.5">
                <label className="text-xs text-muted">Confirm password</label>
                <div className="relative">
                <input
                    type="password"
                    className={`w-full bg-panel2 border rounded-md px-3 py-2 disabled:opacity-50 ${
                    password && confirm && password!==confirm ? "border-red-500" : "border-white/10"
                    }`}
                    value={confirm}
                    onChange={e=>setConfirm(e.target.value)}
                    placeholder="********"
                    disabled={disabled}
                />
                {password && confirm && password===confirm && (
                    <span className="absolute right-3 top-1/2 -translate-y-1/2 text-emerald-400"><Check size={16}/></span>
                )}
                {password && confirm && password!==confirm && (
                    <span className="absolute right-3 top-1/2 -translate-y-1/2 text-red-400"><X size={16}/></span>
                )}
                </div>
            </div>

            {mode === "add" && (
                <label className="inline-flex items-center gap-2 mt-1 select-none">
                <input type="checkbox" checked={isAdmin} onChange={e=>setIsAdmin(e.target.checked)} disabled={disabled}/>
                <span>Administrator</span>
                </label>
            )}
            </div>

            <div className="mt-4 flex justify-end gap-2">
            <button className="px-3 py-1.5 rounded-md bg-panel/50 border border-white/10" onClick={onClose}>Cancel</button>
            <button className="px-3 py-1.5 rounded-md bg-green-600 hover:bg-green-700 text-white disabled:opacity-50" disabled={!canSave} onClick={submit}>
                Save
            </button>
            </div>
        </div>
        </div>
    );
    }

/* ---------- Main page ---------- */
export default function Settings() {
    const { token, user } = useAuth();
    const isAdmin = !!user?.is_admin;

    const [tab, setTab] = useState("users"); // users | machines | logs

    /* Users */
    const [users, setUsers] = useState([]);
    const [uLoading, setULoading] = useState(false);
    const [uMsg, setUMsg] = useState(null); // on ne l'utilise plus pour "loaded", seulement pour erreurs
    const [modal, setModal] = useState({ open:false, mode:"add", user:null });

    // NEW: search, role filter, pagination
    const [query, setQuery] = useState("");
    const [roleFilter, setRoleFilter] = useState("all"); // all | admin | standard
    const [page, setPage] = useState(1);
    const pageSize = 7;

    const loadUsers = async () => {
        setULoading(true);
        setUMsg(null);
        try {
        const rows = await api.listUsers(token);
        setUsers(rows || []);
        } catch (e) {
        setUMsg({ type:"error", text: e?.body?.detail || "Failed to load users" });
        } finally {
        setULoading(false);
        }
    };

    useEffect(() => {
        if (tab === "users" && isAdmin) {
        loadUsers();
        } else if (tab === "users" && !isAdmin) {
        setUsers([]);
        setUMsg({ type: "warning", text: "Admin privileges are required to view users." });
        }
    }, [tab, isAdmin]); // eslint-disable-line

    // reset pagination quand on change les filtres
    useEffect(() => { setPage(1); }, [query, roleFilter]);

    // Filtres + pagination (client-side)
    const filtered = useMemo(() => {
        const q = query.trim().toLowerCase();
        return (users || []).filter(u => {
        const matchesRole =
            roleFilter === "all" ? true :
            roleFilter === "admin" ? !!u.is_admin :
            !u.is_admin;

        const matchesQuery = !q || [u.username, u.email]
            .some(x => (x || "").toLowerCase().includes(q));

        return matchesRole && matchesQuery;
        });
    }, [users, query, roleFilter]);

    const pageCount = Math.max(1, Math.ceil(filtered.length / pageSize));
    const currentPage = Math.min(page, pageCount);
    const start = (currentPage - 1) * pageSize;
    const visibleUsers = filtered.slice(start, start + pageSize);

    const doAdd = () => setModal({ open:true, mode:"add", user:null });
    const doEdit = (user) => setModal({ open:true, mode:"edit", user });
    const doDelete = async (u) => {
        try { await api.deleteUser(token, u.id); loadUsers(); }
        catch (e) { setUMsg({ type:"error", text: e?.body?.detail || "Delete failed" }); }
    };
    const saveUser = async (payload) => {
        try {
        if (modal.mode === "add") { await api.createUser(token, payload); }
        else { await api.updateUserPassword(token, modal.user.id, payload); }
        setModal({ open:false, mode:"add", user:null });
        loadUsers();
        } catch (e) { setUMsg({ type:"error", text: e?.body?.detail || "Save failed" }); }
    };

    /* Machines */
    const [mState, setMState] = useState("stopped"); // running|stopped|loading
    const [metrics, setMetrics] = useState(null);
    const refreshMachines = async () => {
        try {
        const [state, m] = await Promise.all([api.engineState(token), api.metrics(token)]);
        setMetrics(m?.monitored || null);

        const aggregates = ["file", "folder", "ip"].map((key) => state?.[key] || {});
        const totalActive = aggregates.reduce((acc, cur) => acc + (cur.active || 0), 0);
        const totalPaused = aggregates.reduce((acc, cur) => acc + (cur.paused || 0), 0);
        const totalStopped = aggregates.reduce((acc, cur) => acc + (cur.stopped || 0), 0);

        // const nextState = totalActive > 0 ? "running" : totalStopped > 0 ? "stopped" : totalPaused > 0 ? "paused" : "stopped";
        // setMState(nextState);
        const nextState =
            totalActive > 0 && totalStopped === 0 && totalPaused === 0
                ? "running"
                : totalActive > 0 && (totalStopped > 0 || totalPaused > 0)
                ? "mixed"
                : totalPaused > 0
                ? "paused"
                : "stopped";
        setMState(nextState);

        } catch { /* ignore */ }
    };
    useEffect(() => { if (tab==="machines") refreshMachines(); }, [tab]); // eslint-disable-line

    // const startAll = async () => {
    //     setMState("loading");
    //     try { await api.startAll(token); await refreshMachines(); }
    //     catch { setMState("stopped"); }
    // };
    // const stopAll = async () => {
    //     setMState("loading");
    //     try { await api.stopAll(token); await refreshMachines(); }
    //     catch { setMState("running"); }
    // };
    // const stopAll = async () => {
    //     console.log("CLICK stopAll, token=", token);  // <---
    //     setMState("loading");
    //     try {
    //         console.log("API CALL stopAll...");
    //         await api.stopAll(token);
    //         console.log("API CALL OK");
    //         await refreshMachines();
    //     } catch (e) {
    //         console.error("Erreur stopAll:", e);
    //         setMState("running");
    //     }
    // };

    const startAll = async () => {
        setMState("loading");
        try {
            await api.startAll(token);
            // Attendre un peu puis rafraîchir
            setTimeout(() => {
                refreshMachines().catch(console.error);
            }, 1000);
        } catch (e) {
            console.error("Erreur startAll:", e);
            setTimeout(() => {
                refreshMachines().catch(console.error);
            }, 500);
        }
    };

    const stopAll = async () => {
        console.log("CLICK stopAll, token=", token);
        setMState("loading");
        try {
            console.log("API CALL stopAll...");
            await api.stopAll(token);
            console.log("API CALL OK");
            // Attendre un peu puis rafraîchir
            setTimeout(() => {
                refreshMachines().catch(console.error);
            }, 1000);
        } catch (e) {
            console.error("Erreur stopAll:", e);
            // En cas d'erreur, essayer de rafraîchir quand même
            setTimeout(() => {
                refreshMachines().catch(console.error);
            }, 500);
        }
    };
    // const stopAll = async () => {
    //     setMState("loading");
    //     try {
    //         await Promise.all([
    //         api.fetchJson("/engine/file/stop-all", { method: "POST", token }),
    //         api.fetchJson("/engine/folder/stop-all", { method: "POST", token }),
    //         api.fetchJson("/engine/ip/stop-all", { method: "POST", token }),
    //         ]);
    //         // Forcer directement l'état en "stopped"
    //         setMState("stopped");
    //         // Puis re-synchroniser avec le backend
    //         setTimeout(() => {
    //         refreshMachines().catch(console.error);
    //         }, 1000);
    //     } catch (e) {
    //         console.error("Erreur stopAll:", e);
    //         setMState("running");
    //     }
    // };




    /* Logs purge (inchangé pour l’instant) */
    const [logType, setLogType] = useState("activity");
    const [level, setLevel] = useState("");
    const [from, setFrom] = useState("");
    const [to, setTo] = useState("");
    const [lMsg, setLMsg] = useState(null);
    const purge = async () => {
        if (!window.confirm("Are you sure you want to purge logs with the selected filters? This action cannot be undone.")) {
            return;
        }
        setLMsg(null);
        try { await api.purgeHidsLog(token, { type: logType, level: level || undefined, from: from || undefined, to: to || undefined }); setLMsg({ type:"success", text:"Logs purged" }); }
        catch (e) { setLMsg({ type:"error", text: e?.body?.detail || "Purge failed" }); }
    };
    const clearAllOfType = async () => {
        if (!window.confirm(`Are you sure you want to clear ALL ${logType} logs? This action cannot be undone.`)) {
            return;
        }
        setLMsg(null);
        try {
            await api.clearHidsLog(token, { type: logType });
            setLMsg({ type:"success", text:`All ${logType} logs cleared.` });
        } catch (e) {
            setLMsg({ type:"error", text: e?.body?.detail || "Clear failed" });
        }
    };

    return (
        <div className="space-y-6">
            {/* Admin banner */}
            {user && !isAdmin && (
                <div className="px-4 py-2 rounded-md bg-amber-500/20 text-amber-300">
                You are logged in as a non-admin user. All Settings actions are disabled.
                </div>
            )}

            <div className="flex items-center justify-between">
                <div className="flex gap-2">
                {["users","machines","logs"].map(t => (
                    <button key={t}
                    onClick={()=>setTab(t)}
                    className={`px-3 py-1.5 rounded-md border capitalize ${tab===t ? "bg-panel2 border-white/10" : "bg-panel/50 border-white/5"}`}>
                    {t}
                    </button>
                ))}
                </div>
            </div>

            {/* USERS TAB */}
            {tab==="users" && (
                <div className="space-y-6"> 
                    {/* Erreurs uniquement (plus de bannière "X users loaded") */}
                    {uMsg?.type==="error" && (
                        <div className="mb-1 px-3 py-2 rounded-md bg-red-500/20 text-red-300">
                        {uMsg.text}
                        </div>
                    )}

                    {/* Barre filtres/recherche */}
                    <div className="flex flex-wrap gap-2 items-center justify-between card p-3">
                        <div className="flex gap-2 items-center">
                        <select
                            value={roleFilter}
                            onChange={e=>setRoleFilter(e.target.value)}
                            className="bg-panel2 border border-white/10 rounded-md px-2 py-1"
                        >
                            <option value="all">All users</option>
                            <option value="admin">Admins</option>
                            <option value="standard">Standard</option>
                        </select>

                        <input
                            value={query}
                            onChange={e=>setQuery(e.target.value)}
                            placeholder="Search username or email…"
                            className="bg-panel2 border border-white/10 rounded-md px-3 py-1.5 w-64"
                        />
                        </div>

                        <button
                        onClick={doAdd}
                        className="px-3 py-1.5 rounded-md border border-white/10 bg-panel2 hover:bg-panel disabled:opacity-50 disabled:cursor-not-allowed"
                        disabled={!isAdmin}
                        title={!isAdmin ? "Admin required" : "Add user"}
                        >
                        + Add user
                        </button>
                    </div>

                    {/* Table */}
                    <div className="card rounded-xl overflow-hidden">
                        <table className="w-full text-sm">
                            <thead className="bg-white/5 text-muted">
                                <tr>
                                <th className="text-left px-4 py-3">Username</th>
                                <th className="text-left px-4 py-3">Email</th>
                                <th className="text-left px-4 py-3">Role</th>
                                <th className="text-right px-4 py-3">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {uLoading && (
                                <tr><td colSpan="4" className="px-4 py-6 text-center text-muted">Loading users…</td></tr>
                                )}
                                {!uLoading && visibleUsers.length === 0 && (
                                <tr><td colSpan="4" className="px-4 py-6 text-center text-muted">No users to display.</td></tr>
                                )}
                                {visibleUsers.map(u => (
                                <tr key={u.id} className="border-t border-white/5">
                                    <td className="px-4 py-2">{u.username}</td>
                                    <td className="px-4 py-2">{u.email || "—"}</td>
                                    <td className="px-4 py-2">
                                    <Badge tone={u.is_admin ? "role" : "muted"}>{u.is_admin ? "Admin" : "Standard"}</Badge>
                                    </td>
                                    <td className="px-4 py-2">
                                    <div className="flex justify-end gap-2">
                                        <IconButton title={!isAdmin ? "Admin required" : "Change password"} onClick={()=>doEdit(u)} disabled={!isAdmin}><Pencil size={16}/></IconButton>
                                        <IconButton title={!isAdmin ? "Admin required" : "Delete user"} onClick={()=>doDelete(u)} disabled={!isAdmin}><Trash2 size={16}/></IconButton>
                                    </div>
                                    </td>
                                </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    {/* Pagination */}
                    <div className="flex items-center justify-between">
                        <div className="text-xs text-muted">
                        Page {currentPage} / {pageCount} — {filtered.length} user{filtered.length!==1 ? "s" : ""}
                        </div>
                        <div className="flex gap-2">
                        <button
                            className="px-3 py-1.5 rounded-md border border-white/10 bg-panel2 disabled:opacity-50"
                            onClick={()=>setPage(p=>Math.max(1, p-1))}
                            disabled={currentPage<=1}
                            title="Previous page"
                            aria-label="Previous page"
                        >
                            Prev
                        </button>
                        <button
                            className="px-3 py-1.5 rounded-md border border-white/10 bg-panel2 disabled:opacity-50"
                            onClick={()=>setPage(p=>Math.min(pageCount, p+1))}
                            disabled={currentPage>=pageCount}
                            title="Next page"
                            aria-label="Next page"
                        >
                            Next
                        </button>
                        </div>
                    </div>

                    <UserModal
                        open={modal.open}
                        mode={modal.mode}
                        user={modal.user}
                        onClose={()=>setModal({ open:false, mode:"add", user:null })}
                        onSave={saveUser}
                        disabled={!isAdmin}
                    />
                </div>
            )}

            {/* MACHINES TAB */}
            {tab==="machines" && (
                <div className="grid gap-6 md:grid-cols-2">
                    <div className="card p-4 flex flex-col items-center justify-center">
                        <h3 className="text-lg font-medium mb-4">Global control</h3>
                        <div className={`relative w-44 h-44 mb-3 ${!isAdmin ? "opacity-60" : ""}`}>
                            {/* {mState==="running" && <div className="absolute inset-0 rounded-full bg-emerald-500/10 animate-ping" />} */}
                            {mState === "running" && (
                                <div className="absolute inset-0 rounded-full bg-emerald-500/10 animate-ping pointer-events-none z-0" />
                            )}
                            <div className="relative z-10 w-full h-full rounded-full bg-panel2 border-2 border-white/10 flex items-center justify-center">
                                {mState==="stopped" && (
                                <button
                                    onClick={startAll}
                                    disabled={!isAdmin}
                                    className="w-20 h-20 rounded-full bg-emerald-600/20 hover:bg-emerald-600/30 border border-white/10 flex items-center justify-center disabled:cursor-not-allowed"
                                    title="Start all engines"
                                    aria-label="Start all engines"
                                >
                                    <Play size={36} className="text-emerald-400"/>

                                </button>
                                )}
                                {mState==="paused" && (
                                <div className="flex gap-3">
                                    <button
                                        onClick={startAll}
                                        disabled={!isAdmin}
                                        className="w-20 h-20 rounded-full bg-emerald-600/20 hover:bg-emerald-600/30 border border-white/10 flex items-center justify-center disabled:cursor-not-allowed"
                                        title="Resume all engines"
                                        aria-label="Resume all engines"
                                    >
                                        <Play size={36} className="text-emerald-300"/>
                                    </button>
                                    <button
                                        onClick={stopAll}
                                        disabled={!isAdmin}
                                        className="w-20 h-20 rounded-full bg-red-600/20 hover:bg-red-600/30 border border-white/10 flex items-center justify-center disabled:cursor-not-allowed"
                                        title="Stop all engines"
                                        aria-label="Stop all engines"
                                    >
                                        <Square size={32} className="text-red-300"/>
                                    </button>
                                </div>
                                )}
                                {/* {mState==="running" && (
                                <button
                                    onClick={stopAll}
                                    disabled={!isAdmin}
                                    className="w-20 h-20 rounded-full bg-red-600/20 hover:bg-red-600/30 border border-white/10 flex items-center justify-center disabled:cursor-not-allowed"
                                    title="Stop all engines"
                                    aria-label="Stop all engines"
                                >
                                    <Pause size={36} className="text-red-400"/>
                                </button>
                                )} */}
                                {(mState==="running" || mState==="mixed") && (
                                    <button
                                        onClick={stopAll}
                                        disabled={!isAdmin}
                                        className="w-20 h-20 rounded-full bg-red-600/20 hover:bg-red-600/30 
                                                border border-white/10 flex items-center justify-center 
                                                disabled:cursor-not-allowed"
                                        title="Stop all engines"
                                        aria-label="Stop all engines"
                                    >
                                        <Pause size={36} className="text-red-400"/>
                                    </button>
                                )}

                                {mState==="loading" && (
                                <svg className="animate-spin text-white" viewBox="0 0 24 24" width="48" height="48" role="img" aria-label="Loading">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                                </svg>
                                )}
                            </div>
                            {/* <div className="w-full h-full rounded-full bg-panel2 border-2 border-white/10 flex items-center justify-center">
                                
                            </div> */}
                        </div>
                        <div className="text-muted text-sm">
                            {mState==="stopped" && "All engines stopped"}
                            {mState==="paused" && "Engines paused"}
                            {mState==="running" && "Engines running"}
                            {mState==="mixed" && "Some engines running"}
                            {mState==="loading" && "Updating..."}
                        </div>
                        {!isAdmin && <div className="mt-2 text-xs text-muted">Admin required to start/stop.</div>}
                    </div>

                    <div className="card p-4">
                        <h3 className="text-lg font-medium mb-4">Monitored entities</h3>
                        <div className="grid grid-cols-3 gap-3">
                            <div className="rounded-xl p-3 bg-white/5">
                                <div className="text-muted text-xs mb-1">Files</div>
                                <div className="text-2xl font-semibold">{metrics?.files?.total ?? "—"}</div>
                            </div>
                            <div className="rounded-xl p-3 bg-white/5">
                                <div className="text-muted text-xs mb-1">Folders</div>
                                <div className="text-2xl font-semibold">{metrics?.folders?.total ?? "—"}</div>
                            </div>
                            <div className="rounded-xl p-3 bg-white/5">
                                <div className="text-muted text-xs mb-1">IPs</div>
                                <div className="text-2xl font-semibold">{metrics?.ips?.total ?? "—"}</div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* LOGS TAB */}
            {tab==="logs" && (
                <div className="card p-4 space-y-4">
                {lMsg && (
                    <div className={`px-3 py-2 rounded-md ${lMsg.type==="success" ? "bg-emerald-500/20 text-emerald-300" : "bg-red-500/20 text-red-300"}`}>{lMsg.text}</div>
                )}
                {!isAdmin && (
                    <div className="px-3 py-2 rounded-md bg-amber-500/20 text-amber-300">
                    Viewing only — admin required to purge or clear logs.
                    </div>
                )}
                <div className="grid md:grid-cols-2 gap-4">
                    <div className="space-y-3">
                    <div className="text-sm text-muted">Target</div>
                    <div className="flex flex-wrap gap-2">
                        <select value={logType} onChange={e=>setLogType(e.target.value)} className="bg-panel2 border border-white/10 rounded-md px-2 py-1">
                        <option value="activity">Activity logs</option>
                        <option value="alerts">Alerts logs</option>
                        </select>
                        <select value={level} onChange={e=>setLevel(e.target.value)} className="bg-panel2 border border-white/10 rounded-md px-2 py-1">
                        <option value="">Level: any</option>
                        <option>INFO</option>
                        <option>WARNING</option>
                        <option>ERROR</option>
                        <option>CRITICAL</option>
                        </select>
                    </div>

                    <div className="grid grid-cols-2 gap-2">
                        <div className="grid gap-1">
                        <label className="text-xs text-muted">From</label>
                        <input type="datetime-local" className="bg-panel2 border border-white/10 rounded-md px-2 py-1" value={from} onChange={e=>setFrom(e.target.value)} />
                        </div>
                        <div className="grid gap-1">
                        <label className="text-xs text-muted">To</label>
                        <input type="datetime-local" className="bg-panel2 border border-white/10 rounded-md px-2 py-1" value={to} onChange={e=>setTo(e.target.value)} />
                        </div>
                    </div>
                    </div>

                    <div className="space-y-3">
                    <div className="text-sm text-muted">Actions</div>
                    <div className="flex gap-2">
                        <button onClick={purge} disabled={!isAdmin} className="px-3 py-1.5 rounded-md bg-red-600/80 hover:bg-red-600 text-white disabled:opacity-50 disabled:cursor-not-allowed">Purge (filters)</button>
                        <button onClick={clearAllOfType} disabled={!isAdmin} className="px-3 py-1.5 rounded-md bg-red-900/60 hover:bg-red-900 text-white disabled:opacity-50 disabled:cursor-not-allowed">Clear ALL of type</button>
                    </div>
                    <div className="text-xs text-muted">
                        Purge supprime les lignes qui correspondent aux filtres (type, level, période).
                        Clear supprime <b>tout</b> pour le type choisi.
                    </div>
                    </div>
                </div>
                </div>
            )}
            </div>
    );
}
