import { useEffect, useMemo, useState } from "react";
import { useAuth } from "../context/AuthProvider";
import { api } from "../lib/api";
import EngineCard from "../components/EngineCard";
import StatCard from "../components/StatCard";
import {
    ResponsiveContainer, PieChart, Pie, Cell, Legend, Tooltip,
    LineChart, Line, XAxis, YAxis, Brush
} from "recharts";

// Fonction utilitaire pour "bucketer" les timestamps
function bucket(ts, stepMs) {
  return Math.floor(new Date(ts).getTime() / stepMs) * stepMs;
}

// Préréglages de la plage de temps
const PRESETS = [
    { key: "2h", label: "Last 2h", ms: 2 * 60 * 60 * 1000 },
    { key: "24h", label: "Last 24h", ms: 24 * 60 * 60 * 1000 },
    { key: "7d", label: "Last 7d", ms: 7 * 24 * 60 * 60 * 1000 },
    { key: "30d", label: "Last 30d", ms: 30 * 24 * 60 * 60 * 1000 },
    { key: "365d", label: "Last 1y", ms: 365 * 24 * 60 * 60 * 1000 },
];

// Préréglages d'intervalle pour le graphique en ligne
const INTERVALS = [
    { key: "auto", label: "Auto", ms: null },
    { key: "1m", label: "1 min", ms: 60 * 1000 },
    { key: "5m", label: "5 min", ms: 5 * 60 * 1000 },
    { key: "15m", label: "15 min", ms: 15 * 60 * 1000 },
    { key: "1h", label: "1 hour", ms: 60 * 60 * 1000 },
    { key: "1d", label: "1 day", ms: 24 * 60 * 60 * 1000 },
];

// Choix automatique du pas de temps
const pickAutoStep = (rangeMs) => rangeMs <= 6 * 60 * 60 * 1000 ? 60 * 1000
  : rangeMs <= 3 * 24 * 60 * 60 * 1000 ? 60 * 60 * 1000 : 24 * 60 * 60 * 1000;

// Formatage des étiquettes de temps
const fmtTick = (tsMs, rangeMs) => {
    const d = new Date(tsMs);
    if (rangeMs <= 24 * 60 * 60 * 1000) return d.toLocaleTimeString();
    if (rangeMs <= 30 * 24 * 60 * 60 * 1000)
        return d.toLocaleDateString() + " " + d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    return d.toLocaleDateString();
};

export default function Dashboard() {
    const { token } = useAuth();
    const [metrics, setMetrics] = useState(null);
    const [engine, setEngine] = useState(null);
    const [events, setEvents] = useState([]);
    const [error, setError] = useState(null);

    // Contrôles de plage pour le graphique temporel
    const [mode, setMode] = useState("preset");
    const [preset, setPreset] = useState("2h");
    const [customStart, setCustomStart] = useState(() => {
        const t = new Date(Date.now() - 2 * 60 * 60 * 1000);
        return new Date(t.getTime() - t.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
    });
    const [customEnd, setCustomEnd] = useState(() => {
        const t = new Date();
        return new Date(t.getTime() - t.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
    });
    const [interval, setInterval] = useState("auto");

    const reload = async () => {
        try {
        // Effacer l'erreur précédente
        setError(null);
        // Appels API pour les métriques, l'activité et les alertes
        const [m, activityData, alertsData] = await Promise.all([
            api.metrics(token),
            api.listHidsLog(token, { type: "activity", page: 1, limit: 50 }),
            api.listHidsLog(token, { type: "alerts", page: 1, limit: 50 }),
        ]);
        
        // Combinaison et tri des événements par date
        const combinedEvents = [
            ...(activityData?.lines || []),
            ...(alertsData?.lines || [])
        ].sort((a, b) => new Date(b.ts) - new Date(a.ts));

        // Obtenir l'état du moteur ou utiliser un état de secours
        let s = null;
        try { s = await api.fetchJson("/engine/state", { token }); }
        catch {
            const mm = m?.monitored ?? {};
            const f = mm.files ?? { total: 0, active: 0 };
            const d = mm.folders ?? { total: 0, active: 0 };
            const ip = mm.ips ?? { total: 0, active: 0 };
            const derived = (base) => ({
            total: base.total,
            active: base.active,
            paused: Math.max(0, base.total - base.active),
            stopped: 0,
            });
            const fileCounts = derived(f);
            const folderCounts = derived(d);
            const ipCounts = derived(ip);
            const totalActive = fileCounts.active + folderCounts.active + ipCounts.active;
            const totalPaused = fileCounts.paused + folderCounts.paused + ipCounts.paused;
            const engineStatus = totalActive > 0 ? "running" : totalPaused > 0 ? "paused" : "stopped";
            s = {
            engine: engineStatus,
            file: fileCounts,
            folder: folderCounts,
            ip: ipCounts,
            };
        }
        setMetrics(m);
        setEvents(combinedEvents);
        setEngine(s);
        } catch (error) {
        console.error("Failed to reload dashboard data:", error);
        setError("Erreur de chargement des données. Veuillez vérifier la connexion ou les logs du backend.");
        }
    };

    useEffect(() => { reload().catch(console.error); }, [token]);

    // Donut (proportions)
    const donutData = useMemo(() => {
        const mm = metrics?.monitored ?? { files: { total: 0 }, folders: { total: 0 }, ips: { total: 0 }, total: 0 };
        return [
        { name: "Files", value: mm.files?.total || 0 },
        { name: "Folders", value: mm.folders?.total || 0 },
        { name: "IPs", value: mm.ips?.total || 0 },
        ];
    }, [metrics]);
    const DONUT_COLORS = ["#60a5fa", "#a78bfa", "#34d399"];

    // Mini graphique temporel
    const eventsOverTime = useMemo(() => {
        let startMs, endMs;
        if (mode === "preset") {
        const p = PRESETS.find(p => p.key === preset) ?? PRESETS[0];
        endMs = Date.now(); startMs = endMs - p.ms;
        } else {
        const s = Date.parse(customStart); const e = Date.parse(customEnd);
        endMs = Number.isFinite(e) ? e : Date.now();
        startMs = Number.isFinite(s) ? s : endMs - 2 * 60 * 60 * 1000;
        if (startMs > endMs) [startMs, endMs] = [endMs - 60 * 60 * 1000, endMs];
        }
        const manual = INTERVALS.find(i => i.key === interval)?.ms ?? null;
        const STEP = manual || pickAutoStep(endMs - startMs);

        const table = new Map();
        for (const ev of events) {
        const t = +new Date(ev.ts || 0); if (!Number.isFinite(t) || t < startMs || t > endMs) continue;
        const b = bucket(t, STEP); table.set(b, (table.get(b) || 0) + 1);
        }
        const out = [];
        for (let t = bucket(startMs, STEP); t <= endMs; t += STEP) out.push({ ts: t, count: table.get(t) || 0 });
        return { points: out, startMs, endMs };
    }, [events, mode, preset, customStart, customEnd, interval]);

    const doAction = async (kind, action) => {
        await api.fetchJson(`/engine/${kind}/${action}`, { method: "POST", token });
        await reload();
    };
    
    // const doAction = async (kind, action) => {
    //     try {
    //         // Mettre à jour l'état optimistiquement avant l'appel API
    //         setEngine(prev => {
    //             if (!prev) return prev;
    //             const newState = { ...prev };
    //             const current = newState[kind];
                
    //             if (action === "pause-all" || action === "stop-all") {
    //                 newState[kind] = { ...current, active: 0, paused: current.total };
    //             } else if (action === "resume-all") {
    //                 newState[kind] = { ...current, active: current.total, paused: 0 };
    //             }
    //             return newState;
    //         });

    //         await api.fetchJson(`/engine/${kind}/${action}`, { method: "POST", token });
            
    //         // Recharger les données réelles après un court délai
    //         setTimeout(() => {
    //             reload().catch(console.error);
    //         }, 500);
            
    //     } catch (error) {
    //         console.error(`Action ${action} failed:`, error);
    //         // Recharger pour rétablir l'état correct
    //         reload().catch(console.error);
    //     }
    // };

    if (error) {
        return (
        <div className="flex items-center justify-center h-full text-center text-red-500">
            <p>{error}</p>
        </div>
        );
    }

    if (!metrics) return <div>Loading…</div>;
    const m = metrics.monitored;

    return (
        <div className="space-y-6">
            {/* Ligne 1: cartes du moteur + compteurs */}
            <div className="grid gap-4 xl:grid-cols-4 md:grid-cols-2">
                <EngineCard title="File Monitoring" counts={engine?.file} onAction={(a) => doAction("file", a)} />
                <EngineCard title="Folder Monitoring" counts={engine?.folder} onAction={(a) => doAction("folder", a)} />
                <EngineCard title="IP Monitoring" counts={engine?.ip} onAction={(a) => doAction("ip", a)} />
                <StatCard title="Entities Monitored" value={m.total}
                    hint={`${m.files.total} files · ${m.folders.total} folders · ${m.ips.total} IPs`} />
            </div>

            {/* /* Ligne 2: graphique en anneau + activité récente */}
            <div className="grid gap-4 xl:grid-cols-2 md:grid-cols-2 ">
                {/* Le graphique en anneau occupe 60% de la largeur */}
                <div className="card p-4 flex-[60] h-[37vh] flex flex-col">
                    <div className="mb-2 text-sm text-muted">Entities by Type</div>
                    <div className="h-96">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie data={donutData} dataKey="value" nameKey="name" innerRadius="50%" outerRadius="80%">
                                    {donutData.map((entry, idx) => <Cell key={idx} fill={DONUT_COLORS[idx % DONUT_COLORS.length]} />)}
                                </Pie>
                                <Tooltip />
                                <Legend />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* L'activité récente occupe 40% de la largeur */}
                <div className="card p-4 flex-[40] h-[37vh] flex flex-col">
                    <div className="mb-2 text-sm text-muted">Recent activity</div>
                        <ul className="soft-scroll space-y-2 max-h-96 overflow-auto pr-2">
                            {events.slice(0, 25).map((e, i) => { // Afficher plus d'événements
                                const when = e?.ts ? new Date(e.ts).toLocaleString() : "—";
                                return (
                                    <li key={i} className="text-sm text-muted flex items-center gap-2">
                                        {e.level === "WARNING" && (
                                            <span className="badge bg-yellow-500/20 text-yellow-300">warning</span>
                                        )}
                                        {e.level === "INFO" && (
                                            <span className="badge bg-green-500/20 text-green-300">info</span>
                                        )}
                                        {e.level === "ERROR" && (
                                            <span className="badge bg-red-500 text-white">error</span>
                                        )}
                                        <span className="text-white truncate">{e.msg}</span>
                                        <span className="ml-auto flex-none">{when}</span>
                                    </li>
                                );
                            })}
                            {events.length === 0 && <div className="text-muted">No events yet</div>}
                        </ul>
                    </div>
                </div>

            {/* Ligne 3: petit graphique temporel (inchangé) */}
            <div className="card p-4">
                <div className="mb-3 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                    <div className="text-sm text-muted">Events Over Time</div>
                    <div className="flex flex-wrap gap-2 items-center">
                        <div className="flex rounded-md overflow-hidden border border-white/10">
                            <button
                                onClick={() => setMode("preset")}
                                className={`px-3 py-1.5 text-sm ${mode === "preset" ? "bg-panel2" : "bg-panel/50"}`}
                                title="Use quick presets"
                            >
                                Presets
                            </button>
                            <button
                                onClick={() => setMode("custom")}
                                className={`px-3 py-1.5 text-sm ${mode === "custom" ? "bg-panel2" : "bg-panel/50"}`}
                                title="Pick an absolute date range"
                            >
                                Custom
                            </button>
                        </div>
                        {mode === "preset" ? (
                            <select
                                value={preset}
                                onChange={e => setPreset(e.target.value)}
                                className="bg-panel2 border border-white/10 rounded-md text-sm px-2 py-1 focus:outline-none"
                                title="Time range"
                            >
                                {PRESETS.map(r => <option key={r.key} value={r.key}>{r.label}</option>)}
                            </select>
                        ) : (
                            <div className="flex flex-wrap items-center gap-2">
                                <label className="text-xs text-muted">From</label>
                                <input
                                    type="datetime-local"
                                    value={customStart}
                                    onChange={e => setCustomStart(e.target.value)}
                                    className="bg-panel2 border border-white/10 rounded-md text-sm px-2 py-1"
                                />
                                <label className="text-xs text-muted">to</label>
                                <input
                                    type="datetime-local"
                                    value={customEnd}
                                    onChange={e => setCustomEnd(e.target.value)}
                                    className="bg-panel2 border border-white/10 rounded-md text-sm px-2 py-1"
                                />
                            </div>
                        )}
                        <select
                            value={interval}
                            onChange={e => setInterval(e.target.value)}
                            className="bg-panel2 border border-white/10 rounded-md text-sm px-2 py-1 focus:outline-none"
                            title="Aggregation"
                        >
                            {INTERVALS.map(i => <option key={i.key} value={i.key}>{i.label}</option>)}
                        </select>
                    </div>
                </div>
                <div className="h-56">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={eventsOverTime.points}>
                        <XAxis
                            dataKey="ts"
                            type="number"
                            domain={["dataMin", "dataMax"]}
                            tickFormatter={(v) => fmtTick(v, eventsOverTime.endMs - eventsOverTime.startMs)}
                        />
                        <YAxis allowDecimals={false} />
                        <Tooltip
                            labelFormatter={(v) => new Date(v).toLocaleString()}
                            formatter={(val) => [val, "alerts"]}
                        />
                        <Line type="monotone" dataKey="count" dot={false} />
                        <Brush
                            dataKey="ts"
                            height={22}
                            travellerWidth={12}
                            tickFormatter={(v) => fmtTick(v, eventsOverTime.endMs - eventsOverTime.startMs)}
                        />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
}
