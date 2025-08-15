from fastapi import FastAPI, Depends
from app.core.logging import logger
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine

from app.core.scheduler import start_scheduler, shutdown_scheduler, add_interval_job, FREQ_SECONDS
from app.services.scan_tasks import scan_file, scan_folder, scan_ip
from app.db.session import SessionLocal
from app.db.models import MonitoredFile, MonitoredFolder, MonitoredIP

from app.api.status import router as status_router
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.monitoring import router as monitoring_router

from app.api.status import router as status_router
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.monitoring import router as monitoring_router

from app.api.activity import router as activity_router

logger.info(f"Starting {settings.APP_NAME}... (version: {settings.VERSION})")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    # version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.on_event("startup")
def on_startup():
    """
    Fonction de démarrage de l'application.
    """
    logger.info("Creating database tables (if not exist)...")
    
    Base.metadata.create_all(bind=engine)
    logger.info("Database ready.")
    
    start_scheduler()
    db = SessionLocal()
    try:
        for f in db.query(MonitoredFile).filter(MonitoredFile.status == "active").all():
            sec = FREQ_SECONDS.get(getattr(f, "frequency", "hourly"), 3600)
            add_interval_job("file", f.id, sec, scan_file, item_id=f.id, path=f.path)
        for d in db.query(MonitoredFolder).filter(MonitoredFolder.status == "active").all():
            sec = FREQ_SECONDS.get(getattr(d, "frequency", "hourly"), 3600)
            add_interval_job("folder", d.id, sec, scan_folder, item_id=d.id, path=d.path)
        for i in db.query(MonitoredIP).filter(MonitoredIP.status == "active").all():
            sec = FREQ_SECONDS.get(getattr(i, "frequency", "hourly"), 3600)
            add_interval_job("ip", i.id, sec, scan_ip, item_id=i.id, ip=i.ip, hostname=i.hostname)
    finally:
        db.close()

@app.on_event("shutdown")
def on_shutdown():
    """
    Fonction d'arrêt de l'application.
    """
    logger.info("Shutting down application...")
    
    shutdown_scheduler()
    
app.include_router(status_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
# app.include_router(users_router, prefix="/api")
app.include_router(users_router)
app.include_router(monitoring_router)
app.include_router(activity_router)