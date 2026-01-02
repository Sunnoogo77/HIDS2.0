from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.core.logging import logger
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine as db_engine
Base.metadata.create_all(bind=db_engine)

from app.core.scheduler import start_scheduler, shutdown_scheduler, add_interval_job, FREQ_SECONDS
from app.services.scan_tasks import scan_file, scan_folder, scan_ip
from app.db.session import SessionLocal
from app.db.models import MonitoredFile, MonitoredFolder, MonitoredIP

from app.api.status import router as status_router
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.monitoring import router as monitoring_router
from app.api.metrics import router as metrics_router
from app.api.reports import router as reports_router
from app.api import engine as engine_routes
from app.api import fs 
from app.api import network as network_routes
from app.api import network_ws as network_ws_routes
# Importation du nouveau routeur unifié pour les logs
from app.api import logs

logger.info(f"Starting {settings.APP_NAME}... (version: {settings.VERSION})")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# --- CORS ---
origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.on_event("startup")
# def on_startup():
#     """
#     Fonction de démarrage de l'application.
#     """
#     logger.info("Creating database tables (if not exist)...")
    
#     Base.metadata.create_all(bind=db_engine)
#     logger.info("Database ready.")
    
#     start_scheduler()
#     db = SessionLocal()
#     try:
#         for f in db.query(MonitoredFile).filter(MonitoredFile.status == "active").all():
#             sec = FREQ_SECONDS.get(getattr(f, "frequency", "hourly"), 3600)
#             add_interval_job("file", f.id, sec, scan_file, item_id=f.id, path=f.path)
#         for d in db.query(MonitoredFolder).filter(MonitoredFolder.status == "active").all():
#             sec = FREQ_SECONDS.get(getattr(d, "frequency", "hourly"), 3600)
#             add_interval_job("folder", d.id, sec, scan_folder, item_id=d.id, path=d.path)
#         for i in db.query(MonitoredIP).filter(MonitoredIP.status == "active").all():
#             sec = FREQ_SECONDS.get(getattr(i, "frequency", "hourly"), 3600)
#             add_interval_job("ip", i.id, sec, scan_ip, item_id=i.id, ip=i.ip, hostname=i.hostname)
#     finally:
#         db.close()

@app.on_event("startup")
def on_startup():
    """
    Fonction de démarrage de l'application.
    """
    logger.info("Creating database tables (if not exist)...")
    Base.metadata.create_all(bind=db_engine)
    logger.info("Database ready.")
    
    # Démarrer le scheduler d'abord
    start_scheduler()
    logger.info("Scheduler started.")
    
    # Ensuite planifier les jobs
    db = SessionLocal()
    try:
        # Vérifier que le scheduler est actif
        from app.core.scheduler import get_scheduler
        scheduler = get_scheduler()
        if not scheduler.running:
            logger.error("Scheduler is not running!")
            return
            
        logger.info("Scheduling existing monitoring jobs...")
        
        for f in db.query(MonitoredFile).filter(MonitoredFile.status == "active").all():
            sec = FREQ_SECONDS.get(getattr(f, "frequency", "hourly"), 3600)
            add_interval_job("file", f.id, sec, scan_file, item_id=f.id, path=f.path)
            logger.info(f"Scheduled file monitoring: {f.path} (every {sec}s)")
            
        for d in db.query(MonitoredFolder).filter(MonitoredFolder.status == "active").all():
            sec = FREQ_SECONDS.get(getattr(d, "frequency", "hourly"), 3600)
            add_interval_job("folder", d.id, sec, scan_folder, item_id=d.id, path=d.path)
            logger.info(f"Scheduled folder monitoring: {d.path} (every {sec}s)")
            
        for i in db.query(MonitoredIP).filter(MonitoredIP.status == "active").all():
            sec = FREQ_SECONDS.get(getattr(i, "frequency", "hourly"), 3600)
            add_interval_job("ip", i.id, sec, scan_ip, item_id=i.id, ip=i.ip, hostname=i.hostname)
            logger.info(f"Scheduled IP monitoring: {i.ip} (every {sec}s)")
            
        logger.info("All monitoring jobs scheduled successfully.")
        
    except Exception as e:
        logger.error(f"Error during startup job scheduling: {e}")
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
app.include_router(users_router)
app.include_router(monitoring_router)
# Inclus le nouveau routeur unifié pour les logs
app.include_router(logs.router, prefix="/api")
app.include_router(metrics_router)
app.include_router(reports_router)
app.include_router(engine_routes.router)
app.include_router(fs.router)
app.include_router(network_routes.router)
app.include_router(network_ws_routes.router)
