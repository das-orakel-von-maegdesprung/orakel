from utils.database import get_chat_history_collection
from datetime import datetime
from flask import jsonify, Blueprint
from bson.objectid import ObjectId
from datetime import datetime

from blueprints.auth import admin_required


logging_bp = Blueprint("logging", __name__)

def get_last_chats(email, limit=5):
    chats = (
        get_chat_history_collection()
        .find({"email": email})
        .sort("timestamp", -1)
        .limit(limit)
    )
    return [{"message": c["message"], "response": c["response"]} for c in chats]


def log_chat_to_db(user_message, ai_response,email):
    get_chat_history_collection().insert_one({
        "message": user_message,
        "response": ai_response,
        "email": email,
        "timestamp": datetime.utcnow()
    })
    
    
def delete_old_chats():
    cutoff = datetime.strptime("2025-07-26 12:32:50", "%Y-%m-%d %H:%M:%S")
    result = get_chat_history_collection().delete_many({
        "timestamp": {"$lt": cutoff}
    })
    print(f"Deleted {result.deleted_count} old chat(s).")

def delete_chats_with_message(msg):
    result = get_chat_history_collection().delete_many({"message": msg})
    print(f"Deleted {result.deleted_count} chat(s) where message is '{msg}'.")
delete_chats_with_message("hjhj")


    
def delete_all_chats_for_email(email):
    result = get_chat_history_collection().delete_many({"email": email})
    print(f"Deleted {result.deleted_count} chat(s) for {email}.")


def update_email(old_email, new_email):
    result = get_chat_history_collection().update_many(
        {"email": old_email},
        {"$set": {"email": new_email}}
    )
    print(f"Updated {result.modified_count} chat(s) from {old_email} to {new_email}.")


