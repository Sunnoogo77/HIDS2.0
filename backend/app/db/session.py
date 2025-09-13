# # app/db/session.py
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from app.core.config import settings

# engine = create_engine(
#     settings.DATABASE_URL, 
#     connect_args={"check_same_thread": False}
# )
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# app/db/session.py
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL

# Only pass sqlite-specific connect args when using sqlite
url = make_url(DATABASE_URL)
engine_kwargs = {"pool_pre_ping": True}
if url.drivername.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_kwargs)

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
