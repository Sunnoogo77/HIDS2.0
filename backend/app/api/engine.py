from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_active_user
from app.db.models import User as ORMUser
from app.services.monitoring_service import (
    get_file_items, update_file_item,
    get_folder_items, update_folder_item,
    get_ip_items, update_ip_item
)
from app.core.scheduler import add_interval_job, remove_job, FREQ_SECONDS
from app.services.scan_tasks import scan_file, scan_folder, scan_ip

router = APIRouter(
    prefix="/api/engine",
    tags=["engine"],
    dependencies=[Depends(get_current_active_user)],
)

def _iter(kind: str):
    if kind == "file":
        return "file", get_file_items, update_file_item, scan_file
    if kind == "folder":
        return "folder", get_folder_items, update_folder_item, scan_folder
    if kind == "ip":
        return "ip", get_ip_items, update_ip_item, scan_ip
    raise HTTPException(status_code=400, detail="unknown kind")

@router.get("/state")
def engine_state():
    # état synthétique pour dashboard
    kinds = ["file", "folder", "ip"]
    out = {}
    for k in kinds:
        tag, getter, *_ = _iter(k)
        items = getter(skip=0, limit=10000)
        total = len(items)
        active = sum(1 for x in items if getattr(x, "status", "active") == "active")
        paused = total - active
        out[k] = {"total": total, "active": active, "paused": paused}
    out["engine"] = "running"  # si l’app est up & scheduler lancé
    return out

@router.post("/{kind}/pause-all")
def pause_all(kind: str):
    tag, getter, updater, _ = _iter(kind)
    items = getter(skip=0, limit=10000)
    for it in items:
        if getattr(it, "status", "active") == "active":
            # set paused
            updater(it.id, type(it)(**{**it.dict(), "status": "paused"}))
            remove_job(tag, it.id)
    return {"ok": True, "paused": len(items)}

@router.post("/{kind}/resume-all")
def resume_all(kind: str):
    tag, getter, updater, scan_fn = _iter(kind)
    items = getter(skip=0, limit=10000)
    for it in items:
        # set active
        updater(it.id, type(it)(**{**it.dict(), "status": "active"}))
        sec = FREQ_SECONDS.get(getattr(it, "frequency", "hourly"), 3600)
        if tag == "file":
            add_interval_job("file", it.id, sec, scan_fn, item_id=it.id, path=it.path)
        elif tag == "folder":
            add_interval_job("folder", it.id, sec, scan_fn, item_id=it.id, path=it.path)
        else:
            add_interval_job("ip", it.id, sec, scan_fn, item_id=it.id, ip=it.ip, hostname=getattr(it, "hostname", None))
    return {"ok": True}

@router.post("/{kind}/stop-all")
def stop_all(kind: str):
    # arrêt fort = retirer les jobs + passer en paused
    tag, getter, updater, _ = _iter(kind)
    items = getter(skip=0, limit=10000)
    for it in items:
        remove_job(tag, it.id)
        if getattr(it, "status", "active") == "active":
            updater(it.id, type(it)(**{**it.dict(), "status": "paused"}))
    return {"ok": True}
