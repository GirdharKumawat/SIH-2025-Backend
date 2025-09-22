from config import settings
from typing import Optional
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt

def get_password_hash(password: str) -> str:
    """
    Hash the password using bcrypt
    """

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)

    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password
    """

    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict) -> str:
    """
    Create a JWT access token
    """

    payload = data.copy()
    payload.update({ "exp": datetime.now(timezone.utc) + timedelta(minutes=int(settings.access_token_expire_minutes))})

    return jwt.encode(payload, settings.secret_key, algorithm="HS256")

def verify_token(token: str) -> Optional[dict]:
    """
    Verify a JWT token and return the payload if valid, else None
    """

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
