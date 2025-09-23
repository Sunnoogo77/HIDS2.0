# backend/app/models/alerts.py
from pydantic import BaseModel
from typing import Any, Optional, List
from datetime import datetime

class AlertOut(BaseModel):
    id: int | None = None
    ts: datetime | None = None
    severity: str | None = None
    rule: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    entity_label: Optional[str] = None
    message: Optional[str] = None
    meta: Optional[Any] = None
    class Config:
        from_attributes = True

class ActivityOut(BaseModel):
    id: int | None = None
    ts: datetime | None = None
    kind: str | None = None
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    entity_label: Optional[str] = None
    message: Optional[str] = None
    meta: Optional[Any] = None
    class Config:
        from_attributes = True

class PageOut(BaseModel):
    items: List[Any]
    count: int
    total: int
