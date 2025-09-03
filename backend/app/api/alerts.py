# # backend/app/api/alerts.py
# from fastapi import APIRouter, Depends, Query, HTTPException
# from app.core.security import get_current_active_user
# from pathlib import Path
# import os
# import re

# router = APIRouter(
#     prefix="/alerts",
#     tags=["alerts"],
#     dependencies=[Depends(get_current_active_user)]
# )

# LOG_DIR = Path(os.getenv("HIDS_LOG_DIR", "logs")).resolve()

# # Regex pour les logs d'activité et d'alerte
# HIDS_LOG_REGEX = re.compile(r"^(\d{4}-\d{2}-\d{2})\s(\d{2}:\d{2}:\d{2}),(\d{3})\s\|\s([A-Z]+)\s\|\s(.+?)\s\|\s(.+)$")
# HIDS_ALERT_REGEX = re.compile(r"^(\d{4}-\d{2}-\d{2})\s(\d{2}:\d{2}:\d{2}),(\d{3})\s\|\s([A-Z]+)\s\|\s(.+)$")

# def parse_log_line(line: str):
#     """Parse une ligne de log HIDS et retourne un dictionnaire."""
#     line = line.strip()
#     if not line:
#         return None
    
#     match = HIDS_LOG_REGEX.match(line)
#     if match:
#         date, time, ms, level, source, message = match.groups()
#         return {
#             "ts": f"{date}T{time}.{ms}Z",
#             "level": level,
#             "source": source.strip(),
#             "msg": message.strip(),
#             "text": line
#         }
    
#     match = HIDS_ALERT_REGEX.match(line)
#     if match:
#         date, time, ms, level, message = match.groups()
#         return {
#             "ts": f"{date}T{time}.{ms}Z",
#             "level": level,
#             "source": "",
#             "msg": message.strip(),
#             "text": line
#         }
    
#     return {
#         "ts": None,
#         "level": "RAW",
#         "source": "",
#         "msg": line,
#         "text": line
#     }

# def read_log_file(filename: str):
#     """Lit un fichier de log et renvoie les lignes parsées."""
#     fp = (LOG_DIR / filename).resolve()
    
#     if not str(fp).startswith(str(LOG_DIR)):
#         raise HTTPException(status_code=400, detail="Invalid path")

#     if not fp.exists():
#         return []

#     try:
#         lines = fp.read_text(encoding="utf-8", errors="ignore").splitlines()
#         parsed_lines = [parse_log_line(line) for line in lines]
#         return [l for l in parsed_lines if l is not None]
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error reading file: {e}")

# @router.get("")
# def get_alerts(
#     page: int = Query(1, ge=1),
#     limit: int = Query(15, ge=1, le=500),
#     level: str | None = Query(None, description="DEBUG|INFO|WARNING|ERROR|CRITICAL"),
#     contains: str | None = Query(None),
# ):
#     """
#     Endpoint pour récupérer les alertes à partir du fichier alerts.log.
#     """
#     all_logs = read_log_file("alerts.log")
    
#     filtered_logs = [
#         log for log in all_logs
#         if (not level or log['level'].lower() == level.lower()) and
#             (not contains or contains.lower() in log['msg'].lower())
#     ]
    
#     filtered_logs.reverse()

#     total = len(filtered_logs)
#     page_count = max(1, (total + limit - 1) // limit)
#     page = min(page, page_count)
#     start_index = (page - 1) * limit
#     end_index = start_index + limit
#     paginated_logs = filtered_logs[start_index:end_index]
    
#     return {
#         "lines": paginated_logs,
#         "total": total,
#         "page_count": page_count
#     }
