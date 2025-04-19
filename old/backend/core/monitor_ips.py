
# core/monitor_ips.py
import os
import time
from datetime import datetime
from threading import Thread
import psutil
from utils.json_handler import read_json, write_json
from utils.logger import log_event

CONFIG_FILE = os.path.join("data", "config.json")
STATUS_FILE = os.path.join("data", "status.json")
ALERTS_FILE = os.path.join("data", "alerts.json")

class IPMonitor(Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.running = False
        self.interval = 10
        self.monitored_ips = []
        self.prev_state = {}
        self.pid = os.getpid()
        self.start_time = datetime.now().isoformat()

    def load_config(self):
        config = read_json(CONFIG_FILE)
        if not config or not config.get("ips"):
            return False
        self.interval = config.get("interval", 10)
        self.monitored_ips = config["ips"]
        return True

    def update_status(self):
        status = read_json(STATUS_FILE) or {}
        status["monitor_ips"] = {
            "PID": self.pid,
            "StartTime": self.start_time,
            "Status": "Running" if self.running else "Stopped",
            "Interval": self.interval,
            "MonitoredCount": len(self.monitored_ips),
            "MonitoredIPs": self.monitored_ips,
            "LastUpdate": datetime.now().isoformat()
        }
        write_json(STATUS_FILE, status)

    def add_alert(self, message):
        alerts = read_json(ALERTS_FILE) or {"files": [], "folders": [], "ips": []}
        timestamp = datetime.now().isoformat()
        alerts["ips"].append({
            "Timestamp": timestamp,
            "Message": message
        })
        write_json(ALERTS_FILE, alerts)
        log_event("IPs", message)

    def run(self):
        self.running = True
        if not self.load_config():
            log_event("IPs", "No IPs to monitor or invalid config.json")
            return
        while self.running:
            current_connections = psutil.net_connections(kind='inet')
            for ip in self.monitored_ips:
                found = False
                for conn in current_connections:
                    if conn.raddr and conn.raddr.ip == ip:
                        found = True
                        break
                if found and ip not in self.prev_state:
                    msg = f"Connection to {ip} established."
                    self.add_alert(msg)
                    self.prev_state[ip] = True
                elif not found and ip in self.prev_state:
                    msg = f"Connection to {ip} lost."
                    self.add_alert(msg)
                    del self.prev_state[ip]
            self.update_status()
            time.sleep(self.interval)
        self.update_status()

    def stop(self):
        self.running = False