import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthProvider'
import { api } from '../lib/api'
import Table from '../components/Table'
const FREQS = ['minutely','hourly','daily','weekly']

export default function Surveillance(){
    const { token } = useAuth()
    const [tab, setTab] = useState('files')
    const [files, setFiles] = useState([])
    const [folders, setFolders] = useState([])
    const [ips, setIps] = useState([])

    const reload = async () => {
        if(tab==='files') setFiles(await api.listFiles(token))
        if(tab==='folders') setFolders(await api.listFolders(token))
        if(tab==='ips') setIps(await api.listIps(token))
    }
    useEffect(()=>{ reload().catch(console.error) },[tab])

    const createItem = async () => {
        if(tab==='files'){
        const path = prompt('File path?','/etc/hosts'); if(!path) return
        await api.createFile(token,{ path, frequency:'hourly', status:'active' })
        }
        if(tab==='folders'){
        const path = prompt('Folder path?','/var/log'); if(!path) return
        await api.createFolder(token,{ path, frequency:'hourly', status:'active' })
        }
        if(tab==='ips'){
        const ip = prompt('IP?','10.0.0.1'); if(!ip) return
        const hostname = prompt('Hostname?','lab') || null
        await api.createIp(token,{ ip, hostname, frequency:'hourly', status:'active' })
        }
        await reload()
    }

    const togglePause = async (it, kind) => {
        const next = {...it, status: it.status==='active' ? 'paused' : 'active'}
        if(kind==='files') await api.updateFile(token, it.id, next)
        if(kind==='folders') await api.updateFolder(token, it.id, next)
        if(kind==='ips') await api.updateIp(token, it.id, next)
        await reload()
    }
    const scanNow = async (it, kind) => {
        if(kind==='files') await api.scanNowFile(token, it.id)
        if(kind==='folders') await api.scanNowFolder(token, it.id)
        if(kind==='ips') await api.scanNowIp(token, it.id)
        alert('Scan triggered ✅')
    }
    const del = async (it, kind) => {
        if(!confirm('Delete?')) return
        if(kind==='files') await api.deleteFile(token, it.id)
        if(kind==='folders') await api.deleteFolder(token, it.id)
        if(kind==='ips') await api.deleteIp(token, it.id)
        await reload()
    }

    return (
        <div className="space-y-6">
        <div className="flex items-center justify-between">
            <div className="text-xl font-semibold">Surveillance</div>
            <button className="btn" onClick={createItem}>+ Add</button>
        </div>

        <div className="flex gap-2">
            {['files','folders','ips'].map(t=>(
            <button key={t} className={`btn ${tab===t?'ring-2 ring-accent/40':''}`} onClick={()=>setTab(t)}>
                {t.toUpperCase()}
            </button>
            ))}
        </div>

        {tab==='files' && <Table
            columns={['Path','Frequency','Status','Actions']}
            rows={files.map(f=>(
            <tr key={f.id}>
                <td className="px-4 py-3">{f.path}</td>
                <td className="px-4 py-3">{f.frequency}</td>
                <td className="px-4 py-3"><span className="badge">{f.status}</span></td>
                <td className="px-4 py-3 flex gap-2">
                <button className="btn" onClick={()=>scanNow(f,'files')}>Scan Now</button>
                <button className="btn" onClick={()=>togglePause(f,'files')}>{f.status==='active'?'Pause':'Resume'}</button>
                <button className="btn" onClick={()=>del(f,'files')}>Delete</button>
                </td>
            </tr>
            ))}
        />}

        {tab==='folders' && <Table
            columns={['Path','Frequency','Status','Actions']}
            rows={folders.map(d=>(
            <tr key={d.id}>
                <td className="px-4 py-3">{d.path}</td>
                <td className="px-4 py-3">{d.frequency}</td>
                <td className="px-4 py-3"><span className="badge">{d.status}</span></td>
                <td className="px-4 py-3 flex gap-2">
                <button className="btn" onClick={()=>scanNow(d,'folders')}>Scan Now</button>
                <button className="btn" onClick={()=>togglePause(d,'folders')}>{d.status==='active'?'Pause':'Resume'}</button>
                <button className="btn" onClick={()=>del(d,'folders')}>Delete</button>
                </td>
            </tr>
            ))}
        />}

        {tab==='ips' && <Table
            columns={['IP','Hostname','Frequency','Status','Actions']}
            rows={ips.map(i=>(
            <tr key={i.id}>
                <td className="px-4 py-3">{i.ip}</td>
                <td className="px-4 py-3">{i.hostname||'-'}</td>
                <td className="px-4 py-3">{i.frequency}</td>
                <td className="px-4 py-3"><span className="badge">{i.status}</span></td>
                <td className="px-4 py-3 flex gap-2">
                <button className="btn" onClick={()=>scanNow(i,'ips')}>Scan Now</button>
                <button className="btn" onClick={()=>togglePause(i,'ips')}>{i.status==='active'?'Pause':'Resume'}</button>
                <button className="btn" onClick={()=>del(i,'ips')}>Delete</button>
                </td>
            </tr>
            ))}
        />}
        </div>
    )
}
