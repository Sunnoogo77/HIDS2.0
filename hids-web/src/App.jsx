// import { Routes, Route, Navigate } from 'react-router-dom'
// import Login from './pages/Login'
// import Dashboard from './pages/Dashboard'
// import Surveillance from './pages/Surveillance'
// import AlertsLogs from './pages/AlertsLogs'
// import Reports from './pages/Reports'
// import Settings from './pages/Settings'
// import Sidebar from './components/Sidebar'
// import Topbar from './components/Topbar'
// import { useAuth } from './context/AuthProvider'

// function Protected({ children }) {
//   const { token } = useAuth()
//   if (!token) return <Navigate to="/login" replace />
//   return children
// }

// export default function App() {
//   return (
//     <div className="min-h-screen flex">
//       <Routes>
//         <Route path="/login" element={<Login />} />
//         <Route
//           path="/*"
//           element={
//             <Protected>
//               <Layout>
//                 <Routes>
//                   <Route path="/" element={<Navigate to="/dashboard" />} />
//                   <Route path="/dashboard" element={<Dashboard />} />
//                   <Route path="/surveillance" element={<Surveillance />} />
//                   <Route path="/alerts" element={<AlertsLogs />} />
//                   <Route path="/reports" element={<Reports />} />
//                   <Route path="/settings" element={<Settings />} />
//                 </Routes>
//               </Layout>
//             </Protected>
//           }
//         />
//       </Routes>
//     </div>
//   )
// }

// function Layout({ children }) {
//   return (
//     <>
//       {/* Sidebar fixe */}
//       <aside className="w-64 shrink-0">
//         <Sidebar />
//       </aside>

//       {/* Colonne principale (topbar + contenu) */}
//       <div className="flex-1 flex h-screen min-w-0 flex flex-col">
//         <Topbar />

//         {/* Le SEUL scroll vertical est ici */}
//         <main className="flex-1 overflow-auto pt-4 px-6">
//           <div>
//             {children}
//           </div>
//         </main>
//       </div>
//     </>
//   )
// }


import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Surveillance from "./pages/Surveillance";
import AlertsLogs from "./pages/AlertsLogs";
import Reports from "./pages/Reports";
import Settings from "./pages/Settings";
import Connections from "./pages/Connections";
import Sidebar from "./components/Sidebar";
import Topbar from "./components/Topbar";
import { useAuth } from "./context/AuthProvider";

function Protected({ children }) {
  const { token } = useAuth();
  if (!token) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  return (
    <div className="min-h-screen flex bg-slate-950 text-white">
      {/* Fonds globaux cohérents (dégradé + quadrillage + halos cyan/bleu) */}
      <div className="fixed inset-0 -z-10 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950" />
      <div className="fixed -top-24 -left-24 -z-10 h-80 w-80 rounded-full bg-cyan-500/15 blur-3xl" />
      <div className="fixed bottom-[-6rem] right-24 -z-10 h-96 w-96 rounded-full bg-blue-500/10 blur-3xl" />
      <div
        className="fixed inset-0 -z-10"
        style={{
          backgroundImage:
            "linear-gradient(to right, rgba(148,163,184,0.06) 1px, transparent 1px)," +
            "linear-gradient(to bottom, rgba(148,163,184,0.06) 1px, transparent 1px)",
          backgroundSize: "32px 32px",
        }}
      />

      <Routes>
        {/* Login page */}
        <Route path="/login" element={<Login />} />

        {/* Routes protégées */}
        <Route
          path="/*"
          element={
            <Protected>
              <Layout>
                <Routes>
                  <Route path="/" element={<Navigate to="/dashboard" />} />
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/surveillance" element={<Surveillance />} />
                  <Route path="/alerts" element={<AlertsLogs />} />
                  <Route path="/connections" element={<Connections />} />
                  <Route path="/reports" element={<Reports />} />
                  <Route path="/settings" element={<Settings />} />
                </Routes>
              </Layout>
            </Protected>
          }
        />
      </Routes>
    </div>
  );
}

function Layout({ children }) {
  return (
    <>
      {/* Sidebar fixe (design cohérent glassmorphism) */}
      <aside className="w-64 shrink-0 border-r border-white/10 bg-slate-900/70 backdrop-blur-xl">
        <Sidebar />
      </aside>

      {/* Colonne principale (topbar + contenu) */}
      <div className="flex-1 flex h-screen min-w-0 flex-col">
        <Topbar />

        {/* Le SEUL scroll vertical est ici */}
        <main className="flex-1 overflow-auto p-6">
          <div className="min-h-full">{children}</div>
        </main>
      </div>
    </>
  );
}
