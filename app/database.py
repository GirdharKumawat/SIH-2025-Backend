from pymongo import MongoClient
from app.config import settings

# Simple MongoDB connection
client = None
db = None

 
def connect_to_mongo():
    global client, db
    client = MongoClient(settings.database_url)
    db = client["chatapp"]
    

def get_database():
    return db
