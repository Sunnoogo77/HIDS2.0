// export default function EngineCard({ title, counts, onAction }) {
//     const { total=0, active=0, paused=0 } = counts||{}
//     const status = active>0 ? 'running' : (paused===total && total>0 ? 'paused' : 'stopped')
//     const tone = status==='running'?'success':status==='paused'?'warn':'danger'
//     const dot = tone==='success'?'bg-success':tone==='warn'?'bg-warn':'bg-danger'

//     return (
//         <div className="card p-5">
//         <div className="flex items-center justify-between">
//             <div>
//             <div className="text-sm text-muted">{title}</div>
//             <div className="text-2xl font-semibold flex items-center gap-2">
//                 <span className={`inline-block w-2 h-2 rounded-full ${dot}`} />
//                 {status.charAt(0).toUpperCase()+status.slice(1)}
//             </div>
//             <div className="text-xs text-muted mt-1">{active}/{total} active · {paused} paused</div>
//             </div>
//             <div className="flex gap-2">
//             <button className="btn" onClick={()=>onAction('pause-all')}>Pause</button>
//             <button className="btn" onClick={()=>onAction('resume-all')}>Resume</button>
//             <button className="btn" onClick={()=>onAction('stop-all')}>Stop</button>
//             </div>
//         </div>
//         </div>
//     )
// }


export default function EngineCard({ title, counts = {}, onAction }) {
    const { total = 0, active = 0, paused = 0 } = counts;
    const status =
        active > 0 ? "running" : total === 0 ? "stopped" : paused === total ? "paused" : "stopped";

    const tone =
        status === "running" ? "success" : status === "paused" ? "warn" : "danger";
    const dot =
        tone === "success" ? "bg-success" : tone === "warn" ? "bg-warn" : "bg-danger";

    // Boutons conditionnels
    const actions =
        status === "running"
        ? [
            { key: "pause-all", label: "Pause" },
            { key: "stop-all", label: "Stop" },
            ]
        : status === "paused"
        ? [
            { key: "resume-all", label: "Resume" },
            { key: "stop-all", label: "Stop" },
            ]
        : /* stopped */
            [{ key: "resume-all", label: "Start" }];

    return (
        <div className="card p-4">
        {/* Titre plus mis en avant */}
        <div className="text-xs text-muted">{title}</div>

        <div className="mt-1 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            {/* Etat */}
            <div>
            <div className="text-2xl font-semibold flex items-center gap-2 leading-none">
                <span className={`inline-block w-2 h-2 rounded-full ${dot}`} />
                {status.charAt(0).toUpperCase() + status.slice(1)}
            </div>
            <div className="text-xs text-muted mt-1">
                {active}/{total} active · {paused} paused
            </div>
            </div>

            {/* Actions (wrap sur petits écrans) */}
            <div className="flex flex-wrap gap-2">
            {actions.map((a) => (
                <button
                key={a.key}
                className="btn px-3 py-1.5 text-sm"
                onClick={() => onAction(a.key)}
                >
                {a.label}
                </button>
            ))}
            </div>
        </div>
        </div>
    );
}
