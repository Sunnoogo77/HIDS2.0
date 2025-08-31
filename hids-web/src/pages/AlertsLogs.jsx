// src/pages/AlertsLogs.jsx

import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { useAuth } from "../context/AuthProvider";
import { useNavigate } from "react-router-dom";

const PAGE_SIZE = 15;

// ── UI bits ────────────────────────────────────────────────────────────────────
function Badge({ children, className = "" }) {
  return (
    <span className={`px-2 py-1 rounded-full text-xs font-bold inline-flex items-center ${className}`}>
      {children}
    </span>
  );
}

// Composant LevelBadge mis à jour pour correspondre aux couleurs douces
const LevelBadge = ({ level }) => {
  const L = String(level || "").toUpperCase();
  const cls =
    L === "CRITICAL" ? "bg-red-500/30 text-white" :
    L === "HIGH"     ? "bg-red-500/20 text-red-300" :
    L === "MEDIUM"   ? "bg-yellow-500/20 text-yellow-300" :
    L === "LOW"      ? "bg-sky-500/20 text-sky-300" :
    L === "WARNING"  ? "bg-yellow-500/20 text-yellow-300" :
    L === "INFO"     ? "bg-green-500/20 text-green-300" :
                    "bg-white/5 text-muted";
  return <Badge className={cls}>{L || "—"}</Badge>;
};

function TableShell({ headers, children }) {
  return (
    <div className="card p-0 overflow-hidden">
      <table className="w-full text-sm">
        <thead className="bg-white/5 text-muted sticky top-0">
          <tr>
            {headers.map((h, i) => (
              <th key={i} className={`px-4 py-3 ${i === headers.length - 1 ? "text-right" : "text-left"}`}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>{children}</tbody>
      </table>
    </div>
  );
}

function Pager({ page, pageCount, onPage }) {
  return (
    <div className="flex items-center justify-between gap-2">
      <div className="text-xs text-muted">Page {Math.min(page, pageCount) || 1} / {pageCount || 1}</div>
      <div className="flex gap-2">
        <button
          className="px-3 py-1.5 rounded-md border border-white/10 bg-panel/50 disabled:opacity-50"
          onClick={() => onPage(Math.max(1, page - 1))}
          disabled={page <= 1}
        >← Prev</button>
        <button
          className="px-3 py-1.5 rounded-md border border-white/10 bg-panel/50 disabled:opacity-50"
          onClick={() => onPage(Math.min(pageCount || 1, page + 1))}
          disabled={page >= (pageCount || 1)}
        >Next →</button>
      </div>
    </div>
  );
}

// ── Page ──────────────────────────────────────────────────────────────────────
export default function AlertsLogs() {
  const { token, user } = useAuth(); // on récupère l'objet user
  const navigate = useNavigate();

  const [tab, setTab] = useState("alerts"); // "alerts" | "activity"
  const [page, setPage] = useState(1);

  // filtres
  const [level, setLevel] = useState("");
  const [contains, setContains] = useState("");

  // données
  const [items, setItems] = useState([]);
  const [pageCount, setPageCount] = useState(1);
  const [loading, setLoading] = useState(false);

  // reset pagination si on change d’onglet
  useEffect(() => {
    setPage(1);
    setLevel("");
    setContains("");
  }, [tab]);

  // charge une page depuis le backend
  useEffect(() => {
    // Si le token n'est pas encore disponible, on ne fait pas l'appel
    if (!token) {
        return;
    }

    let stopped = false;
    (async () => {
      setLoading(true);
      try {
        const r = await api.listHidsLog(token, {
          type: tab, page, limit: PAGE_SIZE, level, contains
        });
        if (stopped) return;
        setItems(r.lines || []);
        setPageCount(r.page_count || 1);
      } catch (e) {
        console.error("Failed to fetch logs:", e);
        if (!stopped) {
          setItems([]);
          setPageCount(1);
        }
      } finally {
        if (!stopped) setLoading(false);
      }
    })();
    return () => { stopped = true; };
  }, [token, tab, page, level, contains]);

  const onClear = async () => {
    // On utilise une boîte de dialogue personnalisée au lieu de window.confirm
    // const confirmed = await showCustomConfirmDialog("⚠️ This will permanently clear logs. Continue?");
    if (!window.confirm(`⚠️ This will permanently clear ${tab} logs. Continue?`)) return;
    try {
      await api.clearHidsLog(token, tab);
      setPage(1);
    } catch (e) {
      // On utilise une boîte de dialogue personnalisée au lieu de window.alert
      // showCustomAlertDialog("Clear failed: " + (e?.body?.detail || e.message));
      window.alert("Clear failed: " + (e?.body?.detail || e.message));
    }
  };

  const headers = ["Date", "Time", "Level", "Source", "Message"];

  // Déterminer les niveaux de filtre en fonction de l'onglet actif
  const levels = tab === "alerts"
    ? ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
    : ["INFO", "WARNING", "ERROR"];

  const isAdmin = user?.is_admin; // Vérifie si l'utilisateur est admin

  return (
    <div className="space-y-6">
      {/* Tabs + Clear */}
      <div className="flex items-center justify-between">
        <div className="flex gap-2">
          {["alerts", "activity"].map(t => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`px-3 py-1.5 rounded-md border capitalize ${tab===t ? "bg-panel2 border-white/10" : "bg-panel/50 border-white/5"}`}
            >{t}</button>
          ))}
        </div>

        <button
          onClick={onClear}
          disabled={!isAdmin} // Bouton désactivé si l'utilisateur n'est pas admin
          className="px-3 py-1.5 rounded-md border border-white/10 text-white disabled:opacity-50 disabled:cursor-not-allowed"
          title={`Clear ${tab} logs (admin only server-side)`}
          style={{
            background: isAdmin ? "linear-gradient(90deg, #d32f2f, #ef5350)" : "rgba(255, 255, 255, 0.05)",
            borderColor: isAdmin ? "#ef5350" : "rgba(255, 255, 255, 0.1)",
            color: isAdmin ? "white" : "rgba(255, 255, 255, 0.5)",
          }}
        >
          Clear logs
        </button>
      </div>

      {/* Filtres */}
      <div className="card p-3">
        <div className="flex flex-wrap gap-3">
          <select
            className="bg-panel2 border border-white/10 rounded-md text-sm px-2 py-1"
            value={level}
            onChange={e=>{ setLevel(e.target.value); setPage(1); }}
          >
            <option value="">Level: any</option>
            {levels.map(l => (
              <option key={l} value={l}>{l}</option>
            ))}
          </select>

          <input
            className="bg-panel2 border border-white/10 rounded-md text-sm px-2 py-1"
            placeholder="Search message…"
            value={contains}
            onChange={e=>{ setContains(e.target.value); setPage(1); }}
          />
        </div>
      </div>

      {/* Tableau */}
      <TableShell headers={headers}>
        {loading && (<tr><td colSpan={headers.length} className="px-4 py-6 text-muted">Loading…</td></tr>)}
        {!loading && items.length === 0 && (
          <tr><td colSpan={headers.length} className="px-4 py-6 text-muted">No log lines</td></tr>
        )}
        {!loading && items.map((ln, i)=>(
          <tr key={`${ln.ts}-${i}`} className="border-t border-white/5">
            <td className="px-4 py-2">{ln.ts ? new Date(ln.ts).toLocaleDateString() : "—"}</td>
            <td className="px-4 py-2 text-muted">{ln.ts ? new Date(ln.ts).toLocaleTimeString() : "—"}</td>
            <td className="px-4 py-2"><LevelBadge level={ln.level} /></td>
            <td className="px-4 py-2">{ln.source || "—"}</td>
            <td className="px-4 py-2 text-right font-mono">{ln.msg || "—"}</td>
          </tr>
        ))}
      </TableShell>

      <Pager page={page} pageCount={pageCount} onPage={setPage}/>
    </div>
  );
}
