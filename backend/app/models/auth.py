# File: backend/app/models/auth.py
from pydantic import BaseModel, EmailStr
from typing import Optional


class AuthLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str  # e.g. "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None