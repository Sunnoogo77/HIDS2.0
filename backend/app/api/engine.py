from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_active_user
from app.db.models import User as ORMUser
from app.services.monitoring_service import (
    get_file_items, update_file_status,  # CHANGÉ : update_file_item -> update_file_status
    get_folder_items, update_folder_status,  # CHANGÉ
    get_ip_items, update_ip_status  # CHANGÉ
)
from app.core.scheduler import add_interval_job, remove_job, FREQ_SECONDS
from app.services.scan_tasks import scan_file, scan_folder, scan_ip
from typing import Dict, Any

# Helper admin:
def require_admin(user: ORMUser = Depends(get_current_active_user)):
    if not getattr(user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user

router = APIRouter(
    prefix="/api/engine",
    tags=["engine"],
    dependencies=[Depends(get_current_active_user)],
)

# Refactoring de la fonction d'itération pour plus de clarté
def _get_monitoring_functions(kind: str) -> Dict[str, Any]:
    """
    Retourne les fonctions et tags pertinents pour un type de surveillance donné.
    """
    if kind == "file":
        return {"tag": "file", "getter": get_file_items, "updater": update_file_status, "scan_fn": scan_file}  # CHANGÉ
    if kind == "folder":
        return {"tag": "folder", "getter": get_folder_items, "updater": update_folder_status, "scan_fn": scan_folder}  # CHANGÉ
    if kind == "ip":
        return {"tag": "ip", "getter": get_ip_items, "updater": update_ip_status, "scan_fn": scan_ip}  # CHANGÉ
    raise HTTPException(status_code=400, detail="unknown kind")

@router.get("/state")
def engine_state():
    """
    Retourne un état synthétique du moteur pour le dashboard.
    """
    kinds = ["file", "folder", "ip"]
    out = {}
    for k in kinds:
        fns = _get_monitoring_functions(k)
        getter = fns["getter"]
        items = getter(skip=0, limit=10000)
        total = len(items)
        active = sum(1 for x in items if getattr(x, "status", "active") == "active")
        paused = total - active
        out[k] = {"total": total, "active": active, "paused": paused}
    out["engine"] = "running"
    return out

@router.post("/{kind}/pause-all")
def pause_all(kind: str):
    """
    Met en pause tous les éléments d'un type donné.
    """
    try:
        fns = _get_monitoring_functions(kind)
        tag, getter, updater = fns["tag"], fns["getter"], fns["updater"]
        items = getter(skip=0, limit=10000)
        paused_count = 0
        
        for it in items:
            if getattr(it, "status", "active") == "active":
                # CORRECTION : Utiliser la fonction de mise à jour du statut
                updater(it.id, "paused")  # CHANGÉ : "paused" au lieu de {"status": "paused"}
                remove_job(tag, it.id)
                paused_count += 1
                
        return {"ok": True, "paused": paused_count}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@router.post("/{kind}/resume-all")
def resume_all(kind: str):
    """
    Relance tous les éléments d'un type donné.
    """
    try:
        fns = _get_monitoring_functions(kind)
        tag, getter, updater, scan_fn = fns["tag"], fns["getter"], fns["updater"], fns["scan_fn"]
        items = getter(skip=0, limit=10000)
        resumed_count = 0
        
        for it in items:
            if getattr(it, "status", "paused") == "paused":
                # CORRECTION : Utiliser la fonction de mise à jour du statut
                updater(it.id, "active")  # CHANGÉ : "active" au lieu de {"status": "active"}
                
                sec = FREQ_SECONDS.get(getattr(it, "frequency", "hourly"), 3600)
                if tag == "file":
                    add_interval_job("file", it.id, sec, scan_fn, item_id=it.id, path=it.path)
                elif tag == "folder":
                    add_interval_job("folder", it.id, sec, scan_fn, item_id=it.id, path=it.path)
                else:
                    add_interval_job("ip", it.id, sec, scan_fn, item_id=it.id, ip=it.ip, hostname=getattr(it, "hostname", None))
                resumed_count += 1
                
        return {"ok": True, "resumed": resumed_count}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@router.post("/{kind}/stop-all")
def stop_all(kind: str):
    """
    Arrêt fort: retire les jobs et met les éléments en pause.
    """
    try:
        fns = _get_monitoring_functions(kind)
        tag, getter, updater = fns["tag"], fns["getter"], fns["updater"]
        items = getter(skip=0, limit=10000)
        stopped_count = 0
        
        for it in items:
            remove_job(tag, it.id)
            if getattr(it, "status", "active") == "active":
                # CORRECTION : Utiliser la fonction de mise à jour du statut
                updater(it.id, "paused")  # CHANGÉ : "paused" au lieu de {"status": "paused"}
                    
            stopped_count += 1
            
        return {"ok": True, "stopped": stopped_count}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@router.post("/all/start", dependencies=[Depends(require_admin)])
def start_all():
    """
    Relance tous les types de surveillance (fichiers, dossiers, IP).
    """
    resume_all("file")
    resume_all("folder")
    resume_all("ip")
    return {"ok": True}

@router.post("/all/stop", dependencies=[Depends(require_admin)])
def hard_stop_all():
    """
    Arrête tous les types de surveillance.
    """
    stop_all("file")
    stop_all("folder")
    stop_all("ip")
    return {"ok": True}