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
