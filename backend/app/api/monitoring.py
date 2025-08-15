# File: backend/app/api/monitoring.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.models.monitoring import (
    FileItemCreate, FileItemRead,
    IPItemCreate, IPItemRead,
    FolderItemCreate, FolderItemRead
)
from app.services.monitoring_service import (
    get_file_items, get_file_item, create_file_item, update_file_item, delete_file_item,
    get_ip_items, get_ip_item, create_ip_item, update_ip_item, delete_ip_item,
    get_folder_items, get_folder_item, create_folder_item, update_folder_item, delete_folder_item
)
from app.core.security import get_current_active_user
from app.db.models import User as ORMUser

router = APIRouter(
    prefix="/api/monitoring",
    tags=["monitoring"],
    dependencies=[Depends(get_current_active_user)]
)

# --- File monitoring endpoints ---
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
# def add_file_item(file_in: FileItemCreate):
#     return create_file_item(file_in)
def add_file_item(file_in: FileItemCreate):
    try:
        return create_file_item(file_in)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="File path already exists")

@router.put("/files/{file_id}", response_model=FileItemRead)
def edit_file_item(file_id: int, file_in: FileItemCreate):
    item = get_file_item(file_id)
    if not item:
        raise HTTPException(status_code=404, detail="File not found")
    return update_file_item(file_id, file_in)

@router.delete("/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_file_item(file_id: int):
    item = get_file_item(file_id)
    if not item:
        raise HTTPException(status_code=404, detail="File not found")
    delete_file_item(file_id)
    return None

# --- IP monitoring endpoints ---
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
# def add_ip_item(ip_in: IPItemCreate):
#     return create_ip_item(ip_in)
def add_ip_item(ip_in: IPItemCreate):
    try:
        return create_ip_item(ip_in)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="IP address already exists")

@router.put("/ips/{ip_id}", response_model=IPItemRead)
def edit_ip_item(ip_id: int, ip_in: IPItemCreate):
    item = get_ip_item(ip_id)
    if not item:
        raise HTTPException(status_code=404, detail="IP not found")
    return update_ip_item(ip_id, ip_in)

@router.delete("/ips/{ip_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_ip_item(ip_id: int):
    item = get_ip_item(ip_id)
    if not item:
        raise HTTPException(status_code=404, detail="IP not found")
    delete_ip_item(ip_id)
    return None

# --- Folder monitoring endpoints ---
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

# @router.post("/folders", response_model=FolderItemRead, status_code=status.HTTP_201_CREATED)
# def add_folder_item(folder_in: FolderItemCreate):
#     return create_folder_item(folder_in)
# def add_folder_item(folder_in: FolderItemCreate):
#     try:
#         return create_folder_item(folder_in)
#     except IntegrityError:
#         raise HTTPException(status_code=409, detail="Folder path already exists")
@router.post("/folders", response_model=FolderItemRead, status_code=status.HTTP_201_CREATED)
def add_folder_item(folder_in: FolderItemCreate):
    try:
        return create_folder_item(folder_in)
    except IntegrityError:
        # doublon sur path => 409
        raise HTTPException(status_code=409, detail="Folder already monitored")
    except Exception as e:
        # filet de sécurité: requalifie les contraintes uniques non mappées
        if "UNIQUE constraint failed: monitored_folders.path" in str(e):
            raise HTTPException(status_code=409, detail="Folder already monitored")
        raise


@router.put("/folders/{folder_id}", response_model=FolderItemRead)
def edit_folder_item(folder_id: int, folder_in: FolderItemCreate):
    item = get_folder_item(folder_id)
    if not item:
        raise HTTPException(status_code=404, detail="Folder not found")
    return update_folder_item(folder_id, folder_in)

@router.delete("/folders/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_folder_item(folder_id: int):
    item = get_folder_item(folder_id)
    if not item:
        raise HTTPException(status_code=404, detail="Folder not found")
    delete_folder_item(folder_id)
    return None
