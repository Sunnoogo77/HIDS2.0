// export default function EngineCard({ title, counts = {}, onAction }) {
//     const { total = 0, active = 0, paused = 0 } = counts;
//     const status =
//         active > 0 ? "running" : total === 0 ? "stopped" : paused === total ? "paused" : "stopped";

//     const tone =
//         status === "running" ? "success" : status === "paused" ? "warn" : "danger";
//     const dot =
//         tone === "success" ? "bg-success" : tone === "warn" ? "bg-warn" : "bg-danger";

//     // Boutons conditionnels
//     const actions =
//         status === "running"
//         ? [
//             { key: "pause-all", label: "Pause" },
//             { key: "stop-all", label: "Stop" },
//             ]
//         : status === "paused"
//         ? [
//             { key: "resume-all", label: "Resume" },
//             { key: "stop-all", label: "Stop" },
//             ]
//         : /* stopped */
//             [{ key: "resume-all", label: "Start" }];

//     return (
//         <div className="card p-4">
//         {/* Titre plus mis en avant */}
//         <div className="text-xs text-muted">{title}</div>

//         <div className="mt-1 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
//             {/* Etat */}
//             <div>
//             <div className="text-2xl font-semibold flex items-center gap-2 leading-none">
//                 <span className={`inline-block w-2 h-2 rounded-full ${dot}`} />
//                 {status.charAt(0).toUpperCase() + status.slice(1)}
//             </div>
//             <div className="text-xs text-muted mt-1">
//                 {active}/{total} active · {paused} paused
//             </div>
//             </div>

//             {/* Actions (wrap sur petits écrans) */}
//             <div className="flex flex-wrap gap-2">
//             {actions.map((a) => (
//                 <button
//                 key={a.key}
//                 className="btn px-3 py-1.5 text-sm"
//                 onClick={() => onAction(a.key)}
//                 >
//                 {a.label}
//                 </button>
//             ))}
//             </div>
//         </div>
//         </div>
//     );
// }

import { useState } from "react";


export default function EngineCard({ title, counts = {}, onAction, disabled = false }) {
    const { total = 0, active = 0, paused = 0 } = counts;
    const [isLoading, setIsLoading] = useState(false);
    
    const status = active > 0 ? "running" : total === 0 ? "stopped" : paused === total ? "paused" : "stopped";

    const tone = status === "running" ? "success" : status === "paused" ? "warn" : "danger";
    const dot = tone === "success" ? "bg-success" : tone === "warn" ? "bg-warn" : "bg-danger";

    // Boutons conditionnels
    const actions = status === "running"
        ? [{ key: "pause-all", label: "Pause" }, { key: "stop-all", label: "Stop" }]
        : status === "paused"
        ? [{ key: "resume-all", label: "Resume" }, { key: "stop-all", label: "Stop" }]
        : [{ key: "resume-all", label: "Start" }];

    const handleAction = async (actionKey) => {
        if (disabled || isLoading) return;
        
        setIsLoading(true);
        try {
            await onAction(actionKey);
        } catch (error) {
            console.error("Action failed:", error);
        } finally {
            // Reset après un délai pour voir la confirmation
            setTimeout(() => setIsLoading(false), 1000);
        }
    };

    return (
        <div className={`card p-4 transition-all duration-200 ${isLoading ? 'opacity-70' : ''}`}>
            <div className="text-xs text-muted">{title}</div>

            <div className="mt-1 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                {/* Etat */}
                <div>
                    <div className="text-2xl font-semibold flex items-center gap-2 leading-none">
                        <span className={`inline-block w-2 h-2 rounded-full ${dot} ${isLoading ? 'animate-pulse' : ''}`} />
                        {isLoading ? "Updating..." : status.charAt(0).toUpperCase() + status.slice(1)}
                    </div>
                    <div className="text-xs text-muted mt-1">
                        {active}/{total} active · {paused} paused
                    </div>
                </div>

                {/* Actions */}
                {/* <div className="flex flex-wrap gap-2">
                    {actions.map((a) => (
                        <button
                            key={a.key}
                            className={`btn px-3 py-1.5 text-sm transition-all ${
                                disabled || isLoading ? 'opacity-50 cursor-not-allowed' : 'hover:scale-105'
                            }`}
                            onClick={() => handleAction(a.key)}
                            disabled={disabled || isLoading}
                        >
                            {isLoading ? "..." : a.label}
                        </button>
                    ))}
                </div> */}
                {/* Actions */}
                <div className="flex flex-row gap-3 flex-nowrap">
                {actions.map((a) => (
                    <button
                    key={a.key}
                    className={`px-4 py-2 text-sm rounded-xl border border-white/10 bg-panel2 
                                transition-all duration-200
                                ${disabled || isLoading 
                                    ? "opacity-50 cursor-not-allowed" 
                                    : "hover:scale-105 hover:bg-panel hover:shadow-lg"
                                }`}
                    onClick={() => handleAction(a.key)}
                    disabled={disabled || isLoading}
                    >
                    {isLoading ? "..." : a.label}
                    </button>
                ))}
                </div>

            </div>
        </div>
    );
}