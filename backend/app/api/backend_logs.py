from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.security import get_current_active_user
from pathlib import Path
import os

router = APIRouter(
    prefix="/api/logs/backend",
    tags=["backend-logs"],
    dependencies=[Depends(get_current_active_user)]
)

LOG_DIR = Path(os.getenv("HIDS_LOG_DIR", "logs")).resolve()

def _safe_join(filename: str) -> Path:
    fp = (LOG_DIR / filename).resolve()
    if not str(fp).startswith(str(LOG_DIR)):
        raise HTTPException(status_code=400, detail="Invalid path")
    return fp

@router.get("/files")
def list_files():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    files = [f.name for f in LOG_DIR.iterdir() if f.is_file() and f.name.lower().endswith((".log", ".log.txt", ".txt"))]
    files.sort()
    return {"files": files or ["app.log"]}

@router.get("")
def read_logs(
    file: str = Query("app.log"),
    page: int = Query(1, ge=1),
    limit: int = Query(15, ge=1, le=500),
    level: str | None = Query(None, description="DEBUG|INFO|WARNING|ERROR|CRITICAL"),
    contains: str | None = Query(None),
):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    fp = _safe_join(file)
    if not fp.exists():
        return {"file": file, "page": 1, "page_count": 1, "lines": []}

    lines = fp.read_text(encoding="utf-8", errors="ignore").splitlines()

    def parse(line: str):
        l = line.strip()
        lv = None
        # Naïf : détecte un niveau de log standard
        for cand in ["DEBUG","INFO","WARNING","ERROR","CRITICAL"]:
            if f" {cand} " in l or l.startswith(cand) or f"[{cand}]" in l:
                lv = cand
                break
        # L'horodatage n'est pas garanti, on retourne la ligne brute pour la lisibilité
        return {"ts": "", "level": lv, "msg": l, "text": l}

    rows = [parse(l) for l in lines]

    if level:
        rows = [r for r in rows if (r["level"] or "").upper() == level.upper()]
    if contains:
        s = contains.lower()
        rows = [r for r in rows if s in (r["msg"] or "").lower()]

    total = len(rows)
    page_count = max(1, (total + limit - 1) // limit)
    page = min(page, page_count)
    start = (page - 1) * limit
    end = start + limit
    return {"file": file, "page": page, "page_count": page_count, "lines": rows[start:end]}
