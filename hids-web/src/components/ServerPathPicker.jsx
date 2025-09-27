function ServerPathPicker({ open, onClose, token, initial="/", kind="dir", onPick }) {
    // kind: "dir" pour folders, "file" pour files
    const [cwd, setCwd] = useState(initial || "/");
    const [items, setItems] = useState([]);
    const [sel, setSel] = useState(null);
    const [loading, setLoading] = useState(false);
    const up = () => setCwd(prev => (prev === "/" ? "/" : prev.split("/").slice(0,-1).join("/") || "/"));

    useEffect(() => {
        if (!open) return;
        setLoading(true);
        fsList(token, cwd, kind === "dir" ? "any" : "any")
        .then(d => { setItems(d.items); setCwd(d.cwd); setSel(null); })
        .catch(console.error)
        .finally(() => setLoading(false));
    }, [open, cwd, token, kind]);

    if (!open) return null;

    // Breadcrumbs
    const crumbs = cwd.split("/").filter(Boolean);
    const goCrumb = (idx) => {
        const p = "/" + crumbs.slice(0, idx+1).join("/");
        setCwd(p || "/");
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
        <div className="absolute inset-0 bg-black/60" onClick={onClose} />
        <div className="relative z-10 w-[700px] max-h-[80vh] rounded-xl bg-panel p-4 border border-white/10 shadow-lg flex flex-col">
            <div className="text-lg font-medium mb-3">Select {kind === "dir" ? "folder" : "file"} (server)</div>

            <div className="flex items-center gap-2 text-sm mb-2">
            <button className="px-2 py-1 bg-panel2 rounded border border-white/10" onClick={up}>↑ Up</button>
            <div className="truncate">
                <span className="text-muted">/</span>
                {crumbs.map((c, i) => (
                <span key={i}>
                    <button className="underline text-muted hover:text-white" onClick={() => goCrumb(i)}>{c}</button>
                    {i < crumbs.length-1 && <span className="text-muted"> / </span>}
                </span>
                ))}
                {crumbs.length === 0 && <span className="text-muted">/</span>}
            </div>
            </div>

            <div className="flex-1 overflow-auto rounded border border-white/10">
            <table className="w-full text-sm">
                <thead className="bg-white/5 text-muted">
                <tr>
                    <th className="text-left px-3 py-2">Name</th>
                    <th className="text-left px-3 py-2 w-28">Type</th>
                    <th className="text-left px-3 py-2">Path</th>
                </tr>
                </thead>
                <tbody>
                {loading && <tr><td colSpan={3} className="px-3 py-4 text-muted">Loading…</td></tr>}
                {!loading && items.length === 0 && <tr><td colSpan={3} className="px-3 py-4 text-muted">Empty</td></tr>}
                {!loading && items.map(it => (
                    <tr key={it.path}
                        className={`border-t border-white/5 hover:bg-white/5 cursor-pointer ${sel?.path===it.path ? "bg-white/10" : ""}`}
                        onDoubleClick={() => { if (it.type==="dir") setCwd(it.path); else setSel(it); }}
                        onClick={() => setSel(it)}>
                    <td className="px-3 py-2 text-white">{it.name}</td>
                    <td className="px-3 py-2">{it.type}</td>
                    <td className="px-3 py-2 text-muted">{it.path}</td>
                    </tr>
                ))}
                </tbody>
            </table>
            </div>

            <div className="mt-3 flex justify-between items-center">
            <div className="text-xs text-muted">
                Double‑clique sur un dossier pour l’ouvrir.  
                Sélectionne un {kind==="dir" ? "dossier" : "fichier"} puis “Use this path”.
            </div>
            <div className="flex gap-2">
                <button className="btn-secondary" onClick={onClose}>Cancel</button>
                <button
                className="btn-primary"
                disabled={!sel || (kind==="dir" && sel.type!=="dir") || (kind==="file" && sel.type!=="file")}
                onClick={() => onPick(sel.path)}
                >
                Use this path
                </button>
            </div>
            </div>
        </div>
        </div>
    );
}
