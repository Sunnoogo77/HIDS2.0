export default function Table({ columns=[], rows=[], empty="No data" }){
    return (
        <div className="card overflow-hidden">
        <table className="w-full">
            <thead className="bg-panel2">
            <tr>{columns.map((c,i)=><th key={i} className="text-left px-4 py-3 text-muted text-sm">{c}</th>)}</tr>
            </thead>
            <tbody>
            {rows.length===0 && <tr><td className="px-4 py-6 text-muted" colSpan={columns.length}>{empty}</td></tr>}
            {rows.map((r,i)=><tr key={i} className="border-t border-white/5 hover:bg-white/[.02]">{r}</tr>)}
            </tbody>
        </table>
        </div>
    )
}
