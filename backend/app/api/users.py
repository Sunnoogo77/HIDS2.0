from fastapi import APIRouter, HTTPException, status
from app.models.user import UserCreate, UserRead
from app.services.user_service import create_user

router = APIRouter(tags=["users"])

@router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(user_in: UserCreate):
    try:
        user = create_user(user_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return user
