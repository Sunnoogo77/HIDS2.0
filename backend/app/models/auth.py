# File: backend/app/models/auth.py
from pydantic import BaseModel, EmailStr
from typing import Optional


class AuthLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str  # e.g. "bearer"


class TokenData(BaseModel):
    email: Optional[EmailStr] = None