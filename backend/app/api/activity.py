# backend/app/api/activity.py
from fastapi import APIRouter, Depends, Query
from app.core.security import get_current_active_user
import os, json

LOG_PATH = os.getenv("HIDS_LOG_PATH", "logs/hids.log")
router = APIRouter(prefix="/api", tags=["activity"], dependencies=[Depends(get_current_active_user)])

@router.get("/activity")
def get_activity(limit: int = Query(200, ge=1, le=1000)):
    if not os.path.exists(LOG_PATH):
        return []
    # on lit les dernières lignes simplement
    with open(LOG_PATH, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()[-limit:]
    out = []
    for line in lines:
        try:
            # nos logs: "ts | LEVEL | {json}"
            payload = line.split("|", 2)[2].strip()
            out.append(json.loads(payload))
        except Exception:
            out.append({"raw": line.strip()})
    return out
