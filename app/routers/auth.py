from fastapi import APIRouter, HTTPException, Depends, Header
from datetime import timedelta
from app.models import User
from app.schemas import UserCreate, UserResponse, Token, UserLogin
from app.utils import verify_password, get_password_hash, create_access_token, verify_token
from app.config import settings

router = APIRouter()

def get_current_user(authorization: str = Header(None)):
    """Get current user from Authorization header"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.split(" ")[1]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    username = payload.get("sub")
    user = User.find_by_username(username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.post("/signup", response_model=UserResponse)
async def signup(user: UserCreate):
    # Check if user exists
    if User.find_by_username(user.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    if User.find_by_email(user.email):
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Create user
    hashed_password = get_password_hash(user.password)
    User.create(user.username, user.email, hashed_password, user.full_name)
    
    # Return user info
    return {
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": True
    }

@router.post("/login", response_model=Token)
async def login(user_login: UserLogin):
    # Find user
    user = User.find_by_username(user_login.username)
    if not user or not verify_password(user_login.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create token
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user = Depends(get_current_user)):
    return {
        "username": current_user["username"],
        "email": current_user["email"],
        "full_name": current_user.get("full_name"),
        "is_active": current_user.get("is_active", True)
    }