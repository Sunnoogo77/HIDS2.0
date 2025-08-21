import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { api } from '../lib/api'

const AuthCtx = createContext(null)
export const useAuth = () => useContext(AuthCtx)

export function AuthProvider({ children }) {
    const [token, setToken] = useState(() => localStorage.getItem('hids.token') || '')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')

    const login = async (username, password) => {
        setLoading(true); setError('')
        try {
        const data = await api.login(username, password)
        setToken(data.access_token)
        localStorage.setItem('hids.token', data.access_token)
        return true
        } catch (e) {
        setError(e.message); return false
        } finally { setLoading(false) }
    }

    const logout = () => {
        setToken('')
        localStorage.removeItem('hids.token')
    }

    const value = useMemo(()=>({ token, login, logout, loading, error }), [token, loading, error])
    return <AuthCtx.Provider value={value}>{children}</AuthCtx.Provider>
}
