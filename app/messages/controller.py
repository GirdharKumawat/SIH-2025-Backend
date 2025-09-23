from datetime import datetime
from bson import ObjectId
from fastapi import APIRouter
from starlette.websockets import WebSocket, WebSocketDisconnect
from app.users.controller import get_current_user_from_token
from database import groups_collection, messages_collection
from typing import Dict

# Router for message endpoints
message_router = APIRouter()

class ConnectionManager:
    """
    Manages WebSocket connections for real-time messaging
    """

    # Constructor to initialize the connection manager
    def __init__(self):
        self.active_users: Dict[str, WebSocket] = {}

    # Connect a user to the WebSocket
    async def connect(self, user_id: str, websocket:WebSocket):
        await websocket.accept()
        self.active_users[user_id] = websocket

    # Disconnect a user from the WebSocket
    def disconnect(self, user_id: str):
        self.active_users.pop(user_id, None)

    # Send a message to a specific group
    async def send_msg_to_group(self, group_id: str, sender_id: str, message: str):
        # Find the group in the database
        group = await groups_collection.find_one({"_id": ObjectId(group_id)})
        if not group:
            return

        # Check if the sender is a member of the group
        if sender_id not in group["members"]:
            return

        # Store the message in the database
        msg_doc = {
            "group_id": group_id,
            "sender_id": sender_id,
            "message": message,
            "delivered_to": [sender_id],
            "created_at": datetime.now()
        }
        msg_insert_result = await messages_collection.insert_one(msg_doc)

        # Send the message to all active members of the group
        delivered_to = []

        for member_id in group["members"]:
            if member_id in self.active_users and member_id != sender_id:
                # Send the message
                await self.active_users[member_id].send_json({
                    "group_id": group_id,
                    "sender_id": sender_id,
                    "message": message,
                    "created_at": msg_doc["created_at"].isoformat()
                })
                delivered_to.append(member_id)

        # Mark messages as delivered
        await messages_collection.update_one(
            {"_id": msg_insert_result.inserted_id},
            {"$push": {"delivered_to": {"$each": delivered_to}}}
        )

# Instantiate the connection manager
manager = ConnectionManager()

@message_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str):
    """
    WebSocket endpoint for real-time messaging
    Header: Authorization (Bearer <token>)
    Message JSON: {"group_id": str, "message": str}
    """

    # Retrieve the current user from the JWT token
    user_payload = get_current_user_from_token(token)

    # Connect the user to the WebSocket (Connect)
    await manager.connect(user_payload["_id"], websocket)

    # Check for undelivered messages and send them
    group_cursor = groups_collection.find({"members": {"$in": [user_payload["_id"]]}}, {"_id": 1})
    groups = await group_cursor.to_list(length=None)
    group_ids = [str(group["_id"]) for group in groups]

    messages_cursor = messages_collection.find({"group_id": {"$in": group_ids}, "delivered_to": {"$ne": user_payload["_id"]}})
    messages = await messages_cursor.to_list(length=None)
    for message in messages:
        # Send the undelivered message
        await websocket.send_json({
            "group_id": message["group_id"],
            "sender_id": message["sender_id"],
            "message": message["message"],
            "created_at": message["created_at"].isoformat()
        })

    ids = [message["_id"] for message in messages]
    if ids:
        # Mark messages as delivered
        await messages_collection.update_many(
            {"_id": {"$in": ids}},
            {"$addToSet": {"delivered_to": user_payload["_id"]}}
        )

    # Listen for incoming messages (Message)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.send_msg_to_group(data["group_id"], user_payload["_id"], data["message"])

    # Handle disconnection (Disconnect)
    except WebSocketDisconnect:
        manager.disconnect(user_payload["_id"])
