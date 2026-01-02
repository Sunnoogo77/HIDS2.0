from datetime import datetime, timezone
from typing import Optional, List

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from app.core.security import get_current_active_user
from app.db.session import SessionLocal
from app.db.models import MonitoredFile, MonitoredFolder, MonitoredIP
from app.services.network_monitor import get_connections_snapshot


router = APIRouter(
    prefix="/api/network",
    tags=["network"],
    dependencies=[Depends(get_current_active_user)],
)


class ConnectionItem(BaseModel):
    key: str
    proto: str
    laddr_ip: Optional[str]
    laddr_port: Optional[int]
    raddr_ip: Optional[str]
    raddr_port: Optional[int]
    status: Optional[str]
    pid: Optional[int]
    process_name: Optional[str]
    first_seen: str
    last_seen: str
    count: int


class ConnectionsResponse(BaseModel):
    ts: str
    engine_running: bool
    items: List[ConnectionItem]
    error: Optional[str] = None


def _parse_since(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        ts = float(value)
        if ts > 1e12:
            ts /= 1000.0
        return datetime.fromtimestamp(ts, tz=timezone.utc)
    except Exception:
        pass
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def _engine_running() -> bool:
    db = SessionLocal()
    try:
        files_active = db.query(MonitoredFile).filter(MonitoredFile.status == "active").count()
        folders_active = db.query(MonitoredFolder).filter(MonitoredFolder.status == "active").count()
        ips_active = db.query(MonitoredIP).filter(MonitoredIP.status == "active").count()
        return (files_active + folders_active + ips_active) > 0
    finally:
        db.close()


@router.get("/connections", response_model=ConnectionsResponse)
def list_connections(
    since: Optional[str] = Query(None, description="ISO 8601 or epoch seconds/ms"),
    limit: int = Query(500, ge=1, le=5000),
    require_running: bool = Query(True),
):
    running = _engine_running()
    if require_running and not running:
        ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        return ConnectionsResponse(ts=ts, engine_running=False, items=[])

    since_dt = _parse_since(since)
    items, error, ts = get_connections_snapshot(since=since_dt, limit=limit)
    return ConnectionsResponse(ts=ts, engine_running=running, items=items, error=error)
