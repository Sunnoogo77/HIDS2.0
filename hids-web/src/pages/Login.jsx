import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthProvider";
import { ShieldCheck, Cpu, Activity, BellRing, Lock } from "lucide-react";

export default function Login() {
    const { login, error, loading } = useAuth();
    const [username, setUsername] = useState("admin_Hids");
    const [password, setPassword] = useState("st21@g-p@ss!");
    const navigate = useNavigate();

    const submit = async (event) => {
        event.preventDefault();
        const success = await login(username, password);
        if (success) {
            navigate("/dashboard");
        }
    };

    return (
        <div className="min-h-screen bg-slate-950 text-white">
            <div className="grid min-h-screen lg:grid-cols-[2fr_3fr]">
                {/* Sign-in panel */}
                <div className="relative flex items-center justify-center px-6 py-16 lg:px-12">
                    <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-slate-950 to-slate-900" />
                    <div className="absolute -top-32 -left-24 h-64 w-64 rounded-full bg-cyan-500/20 blur-3xl" />
                    <div className="absolute bottom-16 right-20 h-40 w-40 rounded-full bg-sky-500/10 blur-3xl" />

                    <div className="relative z-10 w-full max-w-md">
                        <div className="rounded-3xl border border-white/10 bg-slate-900/70 p-10 shadow-2xl backdrop-blur">
                            <div className="space-y-2 text-center">
                                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-cyan-500/20 text-cyan-400">
                                    <ShieldCheck className="h-6 w-6" />
                                </div>
                                <h1 className="text-3xl font-semibold tracking-tight">HIDS Web</h1>
                                <p className="text-sm uppercase tracking-[0.35em] text-white/40">
                                    Host Intrusion Detection System
                                </p>
                            </div>

                            <form onSubmit={submit} className="mt-8 space-y-6">
                                <div className="space-y-5">
                                    <label className="block">
                                        <span className="mb-2 block text-sm font-medium text-white/70">Username</span>
                                        <input
                                            className="w-full rounded-lg border border-slate-700 bg-slate-800/70 px-4 py-3 text-white placeholder-white/40 shadow-inner outline-none transition focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/60"
                                            placeholder="Enter your username"
                                            value={username}
                                            onChange={(event) => setUsername(event.target.value)}
                                            autoComplete="username"
                                        />
                                    </label>

                                    <label className="block">
                                        <span className="mb-2 block text-sm font-medium text-white/70">Password</span>
                                        <input
                                            className="w-full rounded-lg border border-slate-700 bg-slate-800/70 px-4 py-3 text-white placeholder-white/40 shadow-inner outline-none transition focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/60"
                                            type="password"
                                            placeholder="Enter your password"
                                            value={password}
                                            onChange={(event) => setPassword(event.target.value)}
                                            autoComplete="current-password"
                                        />
                                    </label>
                                </div>

                                {error && (
                                    <div className="rounded-lg border border-red-700/50 bg-red-900/40 p-3 text-sm text-red-200">
                                        {String(error)}
                                    </div>
                                )}

                                <button
                                    type="submit"
                                    className="w-full rounded-lg bg-gradient-to-r from-cyan-500 via-blue-500 to-sky-600 py-3 font-semibold shadow-lg shadow-cyan-500/30 transition duration-200 hover:from-cyan-400 hover:via-blue-500 hover:to-sky-500 focus:outline-none focus:ring-2 focus:ring-cyan-400/70 focus:ring-offset-2 focus:ring-offset-slate-950 disabled:cursor-not-allowed disabled:opacity-50"
                                    disabled={loading}
                                >
                                    {loading ? (
                                        <div className="flex items-center justify-center gap-2 text-sm">
                                            <span className="h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent" />
                                            Signing in...
                                        </div>
                                    ) : (
                                        "Sign In"
                                    )}
                                </button>

                                <p className="border-t border-white/10 pt-4 text-center text-xs text-white/40">
                                    Demo credentials pre-filled
                                </p>
                            </form>
                        </div>
                    </div>
                </div>

                {/* Visual panel */}
                <div className="relative hidden overflow-hidden lg:flex">
                    <div className="absolute inset-0 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950" />
                    <div className="absolute -top-20 -right-16 h-72 w-72 rounded-full bg-blue-500/10 blur-3xl" />
                    <div className="absolute bottom-[-6rem] left-32 h-96 w-96 rounded-full bg-cyan-500/20 blur-3xl" />
                    <div className="absolute inset-0" style={{
                        backgroundImage:
                            "linear-gradient(to right, rgba(148, 163, 184, 0.06) 1px, transparent 1px)," +
                            "linear-gradient(to bottom, rgba(148, 163, 184, 0.06) 1px, transparent 1px)",
                        backgroundSize: "32px 32px"
                    }} />

                    <div className="relative z-10 flex h-full w-full flex-col justify-between px-16 py-20">
                        <div className="space-y-6">
                            <span className="inline-flex items-center gap-2 rounded-full border border-cyan-500/40 bg-cyan-500/10 px-4 py-1 text-sm font-medium text-cyan-200">
                                <Lock className="h-4 w-4" />
                                Real-time protection
                            </span>
                            <h2 className="text-4xl font-semibold leading-snug text-white">
                                Advanced Host Intrusion Detection for critical infrastructure
                            </h2>
                            <p className="max-w-xl text-base text-white/70">
                                HIDS Web correlates file mutations, IP anomalies, and real-time telemetry to keep your hosts secured around the clock.
                            </p>

                            <div className="grid gap-4 sm:grid-cols-2">
                                <FeatureCard
                                    icon={<ShieldCheck className="h-6 w-6 text-cyan-400" />}
                                    title="File Integrity"
                                    description="Baseline hashing and drift detection with instant alerting."
                                />
                                <FeatureCard
                                    icon={<Cpu className="h-6 w-6 text-sky-400" />}
                                    title="Agent Orchestration"
                                    description="Centralized control for every monitored host and sensor."
                                />
                                <FeatureCard
                                    icon={<Activity className="h-6 w-6 text-teal-400" />}
                                    title="Live Telemetry"
                                    description="Correlate events in real time to spot suspicious behavior early."
                                />
                                <FeatureCard
                                    icon={<BellRing className="h-6 w-6 text-blue-400" />}
                                    title="Actionable Alerts"
                                    description="Priority scoring so teams focus on what matters first."
                                />
                            </div>
                        </div>

                        <div className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 px-6 py-5">
                            <div>
                                <p className="text-sm uppercase tracking-[0.28em] text-white/40">Live posture</p>
                                <p className="text-lg font-semibold text-white">99.9% hosts secured</p>
                            </div>
                            <div className="flex gap-6 text-sm text-white/70">
                                <div className="space-y-1 text-right">
                                    <p className="font-semibold text-white">03</p>
                                    <p className="text-xs uppercase tracking-wider text-white/50">Files</p>
                                </div>
                                <div className="space-y-1 text-right">
                                    <p className="font-semibold text-white">06</p>
                                    <p className="text-xs uppercase tracking-wider text-white/50">IPs</p>
                                </div>
                                <div className="space-y-1 text-right">
                                    <p className="font-semibold text-white">24</p>
                                    <p className="text-xs uppercase tracking-wider text-white/50">Alerts cleared</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

function FeatureCard({ icon, title, description }) {
    return (
        <div className="rounded-xl border border-white/10 bg-white/5 p-4 shadow-md shadow-black/20 backdrop-blur transition hover:border-cyan-400/40 hover:bg-cyan-500/10">
            <div className="flex items-start gap-3">
                <span className="flex h-10 w-10 items-center justify-center rounded-full bg-white/10">
                    {icon}
                </span>
                <div>
                    <p className="text-sm font-semibold text-white">{title}</p>
                    <p className="mt-1 text-xs text-white/60">{description}</p>
                </div>
            </div>
        </div>
    );
}
