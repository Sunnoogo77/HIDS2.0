import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# core/monitor_files.py
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

class FileMonitor(Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.running = False
        self.interval = 10
        self.monitored_files = {}
        self.pid = os.getpid()
        self.start_time = datetime.now().isoformat()

    def calculate_hash(self, filepath):
        try:
            with open(filepath, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return None

    def load_config(self):
        config = read_json(CONFIG_FILE)
        if not config or not config.get("files"):
            return False
        self.interval = config.get("interval", 10)
        for path in config["files"]:
            if os.path.exists(path):
                file_hash = self.calculate_hash(path)
                self.monitored_files[path] = file_hash
                log_event("Files", f"Added file: {path} (Hash: {file_hash})")
        return True

    def update_status(self):
        status = read_json(STATUS_FILE) or {}
        status["monitor_files"] = {
            "PID": self.pid,
            "StartTime": self.start_time,
            "Status": "Running" if self.running else "Stopped",
            "Interval": self.interval,
            "MonitoredCount": len(self.monitored_files),
            "monitoredFiles": list(self.monitored_files.keys()),
            "LastUpdate": datetime.now().isoformat()
        }
        write_json(STATUS_FILE, status)

    def add_alert(self, filepath, old_hash, new_hash):
        alerts = read_json(ALERTS_FILE) or {"files": [], "folders": [], "ips": []}
        timestamp = datetime.now().isoformat()
        alert_msg = f"File changed! {filepath}"
        alerts["files"].append({
            "Timestamp": timestamp,
            "Message": alert_msg
        })
        write_json(ALERTS_FILE, alerts)
        log_event("Files", f"{alert_msg} | Old Hash: {old_hash} | New Hash: {new_hash}")

    def run(self):
        status = read_json(STATUS_FILE) or {}
        current = status.get("monitor_files", {})
        if current.get("Status") == "Running":
            log_event("Files", "Attempt to start monitor_files but it's already running.")
            return

        self.running = True
        self.update_status()  # Write status right away (second safety)

        if not self.load_config():
            log_event("Files", "No files to monitor or invalid config.json")
            self.running = False
            self.update_status()
            return

        while self.running:
            for filepath in list(self.monitored_files.keys()):
                if os.path.exists(filepath):
                    current_hash = self.calculate_hash(filepath)
                    if self.monitored_files[filepath] != current_hash:
                        self.add_alert(filepath, self.monitored_files[filepath], current_hash)
                        self.monitored_files[filepath] = current_hash
                else:
                    log_event("Files", f"WARNING: File Missing - {filepath}")
                    self.monitored_files.pop(filepath, None)
            self.update_status()
            time.sleep(self.interval)

        self.update_status()

    def stop(self):
        self.running = False