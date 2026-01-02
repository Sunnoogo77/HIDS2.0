# app/db/session.py
from typing import Generator
import random
import time
from sqlalchemy import create_engine, event
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL

# Only pass sqlite-specific connect args when using sqlite
url = make_url(DATABASE_URL)
engine_kwargs = {"pool_pre_ping": True}
if url.drivername.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False, "timeout": 30}

engine = create_engine(DATABASE_URL, **engine_kwargs)

if url.drivername.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.close()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a DB session and closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def commit_with_retry(db: Session, retries: int = 3, base_delay: float = 0.1) -> None:
    """Commit helper with exponential backoff for SQLite 'database is locked'."""
    for attempt in range(retries):
        try:
            db.commit()
            return
        except OperationalError as exc:
            if "database is locked" not in str(exc).lower():
                raise
            db.rollback()
            if attempt >= retries - 1:
                raise
            time.sleep(base_delay * (2 ** attempt) + random.uniform(0, base_delay))
