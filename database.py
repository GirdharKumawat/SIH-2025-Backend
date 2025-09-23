from pymongo import AsyncMongoClient
from config import settings

# MongoDB client setup
client = AsyncMongoClient(settings.database_url)
db = client["chatapp"]

# Collections
users_collection = db.users
groups_collection = db.groups
messages_collection = db.messages
