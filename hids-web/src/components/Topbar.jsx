import { useAuth } from '../context/AuthProvider'
    export default function Topbar(){
    const { logout } = useAuth()
    return (
        <header className="flex items-center justify-between px-6 h-16 border-b border-white/5 bg-panel sticky top-0 z-10">
        <div className="text-muted">Version 2.0</div>
        <button className="btn" onClick={logout}>Logout</button>
        </header>
    )
}
