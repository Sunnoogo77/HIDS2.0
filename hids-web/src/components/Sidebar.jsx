// // import { NavLink } from 'react-router-dom'
// // import { LayoutDashboard, Shield, Bell, FileText, Settings } from 'lucide-react'

// // const LinkItem = ({to, icon:Icon, label}) => (
// //     <NavLink to={to} className={({isActive}) =>
// //         `flex items-center gap-3 px-4 py-2 rounded-xl transition
// //         ${isActive ? 'bg-panel2 text-white' : 'text-muted hover:text-white hover:bg-panel2'}`
// //     }>
// //         <Icon size={18} /> <span>{label}</span>
// //     </NavLink>
// // )

// // export default function Sidebar(){
// //     return (
// //         <aside className="w-64 p-4 border-r border-white/5 bg-panel min-h-screen">
// //         <div className="px-3 pb-4">
// //             <div className="text-xl font-semibold">HIDS‑Web <span className="text-muted text-sm">2.0</span></div>
// //         </div>
// //         <nav className="flex flex-col gap-1">
// //             <LinkItem to="/dashboard" icon={LayoutDashboard} label="Dashboard" />
// //             <LinkItem to="/surveillance" icon={Shield} label="Surveillance" />
// //             <LinkItem to="/alerts" icon={Bell} label="Alerts & Logs" />
// //             <LinkItem to="/reports" icon={FileText} label="Reports" />
// //             <LinkItem to="/settings" icon={Settings} label="Settings" />
// //         </nav>
// //         </aside>
// //     )
// // }



// // Fichier corrigé : hids-web/src/components/Sidebar.jsx

// import { NavLink } from 'react-router-dom'
// import { LayoutDashboard, Shield, Bell, FileText, Settings } from 'lucide-react'
// import { useAuth } from '../context/AuthProvider'; // Importez le hook useAuth

// const LinkItem = ({to, icon:Icon, label}) => (
//     <NavLink to={to} className={({isActive}) =>
//         `flex items-center gap-3 px-4 py-2 rounded-xl transition
//         ${isActive ? 'bg-panel2 text-white' : 'text-muted hover:text-white hover:bg-panel2'}`
//     }>
//         <Icon size={18} /> <span>{label}</span>
//     </NavLink>
// )

// export default function Sidebar(){
//     const { user } = useAuth(); // Obtenez l'utilisateur du contexte

//     return (
//         <aside className="w-64 p-4 border-r border-white/5 bg-panel min-h-screen">
//         <div className="px-3 pb-4">
//             <div className="text-xl font-semibold">HIDS‑Web <span className="text-muted text-sm">2.0</span></div>
//         </div>
//         <nav className="flex flex-col gap-1">
//             <LinkItem to="/dashboard" icon={LayoutDashboard} label="Dashboard" />
//             <LinkItem to="/surveillance" icon={Shield} label="Surveillance" />
//             <LinkItem to="/alerts" icon={Bell} label="Alerts & Logs" />
//             <LinkItem to="/reports" icon={FileText} label="Reports" />
            
//             {/* Conditionnez l'affichage du lien "Settings" */}
//             {user?.is_admin && (
//                 <LinkItem to="/settings" icon={Settings} label="Settings" />
//             )}
//         </nav>
//         </aside>
//     )
// }


// hids-web/src/components/Sidebar.jsx
import { NavLink } from "react-router-dom";
import { LayoutDashboard, Shield, Bell, FileText, Settings, ShieldCheck } from "lucide-react";
import { useAuth } from "../context/AuthProvider";

const LinkItem = ({ to, icon: Icon, label }) => (
  <NavLink
    to={to}
    className={({ isActive }) =>
      [
        "flex items-center gap-3 px-4 py-2 rounded-lg text-sm font-medium transition",
        "border border-transparent",
        isActive
          ? "bg-cyan-500/10 border-cyan-400/30 text-white"
          : "text-white/70 hover:text-white hover:bg-white/5 hover:border-white/10",
      ].join(" ")
    }
  >
    <Icon size={18} className="text-white/80" />
    <span>{label}</span>
  </NavLink>
);

export default function Sidebar() {
  const { user } = useAuth();

  return (
    <aside className="w-64 shrink-0 border-r border-white/10 bg-slate-900/70 backdrop-blur-xl min-h-screen flex flex-col">
      {/* Header */}
      <div className="px-5 py-6 border-b border-white/10">
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-5 w-5 text-cyan-400" />
          <span className="text-sm font-semibold tracking-tight">HIDS-Web</span>
          <span className="ml-1 rounded-md border border-white/10 bg-white/5 px-1.5 py-0.5 text-[10px] text-white/60">
            2.0
          </span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex flex-col gap-1 p-4 flex-1">
        <LinkItem to="/dashboard" icon={LayoutDashboard} label="Dashboard" />
        <LinkItem to="/surveillance" icon={Shield} label="Surveillance" />
        <LinkItem to="/alerts" icon={Bell} label="Alerts & Logs" />
        <LinkItem to="/reports" icon={FileText} label="Reports" />

        {user?.is_admin && (
          <LinkItem to="/settings" icon={Settings} label="Settings" />
        )}
      </nav>
    </aside>
  );
}
