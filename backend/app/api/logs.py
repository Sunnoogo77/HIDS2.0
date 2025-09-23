# backend/app/api/logs.py
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field

from app.core.security import get_current_active_user

# ⚠️ Définir le router AVANT d'utiliser les décorateurs
router = APIRouter(
    prefix="/logs",
    tags=["logs"],
    dependencies=[Depends(get_current_active_user)]
)

LOG_DIR = Path(os.getenv("HIDS_LOG_DIR", "logs")).resolve()

# Regex pour les logs d'activité et d'alerte avec et sans la source
HIDS_LOG_REGEX_FULL = re.compile(
    r"^(\d{4}-\d{2}-\d{2})\s(\d{2}:\d{2}:\d{2}),(\d{3})\s\|\s([A-Z]+)\s\|\s(.+?)\s\|\s(.+)$"
)
HIDS_LOG_REGEX_NO_SOURCE = re.compile(
    r"^(\d{4}-\d{2}-\d{2})\s(\d{2}:\d{2}:\d{2}),(\d{3})\s\|\s([A-Z]+)\s\|\s(.+)$"
)

def parse_log_line(line: str):
    """Parse une ligne de log HIDS et retourne un dictionnaire."""
    line = line.strip()
    if not line:
        return None

    match = HIDS_LOG_REGEX_FULL.match(line)
    if match:
        date, time, ms, level, source, message = match.groups()
        return {
            "ts": f"{date}T{time}.{ms}Z",
            "level": level,
            "source": source.strip(),
            "msg": message.strip(),
            "text": line
        }

    match = HIDS_LOG_REGEX_NO_SOURCE.match(line)
    if match:
        date, time, ms, level, message = match.groups()
        return {
            "ts": f"{date}T{time}.{ms}Z",
            "level": level,
            "source": "",
            "msg": message.strip(),
            "text": line
        }

    return {
        "ts": None,
        "level": "RAW",
        "source": "",
        "msg": line,
        "text": line
    }

def read_log_file(filename: str):
    """Lit un fichier de log et renvoie les lignes parsées."""
    fp = (LOG_DIR / filename).resolve()

    if not str(fp).startswith(str(LOG_DIR)):
        raise HTTPException(status_code=400, detail="Invalid path")

    if not fp.exists():
        return []

    try:
        lines = fp.read_text(encoding="utf-8", errors="ignore").splitlines()
        parsed_lines = [parse_log_line(line) for line in lines]
        return [l for l in parsed_lines if l is not None]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {e}")

@router.get("/hids")
def get_hids_logs(
    log_type: str = Query("activity", description="Type de log: 'activity' ou 'alerts'"),
    page: int = Query(1, ge=1),
    limit: int = Query(15, ge=1, le=500),
    level: Optional[str] = Query(None, description="DEBUG|INFO|WARNING|ERROR|CRITICAL"),
    contains: Optional[str] = Query(None),
):
    """
    Endpoint unifié pour récupérer les logs d'activité ou d'alerte.
    """
    if log_type not in ["activity", "alerts"]:
        raise HTTPException(status_code=400, detail="Log type must be 'activity' or 'alerts'")

    filename = "hids.log" if log_type == "activity" else "alerts.log"
    all_logs = read_log_file(filename)

    filtered_logs = [
        log for log in all_logs
        if (not level or (log.get('level') or '').lower() == level.lower()) and
            (not contains or contains.lower() in (log.get('msg') or '').lower())
    ]

    filtered_logs.reverse()

    total = len(filtered_logs)
    page_count = max(1, (total + limit - 1) // limit)
    page = min(page, page_count)
    start_index = (page - 1) * limit
    end_index = start_index + limit
    paginated_logs = filtered_logs[start_index:end_index]

    return {
        "lines": paginated_logs,
        "total": total,
        "page_count": page_count
    }

# ---------- Clear & Purge (compat front) ----------

class ClearBody(BaseModel):
    type: str = Field("activity", description="'activity' | 'alerts'")

class PurgeBody(BaseModel):
    type: str                         # 'activity' | 'alerts'
    level: Optional[str] = None
    from_: Optional[str] = Field(None, alias="from")  # accepte 'from' depuis le front
    to: Optional[str] = None

def _parse_iso(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None

def _ensure_admin(current_user=Depends(get_current_active_user)):
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

@router.post("/hids/clear", dependencies=[Depends(_ensure_admin)])
def clear_hids_logs(body: ClearBody):
    """
    Vide entièrement le fichier de logs demandé.
    Corps attendu (front): { "type": "activity" | "alerts" }
    """
    log_type = body.type
    if log_type not in ["activity", "alerts"]:
        raise HTTPException(status_code=400, detail="Log type must be 'activity' or 'alerts'")

    filename = "hids.log" if log_type == "activity" else "alerts.log"
    fp = (LOG_DIR / filename).resolve()

    if not str(fp).startswith(str(LOG_DIR)):
        raise HTTPException(status_code=400, detail="Invalid path")

    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        if fp.exists():
            fp.write_text("", encoding="utf-8")
        return {"status": "success", "message": f"Log file '{filename}' cleared."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing file: {e}")

@router.post("/hids/purge", dependencies=[Depends(_ensure_admin)])
def purge_hids_logs(body: PurgeBody):
    """
    Supprime les lignes correspondant aux filtres.
    Corps attendu (front): { type, level?, from?, to? }
    """
    if body.type not in ["activity", "alerts"]:
        raise HTTPException(status_code=400, detail="type must be 'activity' or 'alerts'")

    filename = "hids.log" if body.type == "activity" else "alerts.log"
    fp = (LOG_DIR / filename).resolve()

    if not str(fp).startswith(str(LOG_DIR)):
        raise HTTPException(status_code=400, detail="Invalid path")

    if not fp.exists():
        return {"status": "success", "message": "Nothing to purge."}

    lines = fp.read_text(encoding="utf-8", errors="ignore").splitlines()
    parsed = [parse_log_line(l) for l in lines]

    t_from = _parse_iso(body.from_)
    t_to = _parse_iso(body.to)
    level = (body.level or "").upper() if body.level else None

    def keep(log):
        # Si rien ne matche les filtres → on garde la ligne
        # Niveau
        if level and ((log.get("level") or "").upper() != level):
            return True  # garder si niveau différent
        # Période
        ts = log.get("ts")
        t = _parse_iso(ts) if ts else None
        if t_from and t and t < t_from:
            return True
        if t_to and t and t > t_to:
            return True
        # Sinon (match filtres) → on SUPPRIME (donc ne PAS garder)
        return False

    kept_text = [p["text"] if p else lines[i] for i, p in enumerate(parsed) if keep(p)]
    fp.write_text("\n".join(kept_text) + ("\n" if kept_text else ""), encoding="utf-8")
    purged = len(lines) - len(kept_text)
    return {"status": "success", "purged": purged}
