// import { useState } from 'react'
// import { useNavigate } from 'react-router-dom'
// import { useAuth } from '../context/AuthProvider'

// export default function Login(){
//     const { login, error, loading } = useAuth()
//     const [username, setU] = useState('admin_Hids')
//     const [password, setP] = useState('st21@g-p@ss!')
//     const nav = useNavigate()

//     const submit = async (e) => {
//         e.preventDefault()
//         // Wait for the login promise to resolve
//         const success = await login(username, password);
//         if (success) {
//             // Redirect only on successful login
//             nav('/dashboard');
//         }
//     }

//     return (
//         <div className="h-screen grid place-items-center p-6">
//             <form onSubmit={submit} className="card p-8 w-full max-w-md space-y-4">
//                 <div className="text-xl font-semibold">Sign in</div>
//                 <input className="input w-full" placeholder="Username" value={username} onChange={e=>setU(e.target.value)} />
//                 <input className="input w-full" type="password" placeholder="Password" value={password} onChange={e=>setP(e.target.value)} />
//                 {error && <div className="text-danger text-sm">{String(error)}</div>}
//                 <button className="btn w-full justify-center">{loading?'…':'Login'}</button>
//             </form>
//         </div>
//     )
// }


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
        const success = await login(username, password);
        if (success) {
            nav('/dashboard');
        }
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-4">
            <div className="w-full max-w-md">
                <form onSubmit={submit} className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 space-y-6 border border-white/20 shadow-2xl">
                    {/* En-tête centrée */}
                    <div className="text-center space-y-2">
                        <div className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                            HIDS Web
                        </div>
                        <div className="text-white/60 text-sm">Host Intrusion Detection System</div>
                    </div>

                    {/* Champs de formulaire */}
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-white/80 mb-2">Username</label>
                            <input 
                                className="w-full px-4 py-3 bg-black/20 border border-white/10 rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                                placeholder="Enter your username"
                                value={username} 
                                onChange={e => setU(e.target.value)} 
                            />
                        </div>
                        
                        <div>
                            <label className="block text-sm font-medium text-white/80 mb-2">Password</label>
                            <input 
                                className="w-full px-4 py-3 bg-black/20 border border-white/10 rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                                type="password" 
                                placeholder="Enter your password"
                                value={password} 
                                onChange={e => setP(e.target.value)} 
                            />
                        </div>
                    </div>

                    {/* Message d'erreur */}
                    {error && (
                        <div className="p-3 bg-red-500/20 border border-red-500/30 rounded-lg text-red-200 text-sm">
                            {String(error)}
                        </div>
                    )}

                    {/* Bouton de connexion */}
                    <button 
                        className="w-full py-3 px-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-medium rounded-lg transition-all duration-200 transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed"
                        disabled={loading}
                    >
                        {loading ? (
                            <div className="flex items-center justify-center">
                                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                                Signing in...
                            </div>
                        ) : (
                            'Sign In'
                        )}
                    </button>

                    {/* Informations de démo */}
                    <div className="text-center text-white/40 text-xs pt-4 border-t border-white/10">
                        Demo credentials pre-filled
                    </div>
                </form>
            </div>
        </div>
    )
}