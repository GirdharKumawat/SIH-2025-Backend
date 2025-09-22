from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Header
from database import users_collection
from app.users.model import UserSignup, UserLogin
from app.utils import get_password_hash, verify_password, create_access_token, verify_token

# Router for user endpoints
user_router = APIRouter()

@user_router.get("/me")
async def get_user(authorization: str = Header(None)):
    """
    Get user details endpoint
    """

    # Extract and verify the token
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

    access_token = authorization.split(" ")[1]

    # Verify the token
    payload = verify_token(access_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Get the user from the database
    user = users_collection.find_one({"username": payload.get("id")})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "username": user["username"],
        "email": user["email"],
        "is_active": user.get("is_active", True),
        "is_verified": user.get("is_verified", False)
    }

@user_router.post("/signup")
async def signup(user: UserSignup):
    """
    User signup endpoint
    """

    # Check if the user already exists
    if users_collection.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already exists")
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already exists")

    # Hashed the password
    hashed_password = get_password_hash(user.password)

    # Create the user
    users_collection.insert_one({
        "username": user.username,
        "email": user.email,
        "password": hashed_password,
        "is_active": True,
        "is_verified": False,
        "created_at": datetime.now(timezone.utc)
    })

    # Create the access token
    access_token = create_access_token({"id": user.username})

    return {
        "token_type": "bearer",
        "access_token": access_token
    }

@user_router.post("/login")
async def login(user: UserLogin):
    """
    User login endpoint
    """

    # Find the user
    db_user = users_collection.find_one({"username": user.username})
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    # Verify the password
    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    # Create the access token
    access_token = create_access_token({"id": db_user["username"]})

    return {
        "token_type": "bearer",
        "access_token": access_token
    }
