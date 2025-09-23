# File: backend/app/api/reports.py
from fastapi import APIRouter, Depends, Query
from typing import Dict, Any, List
import os, json

from app.core.security import get_current_active_user
from app.db.session import SessionLocal
from app.db.models import MonitoredFile, MonitoredFolder, MonitoredIP
from app.api.metrics import _count_jobs_by_kind  # on réutilise la logique
LOG_PATH = os.getenv("HIDS_LOG_PATH", "logs/hids.log")

router = APIRouter(
    prefix="/api",
    tags=["reports"],
    dependencies=[Depends(get_current_active_user)]
)

def _read_recent_events(limit: int = 50) -> list[dict]:
    if not os.path.exists(LOG_PATH):
        return []
    with open(LOG_PATH, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()[-limit*3:]  # on lit un peu plus large
    events = []
    for line in lines:
        payload = line.split("|", 2)[2].strip() if "|" in line else line.strip()
        try:
            ev = json.loads(payload)
            # on ne garde que nos événements d'activité
            if isinstance(ev, dict) and ev.get("type") in {"file_scan","folder_scan","ip_scan"}:
                events.append(ev)
        except Exception:
            continue
    # on limite après filtrage
    return events[-limit:]


@router.get("/reports", summary="Generate consolidated JSON report")
def get_report(limit_events: int = Query(50, ge=0, le=1000)) -> Dict[str, Any]:
    """
    Rapport JSON consolidé:
        - métriques globales
        - inventaire des items (actifs uniquement par défaut)
        - derniers événements (logs d'activité)
    """
    db = SessionLocal()
    try:
        # inventaire (actifs)
        files = db.query(MonitoredFile).filter(MonitoredFile.status == "active").all()
        folders = db.query(MonitoredFolder).filter(MonitoredFolder.status == "active").all()
        ips = db.query(MonitoredIP).filter(MonitoredIP.status == "active").all()

        def _s_file(f):    return {"id": f.id, "path": f.path, "frequency": f.frequency, "status": f.status}
        def _s_folder(d):  return {"id": d.id, "path": d.path, "frequency": d.frequency, "status": d.status}
        def _s_ip(i):      return {"id": i.id, "ip": i.ip, "hostname": i.hostname, "frequency": i.frequency, "status": i.status}

        jobs = _count_jobs_by_kind()
        events = _read_recent_events(limit_events) if limit_events > 0 else []

        return {
            "report": {
                "title": "HIDS-Web JSON Report",
                "version": "2.0",
            },
            "metrics": {
                "monitored": {
                    "files":   len(files),
                    "folders": len(folders),
                    "ips":     len(ips),
                    "total":   len(files) + len(folders) + len(ips),
                },
                "scheduler": jobs
            },
            "inventory": {
                "files":   [_s_file(f)   for f in files],
                "folders": [_s_folder(d) for d in folders],
                "ips":     [_s_ip(i)     for i in ips],
            },
            "events": events[-20:] if len(events) > 20 else events
        }
    finally:
        db.close()
