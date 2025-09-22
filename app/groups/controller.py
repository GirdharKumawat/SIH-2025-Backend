from fastapi import APIRouter, Depends
from app.groups.model import GroupCreate
from app.users.controller import get_current_user
from database import groups_collection

# Initialize the router for group endpoints
group_router = APIRouter()

@group_router.post("/")
async def create_group(group: GroupCreate, user: dict = Depends(get_current_user)):
    """
    Create a new group
    """

    # Insert the new group into the database
    groups_collection.insert_one({
        "name": group.name,
        "description": group.description,
        "members": group.members,
        "created_by": user["user_id"]
    })

    return {
        "message": "Group created successfully",
        "group": group.model_dump()
    }
