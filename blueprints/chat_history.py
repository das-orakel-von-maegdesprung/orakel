from utils.database import get_chat_history_collection
from datetime import datetime
from flask import jsonify, Blueprint
from bson.objectid import ObjectId
from datetime import datetime

from blueprints.auth import admin_required


logging_bp = Blueprint("logging", __name__)


# @logging_bp.route('/api/chat_logs')
# @admin_required
# def get_chat_logs_api():
#     chat_collection = get_chat_collection()
#     logs = list(chat_collection.find().sort("timestamp", -1))

#     formatted_logs = []
#     for log in logs:
#         formatted_logs.append({
#             "email": log.get("email", ""),
#             "message": log.get("message", ""),
#             "response": log.get("response", ""),
#             "timestamp": log["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
#         })

#     return jsonify(formatted_logs)

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