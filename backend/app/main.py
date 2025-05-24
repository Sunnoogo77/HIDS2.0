from fastapi import FastAPI
from app.core.logging import logger
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.api.status import router as status_router
from app.api.auth import router as auth_router
from app.api.users import router as users_router


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

@app.on_event("shutdown")
def on_shutdown():
    """
    Fonction d'arrêt de l'application.
    """
    logger.info("Shutting down application...")
    
app.include_router(status_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")