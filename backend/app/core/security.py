from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from app.core.config import settings

#JWT constant
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 #delais d'expiration du token

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
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT token, returning the payload or None if invalid.
    
    :param token: Token JWT à décoder.
    :return: Payload du token.
    """
    
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None