# blueprints/database.py
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
import os

MONGODB_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(f"MongoDB connection error: {e}")

db = client["chat_database"]
chat_collection = db["chat_logs"]
users = db["users"]

# Chat log function
def log_chat_to_db(user_message, ai_response):
    chat_collection.insert_one({
        "message": user_message,
        "response": ai_response,
        "timestamp": datetime.utcnow()
    })
