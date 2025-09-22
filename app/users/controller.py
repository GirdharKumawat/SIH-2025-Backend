from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Request
from database import users_collection
from app.users.model import UserSignup, UserLogin
from app.utils import get_password_hash, verify_password, create_access_token, verify_token

# Router for user endpoints
user_router = APIRouter()

# ==================== Functions ====================>

def get_current_user(request: Request):
    """
    Get the current user from the request
    """

    # Check for the Authorization header
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

    # Extract the access token
    access_token = authorization.split(" ")[1]

    # Verify the token
    payload = verify_token(access_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    return payload

# ==================== Endpoints ====================>

@user_router.get("/me")
async def get_user(request: Request):
    """
    Get user details endpoint
    """

    # Get the current user
    payload = get_current_user(request)

    # Get the user from the database
    user = users_collection.find_one({"_id": payload["_id"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "username": user["username"],
        "email": user["email"],
        "is_active": user.get("is_active", True),
        "is_verified": user.get("is_verified", False)
    }

@user_router.post("/signup")
async def signup(body: UserSignup):
    """
    User signup endpoint
    """

    # Check if the user already exists
    if users_collection.find_one({"username": body.username}):
        raise HTTPException(status_code=400, detail="Username already exists")
    if users_collection.find_one({"email": body.email}):
        raise HTTPException(status_code=400, detail="Email already exists")

    # Hashed the password
    hashed_password = get_password_hash(body.password)

    # Create the user
    user = users_collection.insert_one({
        "username": body.username,
        "email": body.email,
        "password": hashed_password,
        "is_active": True,
        "is_verified": False,
        "created_at": datetime.now(timezone.utc)
    })

    # Create the access token
    access_token = create_access_token({"_id": str(user.inserted_id), "username": body.username})

    return {
        "token_type": "bearer",
        "access_token": access_token
    }

@user_router.post("/login")
async def login(body: UserLogin):
    """
    User login endpoint
    """

    # Find the user
    user = users_collection.find_one({"username": body.username})
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    # Verify the password
    if not verify_password(body.password, user["password"]):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    # Create the access token
    access_token = create_access_token({"_id": str(user["_id"]), "username": user["username"]})

    return {
        "token_type": "bearer",
        "access_token": access_token
    }
