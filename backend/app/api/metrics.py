# File: backend/app/api/metrics.py
from fastapi import APIRouter, Depends, Query
from typing import Dict, Any
import os, json, time

from app.core.security import get_current_active_user
from app.db.session import SessionLocal
from app.db.models import MonitoredFile, MonitoredFolder, MonitoredIP
from app.core.scheduler import get_scheduler

LOG_PATH = os.getenv("HIDS_LOG_PATH", "logs/hids.log")

router = APIRouter(
    prefix="/api",
    tags=["metrics"],
    dependencies=[Depends(get_current_active_user)]
)

def _count_jobs_by_kind() -> Dict[str, int]:
    """Retourne le nombre de jobs planifiés par type (file/folder/ip)."""
    sch = get_scheduler()
    counts = {"file": 0, "folder": 0, "ip": 0, "total": 0}
    try:
        jobs = sch.get_jobs() if sch and sch.running else []
        for j in jobs:
            # nos ids sont "kind:id"
            jid = str(j.id)
            if jid.startswith("file:"):
                counts["file"] += 1
            elif jid.startswith("folder:"):
                counts["folder"] += 1
            elif jid.startswith("ip:"):
                counts["ip"] += 1
        counts["total"] = len(jobs)
    except Exception:
        pass
    return counts

def _recent_events(limit: int = 50) -> Dict[str, Any]:
    """Lit les dernières lignes du log d’activité et fait un petit résumé."""
    out = {"count": 0, "by_type": {"file_scan": 0, "folder_scan": 0, "ip_scan": 0}, "last": []}
    if not os.path.exists(LOG_PATH):
        return out
    try:
        lines = []
        with open(LOG_PATH, "rb") as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            buf, chunk = b"", 1024
            while size > 0 and len(lines) < limit:
                read = min(chunk, size)
                size -= read
                f.seek(size)
                buf = f.read(read) + buf
                while b"\n" in buf and len(lines) < limit:
                    i = buf.rfind(b"\n")
                    line, buf = buf[i+1:], buf[:i]
                    lines.append(line.decode("utf-8", errors="ignore"))
            if buf and len(lines) < limit:
                lines.append(buf.decode("utf-8", errors="ignore"))

        events = []
        for line in reversed(lines):  # chrono asc
            try:
                payload = line.split("|", 2)[2].strip() if "|" in line else line.strip()
                ev = json.loads(payload)
                events.append(ev)
            except Exception:
                continue

        out["count"] = len(events)
        for ev in events:
            t = ev.get("type")
            if t in out["by_type"]:
                out["by_type"][t] += 1
        out["last"] = events[-5:] if len(events) > 5 else events
        return out
    except Exception:
        return out

@router.get("/metrics")
def get_metrics(limit_events: int = Query(50, ge=0, le=1000)) -> Dict[str, Any]:
    """Compteurs principaux + jobs planifiés + derniers événements (log)."""
    db = SessionLocal()
    try:
        files_total   = db.query(MonitoredFile).count()
        folders_total = db.query(MonitoredFolder).count()
        ips_total     = db.query(MonitoredIP).count()

        files_active   = db.query(MonitoredFile).filter(MonitoredFile.status == "active").count()
        folders_active = db.query(MonitoredFolder).filter(MonitoredFolder.status == "active").count()
        ips_active     = db.query(MonitoredIP).filter(MonitoredIP.status == "active").count()

        jobs = _count_jobs_by_kind()
        events = _recent_events(limit_events) if limit_events > 0 else {"count": 0, "by_type": {}, "last": []}

        return {
            "monitored": {
                "files":   {"total": files_total,   "active": files_active,   "paused": files_total - files_active},
                "folders": {"total": folders_total, "active": folders_active, "paused": folders_total - folders_active},
                "ips":     {"total": ips_total,     "active": ips_active,     "paused": ips_total - ips_active},
                "total":   files_total + folders_total + ips_total
            },
            "scheduler": jobs,
            "events": events,
        }
    finally:
        db.close()
