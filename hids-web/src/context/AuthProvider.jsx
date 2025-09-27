// Fichier : hids-web/src/context/AuthProvider.jsx

import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { api } from '../lib/api'
import { jwtDecode } from 'jwt-decode'; // Assurez-vous d'installer ce paquet

const AuthCtx = createContext(null)
export const useAuth = () => useContext(AuthCtx)

export function AuthProvider({ children }) {
    const [token, setToken] = useState(() => localStorage.getItem('hids.token') || '')
    const [user, setUser] = useState(null); // Nouvel état pour les informations utilisateur
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')

    // Effet pour décoder le token lorsque qu'il change
    useEffect(() => {
        if (token) {
            try {
                // Décoder le token et stocker les informations utilisateur (y compris is_admin)
                const decodedUser = jwtDecode(token);
                setUser(decodedUser);
            } catch (e) {
                console.error("Failed to decode token", e);
                setUser(null);
                setToken('');
                localStorage.removeItem('hids.token');
            }
        } else {
            setUser(null);
        }
    }, [token]);

    // // Quand un token existe, on demande le profil au backend
    // useEffect(() => {
    //     let cancelled = false;
    //     (async () => {
    //         if (!token) { setUser(null); return; }
    //         try {
    //         const me = await api.me(token);   // { id, username, email, is_admin, ... }
    //         if (!cancelled) setUser(me);
    //         } catch (e) {
    //         console.error("Failed to fetch /users/me", e);
    //         if (!cancelled) {
    //             setUser(null);
    //             setToken('');
    //             localStorage.removeItem('hids.token');
    //         }
    //         }
    //     })();
    //     return () => { cancelled = true; };
    //     }, [token]);

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
        setUser(null); // Réinitialisez l'utilisateur
        localStorage.removeItem('hids.token')
    }

    // Le contexte expose maintenant les informations de l'utilisateur
    const value = useMemo(()=>({ token, user, login, logout, loading, error }), [token, user, loading, error])
    return <AuthCtx.Provider value={value}>{children}</AuthCtx.Provider>
}