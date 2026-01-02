import asyncio
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple

from app.core.logging import logger
from app.db.session import SessionLocal
from app.db.models import MonitoredFile, MonitoredFolder, MonitoredIP
from app.services.network_monitor import get_current_connections


MIN_INTERVAL_MS = 250
MAX_INTERVAL_MS = 1000
HEARTBEAT_SECONDS = 10


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.isoformat().replace("+00:00", "Z")


def _engine_running() -> bool:
    db = SessionLocal()
    try:
        files_active = db.query(MonitoredFile).filter(MonitoredFile.status == "active").count()
        folders_active = db.query(MonitoredFolder).filter(MonitoredFolder.status == "active").count()
        ips_active = db.query(MonitoredIP).filter(MonitoredIP.status == "active").count()
        return (files_active + folders_active + ips_active) > 0
    finally:
        db.close()


def clamp_interval_ms(interval_ms: int) -> int:
    return max(MIN_INTERVAL_MS, min(MAX_INTERVAL_MS, interval_ms))


def calculate_delta(
    state: Dict[str, dict],
    last_sent: Dict[str, datetime],
    current_items: List[dict],
    now: datetime,
    heartbeat_interval: int = HEARTBEAT_SECONDS,
) -> Tuple[List[dict], List[dict], List[str]]:
    added: List[dict] = []
    updated: List[dict] = []
    removed: List[str] = []

    current_by_key = {item["key"]: item for item in current_items}

    for key, item in current_by_key.items():
        if key not in state:
            entry = {
                **item,
                "first_seen": _iso(now),
                "last_seen": _iso(now),
                "count": 1,
            }
            state[key] = entry
            last_sent[key] = now
            added.append(entry)
            continue

        entry = state[key]
        prev_status = entry.get("status")
        prev_proc = entry.get("process_name")
        entry.update(item)
        entry["last_seen"] = _iso(now)
        entry["count"] = entry.get("count", 0) + 1

        changed = (prev_status != entry.get("status")) or (prev_proc != entry.get("process_name"))
        due = now - last_sent.get(key, now) >= timedelta(seconds=heartbeat_interval)
        if changed or due:
            updated.append(entry.copy())
            last_sent[key] = now

    for key in list(state.keys()):
        if key not in current_by_key:
            state.pop(key, None)
            last_sent.pop(key, None)
            removed.append(key)

    return added, updated, removed


class ConnectionStreamer:
    def __init__(self) -> None:
        self._clients: Dict[object, int] = {}
        self._state: Dict[str, dict] = {}
        self._last_sent: Dict[str, datetime] = {}
        self._task: Optional[asyncio.Task] = None
        self._interval_ms = 500
        self._last_heartbeat = 0.0
        self._last_engine_running: Optional[bool] = None
        self._engine_cached: Optional[bool] = None
        self._engine_checked_at = 0.0
        self._lock = asyncio.Lock()

    def _recompute_interval(self) -> None:
        if not self._clients:
            self._interval_ms = 500
            return
        self._interval_ms = min(self._clients.values())

    async def register(self, websocket, interval_ms: int) -> None:
        async with self._lock:
            self._clients[websocket] = clamp_interval_ms(interval_ms)
            self._recompute_interval()
            if not self._task or self._task.done():
                self._task = asyncio.create_task(self._run())

        await self._send_snapshot(websocket)

    async def unregister(self, websocket) -> None:
        async with self._lock:
            self._clients.pop(websocket, None)
            self._recompute_interval()
            if not self._clients and self._task:
                self._task.cancel()
                self._task = None

    def _get_engine_running_cached(self) -> bool:
        now = time.monotonic()
        if self._engine_cached is not None and (now - self._engine_checked_at) < 1.0:
            return self._engine_cached
        self._engine_cached = _engine_running()
        self._engine_checked_at = now
        return self._engine_cached

    async def _send_snapshot(self, websocket) -> None:
        now = _now()
        running = self._get_engine_running_cached()
        if not running:
            await self._safe_send(
                websocket,
                {
                    "ts": _iso(now),
                    "engine_running": False,
                    "added": [],
                    "updated": [],
                    "removed": [],
                    "snapshot": True,
                },
            )
            return

        items, error, ts = get_current_connections()
        if error:
            await self._safe_send(websocket, {"ts": ts, "engine_running": True, "error": error})
            return

        added, _, _ = calculate_delta(self._state, self._last_sent, items, now)
        await self._safe_send(
            websocket,
            {
                "ts": ts,
                "engine_running": True,
                "added": added,
                "updated": [],
                "removed": [],
                "snapshot": True,
            },
        )

    async def _broadcast(self, payload: dict) -> None:
        if not self._clients:
            return
        dead = []
        for ws in list(self._clients.keys()):
            ok = await self._safe_send(ws, payload)
            if not ok:
                dead.append(ws)
        if dead:
            async with self._lock:
                for ws in dead:
                    self._clients.pop(ws, None)
                self._recompute_interval()

    async def _safe_send(self, websocket, payload: dict) -> bool:
        try:
            await websocket.send_json(payload)
            return True
        except Exception:
            return False

    async def _run(self) -> None:
        while self._clients:
            start = time.monotonic()
            try:
                await self._tick()
            except Exception as exc:
                logger.warning("network_streamer: tick failed (%s)", exc)
            elapsed = time.monotonic() - start
            delay = max(self._interval_ms / 1000.0 - elapsed, 0)
            await asyncio.sleep(delay)

    async def _tick(self) -> None:
        now = _now()
        running = self._get_engine_running_cached()
        ts = _iso(now)

        if not running:
            removed = list(self._state.keys())
            self._state.clear()
            self._last_sent.clear()
            if removed or self._last_engine_running is not False:
                await self._broadcast(
                    {
                        "ts": ts,
                        "engine_running": False,
                        "added": [],
                        "updated": [],
                        "removed": removed,
                    }
                )
            self._last_engine_running = False
            await self._maybe_heartbeat(now, running)
            return

        items, error, ts = get_current_connections()
        if error:
            await self._broadcast({"ts": ts, "engine_running": True, "error": error})
            return

        added, updated, removed = calculate_delta(self._state, self._last_sent, items, now)
        changed = bool(added or updated or removed) or self._last_engine_running is not True
        self._last_engine_running = True
        if changed:
            await self._broadcast(
                {
                    "ts": ts,
                    "engine_running": True,
                    "added": added,
                    "updated": updated,
                    "removed": removed,
                }
            )
        await self._maybe_heartbeat(now, running)

    async def _maybe_heartbeat(self, now: datetime, running: bool) -> None:
        if time.monotonic() - self._last_heartbeat < HEARTBEAT_SECONDS:
            return
        self._last_heartbeat = time.monotonic()
        await self._broadcast(
            {
                "type": "heartbeat",
                "ts": _iso(now),
                "engine_running": running,
                "added": [],
                "updated": [],
                "removed": [],
            }
        )
