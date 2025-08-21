import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthProvider'
import { api } from '../lib/api'

export default function Reports(){
    const { token } = useAuth()
    const [report, setReport] = useState(null)
    useEffect(()=>{ (async()=> setReport(await api.reports(token)))() },[token])

    const download = () => {
        const blob = new Blob([JSON.stringify(report,null,2)], {type:'application/json'})
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url; a.download = `hids-report-${Date.now()}.json`; a.click()
        URL.revokeObjectURL(url)
    }

    if(!report) return <div>Loading…</div>
    return (
        <div className="space-y-4">
        <div className="flex items-center justify-between">
            <div className="text-xl font-semibold">Reports</div>
            <button className="btn" onClick={download}>Export JSON</button>
        </div>
        <pre className="card p-4 overflow-auto text-sm">{JSON.stringify(report, null, 2)}</pre>
        </div>
    )
}
