from datetime import datetime
from bson import ObjectId
from fastapi import APIRouter
from starlette.websockets import WebSocket, WebSocketDisconnect
from app.users.controller import get_current_user
from database import groups_collection, messages_collection
from typing import Dict

# Initialize the router for message endpoints
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
        # Fetch the group details
        group = await groups_collection.find_one({"_id": ObjectId(group_id)})
        if not group:
            return

        # Check if the user is part of the group
        if sender_id not in group["members"]:
            return

        # Store the message in the database
        message = await messages_collection.insert_one({
            "group_id": group_id,
            "sender_id": sender_id,
            "message": message,
            "delivered_to": [sender_id],
            "created_at": datetime.now()
        })

        # Send the message to all active members of the group
        delivered_to = []

        for member_id in group["members"]:
            if member_id in self.active_users and member_id != sender_id:
                # Send the message
                await self.active_users[member_id].send_json({
                    "group_id": group_id,
                    "sender_id": sender_id,
                    "message": message["message"],
                    "created_at": message["created_at"].isoformat()
                })
                delivered_to.append(member_id)

        # Update the message and mark as delivered
        await messages_collection.update_one(
            {"_id": message.inserted_id},
            {"$push": {"delivered_to": {"$each": delivered_to}}}
        )

# Instantiate the connection manager
manager = ConnectionManager()

@message_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time messaging

    Header: Authorization (Bearer <token>)
    Message JSON: {"group_id": str, "message": str}
    """

    # Retrieve the current user from the JWT token
    user_payload = get_current_user(websocket)

    # Connect the user to the WebSocket (Connect)
    await manager.connect(user_payload["_id"], websocket)

    # Check for undelivered messages and send them
    groups = await groups_collection.find({"members": {"$in": [user_payload["_id"]]}})
    groups_id = [str(group["_id"]) for group in groups]

    # Find all pending messages for the user
    pending_messages = await messages_collection.find({
        "group_id": {"$in": groups_id},
        "delivered_to": {"$ne": user_payload["_id"]}
    })

    # Send all pending messages
    async for message in pending_messages:
        # Send the message
        await websocket.send_json({
            "group_id": message["group_id"],
            "sender_id": message["sender_id"],
            "message": message["message"],
            "created_at": message["created_at"].isoformat()
        })

        # Mark the message as delivered
        await messages_collection.update_one(
            {"_id": message["_id"]},
            {"$push": {"delivered_to": user_payload["_id"]}}
        )

    # Listen for incoming messages (Message)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_msg_to_group(data["group_id"], user_payload["_id"], data["message"])

    # Handle disconnection (Disconnect)
    except WebSocketDisconnect:
        manager.disconnect(user_payload["_id"])
