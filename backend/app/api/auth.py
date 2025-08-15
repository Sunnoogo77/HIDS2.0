# File: backend/app/api/auth.py
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.models.auth import AuthLogin, Token
from app.services.auth_service import authenticate_user, generate_user_token

router = APIRouter(tags=["auth"])


@router.post("/auth/login", response_model=Token)
# def login(form_data: AuthLogin):
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate user and return JWT token.
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = generate_user_token(user)
    return {"access_token": access_token, "token_type": "bearer"}