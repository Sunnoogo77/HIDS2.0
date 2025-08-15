# # File: backend/app/api/monitoring.py
# from typing import List
# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.exc import IntegrityError

# from app.core.scheduler import add_interval_job, remove_job, FREQ_SECONDS
# from app.services.scan_tasks import scan_file, scan_folder, scan_ip

# from app.models.monitoring import (
#     FileItemCreate, FileItemRead,
#     IPItemCreate, IPItemRead,
#     FolderItemCreate, FolderItemRead
# )
# from app.services.monitoring_service import (
#     get_file_items, get_file_item, create_file_item, update_file_item, delete_file_item,
#     get_ip_items, get_ip_item, create_ip_item, update_ip_item, delete_ip_item,
#     get_folder_items, get_folder_item, create_folder_item, update_folder_item, delete_folder_item
# )
# from app.core.security import get_current_active_user
# from app.db.models import User as ORMUser

# router = APIRouter(
#     prefix="/api/monitoring",
#     tags=["monitoring"],
#     dependencies=[Depends(get_current_active_user)]
# )

# # --- File monitoring endpoints ---
# @router.get("/files/{file_id}", response_model=FileItemRead)
# def read_file_item(file_id: int):
#     """Get a single monitored file by ID."""
#     item = get_file_item(file_id)
#     if not item:
#         raise HTTPException(status_code=404, detail="File not found")
#     return item

# @router.get("/files", response_model=List[FileItemRead])
# def read_file_items(skip: int = 0, limit: int = 100):
#     return get_file_items(skip=skip, limit=limit)

# @router.post("/files", response_model=FileItemRead, status_code=status.HTTP_201_CREATED)
# def add_file_item(file_in: FileItemCreate):
#     try:
#         return create_file_item(file_in)
#     except IntegrityError:
#         raise HTTPException(status_code=409, detail="File path already exists")

# @router.put("/files/{file_id}", response_model=FileItemRead)
# def edit_file_item(file_id: int, file_in: FileItemCreate):
#     item = get_file_item(file_id)
#     if not item:
#         raise HTTPException(status_code=404, detail="File not found")
#     return update_file_item(file_id, file_in)

# @router.delete("/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
# def remove_file_item(file_id: int):
#     item = get_file_item(file_id)
#     if not item:
#         raise HTTPException(status_code=404, detail="File not found")
#     delete_file_item(file_id)
#     return None

# # --- IP monitoring endpoints ---
# @router.get("/ips/{ip_id}", response_model=IPItemRead)
# def read_ip_item(ip_id: int):
#     """Get a single monitored IP by ID."""
#     item = get_ip_item(ip_id)
#     if not item:
#         raise HTTPException(status_code=404, detail="IP not found")
#     return item

# @router.get("/ips", response_model=List[IPItemRead])
# def read_ip_items(skip: int = 0, limit: int = 100):
#     return get_ip_items(skip=skip, limit=limit)

# @router.post("/ips", response_model=IPItemRead, status_code=status.HTTP_201_CREATED)
# def add_ip_item(ip_in: IPItemCreate):
#     try:
#         return create_ip_item(ip_in)
#     except IntegrityError:
#         raise HTTPException(status_code=409, detail="IP address already exists")

# @router.put("/ips/{ip_id}", response_model=IPItemRead)
# def edit_ip_item(ip_id: int, ip_in: IPItemCreate):
#     item = get_ip_item(ip_id)
#     if not item:
#         raise HTTPException(status_code=404, detail="IP not found")
#     return update_ip_item(ip_id, ip_in)

# @router.delete("/ips/{ip_id}", status_code=status.HTTP_204_NO_CONTENT)
# def remove_ip_item(ip_id: int):
#     item = get_ip_item(ip_id)
#     if not item:
#         raise HTTPException(status_code=404, detail="IP not found")
#     delete_ip_item(ip_id)
#     return None

# # --- Folder monitoring endpoints ---
# @router.get("/folders/{folder_id}", response_model=FolderItemRead)
# def read_folder_item(folder_id: int):
#     """Get a single monitored folder by ID."""
#     item = get_folder_item(folder_id)
#     if not item:
#         raise HTTPException(status_code=404, detail="Folder not found")
#     return item

# @router.get("/folders", response_model=List[FolderItemRead])
# def read_folder_items(skip: int = 0, limit: int = 100):
#     return get_folder_items(skip=skip, limit=limit)

# @router.post("/folders", response_model=FolderItemRead, status_code=status.HTTP_201_CREATED)
# def add_folder_item(folder_in: FolderItemCreate):
#     try:
#         return create_folder_item(folder_in)
#     except IntegrityError:
#         # doublon sur path => 409
#         raise HTTPException(status_code=409, detail="Folder already monitored")
#     except Exception as e:
#         # filet de sécurité: requalifie les contraintes uniques non mappées
#         if "UNIQUE constraint failed: monitored_folders.path" in str(e):
#             raise HTTPException(status_code=409, detail="Folder already monitored")
#         raise


# @router.put("/folders/{folder_id}", response_model=FolderItemRead)
# def edit_folder_item(folder_id: int, folder_in: FolderItemCreate):
#     item = get_folder_item(folder_id)
#     if not item:
#         raise HTTPException(status_code=404, detail="Folder not found")
#     return update_folder_item(folder_id, folder_in)

# @router.delete("/folders/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
# def remove_folder_item(folder_id: int):
#     item = get_folder_item(folder_id)
#     if not item:
#         raise HTTPException(status_code=404, detail="Folder not found")
#     delete_folder_item(folder_id)
#     return None

# --------------------------------------------

# # File: backend/app/api/monitoring.py
# # File: backend/app/api/monitoring.py
# from typing import List
# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.exc import IntegrityError

# # Scheduler + scan tasks
# from app.core.scheduler import add_interval_job, remove_job, FREQ_SECONDS
# from app.services.scan_tasks import scan_file, scan_folder, scan_ip

# # Schemas (Pydantic)
# from app.models.monitoring import (
#     FileItemCreate, FileItemRead,
#     IPItemCreate, IPItemRead,
#     FolderItemCreate, FolderItemRead
# )

# # Services (DB CRUD)
# from app.services.monitoring_service import (
#     get_file_items, get_file_item, create_file_item, update_file_item, delete_file_item,
#     get_ip_items, get_ip_item, create_ip_item, update_ip_item, delete_ip_item,
#     get_folder_items, get_folder_item, create_folder_item, update_folder_item, delete_folder_item
# )

# # Auth
# from app.core.security import get_current_active_user
# from app.db.models import User as ORMUser  # (utile si besoin de typer 'current' plus tard)

# router = APIRouter(
#     prefix="/api/monitoring",
#     tags=["monitoring"],
#     dependencies=[Depends(get_current_active_user)]
# )

# # -------------------------------------------------------------------------
# # Helpers internes pour (re)programmer / supprimer les jobs APScheduler
# # -------------------------------------------------------------------------

# def _schedule_file(item) -> None:
#     """(Re)pose un job de scan pour un File si status=active, sinon retire."""
#     if getattr(item, "status", "active") == "active":
#         sec = FREQ_SECONDS.get(getattr(item, "frequency", "hourly"), 3600)
#         add_interval_job("file", item.id, sec, scan_file, item_id=item.id, path=item.path)
#     else:
#         remove_job("file", item.id)

# def _schedule_folder(item) -> None:
#     if getattr(item, "status", "active") == "active":
#         sec = FREQ_SECONDS.get(getattr(item, "frequency", "hourly"), 3600)
#         add_interval_job("folder", item.id, sec, scan_folder, item_id=item.id, path=item.path)
#     else:
#         remove_job("folder", item.id)

# def _schedule_ip(item) -> None:
#     if getattr(item, "status", "active") == "active":
#         sec = FREQ_SECONDS.get(getattr(item, "frequency", "hourly"), 3600)
#         add_interval_job("ip", item.id, sec, scan_ip, item_id=item.id, ip=item.ip, hostname=getattr(item, "hostname", None))
#     else:
#         remove_job("ip", item.id)

# # -------------------------------------------------------------------------
# # File monitoring endpoints
# # -------------------------------------------------------------------------

# @router.get("/files/{file_id}", response_model=FileItemRead)
# def read_file_item(file_id: int):
#     """Get a single monitored file by ID."""
#     item = get_file_item(file_id)
#     if not item:
#         raise HTTPException(status_code=404, detail="File not found")
#     return item

# @router.get("/files", response_model=List[FileItemRead])
# def read_file_items(skip: int = 0, limit: int = 100):
#     return get_file_items(skip=skip, limit=limit)

# @router.post("/files", response_model=FileItemRead, status_code=status.HTTP_201_CREATED)
# def add_file_item(file_in: FileItemCreate):
#     try:
#         item = create_file_item(file_in)
#         # si status actif → poser job
#         try:
#             _schedule_file(item)
#         except Exception:
#             # on ne casse pas le 201 pour un souci de scheduler
#             pass
#         return item
#     except IntegrityError:
#         # politique "strict": doublon => 409 (si le service ne fait pas d'idempotence)
#         raise HTTPException(status_code=409, detail="File path already exists")

# @router.put("/files/{file_id}", response_model=FileItemRead)
# def edit_file_item(file_id: int, file_in: FileItemCreate):
#     item = get_file_item(file_id)
#     if not item:
#         raise HTTPException(status_code=404, detail="File not found")
#     item = update_file_item(file_id, file_in)
#     # (re)programmer selon le status/frequency actuels
#     try:
#         _schedule_file(item)
#     except Exception:
#         pass
#     return item

# @router.delete("/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
# def remove_file_item(file_id: int):
#     item = get_file_item(file_id)
#     if not item:
#         raise HTTPException(status_code=404, detail="File not found")
#     delete_file_item(file_id)
#     # retirer le job s'il existe
#     try:
#         remove_job("file", file_id)
#     except Exception:
#         pass
#     return None

# # -------------------------------------------------------------------------
# # IP monitoring endpoints
# # -------------------------------------------------------------------------

# @router.get("/ips/{ip_id}", response_model=IPItemRead)
# def read_ip_item(ip_id: int):
#     """Get a single monitored IP by ID."""
#     item = get_ip_item(ip_id)
#     if not item:
#         raise HTTPException(status_code=404, detail="IP not found")
#     return item

# @router.get("/ips", response_model=List[IPItemRead])
# def read_ip_items(skip: int = 0, limit: int = 100):
#     return get_ip_items(skip=skip, limit=limit)

# @router.post("/ips", response_model=IPItemRead, status_code=status.HTTP_201_CREATED)
# def add_ip_item(ip_in: IPItemCreate):
#     try:
#         item = create_ip_item(ip_in)
#         try:
#             _schedule_ip(item)
#         except Exception:
#             pass
#         return item
#     except IntegrityError:
#         raise HTTPException(status_code=409, detail="IP address already exists")

# @router.put("/ips/{ip_id}", response_model=IPItemRead)
# def edit_ip_item(ip_id: int, ip_in: IPItemCreate):
#     item = get_ip_item(ip_id)
#     if not item:
#         raise HTTPException(status_code=404, detail="IP not found")
#     item = update_ip_item(ip_id, ip_in)
#     try:
#         _schedule_ip(item)
#     except Exception:
#         pass
#     return item

# @router.delete("/ips/{ip_id}", status_code=status.HTTP_204_NO_CONTENT)
# def remove_ip_item(ip_id: int):
#     item = get_ip_item(ip_id)
#     if not item:
#         raise HTTPException(status_code=404, detail="IP not found")
#     delete_ip_item(ip_id)
#     try:
#         remove_job("ip", ip_id)
#     except Exception:
#         pass
#     return None

# # -------------------------------------------------------------------------
# # Folder monitoring endpoints
# # -------------------------------------------------------------------------

# @router.get("/folders/{folder_id}", response_model=FolderItemRead)
# def read_folder_item(folder_id: int):
#     """Get a single monitored folder by ID."""
#     item = get_folder_item(folder_id)
#     if not item:
#         raise HTTPException(status_code=404, detail="Folder not found")
#     return item

# @router.get("/folders", response_model=List[FolderItemRead])
# def read_folder_items(skip: int = 0, limit: int = 100):
#     return get_folder_items(skip=skip, limit=limit)

# @router.post("/folders", response_model=FolderItemRead, status_code=status.HTTP_201_CREATED)
# def add_folder_item(folder_in: FolderItemCreate):
#     try:
#         item = create_folder_item(folder_in)
#         try:
#             _schedule_folder(item)
#         except Exception:
#             pass
#         return item
#     except IntegrityError:
#         # doublon sur path => 409
#         raise HTTPException(status_code=409, detail="Folder already monitored")
#     except Exception as e:
#         # filet de sécurité: requalifie les contraintes uniques non mappées
#         if "UNIQUE constraint failed: monitored_folders.path" in str(e):
#             raise HTTPException(status_code=409, detail="Folder already monitored")
#         raise

# @router.put("/folders/{folder_id}", response_model=FolderItemRead)
# def edit_folder_item(folder_id: int, folder_in: FolderItemCreate):
#     item = get_folder_item(folder_id)
#     if not item:
#         raise HTTPException(status_code=404, detail="Folder not found")
#     item = update_folder_item(folder_id, folder_in)
#     try:
#         _schedule_folder(item)
#     except Exception:
#         pass
#     return item

# @router.delete("/folders/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
# def remove_folder_item(folder_id: int):
#     item = get_folder_item(folder_id)
#     if not item:
#         raise HTTPException(status_code=404, detail="Folder not found")
#     delete_folder_item(folder_id)
#     try:
#         remove_job("folder", folder_id)
#     except Exception:
#         pass
#     return None


# ------------------------------------------------------

# File: backend/app/api/monitoring.py
from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

# Scheduler + scan tasks
from app.core.scheduler import add_interval_job, remove_job, FREQ_SECONDS
from app.services.scan_tasks import scan_file, scan_folder, scan_ip

# Schemas (Pydantic)
from app.models.monitoring import (
    FileItemCreate, FileItemRead,
    IPItemCreate, IPItemRead,
    FolderItemCreate, FolderItemRead
)

# Services (DB CRUD)
from app.services.monitoring_service import (
    get_file_items, get_file_item, create_file_item, update_file_item, delete_file_item,
    get_ip_items, get_ip_item, create_ip_item, update_ip_item, delete_ip_item,
    get_folder_items, get_folder_item, create_folder_item, update_folder_item, delete_folder_item
)

# Auth
from app.core.security import get_current_active_user
from app.db.models import User as ORMUser  # éventuellement utile

# (optionnel) mini logger
import logging
log = logging.getLogger("monitoring-api")

router = APIRouter(
    prefix="/api/monitoring",
    tags=["monitoring"],
    dependencies=[Depends(get_current_active_user)]
)

# -------------------------------------------------------------------------
# Helpers: support dict OU objet (ORM/Pydantic) de façon uniforme
# -------------------------------------------------------------------------

def _val(obj: Any, name: str, default: Any = None) -> Any:
    """Récupère un champ soit en attribut, soit en clé dict, sinon default."""
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)

def _schedule_file(item: Any) -> None:
    """(Re)pose un job de scan pour un File si status=active, sinon retire."""
    iid = _val(item, "id")
    if iid is None:
        return
    status = _val(item, "status", "active")
    freq = _val(item, "frequency", "hourly")
    path = _val(item, "path")

    if status == "active":
        sec = FREQ_SECONDS.get(freq, 3600)
        try:
            add_interval_job("file", iid, sec, scan_file, item_id=iid, path=path)
            log.debug(f"[scheduler] file #{iid} scheduled every {sec}s (status={status}, freq={freq})")
        except Exception as e:
            log.warning(f"[scheduler] cannot schedule file #{iid}: {e}")
    else:
        try:
            remove_job("file", iid)
            log.debug(f"[scheduler] file #{iid} job removed (status={status})")
        except Exception as e:
            log.warning(f"[scheduler] cannot remove file job #{iid}: {e}")

def _schedule_folder(item: Any) -> None:
    iid = _val(item, "id")
    if iid is None:
        return
    status = _val(item, "status", "active")
    freq = _val(item, "frequency", "hourly")
    path = _val(item, "path")

    if status == "active":
        sec = FREQ_SECONDS.get(freq, 3600)
        try:
            add_interval_job("folder", iid, sec, scan_folder, item_id=iid, path=path)
            log.debug(f"[scheduler] folder #{iid} scheduled every {sec}s (status={status}, freq={freq})")
        except Exception as e:
            log.warning(f"[scheduler] cannot schedule folder #{iid}: {e}")
    else:
        try:
            remove_job("folder", iid)
            log.debug(f"[scheduler] folder #{iid} job removed (status={status})")
        except Exception as e:
            log.warning(f"[scheduler] cannot remove folder job #{iid}: {e}")

def _schedule_ip(item: Any) -> None:
    iid = _val(item, "id")
    if iid is None:
        return
    status = _val(item, "status", "active")
    freq = _val(item, "frequency", "hourly")
    ip = _val(item, "ip")
    hostname = _val(item, "hostname", None)

    if status == "active":
        sec = FREQ_SECONDS.get(freq, 3600)
        try:
            add_interval_job("ip", iid, sec, scan_ip, item_id=iid, ip=ip, hostname=hostname)
            log.debug(f"[scheduler] ip #{iid} scheduled every {sec}s (status={status}, freq={freq})")
        except Exception as e:
            log.warning(f"[scheduler] cannot schedule ip #{iid}: {e}")
    else:
        try:
            remove_job("ip", iid)
            log.debug(f"[scheduler] ip #{iid} job removed (status={status})")
        except Exception as e:
            log.warning(f"[scheduler] cannot remove ip job #{iid}: {e}")

# -------------------------------------------------------------------------
# File monitoring endpoints
# -------------------------------------------------------------------------

@router.get("/files/{file_id}", response_model=FileItemRead)
def read_file_item(file_id: int):
    """Get a single monitored file by ID."""
    item = get_file_item(file_id)
    if not item:
        raise HTTPException(status_code=404, detail="File not found")
    return item

@router.get("/files", response_model=List[FileItemRead])
def read_file_items(skip: int = 0, limit: int = 100):
    return get_file_items(skip=skip, limit=limit)

@router.post("/files", response_model=FileItemRead, status_code=status.HTTP_201_CREATED)
def add_file_item(file_in: FileItemCreate):
    try:
        item = create_file_item(file_in)
        _schedule_file(item)
        return item
    except IntegrityError:
        raise HTTPException(status_code=409, detail="File path already exists")

@router.put("/files/{file_id}", response_model=FileItemRead)
def edit_file_item(file_id: int, file_in: FileItemCreate):
    item = get_file_item(file_id)
    if not item:
        raise HTTPException(status_code=404, detail="File not found")
    item = update_file_item(file_id, file_in)
    _schedule_file(item)
    return item

@router.delete("/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_file_item(file_id: int):
    item = get_file_item(file_id)
    if not item:
        raise HTTPException(status_code=404, detail="File not found")
    delete_file_item(file_id)
    remove_job("file", file_id)
    return None

# -------------------------------------------------------------------------
# IP monitoring endpoints
# -------------------------------------------------------------------------

@router.get("/ips/{ip_id}", response_model=IPItemRead)
def read_ip_item(ip_id: int):
    """Get a single monitored IP by ID."""
    item = get_ip_item(ip_id)
    if not item:
        raise HTTPException(status_code=404, detail="IP not found")
    return item

@router.get("/ips", response_model=List[IPItemRead])
def read_ip_items(skip: int = 0, limit: int = 100):
    return get_ip_items(skip=skip, limit=limit)

@router.post("/ips", response_model=IPItemRead, status_code=status.HTTP_201_CREATED)
def add_ip_item(ip_in: IPItemCreate):
    try:
        item = create_ip_item(ip_in)
        _schedule_ip(item)
        return item
    except IntegrityError:
        raise HTTPException(status_code=409, detail="IP address already exists")

@router.put("/ips/{ip_id}", response_model=IPItemRead)
def edit_ip_item(ip_id: int, ip_in: IPItemCreate):
    item = get_ip_item(ip_id)
    if not item:
        raise HTTPException(status_code=404, detail="IP not found")
    item = update_ip_item(ip_id, ip_in)
    _schedule_ip(item)
    return item

@router.delete("/ips/{ip_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_ip_item(ip_id: int):
    item = get_ip_item(ip_id)
    if not item:
        raise HTTPException(status_code=404, detail="IP not found")
    delete_ip_item(ip_id)
    remove_job("ip", ip_id)
    return None

# -------------------------------------------------------------------------
# Folder monitoring endpoints
# -------------------------------------------------------------------------

@router.get("/folders/{folder_id}", response_model=FolderItemRead)
def read_folder_item(folder_id: int):
    """Get a single monitored folder by ID."""
    item = get_folder_item(folder_id)
    if not item:
        raise HTTPException(status_code=404, detail="Folder not found")
    return item

@router.get("/folders", response_model=List[FolderItemRead])
def read_folder_items(skip: int = 0, limit: int = 100):
    return get_folder_items(skip=skip, limit=limit)

@router.post("/folders", response_model=FolderItemRead, status_code=status.HTTP_201_CREATED)
def add_folder_item(folder_in: FolderItemCreate):
    try:
        item = create_folder_item(folder_in)
        _schedule_folder(item)
        return item
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Folder already monitored")
    except Exception as e:
        if "UNIQUE constraint failed: monitored_folders.path" in str(e):
            raise HTTPException(status_code=409, detail="Folder already monitored")
        raise

@router.put("/folders/{folder_id}", response_model=FolderItemRead)
def edit_folder_item(folder_id: int, folder_in: FolderItemCreate):
    item = get_folder_item(folder_id)
    if not item:
        raise HTTPException(status_code=404, detail="Folder not found")
    item = update_folder_item(folder_id, folder_in)
    _schedule_folder(item)
    return item

@router.delete("/folders/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_folder_item(folder_id: int):
    item = get_folder_item(folder_id)
    if not item:
        raise HTTPException(status_code=404, detail="Folder not found")
    delete_folder_item(folder_id)
    remove_job("folder", folder_id)
    return None
