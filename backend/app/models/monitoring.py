# File: backend/app/models/monitoring.py
from pydantic import BaseModel
from typing import Literal, Optional

class MonitoredItemBase(BaseModel):
    path: str
    frequency: Literal["minutely", "hourly", "daily", "weekly"]
    status: Optional[Literal["active", "paused", "stopped"]] = "stopped"

class FileItemCreate(BaseModel):
    path: str
    frequency: Literal["minutely", "hourly", "daily", "weekly"]
    status: Optional[Literal["active", "paused", "stopped"]] = "active"

class FileItemRead(MonitoredItemBase):
    id: int

    class Config:
        orm_mode = True

class FolderItemCreate(BaseModel):
    path: str
    frequency: Literal["minutely", "hourly", "daily", "weekly"]
    status: Optional[Literal["active", "paused", "stopped"]] = "active"

class FolderItemRead(MonitoredItemBase):
    id: int

    class Config:
        orm_mode = True

class IPMonitoredBase(BaseModel):
    ip: str
    hostname: Optional[str]
    frequency: Literal["minutely", "hourly", "daily", "weekly"]
    status: Optional[Literal["active", "paused", "stopped"]] = "stopped"

class IPItemCreate(IPMonitoredBase):
    status: Optional[Literal["active", "paused", "stopped"]] = "active"

class IPItemRead(IPMonitoredBase):
    id: int
    class Config:
        orm_mode = True