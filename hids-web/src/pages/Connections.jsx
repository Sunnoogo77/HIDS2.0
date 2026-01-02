import { useEffect, useMemo, useRef, useState } from "react";
import { useAuth } from "../context/AuthProvider";
import { api } from "../lib/api";

const STREAM_OPTIONS = [
  { label: "250ms", value: 250 },
  { label: "500ms", value: 500 },
  { label: "1s", value: 1000 },
];

const POLL_OPTIONS = [
  { label: "2s", value: 2000 },
  { label: "5s", value: 5000 },
  { label: "10s", value: 10000 },
];

const formatAddr = (ip, port) => {
  if (!ip && !port) return "-";
  if (ip && port) return `${ip}:${port}`;
  return ip || String(port);
};

const sortConnections = (list) =>
  list.sort((a, b) => new Date(b.last_seen) - new Date(a.last_seen));

const applyDelta = (prev, { added = [], updated = [], removed = [] } = {}) => {
  const map = new Map(prev.map((item) => [item.key, item]));
  added.forEach((item) => map.set(item.key, item));
  updated.forEach((item) => map.set(item.key, item));
  removed.forEach((key) => map.delete(key));
  return sortConnections(Array.from(map.values()));
};

const buildWsUrl = (token, intervalMs) => {
  const base = import.meta.env.VITE_API_BASE || "";
  if (base) {
    const wsBase = base.replace(/^http/, "ws").replace(/\/api\/?$/, "");
    return `${wsBase}/ws/network?interval_ms=${intervalMs}&token=${encodeURIComponent(token)}`;
  }
  const scheme = window.location.protocol === "https:" ? "wss" : "ws";
  return `${scheme}://${window.location.host}/ws/network?interval_ms=${intervalMs}&token=${encodeURIComponent(token)}`;
};

export default function Connections() {
  const { token } = useAuth();
  const [items, setItems] = useState([]);
  const [engineState, setEngineState] = useState("unknown");
  const [streamMs, setStreamMs] = useState(500);
  const [pollMs, setPollMs] = useState(2000);
  const [query, setQuery] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [paused, setPaused] = useState(false);
  const [wsActive, setWsActive] = useState(false);
  const [wsFallback, setWsFallback] = useState(false);
  const lastTsRef = useRef(null);
  const retryRef = useRef(0);

  useEffect(() => {
    if (!token || paused || wsFallback) return;
    let stopped = false;
    let ws = null;

    const connect = () => {
      if (stopped) return;
      ws = new WebSocket(buildWsUrl(token, streamMs));
      ws.onopen = () => {
        setWsActive(true);
        setError("");
        retryRef.current = 0;
      };
      ws.onmessage = (event) => {
        let msg = null;
        try {
          msg = JSON.parse(event.data);
        } catch {
          return;
        }
        if (msg?.error) {
          setError(`Network monitor error: ${msg.error}`);
        }
        if (msg?.engine_running === false) {
          setEngineState("stopped");
          setItems([]);
          lastTsRef.current = null;
          return;
        }
        if (typeof msg?.engine_running === "boolean") {
          setEngineState(msg.engine_running ? "running" : "stopped");
        }
        if (msg?.type === "heartbeat") {
          return;
        }
        if (msg?.added || msg?.updated || msg?.removed) {
          setItems((prev) => applyDelta(prev, msg));
        }
      };
      ws.onerror = () => {
        ws?.close();
      };
      ws.onclose = () => {
        setWsActive(false);
        if (stopped) return;
        retryRef.current += 1;
        if (retryRef.current >= 3) {
          setWsFallback(true);
          return;
        }
        const delay = Math.min(1000 * retryRef.current, 5000);
        setTimeout(connect, delay);
      };
    };

    connect();
    return () => {
      stopped = true;
      if (ws && ws.readyState <= 1) ws.close();
    };
  }, [token, streamMs, paused, wsFallback]);

  useEffect(() => {
    if (!token || !wsFallback || paused) return;
    let stopped = false;
    let timerId = null;

    const poll = async () => {
      if (stopped) return;
      setLoading(true);
      try {
        const state = await api.engineState(token);
        const engine = state?.engine || "unknown";
        setEngineState(engine);

        if (engine !== "running") {
          setItems([]);
          setError("");
          lastTsRef.current = null;
          return;
        }

        const res = await api.listConnections(token, {
          since: lastTsRef.current,
          limit: 500,
          requireRunning: true,
        });
        if (stopped) return;
        if (res.error) {
          setError(`Network monitor error: ${res.error}`);
        } else {
          setError("");
        }
        lastTsRef.current = res.ts;
        setItems((prev) => applyDelta(prev, { added: res.items || [] }));
      } catch (e) {
        if (!stopped) setError(e?.body?.detail || e.message || "Network fetch failed");
      } finally {
        if (!stopped) setLoading(false);
      }
    };

    poll().catch(console.error);
    timerId = setInterval(() => poll().catch(console.error), pollMs);

    return () => {
      stopped = true;
      if (timerId) clearInterval(timerId);
    };
  }, [token, pollMs, wsFallback, paused]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return items;
    return items.filter((item) => {
      const hay = [
        item.raddr_ip,
        item.laddr_ip,
        item.process_name,
        item.proto,
        String(item.pid || ""),
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
      return hay.includes(q);
    });
  }, [items, query]);

  const mode = paused ? "paused" : wsFallback ? "polling" : "live";

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-lg font-semibold">Network Monitor</div>
          <div className="text-xs text-muted flex items-center gap-2">
            <span>
              Engine:{" "}
              <span className={engineState === "running" ? "text-emerald-300" : "text-amber-300"}>
                {engineState}
              </span>
            </span>
            {mode === "live" && (
              <span className={`px-2 py-0.5 rounded-full text-[10px] ${wsActive ? "bg-emerald-500/20 text-emerald-300" : "bg-yellow-500/20 text-yellow-200"}`}>
                LIVE
              </span>
            )}
            {mode === "polling" && (
              <span className="px-2 py-0.5 rounded-full text-[10px] bg-sky-500/20 text-sky-200">POLLING</span>
            )}
            {mode === "paused" && (
              <span className="px-2 py-0.5 rounded-full text-[10px] bg-white/10 text-white/70">PAUSED</span>
            )}
          </div>
        </div>

        <div className="flex items-center gap-3">
          <input
            className="bg-panel2 border border-white/10 rounded-md text-sm px-3 py-1.5"
            placeholder="Filter by IP, process, PID."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />

          {mode === "polling" ? (
            <select
              className="bg-panel2 border border-white/10 rounded-md text-sm px-2 py-1"
              value={pollMs}
              onChange={(e) => setPollMs(Number(e.target.value))}
            >
              {POLL_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  Poll {opt.label}
                </option>
              ))}
            </select>
          ) : (
            <select
              className="bg-panel2 border border-white/10 rounded-md text-sm px-2 py-1"
              value={streamMs}
              onChange={(e) => setStreamMs(Number(e.target.value))}
            >
              {STREAM_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  Stream {opt.label}
                </option>
              ))}
            </select>
          )}

          <button
            className="px-3 py-1.5 rounded-md border border-white/10 bg-panel2 hover:bg-panel transition"
            onClick={() => {
              if (paused) {
                setPaused(false);
                setWsFallback(false);
              } else {
                setPaused(true);
              }
            }}
          >
            {paused ? "Go live" : "Pause"}
          </button>

          {wsFallback && !paused && (
            <button
              className="px-3 py-1.5 rounded-md border border-white/10 bg-panel2 hover:bg-panel transition"
              onClick={() => setWsFallback(false)}
            >
              Retry live
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="px-3 py-2 rounded-md bg-red-500/20 text-red-300">{error}</div>
      )}

      <div className="card p-0 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-white/5 text-muted">
            <tr>
              <th className="text-left px-4 py-3">Remote</th>
              <th className="text-left px-4 py-3">Local</th>
              <th className="text-left px-4 py-3">Proto</th>
              <th className="text-left px-4 py-3">State</th>
              <th className="text-left px-4 py-3">PID</th>
              <th className="text-left px-4 py-3">Process</th>
              <th className="text-left px-4 py-3">First Seen</th>
              <th className="text-left px-4 py-3">Last Seen</th>
              <th className="text-right px-4 py-3">Count</th>
            </tr>
          </thead>
          <tbody>
            {loading && engineState === "running" && items.length === 0 && (
              <tr>
                <td colSpan={9} className="px-4 py-6 text-muted">
                  Loading connections...
                </td>
              </tr>
            )}
            {!loading && engineState !== "running" && (
              <tr>
                <td colSpan={9} className="px-4 py-6 text-muted">
                  Engine not running. Start monitoring to view connections.
                </td>
              </tr>
            )}
            {!loading && engineState === "running" && filtered.length === 0 && (
              <tr>
                <td colSpan={9} className="px-4 py-6 text-muted">
                  No active connections.
                </td>
              </tr>
            )}
            {filtered.map((item) => (
              <tr key={item.key} className="border-t border-white/5">
                <td className="px-4 py-2">{formatAddr(item.raddr_ip, item.raddr_port)}</td>
                <td className="px-4 py-2">{formatAddr(item.laddr_ip, item.laddr_port)}</td>
                <td className="px-4 py-2 uppercase">{item.proto || "-"}</td>
                <td className="px-4 py-2">{item.status || "-"}</td>
                <td className="px-4 py-2">{item.pid || "-"}</td>
                <td className="px-4 py-2">{item.process_name || "-"}</td>
                <td className="px-4 py-2">{item.first_seen ? new Date(item.first_seen).toLocaleString() : "-"}</td>
                <td className="px-4 py-2">{item.last_seen ? new Date(item.last_seen).toLocaleString() : "-"}</td>
                <td className="px-4 py-2 text-right">{item.count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
