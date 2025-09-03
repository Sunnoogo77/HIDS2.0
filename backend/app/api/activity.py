# # # backend/app/api/activity.py
# # from fastapi import APIRouter, Depends, Query
# # from app.core.security import get_current_active_user
# # import os, json

# # LOG_PATH = os.getenv("HIDS_LOG_PATH", "logs/hids.log")
# # router = APIRouter(prefix="/api", tags=["activity"], dependencies=[Depends(get_current_active_user)])

# # @router.get("/activity")
# # def get_activity(limit: int = Query(200, ge=1, le=1000)):
# #     if not os.path.exists(LOG_PATH):
# #         return []
# #     # on lit les dernières lignes simplement
# #     with open(LOG_PATH, "r", encoding="utf-8", errors="ignore") as f:
# #         lines = f.readlines()[-limit:]
# #     out = []
# #     for line in lines:
# #         try:
# #             # nos logs: "ts | LEVEL | {json}"
# #             payload = line.split("|", 2)[2].strip()
# #             out.append(json.loads(payload))
# #         except Exception:
# #             out.append({"raw": line.strip()})
# #     return out

# # # backend/app/api/activity.py
# # from fastapi import APIRouter, Depends, Query, HTTPException
# # from app.core.security import get_current_active_user
# # from sqlalchemy.orm import Session
# # import os, json

# # # ---- Dépendances DB
# # from app.db.session import get_db
# # from app.db.models import ActivityEvent  # tes modèles SQLAlchemy sont tous ici
# # from app.models.alerts import ActivityOut  # <-- tes Pydantic schemas sont dans app/models/alerts.py

# # LOG_PATH = os.getenv("HIDS_LOG_PATH", "logs/hids.log")

# # router = APIRouter(
# #     prefix="/api",
# #     tags=["activity"],
# #     dependencies=[Depends(get_current_active_user)]
# # )

# # def _read_log_lines(limit_total: int) -> list[dict]:
# #     """Fallback: lit le fichier de log si la table est vide."""
# #     if not os.path.exists(LOG_PATH):
# #         return []
# #     with open(LOG_PATH, "r", encoding="utf-8", errors="ignore") as f:
# #         lines = f.readlines()

# #     # On renverse pour avoir les plus récentes d’abord
# #     lines = list(reversed(lines))

# #     out = []
# #     for line in lines:
# #         line = line.strip()
# #         if not line:
# #             continue
# #         try:
# #             # format attendu: "ts | LEVEL | {json}"
# #             parts = line.split("|", 2)
# #             payload = parts[2].strip() if len(parts) >= 3 else "{}"
# #             obj = json.loads(payload)
# #             # normalisation minimale pour coller au front
# #             out.append({
# #                 "id": None,
# #                 "ts": obj.get("ts") or obj.get("timestamp"),
# #                 "kind": obj.get("kind") or obj.get("event") or "log",
# #                 "entity_type": obj.get("entity_type"),
# #                 "entity_id": obj.get("entity_id"),
# #                 "entity_label": obj.get("entity_label") or obj.get("path") or obj.get("ip"),
# #                 "message": obj.get("message") or obj.get("msg") or line,
# #                 "meta": obj
# #             })
# #         except Exception:
# #             out.append({
# #                 "id": None,
# #                 "ts": None,
# #                 "kind": "log",
# #                 "entity_type": None,
# #                 "entity_id": None,
# #                 "entity_label": None,
# #                 "message": line,
# #                 "meta": {"raw": line}
# #             })
# #         if len(out) >= limit_total:
# #             break
# #     return out

# # @router.get("/activity")
# # def list_activity(
# #     db: Session = Depends(get_db),
# #     limit: int = Query(15, ge=1, le=200),
# #     offset: int = Query(0, ge=0),
# #     kind: str | None = Query(None, description="ex: scan_done, file_added…"),
# #     entity_type: str | None = Query(None, description="file|folder|ip")
# # ):
# #     """
# #     Renvoie les événements paginés.
# #     - Priorité à la **DB** (ActivityEvent)
# #     - Fallback sur **HIDS_LOG_PATH** si la table est vide
# #     Réponse: { items, count, total }
# #     """
# #     # 1) Essaye DB
# #     try:
# #         q = db.query(ActivityEvent)
# #         if kind:
# #             q = q.filter(ActivityEvent.kind == kind)
# #         if entity_type:
# #             q = q.filter(ActivityEvent.entity_type == entity_type)

# #         total = q.count()
# #         if total > 0:
# #             rows = (
# #                 q.order_by(ActivityEvent.ts.desc())
# #                     .offset(offset)
# #                     .limit(limit)
# #                     .all()
# #             )
# #             items = [ActivityOut.model_validate(r) for r in rows]
# #             return {"items": items, "count": len(items), "total": total}
# #     except Exception as e:
# #         # Si souci DB, on retombe sur le fichier
# #         pass

# #     # 2) Fallback: fichier log (non indexé, on simule la pagination en mémoire)
# #     raw = _read_log_lines(limit_total=offset + limit)
# #     total = len(raw)
# #     items = raw[offset:offset+limit]
# #     return {"items": items, "count": len(items), "total": total}


# # backend/app/api/activity.py
# from fastapi import APIRouter, Depends, Query, HTTPException
# from app.core.security import get_current_active_user
# from pathlib import Path
# import os
# import re

# router = APIRouter(
#     prefix="/activity",
#     tags=["activity"],
#     dependencies=[Depends(get_current_active_user)]
# )

# LOG_DIR = Path(os.getenv("HIDS_LOG_DIR", "logs")).resolve()

# # Regex pour les logs d'activité
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
# def get_activity_logs(
#     page: int = Query(1, ge=1),
#     limit: int = Query(15, ge=1, le=500),
#     level: str | None = Query(None, description="DEBUG|INFO|WARNING|ERROR|CRITICAL"),
#     contains: str | None = Query(None),
# ):
#     """
#     Endpoint pour récupérer les logs d'activité à partir du fichier hids.log.
#     """
#     all_logs = read_log_file("hids.log")
    
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
