# utils/logger.py
import os
import json
from datetime import datetime

LOG_DIR = os.path.join("logs")
LOG_TEXT_FILE = os.path.join(LOG_DIR, "hids.log")
LOG_JSON_FILE = os.path.join(LOG_DIR, "hids.json")

def ensure_log_files():
    os.makedirs(LOG_DIR, exist_ok=True)
    if not os.path.exists(LOG_TEXT_FILE):
        with open(LOG_TEXT_FILE, 'w', encoding='utf-8') as f:
            pass
    if not os.path.exists(LOG_JSON_FILE):
        with open(LOG_JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)

def log_event(category: str, message: str):
    """Add a log entry in both the log file and JSON file."""
    ensure_log_files()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        "timestamp": timestamp,
        "category": category,
        "event": message
    }

    # Write to JSON
    try:
        with open(LOG_JSON_FILE, 'r', encoding='utf-8') as f:
            logs = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        logs = []

    logs.append(entry)
    with open(LOG_JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, indent=4)

    # Write to text log
    with open(LOG_TEXT_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] [{category}] {message}\n")
