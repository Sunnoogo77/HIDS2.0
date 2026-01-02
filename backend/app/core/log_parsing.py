import json
from typing import Optional


def extract_json_payload(line: str) -> Optional[dict]:
    if not line:
        return None
    text = line.strip()
    if not text:
        return None
    payload = text.rsplit(" | ", 1)[-1]
    try:
        return json.loads(payload)
    except Exception:
        try:
            return json.loads(text)
        except Exception:
            return None


def classify_scan_event(event: dict) -> Optional[str]:
    if not isinstance(event, dict):
        return None
    scan_type = event.get("scan_type")
    if scan_type in {"file", "folder", "ip"}:
        return f"{scan_type}_scan"
    activity_type = (event.get("activity_type") or "").lower()
    if activity_type.startswith("file_"):
        return "file_scan"
    if activity_type.startswith("folder_"):
        return "folder_scan"
    if activity_type.startswith("ip_"):
        return "ip_scan"
    return None
