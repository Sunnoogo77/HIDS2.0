import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthProvider'
import { api } from '../lib/api'
import Table from '../components/Table'

export default function AlertsLogs(){
    const { token } = useAuth()
    const [events, setEvents] = useState([])

    useEffect(()=>{
        (async()=>{ setEvents(await api.activity(token, 400)) })().catch(console.error)
    },[token])

    return (
        <div className="space-y-4">
        <div className="text-xl font-semibold">Alerts & Logs</div>
        <Table
            columns={['Date/Time','Type','Entity','Details']}
            rows={events.slice().reverse().map((e,i)=>(
            <tr key={i}>
                <td className="px-4 py-3">{new Date(e.ts).toLocaleString()}</td>
                <td className="px-4 py-3"><span className="badge">{e.type}</span></td>
                <td className="px-4 py-3">{e.path || e.ip}</td>
                <td className="px-4 py-3">{e.result||''}</td>
            </tr>
            ))}
            empty="No activity yet"
        />
        </div>
    )
}
