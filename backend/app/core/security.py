from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from app.core.config import settings

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
# from app.services.auth_service import  decode_access_token
from app.db.models import User as ORMUser
from app.db.session import SessionLocal

#JWT constant
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 #delais d'expiration du token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT token, embedding 'data' and an expiration.
    
    :param data: Données à inclure dans le token.
    :param expires_delta: Durée d'expiration du token.
    :return: Token JWT.
    """
    #traduire en anglais 
    
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT token, returning the payload or None if invalid.
    
    :param token: Token JWT à décoder.
    :return: Payload du token.
    """
    
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
    except JWTError:
        return None

def get_current_user(token: str = Depends(oauth2_scheme)) -> ORMUser:
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    username = payload["sub"]
    db = SessionLocal()
    user = db.query(ORMUser).filter(ORMUser.username == username).first()
    db.close()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

def get_current_active_user(current_user: ORMUser = Depends(get_current_user)) -> ORMUser:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return current_user