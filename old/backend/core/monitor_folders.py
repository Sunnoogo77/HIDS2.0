# core/monitor_folders.py
import os
import time
import hashlib
from datetime import datetime
from threading import Thread
from utils.json_handler import read_json, write_json
from utils.logger import log_event

CONFIG_FILE = os.path.join("data", "config.json")
STATUS_FILE = os.path.join("data", "status.json")
ALERTS_FILE = os.path.join("data", "alerts.json")

class FolderMonitor(Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.running = False
        self.interval = 10
        self.monitored_folders = {}
        self.pid = os.getpid()
        self.start_time = datetime.now().isoformat()

    def calculate_folder_hash(self, folder):
        hash_string = ""
        for root, _, files in os.walk(folder):
            for file in sorted(files):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'rb') as f:
                        hash_string += hashlib.sha256(f.read()).hexdigest()
                except:
                    continue
        return hashlib.sha256(hash_string.encode()).hexdigest()

    def load_config(self):
        config = read_json(CONFIG_FILE)
        if not config or not config.get("folders"):
            return False
        self.interval = config.get("interval", 10)
        for path in config["folders"]:
            if os.path.exists(path):
                folder_hash = self.calculate_folder_hash(path)
                self.monitored_folders[path] = folder_hash
                log_event("Folders", f"Added folder: {path} (Hash: {folder_hash})")
        return True

    def update_status(self):
        status = read_json(STATUS_FILE) or {}
        status["monitor_folders"] = {
            "PID": self.pid,
            "StartTime": self.start_time,
            "Status": "Running" if self.running else "Stopped",
            "Interval": self.interval,
            "MonitoredCount": len(self.monitored_folders),
            "MonitoredFolders": list(self.monitored_folders.keys()),
            "LastUpdate": datetime.now().isoformat()
        }
        write_json(STATUS_FILE, status)

    def add_alert(self, folder, old_hash, new_hash):
        alerts = read_json(ALERTS_FILE) or {"files": [], "folders": [], "ips": []}
        timestamp = datetime.now().isoformat()
        alert_msg = f"Folder changed! {folder}"
        alerts["folders"].append({
            "Timestamp": timestamp,
            "Message": alert_msg
        })
        write_json(ALERTS_FILE, alerts)
        log_event("Folders", f"{alert_msg} | Old Hash: {old_hash} | New Hash: {new_hash}")

    def run(self):
        self.running = True
        if not self.load_config():
            log_event("Folders", "No folders to monitor or invalid config.json")
            return
        while self.running:
            for folder in list(self.monitored_folders.keys()):
                if os.path.exists(folder):
                    new_hash = self.calculate_folder_hash(folder)
                    if self.monitored_folders[folder] != new_hash:
                        self.add_alert(folder, self.monitored_folders[folder], new_hash)
                        self.monitored_folders[folder] = new_hash
                else:
                    log_event("Folders", f"WARNING: Folder Missing - {folder}")
                    del self.monitored_folders[folder]
            self.update_status()
            time.sleep(self.interval)
        self.update_status()

    def stop(self):
        self.running = False