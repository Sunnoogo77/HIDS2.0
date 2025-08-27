// src/pages/Reports.jsx
import { useEffect, useMemo, useState } from "react";
import { useAuth } from "../context/AuthProvider";
import { api } from "../lib/api";

function Pill({ children, tone = "muted" }) {
    const map = {
        muted: "bg-white/5 text-muted",
        ok: "bg-emerald-500/20 text-emerald-300",
        warn: "bg-amber-500/20 text-amber-300",
        info: "bg-sky-500/20 text-sky-300",
    };
    return (
        <span className={`px-2 py-0.5 rounded-full text-xs border border-white/10 ${map[tone]}`}>
        {children}
        </span>
    );
}

function Card({ title, children, right = null, className = "" }) {
    return (
        <div className={`card p-0 overflow-hidden ${className}`}>
        <div className="flex items-center justify-between px-4 py-3 border-b border-white/10">
            <div className="text-sm text-muted">{title}</div>
            {right}
        </div>
        <div className="p-4">{children}</div>
        </div>
    );
}

function Table({ head, children, className = "" }) {
    return (
        <div className={`rounded-xl overflow-auto scrollbeauty ${className}`}>
        <table className="w-full text-sm">
            <thead className="bg-white/5 text-muted sticky top-0 z-10">
            <tr>
                {head.map((h, i) => (
                <th key={i} className="px-4 py-3 text-left">{h}</th>
                ))}
            </tr>
            </thead>
            <tbody className="[&>tr]:border-t [&>tr]:border-white/5">{children}</tbody>
        </table>
        </div>
    );
}

export default function Reports() {
    const { token } = useAuth();
    const [report, setReport] = useState(null);
    const [tab, setTab] = useState("summary"); // summary | files | folders | ips

    useEffect(() => {
        (async () => {
        const r = await api.reports(token);
        setReport(r);
        })().catch(console.error);
    }, [token]);

    const inv = useMemo(() => {
        const r = report || {};
        const inv = r.inventory || {};
        return {
        files: inv.files || [],
        folders: inv.folders || [],
        ips: inv.ips || [],
        monitored: r.metrics?.monitored || { files: 0, folders: 0, ips: 0, total: 0 },
        scheduler: r.metrics?.scheduler || { file: 0, folder: 0, ip: 0, total: 0 },
        title: r.report?.title || "HIDS-Web JSON Report",
        version: r.report?.version || "—",
        generatedAt: new Date().toLocaleString(),
        };
    }, [report]);

    const download = () => {
        const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `hids-report-${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
    };

    if (!report) return <div>Loading…</div>;

    return (
        <div className="space-y-4 mt-7">
            <div className="flex items-center justify-between mb-10">
                <h1 className="text-2xl font-semibold">Reports</h1>
                <button className="btn " onClick={download}>Export JSON</button>
            </div>

        {/* Split layout: 30% / 70% with reduced top margin */}
        <div className="grid gap-4 lg:grid-cols-[30%_1fr] mt-2">
            {/* Left: raw JSON with pretty scrollbar */}
            <div className="card p-0 overflow-hidden max-h-[75vh]  from-panel via-panel2 to-sky-950">
                    <div className="px-4 py-3   text-muted ">Raw JSON</div>
                    <pre className="p-4 text-sm max-h-[70vh] overflow-auto scrollbeauty text-emerald-200 bg-black/60 rounded-b-xl">
                        {JSON.stringify(report, null, 2)}
                    </pre>
            </div>

            {/* Right: visual with tabs */}
            <div className="space-y-4 ">
            {/* Tabs */}
            <div className="card p-0 overflow-hidden h-[75vh] flex flex-col">
                <div className="px-4 py-3 border-b border-white/10 flex items-center justify-between">
                <div className="flex gap-2">
                    {["summary","files","folders","ips"].map(t => (
                    <button
                        key={t}
                        onClick={() => setTab(t)}
                        className={`capitalize px-3 py-1.5 rounded-md border
                        ${tab===t ? "bg-panel2 border-white/10" : "bg-panel/50 border-white/5"}`}
                    >
                        {t}
                    </button>
                    ))}
                </div>
                <Pill tone="info">Version {inv.version}</Pill>
                </div>

                {/* Tab content (scrollable panel) */}
                <div className="p-4 max-h-[72vh] overflow-auto scrollbeauty">
                {tab === "summary" && (
                    <div className="grid md:grid-cols-2 xl:grid-cols-4 gap-4">
                    <Card title="Entities Monitored">
                        <div className="text-4xl font-semibold mb-1">{inv.monitored.total}</div>
                        <div className="text-muted text-sm">
                        {inv.monitored.files} files · {inv.monitored.folders} folders · {inv.monitored.ips} IPs
                        </div>
                    </Card>
                    <Card title="Schedulers (total)">
                        <div className="text-4xl font-semibold mb-1">{inv.scheduler.total}</div>
                        <div className="text-muted text-sm">
                        file {inv.scheduler.file} · folder {inv.scheduler.folder} · ip {inv.scheduler.ip}
                        </div>
                    </Card>
                    <Card title={inv.title}>
                        <div className="text-2xl font-semibold leading-snug">HIDS-Web</div>
                        <div className="text-muted text-sm">Report title</div>
                    </Card>
                    <Card title="Generated at">
                        <div className="text-2xl font-semibold leading-snug">
                        {new Date(inv.generatedAt).toLocaleDateString()}
                        </div>
                        <div className="text-muted">
                        {new Date(inv.generatedAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
                        <div className="text-xs">local time</div>
                        </div>
                    </Card>

                    {/* Quick snapshots */}
                    <div className="md:col-span-2">
                        <Table head={["Files (top 10)", "Frequency", "Status"]}>
                        {(inv.files.slice(0,10).length ? inv.files.slice(0,10) : []).map(f => (
                            <tr key={`f-${f.id}`}>
                            <td className="px-4 py-2">
                                <div className="text-white">{f.path}</div>
                                <div className="text-xs text-muted">id {f.id}</div>
                            </td>
                            <td className="px-4 py-2"><Pill tone="info">{f.frequency}</Pill></td>
                            <td className="px-4 py-2"><Pill tone="ok">{f.status}</Pill></td>
                            </tr>
                        ))}
                        {inv.files.length === 0 && (
                            <tr><td className="px-4 py-2 text-muted" colSpan={3}>No files in inventory.</td></tr>
                        )}
                        </Table>
                    </div>

                    <div className="md:col-span-2">
                        <Table head={["IPs (top 10)", "Hostname", "Frequency", "Status"]}>
                        {(inv.ips.slice(0,10).length ? inv.ips.slice(0,10) : []).map(ip => (
                            <tr key={`ip-${ip.id}`}>
                            <td className="px-4 py-2">
                                <div className="text-white">{ip.ip}</div>
                                <div className="text-xs text-muted">id {ip.id}</div>
                            </td>
                            <td className="px-4 py-2">{ip.hostname || "—"}</td>
                            <td className="px-4 py-2"><Pill tone="info">{ip.frequency}</Pill></td>
                            <td className="px-4 py-2"><Pill tone="ok">{ip.status}</Pill></td>
                            </tr>
                        ))}
                        {inv.ips.length === 0 && (
                            <tr><td className="px-4 py-2 text-muted" colSpan={4}>No IPs in inventory.</td></tr>
                        )}
                        </Table>
                    </div>
                    </div>
                )}

                {tab === "files" && (
                    <Table head={["ID","Path","Frequency","Status"]}>
                    {inv.files.map(f => (
                        <tr key={`f-${f.id}`}>
                        <td className="px-4 py-2">{f.id}</td>
                        <td className="px-4 py-2 text-white">{f.path}</td>
                        <td className="px-4 py-2"><Pill tone="info">{f.frequency}</Pill></td>
                        <td className="px-4 py-2"><Pill tone="ok">{f.status}</Pill></td>
                        </tr>
                    ))}
                    {inv.files.length === 0 && (
                        <tr><td className="px-4 py-2 text-muted" colSpan={4}>No files in inventory.</td></tr>
                    )}
                    </Table>
                )}

                {tab === "folders" && (
                    <Table head={["ID","Path","Frequency","Status"]}>
                    {inv.folders.map(f => (
                        <tr key={`d-${f.id}`}>
                        <td className="px-4 py-2">{f.id}</td>
                        <td className="px-4 py-2 text-white">{f.path}</td>
                        <td className="px-4 py-2"><Pill tone="info">{f.frequency}</Pill></td>
                        <td className="px-4 py-2"><Pill tone="ok">{f.status}</Pill></td>
                        </tr>
                    ))}
                    {inv.folders.length === 0 && (
                        <tr><td className="px-4 py-2 text-muted" colSpan={4}>No folders in inventory.</td></tr>
                    )}
                    </Table>
                )}

                {tab === "ips" && (
                    <Table head={["ID","IP","Hostname","Frequency","Status"]}>
                    {inv.ips.map(ip => (
                        <tr key={`ip-${ip.id}`}>
                        <td className="px-4 py-2">{ip.id}</td>
                        <td className="px-4 py-2 text-white">{ip.ip}</td>
                        <td className="px-4 py-2">{ip.hostname || "—"}</td>
                        <td className="px-4 py-2"><Pill tone="info">{ip.frequency}</Pill></td>
                        <td className="px-4 py-2"><Pill tone="ok">{ip.status}</Pill></td>
                        </tr>
                    ))}
                    {inv.ips.length === 0 && (
                        <tr><td className="px-4 py-2 text-muted" colSpan={5}>No IPs in inventory.</td></tr>
                    )}
                    </Table>
                )}
                </div>
            </div>
            </div>
        </div>
        </div>
    );
}
