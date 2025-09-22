from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime
from typing import Optional
from config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """
    Hash the password using bcrypt
    """

    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password
    """

    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    """
    Create a JWT access token
    """

    payload = data.copy()
    payload.update({ "exp": datetime.utcnow() + settings.access_token_expire_minutes })

    token = jwt.encode(payload, settings.secret_key)

    return token

def verify_token(token: str) -> Optional[dict]:
    """
    Verify a JWT token and return the payload if valid, else None
    """

    try:
        payload = jwt.decode(token, settings.secret_key)
        return payload
    except JWTError:
        return None
