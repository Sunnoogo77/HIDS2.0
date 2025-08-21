import { NavLink } from 'react-router-dom'
import { LayoutDashboard, Shield, Bell, FileText, Settings } from 'lucide-react'

const LinkItem = ({to, icon:Icon, label}) => (
    <NavLink to={to} className={({isActive}) =>
        `flex items-center gap-3 px-4 py-2 rounded-xl transition
        ${isActive ? 'bg-panel2 text-white' : 'text-muted hover:text-white hover:bg-panel2'}`
    }>
        <Icon size={18} /> <span>{label}</span>
    </NavLink>
)

export default function Sidebar(){
    return (
        <aside className="w-64 p-4 border-r border-white/5 bg-panel min-h-screen">
        <div className="px-3 pb-4">
            <div className="text-xl font-semibold">HIDS‑Web <span className="text-muted text-sm">2.0</span></div>
        </div>
        <nav className="flex flex-col gap-1">
            <LinkItem to="/dashboard" icon={LayoutDashboard} label="Dashboard" />
            <LinkItem to="/surveillance" icon={Shield} label="Surveillance" />
            <LinkItem to="/alerts" icon={Bell} label="Alerts & Logs" />
            <LinkItem to="/reports" icon={FileText} label="Reports" />
            <LinkItem to="/settings" icon={Settings} label="Settings" />
        </nav>
        </aside>
    )
}
