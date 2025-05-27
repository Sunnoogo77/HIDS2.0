# File: backend/app/api/users.py
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List

from app.models.user import UserCreate, UserRead
from app.services.user_service import (
    create_user, 
    get_users, 
    get_user, 
    update_user, 
    delete_user, 
    change_user_password
)
from app.core.security import get_current_active_user

router = APIRouter(prefix="/api", tags=["users"])

# Admin-only decorator
def admin_only(current_user=Depends(get_current_active_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

@router.post(
    "/users",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(admin_only)]
)
def create_user_endpoint(user_in: UserCreate):
    """Create a new user (admin only)."""
    try:
        return create_user(user_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get(
    "/users",
    response_model=List[UserRead],
    dependencies=[Depends(admin_only)]
)
def list_users():
    """List all users (admin only)."""
    return get_users()

@router.get(
    "/users/{user_id}",
    response_model=UserRead,
    dependencies=[Depends(admin_only)]
)
def read_user(user_id: int):
    """Get a single user by ID (admin only)."""
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put(
    "/users/{user_id}",
    response_model=UserRead,
    dependencies=[Depends(admin_only)]
)
def update_user_endpoint(user_id: int, user_in: UserCreate):
    """Update a user’s email/role/status (admin only)."""
    user = update_user(user_id, user_in)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put(
    "/users/{user_id}/password",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_active_user)]
)
def change_password_endpoint(user_id: int, new_password: str):
    """
    Change a user’s password.
    - Admins can change anyone’s password.
    - Users can only change their own.
    """
    current = get_current_active_user()
    if not (current.is_admin or current.id == user_id):
        raise HTTPException(status_code=403, detail="Not allowed")
    if not change_user_password(user_id, new_password):
        raise HTTPException(status_code=404, detail="User not found")

@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(admin_only)]
)
def delete_user_endpoint(user_id: int):
    """Delete a user (admin only)."""
    if not delete_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")

@router.get("/users/me", response_model=UserRead)
def read_users_me(current_user=Depends(get_current_active_user)):
    """Profile of the authenticated user."""
    return current_user
