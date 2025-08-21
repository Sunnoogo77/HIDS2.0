import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthProvider'
import { api } from '../lib/api'

export default function Settings(){
    const { token } = useAuth()
    const [users, setUsers] = useState([])
    useEffect(()=>{ (async()=> {
        try{ setUsers(await api.users(token)) }catch(e){ /* non-admin → ignore */ }
    })() },[token])

    return (
        <div className="space-y-6">
        <div className="text-xl font-semibold">Settings</div>
        <div className="card p-4">
            <div className="text-sm text-muted mb-3">Users & Auth (admin-only)</div>
            <table className="w-full">
            <thead className="text-left text-sm text-muted">
                <tr><th className="py-2">Username</th><th>Email</th><th>Admin</th></tr>
            </thead>
            <tbody>
                {users.map(u=>(
                <tr key={u.id} className="border-t border-white/5">
                    <td className="py-2">{u.username}</td>
                    <td>{u.email}</td>
                    <td>{u.is_admin ? 'Yes':'No'}</td>
                </tr>
                ))}
                {users.length===0 && <tr><td colSpan="3" className="text-muted py-4">You are not admin or no data.</td></tr>}
            </tbody>
            </table>
        </div>
        </div>
    )
}
