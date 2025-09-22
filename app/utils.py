from config import settings
from typing import Optional
import bcrypt
import jwt
import datetime

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
    payload.update({ "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.access_token_expire_minutes) })

    token = jwt.encode(payload, settings.secret_key)

    return token

def verify_token(token: str) -> Optional[dict]:
    """
    Verify a JWT token and return the payload if valid, else None
    """

    try:
        payload = jwt.decode(token, settings.secret_key)
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
