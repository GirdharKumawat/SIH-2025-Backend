from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models import Group, Message
from app.schemas import GroupCreate, GroupResponse, MessageCreate, MessageResponse
from app.routers.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=GroupResponse)
async def create_group(group: GroupCreate, current_user = Depends(get_current_user)):
    """Create a new group"""
    user_id = str(current_user["_id"])
    
    Group.create(group.name, user_id, group.description)
    
    return {
        "name": group.name,
        "description": group.description,
        "owner_id": user_id
    }

@router.get("/", response_model=List[GroupResponse])
async def get_groups(current_user = Depends(get_current_user)):
    """Get user's groups"""
    # For prototype, return empty list or mock data
    return []

@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(group_id: str, current_user = Depends(get_current_user)):
    """Get group by ID"""
    group = Group.find_by_id(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    return {
        "name": group["name"],
        "description": group.get("description"),
        "owner_id": group["owner_id"]
    }

@router.post("/{group_id}/join")
async def join_group(group_id: str, current_user = Depends(get_current_user)):
    """Join a group"""
    user_id = str(current_user["_id"])
    
    Group.add_member(group_id, user_id)
    return {"message": "Joined group successfully"}

@router.post("/{group_id}/messages", response_model=MessageResponse)
async def send_message(group_id: str, message: MessageCreate, current_user = Depends(get_current_user)):
    """Send message to group"""
    user_id = str(current_user["_id"])
    
    Message.create(message.content, user_id, group_id)
    
    return {
        "content": message.content,
        "sender_id": user_id,
        "group_id": group_id
    }

@router.get("/{group_id}/messages", response_model=List[MessageResponse])
async def get_messages(group_id: str, current_user = Depends(get_current_user)):
    """Get group messages"""
    messages = Message.find_by_group(group_id)
    
    return [
        {
            "content": msg["content"],
            "sender_id": msg["sender_id"],
            "group_id": msg["group_id"]
        }
        for msg in messages
    ]