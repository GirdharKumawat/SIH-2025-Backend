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

    # Delete messages that have been received by all intended recipients
    async def delete_messages_if_all_received(self):
        # Delete messages
        await messages_collection.delete_many({
            "$expr": {"$eq": [{"$size": "$received_by"}, {"$size": "$intended_for"}]}
        })

    # Send a message to a specific group
    async def send_message_to_group(self, group_id: str, sender_id: str, message: str):
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
            "received_by": [sender_id],
            "intended_for": group["members"],
            "created_at": datetime.now()
        }
        msg_insert_result = await messages_collection.insert_one(msg_doc)

        # Send the message to all active members of the group
        received_by = []

        for member_id in group["members"]:
            if member_id in self.active_users and member_id != sender_id:
                # Send the message
                await self.active_users[member_id].send_json({
                    "group_id": group_id,
                    "sender_id": sender_id,
                    "message": message,
                    "created_at": msg_doc["created_at"].isoformat()
                })
                received_by.append(member_id)

        # Mark the message as delivered
        await messages_collection.update_one(
            {"_id": msg_insert_result.inserted_id},
            {"$addToSet": {"received_by": {"$each": received_by}}}
        )

        # Delete messages if all intended recipients have received it
        await self.delete_messages_if_all_received()

    # Check and send undelivered messages to a user
    async def check_undelivered_messages(self, user_id: str):
        # Find the all groups the user is a member of
        group_cursor = groups_collection.find({"members": {"$in": [user_id]}}, {"_id": 1})
        groups = await group_cursor.to_list(length=None)
        group_ids = [str(group["_id"]) for group in groups]

        # Find undelivered messages for the user
        messages_cursor = messages_collection.find(
            {"group_id": {"$in": group_ids}, "received_by": {"$ne": user_id}})
        messages = await messages_cursor.to_list(length=None)

        # Send the undelivered message
        for message in messages:
            await self.active_users[user_id].send_json({
                "group_id": message["group_id"],
                "sender_id": message["sender_id"],
                "message": message["message"],
                "created_at": message["created_at"].isoformat()
            })

        # Mark the messages as delivered
        ids = [message["_id"] for message in messages]
        if ids:
            await messages_collection.update_many(
                {"_id": {"$in": ids}},
                {"$addToSet": {"received_by": user_id}}
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

    # Check and send undelivered messages
    await manager.check_undelivered_messages(user_payload["_id"])

    # Listen for incoming messages (Message)
    try:
        while True:
            data = await websocket.receive_json()
            if not "group_id" in data or not "message" in data:
                continue

            await manager.send_message_to_group(data["group_id"], user_payload["_id"], data["message"])

    # Handle disconnection (Disconnect)
    except WebSocketDisconnect:
        manager.disconnect(user_payload["_id"])
