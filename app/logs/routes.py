from database import logs_collection
from fastapi import APIRouter, HTTPException
from bson import ObjectId
from datetime import datetime, timezone
log_router = APIRouter()




@log_router.get("/all-logs")
async def get_all_logs():
    """
    Retrieve all logs from the database
    """

    try:
        logs_cursor = logs_collection.find({})
        logs = await logs_cursor.to_list(length=None)

        for log in logs:
            log["_id"] = str(log["_id"])

        return {"logs": logs}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    
 

async def create_log(username: str, action: str, target: str = None):
    """
    Insert a security log entry into MongoDB.
    
    Args:
        username (str): Who performed the action
        action (str): The action type (LOGIN, SIGNUP, ADD_TO_GROUP, etc.)
        target (str, optional): The object of the action (e.g., group name, user removed)
    """
    log_entry = {
        "username": username,
        "action": action,
        "target": target,
        "timestamp": datetime.now(timezone.utc)
    }
    await logs_collection.insert_one(log_entry)
    