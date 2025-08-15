# app/services/scan_tasks.py
import os, json, logging
from datetime import datetime

LOG_PATH = os.getenv("HIDS_LOG_PATH", "logs/hids.log")
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

logger = logging.getLogger("hids-scheduler")
logger.setLevel(logging.INFO)
if not logger.handlers:
    fh = logging.FileHandler(LOG_PATH)
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

def _write_event(event: dict):
    # log + ligne JSON (facile à parser)
    logger.info(json.dumps(event, ensure_ascii=False))

def scan_file(item_id: int, path: str):
    _write_event({"type":"file_scan","id":item_id,"path":path,"result":"OK","ts":datetime.utcnow().isoformat()})

def scan_folder(item_id: int, path: str):
    _write_event({"type":"folder_scan","id":item_id,"path":path,"result":"OK","ts":datetime.utcnow().isoformat()})

def scan_ip(item_id: int, ip: str, hostname: str|None=None):
    _write_event({"type":"ip_scan","id":item_id,"ip":ip,"hostname":hostname,"result":"OK","ts":datetime.utcnow().isoformat()})
