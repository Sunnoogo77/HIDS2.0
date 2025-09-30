# from fastapi import APIRouter, Depends, HTTPException
# from app.core.security import get_current_active_user
# from app.db.models import User as ORMUser
# from app.services.monitoring_service import (
#     get_file_items, update_file_status,
#     get_folder_items, update_folder_status,
#     get_ip_items, update_ip_status,
# )
# from app.core.scheduler import add_interval_job, remove_job, FREQ_SECONDS
# from app.services.scan_tasks import scan_file, scan_folder, scan_ip
# from typing import Dict, Any


# # Helper admin:
# def require_admin(user: ORMUser = Depends(get_current_active_user)):
#     if not getattr(user, "is_admin", False):
#         raise HTTPException(status_code=403, detail="Admin privileges required")
#     return user


# router = APIRouter(
#     prefix="/api/engine",
#     tags=["engine"],
#     dependencies=[Depends(get_current_active_user)],
# )


# def _get_monitoring_functions(kind: str) -> Dict[str, Any]:
#     """Retourne les fonctions et tags pertinents pour un type de surveillance donné."""
#     if kind == "file":
#         return {"tag": "file", "getter": get_file_items, "updater": update_file_status, "scan_fn": scan_file}
#     if kind == "folder":
#         return {"tag": "folder", "getter": get_folder_items, "updater": update_folder_status, "scan_fn": scan_folder}
#     if kind == "ip":
#         return {"tag": "ip", "getter": get_ip_items, "updater": update_ip_status, "scan_fn": scan_ip}
#     raise HTTPException(status_code=400, detail="unknown kind")


# @router.get("/state")
# def engine_state():
#     """Retourne un état synthétique du moteur pour le dashboard."""
#     kinds = ["file", "folder", "ip"]
#     out: Dict[str, Dict[str, int]] = {}
#     total_active = 0
#     total_stopped = 0

#     for kind in kinds:
#         fns = _get_monitoring_functions(kind)
#         items = fns["getter"](skip=0, limit=10000)
#         status_counts = {"active": 0, "stopped": 0}

#         for item in items:
#             status = getattr(item, "status", "active") or "active"
#             if status == "paused":
#                 status = "stopped"
#             if status != "active":
#                 status = "stopped"
#             status_counts[status] += 1

#         total = sum(status_counts.values())
#         total_active += status_counts["active"]
#         total_stopped += status_counts["stopped"]

#         mode = "running" if status_counts["active"] > 0 else "stopped"

#         out[kind] = {
#             "total": total,
#             "active": status_counts["active"],
#             "paused": 0,
#             "stopped": status_counts["stopped"],
#             "mode": mode,
#         }

#     engine_status = "running" if total_active > 0 else "stopped"
#     out["engine"] = engine_status
#     return out


# @router.post("/{kind}/pause-all")
# def pause_all(kind: str):
#     """Alias de stop_all pour compatibilité."""
#     return stop_all(kind)


# @router.post("/{kind}/resume-all")
# def resume_all(kind: str):
#     """Relance tous les éléments d'un type donné."""
#     try:
#         fns = _get_monitoring_functions(kind)
#         tag, getter, updater, scan_fn = fns["tag"], fns["getter"], fns["updater"], fns["scan_fn"]
#         items = getter(skip=0, limit=10000)
#         resumed_count = 0

#         for item in items:
#             if getattr(item, "status", "active") != "active":
#                 updater(item.id, "active")

#                 interval = FREQ_SECONDS.get(getattr(item, "frequency", "hourly"), 3600)
#                 if tag == "file":
#                     add_interval_job("file", item.id, interval, scan_fn, item_id=item.id, path=item.path)
#                 elif tag == "folder":
#                     add_interval_job("folder", item.id, interval, scan_fn, item_id=item.id, path=item.path)
#                 else:
#                     add_interval_job(
#                         "ip",
#                         item.id,
#                         interval,
#                         scan_fn,
#                         item_id=item.id,
#                         ip=item.ip,
#                         hostname=getattr(item, "hostname", None),
#                     )
#                 resumed_count += 1

#         return {"ok": True, "resumed": resumed_count}
#     except HTTPException as exc:
#         raise exc
#     except Exception as exc:
#         raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {exc}")


# @router.post("/{kind}/stop-all")
# def stop_all(kind: str):
#     """Arrêt fort: retire les jobs et marque les éléments comme stoppés."""
#     try:
#         fns = _get_monitoring_functions(kind)
#         tag, getter, updater = fns["tag"], fns["getter"], fns["updater"]
#         items = getter(skip=0, limit=10000)
#         stopped_count = 0

#         for item in items:
#             remove_job(tag, item.id)
#             updater(item.id, "stopped")
#             stopped_count += 1

#         return {"ok": True, "stopped": stopped_count}
#     except HTTPException as exc:
#         raise exc
#     except Exception as exc:
#         raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {exc}")


# @router.post("/all/start", dependencies=[Depends(require_admin)])
# def start_all():
#     """Relance tous les types de surveillance (fichiers, dossiers, IP)."""
#     resume_all("file")
#     resume_all("folder")
#     resume_all("ip")
#     return {"ok": True}


# @router.post("/all/stop", dependencies=[Depends(require_admin)])
# def hard_stop_all():
#     """Arrête tous les types de surveillance."""
#     stop_all("file")
#     stop_all("folder")
#     stop_all("ip")
#     return {"ok": True}

# # ----------------------------------------------
# # /backend/app/api/engine.py
# from fastapi import APIRouter, Depends, HTTPException
# from app.core.security import get_current_active_user
# from app.db.models import User as ORMUser
# from app.services.monitoring_service import (
#     get_file_items, update_file_status,
#     get_folder_items, update_folder_status,
#     get_ip_items, update_ip_status,
# )
# from app.core.scheduler import add_interval_job, remove_job, FREQ_SECONDS
# from app.services.scan_tasks import scan_file, scan_folder, scan_ip
# from typing import Dict, Any


# # Helper admin:
# def require_admin(user: ORMUser = Depends(get_current_active_user)):
#     if not getattr(user, "is_admin", False):
#         raise HTTPException(status_code=403, detail="Admin privileges required")
#     return user


# router = APIRouter(
#     prefix="/api/engine",
#     tags=["engine"],
#     dependencies=[Depends(get_current_active_user)],
# )


# def _get_monitoring_functions(kind: str) -> Dict[str, Any]:
#     """Retourne les fonctions et tags pertinents pour un type de surveillance donné."""
#     if kind == "file":
#         return {"tag": "file", "getter": get_file_items, "updater": update_file_status, "scan_fn": scan_file}
#     if kind == "folder":
#         return {"tag": "folder", "getter": get_folder_items, "updater": update_folder_status, "scan_fn": scan_folder}
#     if kind == "ip":
#         return {"tag": "ip", "getter": get_ip_items, "updater": update_ip_status, "scan_fn": scan_ip}
#     raise HTTPException(status_code=400, detail="unknown kind")


# @router.get("/state")
# def engine_state():
#     """Retourne un état synthétique du moteur pour le dashboard."""
#     kinds = ["file", "folder", "ip"]
#     out: Dict[str, Dict[str, int]] = {}
#     total_active = 0
#     total_paused = 0
#     total_stopped = 0

#     for kind in kinds:
#         fns = _get_monitoring_functions(kind)
#         items = fns["getter"](skip=0, limit=10000)
#         status_counts = {"active": 0, "paused": 0, "stopped": 0}

#         for item in items:
#             status = getattr(item, "status", "active") or "active"
#             if status not in {"active", "paused", "stopped"}:
#                 status = "stopped"
#             status_counts[status] += 1

#         total = sum(status_counts.values())
#         total_active += status_counts["active"]
#         total_paused += status_counts["paused"]
#         total_stopped += status_counts["stopped"]

#         if status_counts["active"] > 0:
#             mode = "running"
#         elif status_counts["paused"] > 0:
#             mode = "paused"
#         else:
#             mode = "stopped"

#         out[kind] = {
#             "total": total,
#             "active": status_counts["active"],
#             "paused": status_counts["paused"],
#             "stopped": status_counts["stopped"],
#             "mode": mode,
#         }

#     if total_active > 0:
#         engine_status = "running"
#     elif total_paused > 0:
#         engine_status = "paused"
#     else:
#         engine_status = "stopped"

#     out["engine"] = engine_status
#     return out


# @router.post("/{kind}/pause-all", dependencies=[Depends(require_admin)])
# def pause_all(kind: str):
#     """
#     Met tous les éléments d'un type en 'paused':
#     - retire les jobs du scheduler
#     - NE supprime PAS les hashes en base (ils serviront à la reprise)
#     """
#     try:
#         fns = _get_monitoring_functions(kind)
#         tag, getter, updater = fns["tag"], fns["getter"], fns["updater"]
#         items = getter(skip=0, limit=10000)
#         paused_count = 0

#         for item in items:
#             # Retirer le job s'il existe
#             try:
#                 remove_job(tag, item.id)
#             except Exception:
#                 pass
#             # Mettre en pause sans toucher aux hashes
#             updater(item.id, "paused")
#             paused_count += 1

#         return {"ok": True, "paused": paused_count}
#     except HTTPException:
#         raise
#     except Exception as exc:
#         raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {exc}")


# @router.post("/{kind}/resume-all", dependencies=[Depends(require_admin)])
# def resume_all(kind: str):
#     """Relance tous les éléments d'un type donné: passe à 'active' et (re)planifie les jobs."""
#     try:
#         fns = _get_monitoring_functions(kind)
#         tag, getter, updater, scan_fn = fns["tag"], fns["getter"], fns["updater"], fns["scan_fn"]
#         items = getter(skip=0, limit=10000)
#         resumed_count = 0

#         for item in items:
#             if getattr(item, "status", "active") != "active":
#                 updater(item.id, "active")

#                 interval = FREQ_SECONDS.get(getattr(item, "frequency", "hourly"), 3600)
#                 if tag in ("file", "folder"):
#                     add_interval_job(tag, item.id, interval, scan_fn, item_id=item.id, path=item.path)
#                 else:
#                     add_interval_job("ip", item.id, interval, scan_fn,
#                                      item_id=item.id, ip=item.ip, hostname=getattr(item, "hostname", None))
#                 resumed_count += 1

#         return {"ok": True, "resumed": resumed_count}
#     except HTTPException:
#         raise
#     except Exception as exc:
#         raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {exc}")


# @router.post("/{kind}/stop-all", dependencies=[Depends(require_admin)])
# def stop_all(kind: str):
#     """
#     Arrêt fort:
#     - retire les jobs
#     - passe le statut à 'stopped'
#     - les fonctions update_*_status se chargent d'effacer les hashes/états
#     """
#     try:
#         fns = _get_monitoring_functions(kind)
#         tag, getter, updater = fns["tag"], fns["getter"], fns["updater"]
#         items = getter(skip=0, limit=10000)
#         stopped_count = 0

#         for item in items:
#             try:
#                 remove_job(tag, item.id)
#             except Exception:
#                 pass
#             updater(item.id, "stopped")
#             stopped_count += 1

#         return {"ok": True, "stopped": stopped_count}
#     except HTTPException:
#         raise
#     except Exception as exc:
#         raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {exc}")


# @router.post("/all/start", dependencies=[Depends(require_admin)])
# def start_all():
#     """Relance tous les types de surveillance (fichiers, dossiers, IP)."""
#     resume_all("file")
#     resume_all("folder")
#     resume_all("ip")
#     return {"ok": True}


# @router.post("/all/stop", dependencies=[Depends(require_admin)])
# def hard_stop_all():
#     """Arrête tous les types de surveillance."""
#     stop_all("file")
#     stop_all("folder")
#     stop_all("ip")
#     return {"ok": True}



# ----------------------------------------------


# /backend/app/api/engine.py
from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_active_user
from app.db.models import User as ORMUser
from app.services.monitoring_service import (
    get_file_items, update_file_status,
    get_folder_items, update_folder_status,
    get_ip_items, update_ip_status,
)
from app.core.scheduler import add_interval_job, remove_job, FREQ_SECONDS
from app.services.scan_tasks import scan_file, scan_folder, scan_ip
from typing import Dict, Any

# Helper admin
def require_admin(user: ORMUser = Depends(get_current_active_user)):
    if not getattr(user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user

router = APIRouter(
    prefix="/api/engine",
    tags=["engine"],
    dependencies=[Depends(get_current_active_user)],
)

def _get_monitoring_functions(kind: str) -> Dict[str, Any]:
    """Retourne les fonctions et tags pertinents pour un type de surveillance donné."""
    if kind == "file":
        return {"tag": "file", "getter": get_file_items, "updater": update_file_status, "scan_fn": scan_file}
    if kind == "folder":
        return {"tag": "folder", "getter": get_folder_items, "updater": update_folder_status, "scan_fn": scan_folder}
    if kind == "ip":
        return {"tag": "ip", "getter": get_ip_items, "updater": update_ip_status, "scan_fn": scan_ip}
    raise HTTPException(status_code=400, detail="unknown kind")

# ----------------------------------------------------------------------
# STATE
# ----------------------------------------------------------------------
@router.get("/state")
def engine_state():
    """Retourne un état synthétique du moteur pour le dashboard."""
    kinds = ["file", "folder", "ip"]
    out: Dict[str, Dict[str, int]] = {}
    total_active = total_paused = total_stopped = 0

    for kind in kinds:
        fns = _get_monitoring_functions(kind)
        items = fns["getter"](skip=0, limit=10000)
        status_counts = {"active": 0, "paused": 0, "stopped": 0}

        for item in items:
            status = getattr(item, "status", "stopped") or "stopped"
            if status not in {"active", "paused", "stopped"}:
                status = "stopped"
            status_counts[status] += 1

        total_active += status_counts["active"]
        total_paused += status_counts["paused"]
        total_stopped += status_counts["stopped"]

        if status_counts["active"] > 0:
            mode = "running"
        elif status_counts["paused"] > 0:
            mode = "paused"
        else:
            mode = "stopped"

        out[kind] = {**status_counts, "total": sum(status_counts.values()), "mode": mode}

    if total_active > 0:
        engine_status = "running"
    elif total_paused > 0:
        engine_status = "paused"
    else:
        engine_status = "stopped"

    out["engine"] = engine_status
    return out

# ----------------------------------------------------------------------
# ACTIONS SUR UN TYPE (files / folders / ips)
# ----------------------------------------------------------------------
@router.post("/{kind}/pause-all", dependencies=[Depends(require_admin)])
def pause_all(kind: str):
    """Met tous les éléments d'un type en paused."""
    fns = _get_monitoring_functions(kind)
    tag, getter, updater = fns["tag"], fns["getter"], fns["updater"]
    items = getter(skip=0, limit=10000)
    paused_count = 0

    for item in items:
        try:
            remove_job(tag, item.id)
        except Exception:
            pass
        updater(item.id, "paused")   # conserve les hashes
        paused_count += 1

    return {"ok": True, "paused": paused_count}

@router.post("/{kind}/resume-all", dependencies=[Depends(require_admin)])
def resume_all(kind: str):
    """Passe tous les éléments en active + replanifie les jobs."""
    fns = _get_monitoring_functions(kind)
    tag, getter, updater, scan_fn = fns["tag"], fns["getter"], fns["updater"], fns["scan_fn"]
    items = getter(skip=0, limit=10000)
    resumed_count = 0

    for item in items:
        updater(item.id, "active")
        interval = FREQ_SECONDS.get(getattr(item, "frequency", "hourly"), 3600)
        if tag in ("file", "folder"):
            add_interval_job(tag, item.id, interval, scan_fn, item_id=item.id, path=item.path)
        else:
            add_interval_job("ip", item.id, interval, scan_fn,
                             item_id=item.id, ip=item.ip, hostname=getattr(item, "hostname", None))
        resumed_count += 1

    return {"ok": True, "resumed": resumed_count}

@router.post("/{kind}/stop-all", dependencies=[Depends(require_admin)])
def stop_all(kind: str):
    """Arrêt fort: stop + effacement des hashes/états."""
    fns = _get_monitoring_functions(kind)
    tag, getter, updater = fns["tag"], fns["getter"], fns["updater"]
    items = getter(skip=0, limit=10000)
    stopped_count = 0

    for item in items:
        try:
            remove_job(tag, item.id)
        except Exception:
            pass
        updater(item.id, "stopped")  # efface les hashes
        stopped_count += 1

    return {"ok": True, "stopped": stopped_count}

# ----------------------------------------------------------------------
# ACTIONS GLOBALES
# ----------------------------------------------------------------------
@router.post("/all/start", dependencies=[Depends(require_admin)])
def start_all():
    """Active tout: files, folders, ips."""
    resume_all("file")
    resume_all("folder")
    resume_all("ip")
    return {"ok": True, "started": True}

@router.post("/all/stop", dependencies=[Depends(require_admin)])
def hard_stop_all():
    """Stoppe tout: files, folders, ips."""
    stop_all("file")
    stop_all("folder")
    stop_all("ip")
    return {"ok": True, "stopped": True}

@router.post("/all/pause", dependencies=[Depends(require_admin)])
def global_pause():
    """Pause globale."""
    pause_all("file")
    pause_all("folder")
    pause_all("ip")
    return {"ok": True, "paused": True}
