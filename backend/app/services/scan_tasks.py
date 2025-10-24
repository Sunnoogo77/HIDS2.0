# import os, json, logging, hashlib
# from datetime import datetime
# from sqlalchemy.orm import Session

# from app.db.session import SessionLocal
# from app.db.models import MonitoredFile, MonitoredFolder
# from .hash_service import calculate_file_hash, calculate_folder_fingerprint, check_ip_activity

# # Configuration logging
# LOG_PATH = os.getenv("HIDS_LOG_PATH", "logs/hids.log")
# os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

# logger = logging.getLogger("hids-scanner")
# logger.setLevel(logging.INFO)
# if not logger.handlers:
#     fh = logging.FileHandler(LOG_PATH)
#     fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
#     fh.setFormatter(fmt)
#     logger.addHandler(fh)

# def _write_alert(event_type: str, item_id: int, details: dict):
#     """Écrit une alerte dans les logs"""
#     event = {
#         "type": "alert",
#         "alert_type": event_type,
#         "item_id": item_id,
#         "timestamp": datetime.utcnow().isoformat(),
#         **details
#     }
#     logger.warning(json.dumps(event, ensure_ascii=False))

# def _write_activity(event_type: str, item_id: int, details: dict):
#     """Écrit une activité normale dans les logs"""
#     event = {
#         "type": "activity",
#         "activity_type": event_type,
#         "item_id": item_id,
#         "timestamp": datetime.utcnow().isoformat(),
#         **details
#     }
#     logger.info(json.dumps(event, ensure_ascii=False))

# def scan_file(item_id: int, path: str):
#     """Scan réel d'un fichier avec comparaison de hash"""
#     db: Session = SessionLocal()
    
#     try:
#         # Récupérer l'item depuis la base
#         item = db.query(MonitoredFile).filter(MonitoredFile.id == item_id).first()
#         if not item:
#             _write_alert("file_error", item_id, {"error": "Item not found in database", "path": path})
#             return

#         # Vérifier si le fichier existe
#         if not os.path.exists(path):
#             _write_alert("file_not_found", item_id, {"path": path})
#             # Mettre à jour le statut
#             item.current_hash = None
#             item.last_scan = datetime.utcnow()
#             db.commit()
#             return

#         # Calculer le hash actuel
#         current_hash = calculate_file_hash(path)
#         if not current_hash:
#             _write_alert("file_hash_error", item_id, {"path": path})
#             return

#         # Premier scan : établir la baseline
#         if not item.baseline_hash:
#             item.baseline_hash = current_hash
#             item.current_hash = current_hash
#             item.last_scan = datetime.utcnow()
#             db.commit()
#             _write_activity("file_baseline_established", item_id, {
#                 "path": path, 
#                 "baseline_hash": current_hash
#             })
#             return

#         # Scans suivants : comparer avec la baseline
#         item.current_hash = current_hash
#         item.last_scan = datetime.utcnow()
#         db.commit()

#         if current_hash != item.baseline_hash:
#             _write_alert("file_modified", item_id, {
#                 "path": path,
#                 "previous_hash": item.baseline_hash,
#                 "current_hash": current_hash
#             })
#         else:
#             _write_activity("file_unchanged", item_id, {"path": path})

#     except Exception as e:
#         _write_alert("file_scan_error", item_id, {"path": path, "error": str(e)})
#     finally:
#         db.close()

# def scan_folder(item_id: int, path: str):
#     """Scan réel d'un dossier"""
#     db: Session = SessionLocal()
    
#     try:
#         item = db.query(MonitoredFolder).filter(MonitoredFolder.id == item_id).first()
#         if not item:
#             _write_alert("folder_error", item_id, {"error": "Item not found in database", "path": path})
#             return

#         if not os.path.exists(path) or not os.path.isdir(path):
#             _write_alert("folder_not_found", item_id, {"path": path})
#             item.folder_hash = None
#             item.file_count = 0
#             item.last_scan = datetime.utcnow()
#             db.commit()
#             return

#         # Calculer l'empreinte du dossier
#         fingerprint = calculate_folder_fingerprint(path)
#         if not fingerprint:
#             _write_alert("folder_scan_error", item_id, {"path": path})
#             return

#         current_hash, file_count = fingerprint

#         # Premier scan
#         if not item.folder_hash:
#             item.folder_hash = current_hash
#             item.file_count = file_count
#             item.last_scan = datetime.utcnow()
#             db.commit()
#             _write_activity("folder_baseline_established", item_id, {
#                 "path": path,
#                 "baseline_hash": current_hash,
#                 "file_count": file_count
#             })
#             return

#         # Scans suivants
#         previous_file_count = item.file_count
#         item.file_count = file_count
#         item.last_scan = datetime.utcnow()
#         db.commit()

#         if current_hash != item.folder_hash:
#             _write_alert("folder_modified", item_id, {
#                 "path": path,
#                 "previous_hash": item.folder_hash,
#                 "current_hash": current_hash,
#                 "previous_file_count": previous_file_count,
#                 "current_file_count": file_count
#             })
            
#             # Mettre à jour la baseline pour les prochains scans
#             item.folder_hash = current_hash
#             db.commit()
#         else:
#             _write_activity("folder_unchanged", item_id, {
#                 "path": path, 
#                 "file_count": file_count
#             })

#     except Exception as e:
#         _write_alert("folder_scan_error", item_id, {"path": path, "error": str(e)})
#     finally:
#         db.close()

# def scan_ip(item_id: int, ip: str, hostname: str = None):
#     """Scan réel d'une IP"""
#     db: Session = SessionLocal()
    
#     try:
#         item = db.query(MonitoredIP).filter(MonitoredIP.id == item_id).first()
#         if not item:
#             _write_alert("ip_error", item_id, {"error": "Item not found in database", "ip": ip})
#             return

#         # Vérifier l'activité de l'IP
#         ip_status = check_ip_activity(ip)
        
#         # Premier scan
#         if not hasattr(item, 'last_status') or not item.last_status:
#             item.last_status = json.dumps(ip_status)
#             item.last_scan = datetime.utcnow()
#             db.commit()
#             _write_activity("ip_baseline_established", item_id, {
#                 "ip": ip,
#                 "status": ip_status
#             })
#             return

#         # Comparaison avec le statut précédent
#         previous_status = json.loads(item.last_status)
#         item.last_status = json.dumps(ip_status)
#         item.last_scan = datetime.utcnow()
#         db.commit()

#         # Détection des changements
#         if previous_status.get('is_active') != ip_status.get('is_active'):
#             _write_alert("ip_status_changed", item_id, {
#                 "ip": ip,
#                 "previous_active": previous_status.get('is_active'),
#                 "current_active": ip_status.get('is_active'),
#                 "connections": ip_status.get('connections', [])
#             })

#     except Exception as e:
#         _write_alert("ip_scan_error", item_id, {"ip": ip, "error": str(e)})
#     finally:
#         db.close()

import os, json, logging
from datetime import datetime
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models import MonitoredFile, MonitoredFolder, MonitoredIP
from .hash_service import calculate_file_hash, calculate_folder_fingerprint, check_ip_activity

# ───────────────────────────────────────────────
# Configuration des fichiers de logs
# ───────────────────────────────────────────────
HIDS_LOG_PATH = os.getenv("HIDS_LOG_PATH", "logs/hids.log")
ALERTS_LOG_PATH = os.getenv("HIDS_ALERTS_LOG_PATH", "logs/alerts.log")

os.makedirs(os.path.dirname(HIDS_LOG_PATH), exist_ok=True)

# Logger global (toutes activités + trace des alertes)
hids_logger = logging.getLogger("hids")
hids_logger.setLevel(logging.INFO)
if not hids_logger.handlers:
    fh = logging.FileHandler(HIDS_LOG_PATH)
    # fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    fh.setFormatter(fmt)
    hids_logger.addHandler(fh)

# Logger dédié aux alertes (fichier séparé)
alerts_logger = logging.getLogger("alerts")
alerts_logger.setLevel(logging.WARNING)
if not alerts_logger.handlers:
    fh = logging.FileHandler(ALERTS_LOG_PATH)
    # fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    fh.setFormatter(fmt)
    alerts_logger.addHandler(fh)


# ───────────────────────────────────────────────
# Helpers
# ───────────────────────────────────────────────
def _map_severity(severity: str) -> int:
    """Mappe une sévérité textuelle vers logging.*"""
    return {
        "CRITICAL": logging.CRITICAL,
        "HIGH": logging.ERROR,
        "MEDIUM": logging.WARNING,
        "LOW": logging.INFO,
        "INFO": logging.DEBUG,
    }.get(severity.upper(), logging.WARNING)


def _write_alert(event_type: str, item_id: int, severity: str, details: dict):
    """Écrit une alerte dans alerts.log (+ warning dans hids.log)."""
    event = {
        "type": "alert",
        "alert_type": event_type,
        "item_id": item_id,
        "severity": severity.upper(),
        "timestamp": datetime.utcnow().isoformat(),
        **details
    }
    line = json.dumps(event, ensure_ascii=False)

    alerts_logger.log(_map_severity(severity), line)
    hids_logger.warning(line)  # garder aussi une trace globale


def _write_activity(event_type: str, item_id: int, details: dict):
    """Écrit une activité normale dans hids.log uniquement."""
    event = {
        "type": "activity",
        "activity_type": event_type,
        "item_id": item_id,
        "timestamp": datetime.utcnow().isoformat(),
        **details
    }
    hids_logger.info(json.dumps(event, ensure_ascii=False))


# ───────────────────────────────────────────────
# Scans
# ───────────────────────────────────────────────
def scan_file(item_id: int, path: str):
    """Scan réel d'un fichier avec comparaison de hash"""
    db: Session = SessionLocal()
    try:
        item = db.query(MonitoredFile).filter(MonitoredFile.id == item_id).first()
        if not item:
            _write_alert("file_error", item_id, "HIGH", {"error": "Item not found in database", "path": path})
            return

        if not os.path.exists(path):
            _write_alert("file_not_found", item_id, "HIGH", {"path": path})
            item.current_hash = None
            item.last_scan = datetime.utcnow()
            db.commit()
            return

        current_hash = calculate_file_hash(path)
        if not current_hash:
            _write_alert("file_hash_error", item_id, "MEDIUM", {"path": path})
            return

        if not item.baseline_hash:
            item.baseline_hash = current_hash
            item.current_hash = current_hash
            item.last_scan = datetime.utcnow()
            db.commit()
            _write_activity("file_baseline_established", item_id, {
                "path": path, "baseline_hash": current_hash
            })
            return

        # Comparaison
        item.current_hash = current_hash
        item.last_scan = datetime.utcnow()
        db.commit()

        if current_hash != item.baseline_hash:
            _write_alert("file_modified", item_id, "CRITICAL", {
                "path": path,
                "previous_hash": item.baseline_hash,
                "current_hash": current_hash
            })
        else:
            _write_activity("file_unchanged", item_id, {"path": path})

    except Exception as e:
        _write_alert("file_scan_error", item_id, "CRITICAL", {"path": path, "error": str(e)})
    finally:
        db.close()


def scan_folder(item_id: int, path: str):
    """Scan réel d'un dossier"""
    db: Session = SessionLocal()
    try:
        item = db.query(MonitoredFolder).filter(MonitoredFolder.id == item_id).first()
        if not item:
            _write_alert("folder_error", item_id, "HIGH", {"error": "Item not found in database", "path": path})
            return

        if not os.path.exists(path) or not os.path.isdir(path):
            _write_alert("folder_not_found", item_id, "HIGH", {"path": path})
            item.folder_hash = None
            item.file_count = 0
            item.last_scan = datetime.utcnow()
            db.commit()
            return

        fingerprint = calculate_folder_fingerprint(path)
        if not fingerprint:
            _write_alert("folder_scan_error", item_id, "MEDIUM", {"path": path})
            return

        current_hash, file_count = fingerprint

        if not item.folder_hash:
            item.folder_hash = current_hash
            item.file_count = file_count
            item.last_scan = datetime.utcnow()
            db.commit()
            _write_activity("folder_baseline_established", item_id, {
                "path": path, "baseline_hash": current_hash, "file_count": file_count
            })
            return

        previous_file_count = item.file_count
        item.file_count = file_count
        item.last_scan = datetime.utcnow()
        db.commit()

        if current_hash != item.folder_hash:
            _write_alert("folder_modified", item_id, "HIGH", {
                "path": path,
                "previous_hash": item.folder_hash,
                "current_hash": current_hash,
                "previous_file_count": previous_file_count,
                "current_file_count": file_count
            })
            item.folder_hash = current_hash
            db.commit()
        else:
            _write_activity("folder_unchanged", item_id, {"path": path, "file_count": file_count})

    except Exception as e:
        _write_alert("folder_scan_error", item_id, "CRITICAL", {"path": path, "error": str(e)})
    finally:
        db.close()


def scan_ip(item_id: int, ip: str, hostname: str = None):
    """Scan réel d'une IP"""
    db: Session = SessionLocal()
    try:
        item = db.query(MonitoredIP).filter(MonitoredIP.id == item_id).first()
        if not item:
            _write_alert("ip_error", item_id, "HIGH", {"error": "Item not found in database", "ip": ip})
            return

        ip_status = check_ip_activity(ip)

        if not hasattr(item, 'last_status') or not item.last_status:
            item.last_status = json.dumps(ip_status)
            item.last_scan = datetime.utcnow()
            db.commit()
            _write_activity("ip_baseline_established", item_id, {"ip": ip, "status": ip_status})
            return

        previous_status = json.loads(item.last_status)
        item.last_status = json.dumps(ip_status)
        item.last_scan = datetime.utcnow()
        db.commit()

        if previous_status.get('is_active') != ip_status.get('is_active'):
            _write_alert("ip_status_changed", item_id, "MEDIUM", {
                "ip": ip,
                "previous_active": previous_status.get('is_active'),
                "current_active": ip_status.get('is_active'),
                "connections": ip_status.get('connections', [])
            })

    except Exception as e:
        _write_alert("ip_scan_error", item_id, "CRITICAL", {"ip": ip, "error": str(e)})
    finally:
        db.close()
