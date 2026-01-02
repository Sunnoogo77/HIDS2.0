# File: backend/app/services/monitoring_service.py
import os, re

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound, IntegrityError

from app.db.session import SessionLocal, commit_with_retry
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
        normalized_path = normalize_path(file_in.path)
        existing = db.query(MonitoredFile).filter(MonitoredFile.path == normalized_path).first()
        if existing:
            db.close()
            return existing
        # db_item = MonitoredFile(path=normalized_path, frequency=file_in.frequency, status="stopped")
        db_item = MonitoredFile(path=normalize_path(file_in.path),
                        frequency=file_in.frequency,
                        status=file_in.status or "active")
        db.add(db_item)
        commit_with_retry(db)
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
    item.path = normalize_path(file_in.path)
    item.frequency = file_in.frequency
    commit_with_retry(db)
    db.refresh(item)
    db.close()
    return item


def update_file_frequency(file_id: int, frequency: str) -> MonitoredFile:
    db: Session = SessionLocal()
    item = db.query(MonitoredFile).filter(MonitoredFile.id == file_id).first()
    if not item:
        db.close()
        raise NoResultFound(f"File item {file_id} not found")
    item.frequency = frequency
    commit_with_retry(db)
    db.refresh(item)
    db.close()
    return item


def delete_file_item(file_id: int) -> None:
    db: Session = SessionLocal()
    item = db.query(MonitoredFile).filter(MonitoredFile.id == file_id).first()
    if item:
        db.delete(item)
        commit_with_retry(db)
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
            frequency=ip_in.frequency,
            # status="stopped"
            status=ip_in.status or "active"
        )
        db.add(db_item)
        commit_with_retry(db)
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
    commit_with_retry(db)
    db.refresh(item)
    db.close()
    return item


def update_ip_frequency(ip_id: int, frequency: str) -> MonitoredIP:
    db: Session = SessionLocal()
    item = db.query(MonitoredIP).filter(MonitoredIP.id == ip_id).first()
    if not item:
        db.close()
        raise NoResultFound(f"IP item {ip_id} not found")
    item.frequency = frequency
    commit_with_retry(db)
    db.refresh(item)
    db.close()
    return item


def delete_ip_item(ip_id: int) -> None:
    db: Session = SessionLocal()
    item = db.query(MonitoredIP).filter(MonitoredIP.id == ip_id).first()
    if item:
        db.delete(item)
        commit_with_retry(db)
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
        # db_item = MonitoredFolder(path=folder_in.path, frequency=folder_in.frequency, status="stopped")
        db_item = MonitoredFolder(path=normalize_path(folder_in.path),
                        frequency=folder_in.frequency,
                        status=folder_in.status or "active")
        db.add(db_item); commit_with_retry(db); db.refresh(db_item)
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
    item.path = normalize_path(folder_in.path) 
    item.frequency = folder_in.frequency
    commit_with_retry(db)
    db.refresh(item)
    db.close()
    return item


def update_folder_frequency(folder_id: int, frequency: str) -> MonitoredFolder:
    db: Session = SessionLocal()
    item = db.query(MonitoredFolder).filter(MonitoredFolder.id == folder_id).first()
    if not item:
        db.close()
        raise NoResultFound(f"Folder item {folder_id} not found")
    item.frequency = frequency
    commit_with_retry(db)
    db.refresh(item)
    db.close()
    return item


def delete_folder_item(folder_id: int) -> None:
    db: Session = SessionLocal()
    item = db.query(MonitoredFolder).filter(MonitoredFolder.id == folder_id).first()
    if item:
        db.delete(item)
        commit_with_retry(db)
    db.close()


# ------------------------------
# ---- Status update functions ----

def update_file_status(file_id: int, status: str) -> MonitoredFile:
    db: Session = SessionLocal()
    try:
        item = db.query(MonitoredFile).filter(MonitoredFile.id == file_id).first()
        if not item:
            raise NoResultFound(f"File item {file_id} not found")

        if status not in {"active", "paused", "stopped"}:
            raise ValueError(f"Unsupported file status: {status}")

        item.status = status

        if status == "stopped":
            # Hard stop: drop hashes so a fresh baseline is rebuilt on next run
            item.baseline_hash = None
            item.current_hash = None
        # NOTE: 'paused' NE change rien aux hashes.

        commit_with_retry(db)
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

        if status not in {"active", "paused", "stopped"}:
            raise ValueError(f"Unsupported folder status: {status}")

        item.status = status

        if status == "stopped":
            # Arrêt fort: on oublie les états agrégés
            item.folder_hash = None
            item.file_count = 0
        # 'paused' : on ne touche pas

        commit_with_retry(db)
        db.refresh(item)
        return item
    finally:
        db.close()


def update_ip_status(ip_id: int, status: str) -> MonitoredIP:
    """
    Les IPs n’ont pas de vraie pause métier. On accepte 'paused' pour compat UI,
    mais on traite 'paused' comme 'stopped' côté données (pas de hash à conserver).
    """
    db: Session = SessionLocal()
    try:
        item = db.query(MonitoredIP).filter(MonitoredIP.id == ip_id).first()
        if not item:
            raise NoResultFound(f"IP item {ip_id} not found")

        if status not in {"active", "paused", "stopped"}:
            raise ValueError(f"Unsupported IP status: {status}")

        # Normaliser: paused -> stopped pour IP
        normalized = "stopped" if status in {"paused", "stopped"} else "active"
        item.status = normalized

        if normalized == "stopped":
            item.last_status = None

        commit_with_retry(db)
        db.refresh(item)
        return item
    finally:
        db.close()


def normalize_path(path: str) -> str:
    if not path:
        return path
    # Convertir backslashes → slashes
    path = path.replace("\\", "/")
    # Supprimer les espaces début/fin
    path = path.strip()
    # Remplacer doubles slashes par simples (hors protocole type http://)
    path = re.sub(r'(?<!:)//+', '/', path)
    return path
