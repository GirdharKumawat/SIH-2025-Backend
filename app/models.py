from pymongo import MongoClient
from datetime import datetime, timezone
from app.config import settings
from bson import ObjectId








# Simple MongoDB connection
client = MongoClient(settings.database_url)
db = client["chatapp"]

# Collections
users_collection = db.users
groups_collection = db.groups
messages_collection = db.messages

# Simple helper functions for data operations
class User:
    @staticmethod
    def create(username, email, hashed_password, full_name=None):
        user_data = {
            "username": username,
            "email": email,
            "hashed_password": hashed_password,
            "full_name": full_name,
            "is_active": True,
            "is_verified": False,
            "created_at": datetime.now(timezone.utc)
        }
        user = users_collection.find_one({"username": username ,"email": email})
        if user:
            return {"error": "User already exists"}
        result = users_collection.insert_one(user_data)
        return str(result.inserted_id)
    
    @staticmethod
    def update(user_id, update_data):
        
        update_data["updated_at"] = datetime.now(timezone.utc)
        users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
    
    @staticmethod
    def find_by_username(username):
        return users_collection.find_one({"username": username})
    
    @staticmethod
    def find_by_email(email):
        return users_collection.find_one({"email": email})
    
    @staticmethod
    def find_by_id(user_id):
        
        return users_collection.find_one({"_id": ObjectId(user_id)})

class Group:
    @staticmethod
    def create(name, owner_id, description=None):
        group_data = {
            "name": name,
            "description": description,
            "owner_id": owner_id,
            "members": [owner_id],  # Owner is automatically a member
            "created_at": datetime.now(timezone.utc)
        }
        result = groups_collection.insert_one(group_data)
        return str(result.inserted_id)
    
    @staticmethod
    def find_by_id(group_id):
        
        return groups_collection.find_one({"_id": ObjectId(group_id)})
    
    @staticmethod
    def add_member(group_id, user_id):
        
        groups_collection.update_one(
            {"_id": ObjectId(group_id)},
            {"$addToSet": {"members": user_id}}
        )
    
    @staticmethod
    def remove_member(group_id, user_id):
        
        groups_collection.update_one(
            {"_id": ObjectId(group_id)},
            {"$pull": {"members": user_id}}
        )

class Message:
    @staticmethod
    def create(content, sender_id, group_id):
        message_data = {
            "content": content,
            "sender_id": sender_id,
            "group_id": group_id,
            "created_at": datetime.now(timezone.utc)
        }
        result = messages_collection.insert_one(message_data)
        return str(result.inserted_id)
    
    @staticmethod
    def find_by_group(group_id, limit=50):
        return list(messages_collection.find(
            {"group_id": group_id}
        ).sort("created_at", -1).limit(limit))