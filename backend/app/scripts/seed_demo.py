# app/scripts/seed_demo.py
import random
from datetime import datetime, timedelta

from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.db import models

# ---------------- utils ----------------

def colnames(model_cls):
    return {c.name for c in model_cls.__table__.columns}

def kw(model_cls, **candidates):
    """Ne garde que les clés qui existent comme colonnes du modèle."""
    cols = colnames(model_cls)
    return {k: v for k, v in candidates.items() if k in cols}

SEVERITIES = ["low", "medium", "high"]
LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR"]
AE_TYPES = ["file_scan", "folder_scan", "ip_scan", "engine"]
FILE_BASENAMES = [
    "auth.log", "syslog", "kern.log", "nginx/access.log", "nginx/error.log",
    "app/app.log", "db/queries.log", "security/audit.log", "cron.log"
]
HOSTNAMES = ["srv-app-01", "srv-app-02", "edge-01", "db-01", "lab", "gw"]
RULES = ["RX-42", "IOC-15", "YARA-7", "SIG-2201", "IOC-9"]
LOGGERS = ["scanner.worker", "scheduler", "api.request", "db.engine", "alerts.pipeline"]
SOURCES = ["file", "folder", "ip"]

def rand_ip():
    return f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"

def rand_path():
    base = random.choice(FILE_BASENAMES)
    root = random.choice(["/var/log", "/opt", "/srv", "/data"])
    return f"{root}/{base}"

def rand_hostname():
    return random.choice(HOSTNAMES)

def now_utc():
    return datetime.utcnow()

# --------------- seeders ---------------

def seed_activity_events(db, n=100):
    Model = models.ActivityEvent
    print(f"Seeding {n} ActivityEvent… columns={sorted(colnames(Model))}")
    t0 = now_utc()
    rows = []
    for i in range(n):
        ts = t0 - timedelta(minutes=random.randint(0, 48*60))
        typ = random.choice(AE_TYPES)
        level = random.choices(LEVELS, weights=[1, 5, 2, 1], k=1)[0]
        msg = {
            "file_scan":  f"Scanned file {i}: {rand_path()}",
            "folder_scan":f"Indexed folder {i}: {rand_path().rsplit('/',1)[0]}",
            "ip_scan":    f"Probed IP {rand_ip()}",
            "engine":     f"Engine heartbeat (tick {i})"
        }[typ]
        data = kw(
            Model,
            ts=ts,
            type=typ,                # n’est conservé que si la colonne existe
            level=level,             # idem
            message=msg,
            path=rand_path() if typ in ("file_scan", "folder_scan") else None,
            ip=rand_ip() if typ == "ip_scan" else None,
            hostname=rand_hostname() if typ != "ip_scan" and random.random() < 0.5 else None,
        )
        rows.append(Model(**data))
    db.bulk_save_objects(rows)

def seed_alerts(db, n=100):
    Model = models.Alert
    print(f"Seeding {n} Alerts… columns={sorted(colnames(Model))}")
    t0 = now_utc()
    rows = []
    for i in range(n):
        ts = t0 - timedelta(minutes=random.randint(0, 7*24*60))
        sev = random.choices(SEVERITIES, weights=[5, 3, 1], k=1)[0]
        src = random.choice(SOURCES)
        rule = random.choice(RULES)
        hits = random.randint(1, 12)

        details = None
        message = ""
        if src == "file":
            pth = rand_path()
            message = f"Suspicious pattern ({rule}) in {pth}"
            details = {"rule": rule, "hits": hits, "path": pth, "excerpt": "Failed password for invalid user …"}
        elif src == "folder":
            folder = rand_path().rsplit("/", 1)[0]
            message = f"Multiple anomalies detected in folder {folder}"
            details = {"rule": rule, "hits": hits, "folder": folder, "files_impacted": random.randint(1, 7)}
        else:
            ip = rand_ip()
            message = f"Suspicious activity from IP {ip}"
            details = {"rule": rule, "hits": hits, "ip": ip, "port_scan": bool(random.getrandbits(1)),
                        "geo": random.choice(["FR", "US", "DE", "NL", "UK", "CA"])}

        data = kw(
            Model,
            ts=ts,
            severity=sev,            # gardé si colonne existe
            source=src,
            message=message,
            details=details          # gardé si colonne JSON/Text existe
        )
        rows.append(Model(**data))
    db.bulk_save_objects(rows)

def seed_backend_logs(db, n=120):
    if not hasattr(models, "BackendLogLine"):
        print("⚠  models.BackendLogLine absent — on saute cette partie.")
        return
    Model = models.BackendLogLine
    print(f"Seeding {n} BackendLogLine… columns={sorted(colnames(Model))}")
    t0 = now_utc()
    rows = []
    for i in range(n):
        ts = t0 - timedelta(seconds=30*i)
        level = random.choices(LEVELS, weights=[2, 6, 2, 1], k=1)[0]
        logger = random.choice(LOGGERS)
        text = random.choice([
            "task scheduled", "scan started", "scan completed", "no changes detected",
            "new items discovered", "writing results", "retrying after error",
            "db commit ok", "config reloaded",
        ])
        data = kw(
            Model,
            ts=ts,
            level=level,
            logger=logger,
            text=f"{text} (#{i})",
        )
        rows.append(Model(**data))
    db.bulk_save_objects(rows)

def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # (optionnel) remets à zéro si tu veux:
        # for M in (getattr(models, "ActivityEvent", None), getattr(models, "Alert", None), getattr(models, "BackendLogLine", None)):
        #     if M is not None:
        #         db.query(M).delete()
        # db.commit()

        seed_activity_events(db, n=100)
        seed_alerts(db, n=100)
        seed_backend_logs(db, n=120)

        db.commit()
        print("✅ Seed done.")
    finally:
        db.close()

if __name__ == "__main__":
    main()