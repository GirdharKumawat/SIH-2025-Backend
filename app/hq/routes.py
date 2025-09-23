from fastapi import APIRouter, HTTPException
from database import users_collection ,groups_collection
from bson import ObjectId
from app.hq.model import GroupModel, AddMembersModel
hq_router = APIRouter()

# Endpoint to get all users (for HQ purposes)
@hq_router.get("/all-users")
async def get_all_users():
    try:
        users = list(users_collection.find({}, {"_id": 0, "password": 0}))
        return {"users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# endpoint to get user who are not verified
@hq_router.get("/unverified-users")
async def get_unverified_users():
    try:
        users = list(users_collection.find({"is_verified": False}, {"_id": 0, "password": 0}))
        return {"unverified_users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Endpoint to set a user as verified
@hq_router.put("/set-verified/{id}")
async def set_user_verified(id: str):
    print(f"Setting user {id} as verified")
    try:
        result = users_collection.update_one({"_id":ObjectId(id) }, {"$set": {"is_verified": True}})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": f"User {id} has been verified"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Endpoint to get all groups
@hq_router.get("/all-groups")
async def get_all_groups():
    try:
        groups = list(groups_collection.find({}, {"_id": 0}))
        return {"groups": groups}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
# Endpoint to create a new group   
@hq_router.post("/create-group")
async def create_group(group: GroupModel):
    """
    Create a new group with the given name and member IDs.
    """
    print(f"Creating group: {group.dict()}")
    try:
      groups_collection.insert_one(group.dict())
                                    
      return {"message": "Group created successfully", "group": group.dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@hq_router.put("/add-members/{group_id}")
async def add_members_to_group(group_id: str, add_members_data: AddMembersModel):
    """
    Add members to an existing group by group ID.
    """
    print(f"Adding members to group {group_id}: {add_members_data.dict()}")
    try:
        result = groups_collection.update_one(
            {"_id": ObjectId(group_id)},
            {"$addToSet": {"members_id": {"$each": add_members_data.members_id}}} # addToSet to avoid duplicates
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Group not found")
        return {"message": f"Members added to group {group_id}", "added_members": add_members_data.members_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
# deleting group members by id
@hq_router.delete("/delete-member/{group_id}/{member_id}")
async def delete_member_from_group(group_id: str, member_id: str):
    """
    Delete a member from a group by group ID and member ID.
    """
    try:
        result = groups_collection.update_one(
            {"_id": ObjectId(group_id)},
            {"$pull": {"members_id": member_id}} # pull to remove the member
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Group not found")
        return {"message": f"Member {member_id} removed from group {group_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")




