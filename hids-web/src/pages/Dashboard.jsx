import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthProvider'
import { api } from '../lib/api'
import StatCard from '../components/StatCard'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

export default function Dashboard(){
    const { token } = useAuth()
    const [metrics, setMetrics] = useState(null)
    const [events, setEvents] = useState([])

    useEffect(()=>{
        (async()=>{
        const m = await api.metrics(token)
        setMetrics(m)
        const r = await api.reports(token)
        setEvents(r.events || [])
        })().catch(console.error)
    },[token])

    if(!metrics) return <div>Loading…</div>

    const m = metrics.monitored
    const jobs = metrics.scheduler

    const chartData = [
        {name:'file', v: jobs.file||0},
        {name:'folder', v: jobs.folder||0},
        {name:'ip', v: jobs.ip||0},
    ]

    return (
        <div className="space-y-6">
        <div className="grid md:grid-cols-4 gap-4">
            <StatCard title="HIDS Engine" value="Running" hint={`Jobs: ${jobs.total}`} />
            <StatCard title="Files" value={`${m.files.active}/${m.files.total}`} />
            <StatCard title="Folders" value={`${m.folders.active}/${m.folders.total}`} />
            <StatCard title="IPs" value={`${m.ips.active}/${m.ips.total}`} />
        </div>

        <div className="grid md:grid-cols-3 gap-6">
            <div className="card p-4 md:col-span-2">
            <div className="mb-2 text-sm text-muted">Jobs by type</div>
            <div className="h-52">
                <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                    <XAxis dataKey="name"/><YAxis allowDecimals={false}/><Tooltip/>
                    <Bar dataKey="v" />
                </BarChart>
                </ResponsiveContainer>
            </div>
            </div>

            <div className="card p-4">
            <div className="mb-2 text-sm text-muted">Recent activity</div>
            <ul className="space-y-2 max-h-52 overflow-auto pr-2">
                {events.slice(-10).reverse().map((e,i)=>(
                <li key={i} className="text-sm text-muted">
                    <span className="badge">{e.type}</span> <span className="text-white">{e.path || e.ip}</span>
                    <span className="float-right">{new Date(e.ts).toLocaleTimeString()}</span>
                </li>
                ))}
                {events.length===0 && <div className="text-muted">No events yet</div>}
            </ul>
            </div>
        </div>
        </div>
    )
}
