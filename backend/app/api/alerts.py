# backend/app/api/alerts.py (stub)
from fastapi import APIRouter, Depends
from app.core.security import get_current_active_user

router = APIRouter(prefix="/alerts", tags=["alerts"], dependencies=[Depends(get_current_active_user)])

@router.get("")
def get_alerts():
    return {"lines": [], "total": 0, "page_count": 1}
