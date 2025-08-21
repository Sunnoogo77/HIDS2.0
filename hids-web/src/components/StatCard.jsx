export default function StatCard({ title, value, hint, tone='accent' }){
    return (
        <div className="card p-5">
        <div className="text-sm text-muted">{title}</div>
        <div className="text-2xl font-semibold mt-1">{value}</div>
        {hint && <div className="text-xs text-muted mt-2">{hint}</div>}
        </div>
    )
}
