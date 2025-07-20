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

# Database and collections
db = client["chat_database"]

chat_collection = db["chat_logs"]
users = db["users"]
login_tokens = db["login_tokens"]

# Ensure indexes for performance and uniqueness
# Avoids duplicate login tokens and speeds up lookups
login_tokens.create_index([("email", 1), ("code", 1), ("expires_at", 1)])
login_tokens.create_index([("token", 1)], unique=True)
users.create_index("email", unique=True)

# Function for logging chat messages
def log_chat_to_db(user_message, ai_response):
    chat_collection.insert_one({
        "message": user_message,
        "response": ai_response,
        "timestamp": datetime.utcnow()
    })
