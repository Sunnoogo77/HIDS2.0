# File: backend/app/services/auth_service.py
from passlib.context import CryptContext
from app.db.session import SessionLocal
# Import your ORM User model once defined
from app.db.models import User as ORMUser
from app.core.security import create_access_token
from datetime import timedelta
from typing import Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str):
    """
    Stub: query the database for user, verify password.
    Replace ORMUser import and logic when your User model is ready.
    """
    db = SessionLocal()
    user = db.query(ORMUser).filter(ORMUser.username == username).first()
    db.close()
    
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


def generate_user_token(user, expires_minutes: Optional[int] = None) -> str:
    # Correction: Ajoutez le statut is_admin au dictionnaire 'data'
    data = {"sub": user.username, "is_admin": user.is_admin}
    # print(data)  # Debug: Affichez les données du token
    expire_delta = timedelta(minutes=expires_minutes) if expires_minutes else None
    return create_access_token(data=data, expires_delta=expire_delta)
