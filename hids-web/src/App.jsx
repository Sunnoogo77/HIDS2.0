// import { useState } from 'react'
// import reactLogo from './assets/react.svg'
// import viteLogo from '/vite.svg'
// import './App.css'

// function App() {
//   const [count, setCount] = useState(0)

//   return (
//     <>
//       <div>
//         <a href="https://vite.dev" target="_blank">
//           <img src={viteLogo} className="logo" alt="Vite logo" />
//         </a>
//         <a href="https://react.dev" target="_blank">
//           <img src={reactLogo} className="logo react" alt="React logo" />
//         </a>
//       </div>
//       <h1>Vite + React</h1>
//       <div className="card">
//         <button onClick={() => setCount((count) => count + 1)}>
//           count is {count}
//         </button>
//         <p>
//           Edit <code>src/App.jsx</code> and save to test HMR
//         </p>
//       </div>
//       <p className="read-the-docs">
//         Click on the Vite and React logos to learn more
//       </p>
//     </>
//   )
// }

// export default App

import { Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Surveillance from './pages/Surveillance'
import AlertsLogs from './pages/AlertsLogs'
import Reports from './pages/Reports'
import Settings from './pages/Settings'
import Sidebar from './components/Sidebar'
import Topbar from './components/Topbar'
import { useAuth } from './context/AuthProvider'

function Protected({ children }) {
  const { token } = useAuth()
  if (!token) return <Navigate to="/login" replace />
  return children
}

export default function App() {
  return (
    <div className="min-h-screen flex">
      <Routes>
        <Route path="/login" element={<Login />} />
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
                  <Route path="/reports" element={<Reports />} />
                  <Route path="/settings" element={<Settings />} />
                </Routes>
              </Layout>
            </Protected>
          }
        />
      </Routes>
    </div>
  )
}

// function Layout({ children }) {
//   return (
//     <>
//       <Sidebar />
//       <div className="flex-1 flex flex-col">
//         <Topbar />
//         {/* <main className="p-6">{children}</main> */}
//         <main className="p-6">
//           {/* <div className="rounded-2xl bg-panel/50 p-4 border border-white/5"></div> */}
//           <div>
//             {children}
//           </div>
//         </main>
//       </div>
//     </>
//   )
// }

function Layout({ children }) {
  return (
    <>
      {/* Sidebar fixe */}
      <aside className="w-64 shrink-0">
        <Sidebar />
      </aside>

      {/* Colonne principale (topbar + contenu) */}
      <div className="flex-1 flex h-screen min-w-0 flex flex-col">
        <Topbar />

        {/* Le SEUL scroll vertical est ici */}
        <main className="flex-1 overflow-auto pt-4 px-6">
          <div>
            {children}
          </div>
        </main>
      </div>
    </>
  )
}

// function Layout({ children }) {
//   return (
//     <div className="flex h-screen overflow-hidden text-white">
//       {/* Sidebar fixe */}
//       <aside className="w-64 shrink-0">
//         <Sidebar />
//       </aside>

//       {/* Colonne principale (topbar + contenu) */}
//       <div className="flex-1 flex flex-col">
//         <Topbar />

//         {/* Le SEUL scroll vertical est ici */}
//         <main className="flex-1 overflow-auto p-6">
//           <div className="rounded-2xl  p-4">
//             {children}
//           </div>
//         </main>
//       </div>
//     </div>
//   );
// }
