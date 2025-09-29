from fastapi import APIRouter, HTTPException
from database import users_collection ,groups_collection
from bson import ObjectId
from app.hq.model import GroupModel, AddMembersModel
from app.logs.routes import create_log
import os, base64

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
        users_cursor = users_collection.find({"is_verified": False}, {"password": 0})
        users = await users_cursor.to_list(length=None)
        for user in users:
            user["_id"] = str(user["_id"])
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
        user = await users_collection.find_one({"_id": ObjectId(id)})
        await create_log(username="admin", action="VERIFY_USER", target=user["username"]) # username
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
        groups_cursor = groups_collection.find({})
        groups = await groups_cursor.to_list(length=None)

        for group in groups:
            group["_id"] = str(group["_id"])
            members_id_list = group["members"]

            users_cursor = users_collection.find(
                {"_id": {"$in": [ObjectId(member_id) for member_id in members_id_list]}},
                {"password": 0}
            )
            member_details = await users_cursor.to_list(length=None)

            for member in member_details:
                member["_id"] = str(member["_id"])
                
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
        # Generate a new symmetric key
        symmetric_key_bytes = os.urandom(32)

        group_data = group.model_dump()
        group_data["symmetric_key"] = base64.b64encode(symmetric_key_bytes).decode()

        await groups_collection.insert_one(group_data)
        
        await create_log(username="admin", action="CREATE_GROUP", target=group.name)

        return {"message": "Group created successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@hq_router.put("/add-members/{group_id}")
async def add_members_to_group(group_id: str, add_members_data: AddMembersModel):
    """
    Add members to an existing group by group ID
    Expected format: {"members": ["user_id1", "user_id2"]}
    """
    try:
        # Validate group_id format
        if not ObjectId.is_valid(group_id):
            raise HTTPException(status_code=400, detail="Invalid group ID format")
        
        # Check if group exists
        group = await groups_collection.find_one({"_id": ObjectId(group_id)})
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        
        # Validate that all member IDs are valid ObjectIds
        invalid_ids = []
        for member_id in add_members_data.members:
            if not ObjectId.is_valid(member_id):
                invalid_ids.append(member_id)
        
        if invalid_ids:
            raise HTTPException(status_code=400, detail=f"Invalid member IDs: {invalid_ids}")
        
        # Check if users exist
        existing_users = await users_collection.find(
            {"_id": {"$in": [ObjectId(mid) for mid in add_members_data.members]}},
            {"_id": 1}
        ).to_list(length=None)
        
        existing_user_ids = [str(user["_id"]) for user in existing_users]
        non_existing_users = [mid for mid in add_members_data.members if mid not in existing_user_ids]
        
        if non_existing_users:
            raise HTTPException(status_code=400, detail=f"Users not found: {non_existing_users}")
        
        result = await groups_collection.update_one(
            {"_id": ObjectId(group_id)},
            {"$addToSet": {"members": {"$each": add_members_data.members}}}
        )
        group = await groups_collection.find_one({"_id": ObjectId(group_id)})
        await create_log(username="admin", action="ADD_MEMBERS_TO_GROUP", target=group["name"])
        return {
            "message": f"Members added to group {group_id}",
            "added_members": add_members_data.members,
            "members_added_count": len(add_members_data.members)
        }
        
    except HTTPException:
        raise
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

        user = await users_collection.find_one({"_id": ObjectId(member_id)})
        group = await groups_collection.find_one({"_id": ObjectId(group_id)})
        await create_log(username="admin", action="REMOVE_MEMBER_FROM_GROUP", target=f"{user["username"] } from {group["name"]}")
        return {"message": f"Member {member_id} removed from group {group_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@hq_router.delete("/delete-group/{group_id}")
async def delete_group(group_id: str):
    """
    Delete a group by its ID
    """

    try:
        group = await groups_collection.find_one({"_id": ObjectId(group_id)})
        result = await groups_collection.delete_one({"_id":ObjectId(group_id) })
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Group not found")

        
        await create_log(username="admin", action="DELETE_GROUP", target=group["name"])
        return {"message": f"Group {group_id} has been deleted"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
@hq_router.delete("/delete-user/{user_id}")
async def delete_user(user_id: str):
    """
    Delete a user by their ID
    """

    try:
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        result = await users_collection.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="User not found")

        # Also remove the user from any groups they are a member of
        await groups_collection.update_many(
            {"members": user_id},
            {"$pull": {"members": user_id}}
        )

        await create_log(username="admin", action="DELETE_USER", target=user["username"])
        return {"message": f"User {user_id} has been deleted"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
