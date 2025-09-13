# File: backend/app/db/models.py
import enum
from sqlalchemy import Column, String, Boolean, Integer, DateTime, Enum, JSON
from sqlalchemy.sql import func
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id             = Column(Integer, primary_key=True, index=True)
    username       = Column(String, unique=True, index=True, nullable=False)
    email          = Column(String, unique=True, index=True, nullable=False)
    password_hash  = Column(String, nullable=False)
    is_active      = Column(Boolean, default=True, nullable=False)
    is_admin       = Column(Boolean, default=False, nullable=False)
    created_at     = Column(DateTime(timezone=True), server_default=func.now())
    updated_at     = Column(DateTime(timezone=True), onupdate=func.now())

class FrequencyEnum(str, enum.Enum):
    minutely = "minutely"
    hourly   = "hourly"
    daily    = "daily"
    weekly   = "weekly"

class StatusEnum(str, enum.Enum):
    active = "active"
    paused = "paused"

class MonitoredFile(Base):
    __tablename__ = "monitored_files"

    id              = Column(Integer, primary_key=True, index=True)
    path            = Column(String, unique=True, nullable=False)
    frequency       = Column(
        Enum(FrequencyEnum, name="frequency_enum"),
        default=FrequencyEnum.hourly,
        nullable=False
    )
    status          = Column(
        Enum(StatusEnum, name="status_enum"),
        default=StatusEnum.active,
        nullable=False
    )
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    updated_at      = Column(DateTime(timezone=True), onupdate=func.now())

class MonitoredFolder(Base):
    __tablename__ = "monitored_folders"

    id              = Column(Integer, primary_key=True, index=True)
    path            = Column(String, unique=True, nullable=False)
    frequency       = Column(
        Enum(FrequencyEnum, name="frequency_enum"),
        default=FrequencyEnum.hourly,
        nullable=False
    )
    status          = Column(
        Enum(StatusEnum, name="status_enum"),
        default=StatusEnum.active,
        nullable=False
    )
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    updated_at      = Column(DateTime(timezone=True), onupdate=func.now())

class MonitoredIP(Base):
    __tablename__ = "monitored_ips"

    id              = Column(Integer, primary_key=True, index=True)
    ip              = Column(String, unique=True, nullable=False)
    hostname        = Column(String, nullable=True)
    frequency       = Column(
        Enum(FrequencyEnum, name="frequency_enum"),
        default=FrequencyEnum.hourly,
        nullable=False
    )
    status          = Column(
        Enum(StatusEnum, name="status_enum"),
        default=StatusEnum.active,
        nullable=False
    )
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    updated_at      = Column(DateTime(timezone=True), onupdate=func.now())