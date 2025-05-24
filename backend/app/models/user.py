from datetime import datetime
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    is_admin: bool = False

class UserRead(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        orm_mode = True
