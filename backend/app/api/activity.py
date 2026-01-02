from fastapi import APIRouter

router = APIRouter(prefix="/activity", tags=["activity"])

@router.get("")
def get_activity_logs():
    return {"lines": [], "total": 0, "page_count": 1}
