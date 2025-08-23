// import { useEffect, useState } from 'react'
// import { useAuth } from '../context/AuthProvider'
// import { api } from '../lib/api'
// import StatCard from '../components/StatCard'
// import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

// export default function Dashboard(){
//     const { token } = useAuth()
//     const [metrics, setMetrics] = useState(null)
//     const [events, setEvents] = useState([])

//     useEffect(()=>{
//         (async()=>{
//         const m = await api.metrics(token)
//         setMetrics(m)
//         const r = await api.reports(token)
//         setEvents(r.events || [])
//         })().catch(console.error)
//     },[token])

//     if(!metrics) return <div>Loading…</div>

//     const m = metrics.monitored
//     const jobs = metrics.scheduler

//     const chartData = [
//         {name:'file', v: jobs.file||0},
//         {name:'folder', v: jobs.folder||0},
//         {name:'ip', v: jobs.ip||0},
//     ]

//     return (
//         <div className="space-y-6">
//         <div className="grid md:grid-cols-4 gap-4">
//             <StatCard title="HIDS Engine" value="Running" hint={`Jobs: ${jobs.total}`} />
//             <StatCard title="Files" value={`${m.files.active}/${m.files.total}`} />
//             <StatCard title="Folders" value={`${m.folders.active}/${m.folders.total}`} />
//             <StatCard title="IPs" value={`${m.ips.active}/${m.ips.total}`} />
//         </div>

//         <div className="grid md:grid-cols-3 gap-6">
//             <div className="card p-4 md:col-span-2">
//             <div className="mb-2 text-sm text-muted">Jobs by type</div>
//             <div className="h-52">
//                 <ResponsiveContainer width="100%" height="100%">
//                 <BarChart data={chartData}>
//                     <XAxis dataKey="name"/><YAxis allowDecimals={false}/><Tooltip/>
//                     <Bar dataKey="v" />
//                 </BarChart>
//                 </ResponsiveContainer>
//             </div>
//             </div>

//             <div className="card p-4">
//             <div className="mb-2 text-sm text-muted">Recent activity</div>
//             <ul className="space-y-2 max-h-52 overflow-auto pr-2">
//                 {events.slice(-10).reverse().map((e,i)=>(
//                 <li key={i} className="text-sm text-muted">
//                     <span className="badge">{e.type}</span> <span className="text-white">{e.path || e.ip}</span>
//                     <span className="float-right">{new Date(e.ts).toLocaleTimeString()}</span>
//                 </li>
//                 ))}
//                 {events.length===0 && <div className="text-muted">No events yet</div>}
//             </ul>
//             </div>
//         </div>
//         </div>
//     )
// }



// // --------------------------------------------------------------------------
// import { useEffect, useMemo, useState } from 'react'
// import { useAuth } from '../context/AuthProvider'
// import { api } from '../lib/api'
// import EngineCard from '../components/EngineCard'
// import StatCard from '../components/StatCard'
// import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts'

// function bucket(ts, stepMs){ return Math.floor(new Date(ts).getTime() / stepMs) * stepMs }

// export default function Dashboard(){
//     const { token } = useAuth()
//     const [metrics, setMetrics] = useState(null)
//     const [engine, setEngine] = useState(null)
//     const [events, setEvents] = useState([])

//     // const reload = async () => {
//     //     const [m, e, s] = await Promise.all([
//     //     api.metrics(token),
//     //     api.activity(token),
//     //     api.fetchJson('/engine/state', { token })
//     //     ])
//     //     setMetrics(m); setEvents(e); setEngine(s)
//     // }

//     const reload = async () => {
//     // On charge metrics + activity en parallèle
//     const [m, e] = await Promise.all([
//         api.metrics(token),
//         api.activity(token)
//     ])

//     // Essai /engine/state (peut 404)
//     let s = null
//     try {
//         s = await api.fetchJson('/engine/state', { token })
//     } catch (err) {
//         // Fallback: synthèse depuis metrics.monitored
//         const mm = m?.monitored ?? {}
//         const f = mm.files ?? { total:0, active:0 }
//         const d = mm.folders ?? { total:0, active:0 }
//         const ip = mm.ips ?? { total:0, active:0 }
//         s = {
//         engine: 'running',
//         file:   { total: f.total, active: f.active, paused: Math.max(0, f.total - f.active) },
//         folder: { total: d.total, active: d.active, paused: Math.max(0, d.total - d.active) },
//         ip:     { total: ip.total, active: ip.active, paused: Math.max(0, ip.total - ip.active) },
//         }
//         console.warn('No /engine/state; using fallback from /metrics')
//     }

//     setMetrics(m); setEvents(e); setEngine(s)
//     }

//     // … plus bas : ne bloque plus sur engine
//     // if (!metrics) return <div>Loading…</div>


//     useEffect(()=>{ reload().catch(console.error) },[token])

//     const alertsByType = useMemo(()=>{
//         const agg = { file_scan:0, folder_scan:0, ip_scan:0 }
//         for(const ev of events) if(agg[ev.type]!=null) agg[ev.type]++
//         return [
//         {name:'Files', v: agg.file_scan}, {name:'Folders', v: agg.folder_scan}, {name:'IPs', v: agg.ip_scan}
//         ]
//     },[events])

//     const alertsOverTime = useMemo(()=>{
//         // bucket par minute sur les 2 dernières heures
//         const STEP = 60*1000
//         const now = Date.now()
//         const start = now - 2*60*60*1000
//         const table = new Map()
//         for(const ev of events){
//         const t = new Date(ev.ts).getTime()
//         if(Number.isNaN(t) || t<start) continue
//         const b = bucket(t, STEP)
//         table.set(b, (table.get(b)||0)+1)
//         }
//         const out=[]
//         for(let t = bucket(start, STEP); t<=now; t+=STEP){
//         out.push({ ts:new Date(t).toLocaleTimeString(), count: table.get(t)||0 })
//         }
//         return out
//     },[events])

//     const doAction = async (kind, action) => {
//         await api.fetchJson(`/engine/${kind}/${action}`, { method:'POST', token })
//         await reload()
//     }

//     // if(!metrics || !engine) return 
//     if (!metrics) return <div>Loading…</div>

//     const m = metrics.monitored
//     return (
//         <div className="space-y-6">
//         {/* ligne 1: engine status par catégorie + counters existants */}
//         <div className="grid md:grid-cols-4 gap-4">
//             <EngineCard title="File Monitoring"
//             counts={engine.file}
//             onAction={(a)=>doAction('file', a)}
//             />
//             <EngineCard title="Folder Monitoring"
//             counts={engine.folder}
//             onAction={(a)=>doAction('folder', a)}
//             />
//             <EngineCard title="IP Monitoring"
//             counts={engine.ip}
//             onAction={(a)=>doAction('ip', a)}
//             />
//             <StatCard title="Entities Monitored" value={m.total} hint={`${m.files.total} files · ${m.folders.total} folders · ${m.ips.total} IPs`} />
//         </div>

//         {/* ligne 2: histogramme alertes par type + activity feed (avec dates/heures) */}
//         <div className="grid md:grid-cols-3 gap-6">
//             <div className="card p-4 md:col-span-2">
//             <div className="mb-2 text-sm text-muted">Alerts by Type</div>
//             <div className="h-56">
//                 <ResponsiveContainer width="100%" height="100%">
//                 <BarChart data={alertsByType}>
//                     <XAxis dataKey="name"/><YAxis allowDecimals={false}/><Tooltip/>
//                     <Bar dataKey="v" />
//                 </BarChart>
//                 </ResponsiveContainer>
//             </div>
//             </div>
//             <div className="card p-4">
//             <div className="mb-2 text-sm text-muted">Recent activity</div>
//             <ul className="space-y-2 max-h-56 overflow-auto pr-2">
//                 {events.slice(-15).reverse().map((e,i)=>(
//                 <li key={i} className="text-sm text-muted">
//                     <span className="badge">{e.type}</span>{' '}
//                     <span className="text-white">{e.path || e.ip}</span>
//                     <span className="float-right">{new Date(e.ts).toLocaleString()}</span>
//                 </li>
//                 ))}
//                 {events.length===0 && <div className="text-muted">No events yet</div>}
//             </ul>
//             </div>
//         </div>

//         {/* ligne 3: courbe alertes dans le temps */}
//         <div className="card p-4">
//             <div className="mb-2 text-sm text-muted">Alerts Over Time (last 2h, 1‑min bins)</div>
//             <div className="h-56">
//             <ResponsiveContainer width="100%" height="100%">
//                 <LineChart data={alertsOverTime}>
//                 <XAxis dataKey="ts" /><YAxis allowDecimals={false} />
//                 <Tooltip />
//                 <Line type="monotone" dataKey="count" dot={false} />
//                 </LineChart>
//             </ResponsiveContainer>
//             </div>
//         </div>
//         </div>
//     )
// }
// ---------------------------------------------------------------
// src/pages/Dashboard.jsx
import { useEffect, useMemo, useState } from "react";
import { useAuth } from "../context/AuthProvider";
import { api } from "../lib/api";
import EngineCard from "../components/EngineCard";
import StatCard from "../components/StatCard";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  LineChart, Line, Brush
} from "recharts";

function bucket(ts, stepMs) {
  return Math.floor(new Date(ts).getTime() / stepMs) * stepMs;
}

const PRESETS = [
  { key: "2h",   label: "Last 2h",   ms:   2 * 60 * 60 * 1000 },
  { key: "24h",  label: "Last 24h",  ms:  24 * 60 * 60 * 1000 },
  { key: "7d",   label: "Last 7d",   ms:   7 * 24 * 60 * 60 * 1000 },
  { key: "30d",  label: "Last 30d",  ms:  30 * 24 * 60 * 60 * 1000 },
  { key: "365d", label: "Last 1y",   ms: 365 * 24 * 60 * 60 * 1000 },
];

const INTERVALS = [
  { key: "auto", label: "Auto",   ms: null },
  { key: "1m",   label: "1 min",  ms: 60 * 1000 },
  { key: "5m",   label: "5 min",  ms: 5 * 60 * 1000 },
  { key: "15m",  label: "15 min", ms: 15 * 60 * 1000 },
  { key: "1h",   label: "1 hour", ms: 60 * 60 * 1000 },
  { key: "1d",   label: "1 day",  ms: 24 * 60 * 60 * 1000 },
];

function pickAutoStep(rangeMs) {
  if (rangeMs <= 6 * 60 * 60 * 1000) return 60 * 1000;         // 1m
  if (rangeMs <= 3 * 24 * 60 * 60 * 1000) return 60 * 60 * 1000; // 1h
  return 24 * 60 * 60 * 1000;                                   // 1d
}

function fmtTick(tsMs, rangeMs) {
    const d = new Date(tsMs);
    if (rangeMs <= 24 * 60 * 60 * 1000) return d.toLocaleTimeString();
    if (rangeMs <= 30 * 24 * 60 * 60 * 1000)
        return d.toLocaleDateString() + " " +
            d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    return d.toLocaleDateString();
}

export default function Dashboard() {
    const { token } = useAuth();
    const [metrics, setMetrics] = useState(null);
    const [engine, setEngine] = useState(null);
    const [events, setEvents] = useState([]);

    // Range/interval controls
    const [mode, setMode] = useState("preset");   // 'preset' | 'custom'
    const [preset, setPreset] = useState("2h");   // PRESETS key
    const [customStart, setCustomStart] = useState(() => {
        const t = new Date(Date.now() - 2 * 60 * 60 * 1000);
        return new Date(t.getTime() - t.getTimezoneOffset() * 60000)
        .toISOString().slice(0, 16);
    });
    const [customEnd, setCustomEnd] = useState(() => {
        const t = new Date();
        return new Date(t.getTime() - t.getTimezoneOffset() * 60000)
        .toISOString().slice(0, 16);
    });
    const [interval, setInterval] = useState("auto"); // INTERVALS key

    const reload = async () => {
        const [m, e] = await Promise.all([
        api.metrics(token),
        api.activity(token)
        ]);

        let s = null;
        try {
        s = await api.fetchJson("/engine/state", { token });
        } catch {
        // fallback from metrics if /engine/state is not available
        const mm = m?.monitored ?? {};
        const f = mm.files ?? { total: 0, active: 0 };
        const d = mm.folders ?? { total: 0, active: 0 };
        const ip = mm.ips ?? { total: 0, active: 0 };
        s = {
            engine: "running",
            file:   { total: f.total, active: f.active, paused: Math.max(0, f.total - f.active) },
            folder: { total: d.total, active: d.active, paused: Math.max(0, d.total - d.active) },
            ip:     { total: ip.total, active: ip.active, paused: Math.max(0, ip.total - ip.active) },
        };
        }

        setMetrics(m);
        setEvents(e);
        setEngine(s);
    };

    useEffect(() => { reload().catch(console.error); }, [token]);

    const alertsByType = useMemo(() => {
        const agg = { file_scan: 0, folder_scan: 0, ip_scan: 0 };
        for (const ev of events) if (agg[ev.type] != null) agg[ev.type]++;
        return [
        { name: "Files",   v: agg.file_scan },
        { name: "Folders", v: agg.folder_scan },
        { name: "IPs",     v: agg.ip_scan },
        ];
    }, [events]);

    const alertsOverTime = useMemo(() => {
        // determine window
        let startMs, endMs;
        if (mode === "preset") {
        const p = PRESETS.find(p => p.key === preset) ?? PRESETS[0];
        endMs = Date.now();
        startMs = endMs - p.ms;
        } else {
        const s = Date.parse(customStart);
        const e = Date.parse(customEnd);
        endMs = Number.isFinite(e) ? e : Date.now();
        startMs = Number.isFinite(s) ? s : endMs - 2 * 60 * 60 * 1000;
        if (startMs > endMs) [startMs, endMs] = [endMs - 60 * 60 * 1000, endMs]; // guard
        }

        // step
        const manual = INTERVALS.find(i => i.key === interval)?.ms ?? null;
        const STEP = manual || pickAutoStep(endMs - startMs);

        // aggregate
        const table = new Map();
        for (const ev of events) {
        if (!ev?.ts) continue;
        const t = +new Date(ev.ts);
        if (!Number.isFinite(t) || t < startMs || t > endMs) continue;
        const b = bucket(t, STEP);
        table.set(b, (table.get(b) || 0) + 1);
        }

        const out = [];
        for (let t = bucket(startMs, STEP); t <= endMs; t += STEP) {
        out.push({ ts: t, count: table.get(t) || 0 });
        }
        return { points: out, startMs, endMs, step: STEP };
    }, [events, mode, preset, customStart, customEnd, interval]);

    const doAction = async (kind, action) => {
        await api.fetchJson(`/engine/${kind}/${action}`, { method: "POST", token });
        await reload();
    };

    if (!metrics) return <div>Loading…</div>;
    const m = metrics.monitored;

    return (
        <div className="space-y-6">
        {/* Row 1: engine cards + counters */}
        <div className="grid gap-4 xl:grid-cols-4 md:grid-cols-2">
            <EngineCard title="File Monitoring"   counts={engine?.file}   onAction={(a)=>doAction("file", a)} />
            <EngineCard title="Folder Monitoring" counts={engine?.folder} onAction={(a)=>doAction("folder", a)} />
            <EngineCard title="IP Monitoring"     counts={engine?.ip}     onAction={(a)=>doAction("ip", a)} />
            <StatCard title="Entities Monitored" value={m.total}
                    hint={`${m.files.total} files · ${m.folders.total} folders · ${m.ips.total} IPs`} />
        </div>

        {/* Row 2: histogram + recent activity */}
        <div className="grid md:grid-cols-3 gap-6">
            <div className="card p-4 md:col-span-2">
            <div className="mb-2 text-sm text-muted">Alerts by Type</div>
            <div className="h-56">
                <ResponsiveContainer width="100%" height="100%">
                <BarChart data={alertsByType}>
                    <XAxis dataKey="name" />
                    <YAxis allowDecimals={false} />
                    <Tooltip />
                    <Bar dataKey="v" />
                </BarChart>
                </ResponsiveContainer>
            </div>
            </div>

            <div className="card p-4">
            <div className="mb-2 text-sm text-muted">Recent activity</div>
            <ul className="soft-scroll space-y-2 max-h-56 overflow-auto pr-2">
                {events.slice(-15).reverse().map((e, i) => {
                const when = e?.ts ? new Date(e.ts).toLocaleString() : "—";
                return (
                    <li key={i} className="text-sm text-muted flex items-center gap-2">
                    <span className="badge">{e.type || "event"}</span>
                    <span className="text-white truncate">{e.path || e.ip || e.hostname || "-"}</span>
                    <span className="ml-auto">{when}</span>
                    </li>
                );
                })}
                {events.length === 0 && <div className="text-muted">No events yet</div>}
            </ul>
            </div>
        </div>

        {/* Row 3: time‑series with presets/custom + Brush */}
        <div className="card p-4">
            <div className="mb-3 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div className="text-sm text-muted">Alerts Over Time</div>

            <div className="flex flex-wrap gap-2 items-center">
                <div className="flex rounded-md overflow-hidden border border-white/10">
                <button
                    onClick={() => setMode("preset")}
                    className={`px-3 py-1.5 text-sm ${mode === "preset" ? "bg-panel2" : "bg-panel/50"}`}
                    title="Use quick presets"
                >Presets</button>
                <button
                    onClick={() => setMode("custom")}
                    className={`px-3 py-1.5 text-sm ${mode === "custom" ? "bg-panel2" : "bg-panel/50"}`}
                    title="Pick an absolute date range"
                >Custom</button>
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
                <LineChart data={alertsOverTime.points}>
                <XAxis
                    dataKey="ts"
                    type="number"
                    domain={["dataMin", "dataMax"]}
                    tickFormatter={(v) => fmtTick(v, alertsOverTime.endMs - alertsOverTime.startMs)}
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
                    tickFormatter={(v) => fmtTick(v, alertsOverTime.endMs - alertsOverTime.startMs)}
                />
                </LineChart>
            </ResponsiveContainer>
            </div>
        </div>
        </div>
    );
}
