// import { useAuth } from '../context/AuthProvider'
//     export default function Topbar(){
//     const { logout } = useAuth()
//     return (
//         <header className="flex items-center justify-between px-6 h-16 border-b border-white/5 bg-panel sticky top-0 z-10">
//         <div className="text-muted">Version 2.0</div>
//         <button className="btn" onClick={logout}>Logout</button>
//         </header>
//     )
// }


// hids-web/src/components/Topbar.jsx
import { useAuth } from "../context/AuthProvider";
import { LogOut } from "lucide-react";

export default function Topbar() {
  const { logout } = useAuth();

  return (
    <header className="sticky top-0 z-20 flex items-center justify-between h-16 px-6 border-b border-white/10 bg-slate-900/70 backdrop-blur-xl">
      {/* Left side */}
      <div className="text-xs md:text-sm text-white/60">
        Version <span className="font-medium text-white">2.0</span>
      </div>

      {/* Right side */}
      <button
        onClick={logout}
        className="inline-flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-sm text-white/80 hover:border-cyan-400/40 hover:bg-cyan-500/10 hover:text-white transition"
      >
        <LogOut className="h-4 w-4" />
        Logout
      </button>
    </header>
  );
}
