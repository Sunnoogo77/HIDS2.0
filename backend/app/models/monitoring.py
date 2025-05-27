# File: backend/app/models/monitoring.py
from pydantic import BaseModel
from typing import Literal, Optional

class MonitoredItemBase(BaseModel):
    path: str
    frequency: Literal["minutely", "hourly", "daily", "weekly"]
    status: Optional[Literal["active", "paused"]] = "active"

class FileItemCreate(BaseModel):
    path: str
    frequency: Literal["minutely", "hourly", "daily", "weekly"]

class FileItemRead(MonitoredItemBase):
    id: int

    class Config:
        orm_mode = True

class FolderItemCreate(BaseModel):
    path: str
    frequency: Literal["minutely", "hourly", "daily", "weekly"]

class FolderItemRead(MonitoredItemBase):
    id: int

    class Config:
        orm_mode = True

class IPItemCreate(BaseModel):
    ip: str
    hostname: Optional[str]
    frequency: Literal["minutely", "hourly", "daily", "weekly"]

class IPItemRead(MonitoredItemBase):
    id: int
    hostname: Optional[str]

    class Config:
        orm_mode = True
