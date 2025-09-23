from fastapi import APIRouter, HTTPException
from database import users_collection ,groups_collection
from bson import ObjectId
from app.hq.model import GroupModel, AddMembersModel

# Router for HQ endpoints
hq_router = APIRouter()

@hq_router.get("/all-users")
async def get_all_users():
    """
    Retrieve all users from the database, excluding their passwords
    """

    try:
        users_cursor = users_collection.find({}, {"password": 0})
        users = await users_cursor.to_list(length=None)

        for user in users:
            user["_id"] = str(user["_id"])

        return {"users": users}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@hq_router.get("/unverified-users")
async def get_unverified_users():
    """
    Retrieve all unverified users from the database, excluding their passwords
    """

    try:
        users_cursor = users_collection.find({"is_verified": False}, {"_id": 0, "password": 0})
        users = await users_cursor.to_list(length=None)

        return {"unverified_users": users}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@hq_router.put("/set-verified/{id}")
async def set_user_verified(id: str):
    """
    Set a user's is_verified status to True by their ID
    """

    try:
        result = await users_collection.update_one({"_id":ObjectId(id) }, {"$set": {"is_verified": True}})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")

        return {"message": f"User {id} has been verified"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@hq_router.get("/all-groups")
async def get_all_groups():
    """
    Retrieve all groups along with their member details.
    """

    groups_data = []
    try:
        groups_cursor = groups_collection.find({}, {"_id": 0})
        groups = await groups_cursor.to_list(length=None)

        for group in groups:
            members_id_list = group["members"]

            users_cursor = users_collection.find(
                {"_id": {"$in": [ObjectId(member_id) for member_id in members_id_list]}},
                {"_id": 0, "password": 0}
            )
            member_details = await users_cursor.to_list(length=None)

            group_info = {
                "_id": group["_id"],
                "name": group["name"],
                "members": member_details
            }
            groups_data.append(group_info)
        
        return {"groups": groups_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
@hq_router.post("/create-group")
async def create_group(group: GroupModel):
    """
    Create a new group with the given name and member IDs
    """

    try:
      await groups_collection.insert_one(group.model_dump())

      return {"message": "Group created successfully", "group": group.model_dump()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@hq_router.put("/add-members/{group_id}")
async def add_members_to_group(group_id: str, add_members_data: AddMembersModel):
    """
    Add members to an existing group by group ID
    """

    try:
        # Handle both 'members' and 'members_id' field names
        members_to_add = add_members_data.members if hasattr(add_members_data, 'members') else add_members_data.members_id

        result = await groups_collection.update_one(
            {"_id": ObjectId(group_id)},
            {"$addToSet": {"members": {"$each": add_members_data.members_id}}}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Group not found")

        return {"message": f"Members added to group {group_id}", "added_members": members_to_add}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
@hq_router.delete("/delete-member/{group_id}/{member_id}")
async def delete_member_from_group(group_id: str, member_id: str):
    """
    Delete a member from a group by group ID and member ID
    """

    try:
        result = await groups_collection.update_one(
            {"_id": ObjectId(group_id)},
            {"$pull": {"members": member_id}}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Group not found")

        return {"message": f"Member {member_id} removed from group {group_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
