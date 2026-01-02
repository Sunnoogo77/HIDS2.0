# File: backend/app/api/reports.py
from fastapi import APIRouter, Depends, Query
from typing import Dict, Any
import os
from datetime import datetime

from app.core.security import get_current_active_user
from app.db.session import SessionLocal
from app.db.models import MonitoredFile, MonitoredFolder, MonitoredIP
from app.api.metrics import _count_jobs_by_kind  # on reutilise la logique
from app.core.log_parsing import extract_json_payload

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
        lines = f.readlines()[-limit * 3:]
    events = []
    for line in lines:
        ev = extract_json_payload(line)
        if isinstance(ev, dict) and ev.get("type") == "activity":
            events.append(ev)
    return events[-limit:]


@router.get("/reports", summary="Generate consolidated JSON report")
def get_report(limit_events: int = Query(50, ge=0, le=1000)) -> Dict[str, Any]:
    """
    Rapport JSON consolide:
        - metriques globales
        - inventaire des items (tous statuts confondus)
        - derniers evenements (logs d'activite)
    """
    db = SessionLocal()
    try:
        files = db.query(MonitoredFile).all()
        folders = db.query(MonitoredFolder).all()
        ips = db.query(MonitoredIP).all()

        def _s_file(f):
            return {"id": f.id, "path": f.path, "frequency": f.frequency, "status": f.status}

        def _s_folder(d):
            return {"id": d.id, "path": d.path, "frequency": d.frequency, "status": d.status}

        def _s_ip(i):
            return {"id": i.id, "ip": i.ip, "hostname": i.hostname, "frequency": i.frequency, "status": i.status}

        jobs = _count_jobs_by_kind()
        events = _read_recent_events(limit_events) if limit_events > 0 else []

        return {
            "report": {
                "title": "HIDS-Web JSON Report",
                "version": "2.0",
                "generatedAt": datetime.utcnow().isoformat(),
            },
            "metrics": {
                "monitored": {
                    "files": len(files),
                    "folders": len(folders),
                    "ips": len(ips),
                    "total": len(files) + len(folders) + len(ips),
                },
                "scheduler": jobs,
            },
            "inventory": {
                "files": [_s_file(f) for f in files],
                "folders": [_s_folder(d) for d in folders],
                "ips": [_s_ip(i) for i in ips],
            },
            "events": events[-20:] if len(events) > 20 else events,
        }
    finally:
        db.close()
