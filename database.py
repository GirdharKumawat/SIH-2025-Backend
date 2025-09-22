from pymongo import MongoClient
from config import settings

# MongoDB client setup
client = MongoClient(settings.database_url)
db = client["chatapp"]

# Collections
users_collection = db.users
groups_collection = db.groups
messages_collection = db.messages
