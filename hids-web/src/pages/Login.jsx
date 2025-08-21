import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthProvider'

export default function Login(){
    const { login, error, loading } = useAuth()
    const [username, setU] = useState('admin_Hids')
    const [password, setP] = useState('st21@g-p@ss!')
    const nav = useNavigate()

    const submit = async (e) => {
        e.preventDefault()
        if (await login(username, password)) nav('/dashboard')
    }

    return (
        <div className="h-screen grid place-items-center p-6">
        <form onSubmit={submit} className="card p-8 w-full max-w-md space-y-4">
            <div className="text-xl font-semibold">Sign in</div>
            <input className="input w-full" placeholder="Username" value={username} onChange={e=>setU(e.target.value)} />
            <input className="input w-full" type="password" placeholder="Password" value={password} onChange={e=>setP(e.target.value)} />
            {error && <div className="text-danger text-sm">{String(error)}</div>}
            <button className="btn w-full justify-center">{loading?'…':'Login'}</button>
        </form>
        </div>
    )
}
