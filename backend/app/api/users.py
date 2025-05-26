# File: backend/app/api/users.py
from fastapi import APIRouter, HTTPException, status, Depends
from app.models.user import UserCreate, UserRead
from app.services.user_service import create_user
from app.core.security import get_current_active_user

router = APIRouter(tags=["users"])

@router.post(
    "/users", 
    response_model=UserRead, 
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_active_user)]
)

def create_user_endpoint(
    user_in: UserCreate,
    current_user = Depends(get_current_active_user)
):
    """Creates a new user in the system.
    This endpoint is protected and requires the user to be authenticated.
    Args:
        user_in (UserCreate): The user data to create.
        current_user: The currently authenticated user.
    Returns:
        UserRead: The created user data.
    Raises:
        HTTPException: If the user creation fails.
    """
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Admin privileges required")

    try:
        user = create_user(user_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return user



@router.get("/users/me", response_model=UserRead)
def read_users_me(current_user = Depends(get_current_active_user)):
    """
    Returns the profile of the authenticated user.
    """
    return current_user