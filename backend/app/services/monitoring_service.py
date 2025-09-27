# File: backend/app/services/monitoring_service.py
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from sqlalchemy.exc import IntegrityError


from app.db.session import SessionLocal
from app.db.models import MonitoredFile, MonitoredIP, MonitoredFolder
from app.models.monitoring import FileItemCreate, IPItemCreate, FolderItemCreate


# ---- Monitored Files CRUD ----

def get_file_items(skip: int = 0, limit: int = 100) -> List[MonitoredFile]:
    db: Session = SessionLocal()
    items = db.query(MonitoredFile).offset(skip).limit(limit).all()
    db.close()
    return items


def get_file_item(file_id: int) -> Optional[MonitoredFile]:
    db: Session = SessionLocal()
    item = db.query(MonitoredFile).filter(MonitoredFile.id == file_id).first()
    db.close()
    return item



def create_file_item(file_in: FileItemCreate) -> MonitoredFile:
    db: Session = SessionLocal()
    try:
        existing = db.query(MonitoredFile).filter(MonitoredFile.path == file_in.path).first()
        if existing:
            db.close()
            return existing
        db_item = MonitoredFile(path=file_in.path, frequency=file_in.frequency)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        db.close()
        return db_item
    except IntegrityError:
        db.rollback()
        db.close()
        raise

def update_file_item(file_id: int, file_in: FileItemCreate) -> MonitoredFile:
    db: Session = SessionLocal()
    item = db.query(MonitoredFile).filter(MonitoredFile.id == file_id).first()
    if not item:
        db.close()
        raise NoResultFound(f"File item {file_id} not found")
    item.path = file_in.path
    item.frequency = file_in.frequency
    db.commit()
    db.refresh(item)
    db.close()
    return item


def delete_file_item(file_id: int) -> None:
    db: Session = SessionLocal()
    item = db.query(MonitoredFile).filter(MonitoredFile.id == file_id).first()
    if item:
        db.delete(item)
        db.commit()
    db.close()


# ---- Monitored IPs CRUD ----

def get_ip_items(skip: int = 0, limit: int = 100) -> List[MonitoredIP]:
    db: Session = SessionLocal()
    items = db.query(MonitoredIP).offset(skip).limit(limit).all()
    db.close()
    return items


def get_ip_item(ip_id: int) -> Optional[MonitoredIP]:
    db: Session = SessionLocal()
    item = db.query(MonitoredIP).filter(MonitoredIP.id == ip_id).first()
    db.close()
    return item


def create_ip_item(ip_in: IPItemCreate) -> MonitoredIP:
    db: Session = SessionLocal()
    try:
        existing = db.query(MonitoredIP).filter(MonitoredIP.ip == ip_in.ip).first()
        if existing:
            db.close()
            return existing
        db_item = MonitoredIP(
            ip=ip_in.ip,
            hostname=ip_in.hostname,
            frequency=ip_in.frequency
        )
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        db.close()
        return db_item
    except IntegrityError:
        db.rollback()
        db.close()
        raise


def update_ip_item(ip_id: int, ip_in: IPItemCreate) -> MonitoredIP:
    db: Session = SessionLocal()
    item = db.query(MonitoredIP).filter(MonitoredIP.id == ip_id).first()
    if not item:
        db.close()
        raise NoResultFound(f"IP item {ip_id} not found")
    item.ip = ip_in.ip
    item.hostname = ip_in.hostname
    item.frequency = ip_in.frequency
    db.commit()
    db.refresh(item)
    db.close()
    return item


def delete_ip_item(ip_id: int) -> None:
    db: Session = SessionLocal()
    item = db.query(MonitoredIP).filter(MonitoredIP.id == ip_id).first()
    if item:
        db.delete(item)
        db.commit()
    db.close()


# ---- Monitored Folders CRUD ----

def get_folder_items(skip: int = 0, limit: int = 100) -> List[MonitoredFolder]:
    db: Session = SessionLocal()
    items = db.query(MonitoredFolder).offset(skip).limit(limit).all()
    db.close()
    return items


def get_folder_item(folder_id: int) -> Optional[MonitoredFolder]:
    db: Session = SessionLocal()
    item = db.query(MonitoredFolder).filter(MonitoredFolder.id == folder_id).first()
    db.close()
    return item


def create_folder_item(folder_in: FolderItemCreate) -> MonitoredFolder:
    db: Session = SessionLocal()
    try:
        
        existing = db.query(MonitoredFolder).filter(MonitoredFolder.path == folder_in.path).first()
        if existing:
            db.close()
            return existing
        db_item = MonitoredFolder(path=folder_in.path, frequency=folder_in.frequency)
        db.add(db_item); db.commit(); db.refresh(db_item)
        db.close()
        return db_item
    except IntegrityError:
        db.rollback()
        db.close()
        
        raise


def update_folder_item(folder_id: int, folder_in: FolderItemCreate) -> MonitoredFolder:
    db: Session = SessionLocal()
    item = db.query(MonitoredFolder).filter(MonitoredFolder.id == folder_id).first()
    if not item:
        db.close()
        raise NoResultFound(f"Folder item {folder_id} not found")
    item.path = folder_in.path
    item.frequency = folder_in.frequency
    db.commit()
    db.refresh(item)
    db.close()
    return item


def delete_folder_item(folder_id: int) -> None:
    db: Session = SessionLocal()
    item = db.query(MonitoredFolder).filter(MonitoredFolder.id == folder_id).first()
    if item:
        db.delete(item)
        db.commit()
    db.close()


# ------------------------------
# ---- Status update functions ----

def update_file_status(file_id: int, status: str) -> MonitoredFile:
    db: Session = SessionLocal()
    try:
        item = db.query(MonitoredFile).filter(MonitoredFile.id == file_id).first()
        if not item:
            raise NoResultFound(f"File item {file_id} not found")
        item.status = status
        
        # Si on arrête complètement, on supprime le hash de référence
        if status == "paused":  # "paused" signifie arrêt complet dans votre logique
            item.baseline_hash = None
            item.current_hash = None
            
        db.commit()
        db.refresh(item)
        return item
    finally:
        db.close()

def update_folder_status(folder_id: int, status: str) -> MonitoredFolder:
    db: Session = SessionLocal()
    try:
        item = db.query(MonitoredFolder).filter(MonitoredFolder.id == folder_id).first()
        if not item:
            raise NoResultFound(f"Folder item {folder_id} not found")
        item.status = status
        
        if status == "paused":
            item.folder_hash = None
            item.file_count = 0
            
        db.commit()
        db.refresh(item)
        return item
    finally:
        db.close()

def update_ip_status(ip_id: int, status: str) -> MonitoredIP:
    db: Session = SessionLocal()
    try:
        item = db.query(MonitoredIP).filter(MonitoredIP.id == ip_id).first()
        if not item:
            raise NoResultFound(f"IP item {ip_id} not found")
        item.status = status
        db.commit()
        db.refresh(item)
        return item
    finally:
        db.close()