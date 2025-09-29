from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Request
from database import users_collection ,groups_collection
from app.users.model import UserSignup, UserLogin
from app.utils import get_password_hash, verify_password, create_access_token, verify_token
from app.logs.routes import create_log
# Router for user endpoints
user_router = APIRouter()

# ==================== Functions ====================>

def get_current_user_from_token(access_token: str):
    """
    Get the current user from the access token
    """

    # Verify the access token
    payload = verify_token(access_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    return payload

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

    # Retrieve the user from the token
    return get_current_user_from_token(access_token)

# ==================== Endpoints ====================>

@user_router.get("/me")
async def get_user(request: Request):
    """
    Get user details endpoint
    """

    # Get the current user
    payload = get_current_user(request)

    # Get the user from the database
    user = await users_collection.find_one({"_id": ObjectId(payload["_id"])})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "_id": str(user["_id"]),
        "role": user["role"],
        "username": user["username"],
        "email": user["email"],
        "is_active": user["is_active"],
        "is_verified": user["is_verified"]
    }

@user_router.post("/signup")
async def signup(body: UserSignup):
    """
    User signup endpoint
    """

    # Check if the user already exists
    if await users_collection.find_one({"username": body.username}):
        raise HTTPException(status_code=400, detail="Username already exists")
    if await users_collection.find_one({"email": body.email}):
        raise HTTPException(status_code=400, detail="Email already exists")

    # Hashed the password
    hashed_password = get_password_hash(body.password)

    # Create the user
    user = await users_collection.insert_one({
        "role": "user",
        "username": body.username,
        "email": body.email,
        "password": hashed_password,
        "is_active": True,
        "is_verified": False,
        "created_at": datetime.now(timezone.utc)
    })

    # Create the access token
    access_token = create_access_token({
        "_id": str(user.inserted_id),
        "role": "user",
        "username": body.username,
        "email": body.email
    })
    await create_log(username=body.username, action="SIGNUP")
    return {
        "message": "User created successfully",
        "token_type": "bearer",
        "access_token": access_token
    }

@user_router.post("/login")
async def login(body: UserLogin):
    """
    User login endpoint
    """

    # Find the user
    user = await users_collection.find_one({"username": body.username})
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    # Verify the password
    if not verify_password(body.password, user["password"]):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    # Create the access token
    access_token = create_access_token({
        "_id": str(user["_id"]),
        "role": user["role"],
        "username": user["username"],
        "email": user["email"]
    })
    
    await create_log(username=user["username"], action="LOGIN")

    return {
        "message": "User logged in successfully",
        "token_type": "bearer",
        "access_token": access_token
    }

@user_router.get("/user-groups")
async def get_user_groups(request: Request):
    """
    Get groups of the current user
    """

    # Get the current user
    payload = get_current_user(request)

    try:
        user = await users_collection.find_one({"_id": ObjectId(payload["_id"])})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        groups_cursor = groups_collection.find({"members": str(user["_id"])})
        groups = await groups_cursor.to_list(length=None)

        for group in groups:    
            group["_id"] = str(group["_id"])
        
            # member id and neme/username with group
        groups_with_members = []
        
        for group in groups:
            members_id_list = group["members"]

            users_cursor = users_collection.find(
                {"_id": {"$in": [ObjectId(member_id) for member_id in members_id_list]}},
                {"password": 0,"role":0,"email":0,"is_active":0,"is_verified":0,"created_at":0}
            )
            member_details = await users_cursor.to_list(length=None)

            for member in member_details:
                member["_id"] = str(member["_id"])
            
            group_info = {
                "_id": group["_id"],
                "name": group["name"],
                "members": member_details
            }
            groups_with_members.append(group_info)
        

        return {"groups": groups_with_members}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")