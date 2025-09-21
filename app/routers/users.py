from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models import User
from app.schemas import UserResponse
from app.routers.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
async def get_users(current_user = Depends(get_current_user)):
    """Get all users"""
    # For prototype, just return a simple list
    # In real app, you'd fetch from database
    return [
        {
            "username": current_user["username"],
            "email": current_user["email"],
            "full_name": current_user.get("full_name"),
            "is_active": True
        }
    ]

@router.get("/{username}", response_model=UserResponse)
async def get_user(username: str, current_user = Depends(get_current_user)):
    """Get user by username"""
    user = User.find_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "username": user["username"],
        "email": user["email"],
        "full_name": user.get("full_name"),
        "is_active": user.get("is_active", True)
    }