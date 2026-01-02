import os
import socket
import threading
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple, List, Dict, Any

from app.core.logging import logger

try:
    import psutil
    _PSUTIL_AVAILABLE = True
except Exception:  # pragma: no cover - psutil import failure is environment-specific
    psutil = None
    _PSUTIL_AVAILABLE = False


CACHE_TTL_SECONDS = int(os.getenv("NETWORK_CACHE_TTL_SECONDS", "300"))
PROCESS_CACHE_TTL_SECONDS = int(os.getenv("NETWORK_PROCESS_CACHE_TTL_SECONDS", "60"))
MAX_SCAN_CONNECTIONS = int(os.getenv("NETWORK_MAX_CONNECTIONS", "5000"))

_LOCK = threading.Lock()
_CONN_CACHE: Dict[str, Dict[str, Any]] = {}
_PROC_CACHE: Dict[int, Dict[str, Any]] = {}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.isoformat().replace("+00:00", "Z")


def _proto_name(sock_type: int) -> str:
    if sock_type == socket.SOCK_STREAM:
        return "tcp"
    if sock_type == socket.SOCK_DGRAM:
        return "udp"
    return "unknown"


def _addr_parts(addr) -> Tuple[Optional[str], Optional[int]]:
    if not addr:
        return None, None
    if isinstance(addr, tuple):
        if len(addr) >= 2:
            return addr[0], addr[1]
        return addr[0], None
    if hasattr(addr, "ip") and hasattr(addr, "port"):
        return addr.ip, addr.port
    return None, None


def _process_name(pid: Optional[int]) -> Optional[str]:
    if not pid or not _PSUTIL_AVAILABLE:
        return None
    now = _now()
    cached = _PROC_CACHE.get(pid)
    if cached and cached["expires_at"] > now:
        return cached["name"]
    try:
        name = psutil.Process(pid).name()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        name = None
    except Exception as exc:
        logger.warning("network_monitor: failed to read process name for pid=%s (%s)", pid, exc)
        name = None
    _PROC_CACHE[pid] = {
        "name": name,
        "expires_at": now.replace(microsecond=0) + timedelta(seconds=PROCESS_CACHE_TTL_SECONDS),
    }
    return name


def _cleanup_cache(now: datetime) -> None:
    if CACHE_TTL_SECONDS <= 0:
        return
    cutoff = now.timestamp() - CACHE_TTL_SECONDS
    stale_keys = [k for k, v in _CONN_CACHE.items() if v["last_seen_dt"].timestamp() < cutoff]
    for k in stale_keys:
        _CONN_CACHE.pop(k, None)


def _normalize_connection(conn, now: datetime) -> Optional[Dict[str, Any]]:
    proto = _proto_name(conn.type)
    laddr_ip, laddr_port = _addr_parts(conn.laddr)
    raddr_ip, raddr_port = _addr_parts(conn.raddr)
    pid = conn.pid or None
    status = getattr(conn, "status", None)
    if not laddr_ip and not raddr_ip:
        return None
    key = f"{proto}|{laddr_ip}:{laddr_port}|{raddr_ip}:{raddr_port}|{pid or 0}"
    return {
        "key": key,
        "proto": proto,
        "laddr_ip": laddr_ip,
        "laddr_port": laddr_port,
        "raddr_ip": raddr_ip,
        "raddr_port": raddr_port,
        "status": status,
        "pid": pid,
        "process_name": _process_name(pid),
        "first_seen": _iso(now),
        "last_seen": _iso(now),
        "count": 1,
    }


def _normalize_connection_raw(conn) -> Optional[Dict[str, Any]]:
    proto = _proto_name(conn.type)
    laddr_ip, laddr_port = _addr_parts(conn.laddr)
    raddr_ip, raddr_port = _addr_parts(conn.raddr)
    pid = conn.pid or None
    status = getattr(conn, "status", None)
    if not laddr_ip and not raddr_ip:
        return None
    key = f"{proto}|{laddr_ip}:{laddr_port}|{raddr_ip}:{raddr_port}|{pid or 0}"
    return {
        "key": key,
        "proto": proto,
        "laddr_ip": laddr_ip,
        "laddr_port": laddr_port,
        "raddr_ip": raddr_ip,
        "raddr_port": raddr_port,
        "status": status,
        "pid": pid,
        "process_name": _process_name(pid),
    }


def get_current_connections(limit: int = 5000) -> Tuple[List[Dict[str, Any]], Optional[str], str]:
    now = _now()
    if not _PSUTIL_AVAILABLE:
        return [], "psutil_unavailable", _iso(now)

    try:
        conns = psutil.net_connections(kind="inet")
    except Exception as exc:
        logger.warning("network_monitor: psutil.net_connections failed (%s)", exc)
        return [], "psutil_failed", _iso(now)

    max_items = max(1, min(limit, MAX_SCAN_CONNECTIONS))
    conns = conns[:max_items]
    items: List[Dict[str, Any]] = []
    for conn in conns:
        item = _normalize_connection_raw(conn)
        if item:
            items.append(item)
    return items, None, _iso(now)


def get_connections_snapshot(
    since: Optional[datetime] = None,
    limit: int = 500,
) -> Tuple[List[Dict[str, Any]], Optional[str], str]:
    now = _now()
    if not _PSUTIL_AVAILABLE:
        return [], "psutil_unavailable", _iso(now)

    try:
        conns = psutil.net_connections(kind="inet")
    except Exception as exc:
        logger.warning("network_monitor: psutil.net_connections failed (%s)", exc)
        return [], "psutil_failed", _iso(now)

    if MAX_SCAN_CONNECTIONS > 0:
        conns = conns[:MAX_SCAN_CONNECTIONS]

    with _LOCK:
        _cleanup_cache(now)
        for conn in conns:
            item = _normalize_connection(conn, now)
            if not item:
                continue
            key = item["key"]
            cached = _CONN_CACHE.get(key)
            if cached:
                cached["last_seen_dt"] = now
                cached["count"] += 1
                cached["status"] = item["status"]
                cached["process_name"] = item["process_name"]
            else:
                _CONN_CACHE[key] = {
                    **item,
                    "first_seen_dt": now,
                    "last_seen_dt": now,
                }

        items: List[Dict[str, Any]] = []
        for entry in _CONN_CACHE.values():
            last_seen_dt = entry["last_seen_dt"]
            if since and last_seen_dt <= since:
                continue
            items.append({
                "key": entry["key"],
                "proto": entry["proto"],
                "laddr_ip": entry["laddr_ip"],
                "laddr_port": entry["laddr_port"],
                "raddr_ip": entry["raddr_ip"],
                "raddr_port": entry["raddr_port"],
                "status": entry.get("status"),
                "pid": entry.get("pid"),
                "process_name": entry.get("process_name"),
                "first_seen": _iso(entry["first_seen_dt"]),
                "last_seen": _iso(entry["last_seen_dt"]),
                "count": entry["count"],
            })

    items.sort(key=lambda i: i.get("last_seen") or "", reverse=True)
    return items[:limit], None, _iso(now)
