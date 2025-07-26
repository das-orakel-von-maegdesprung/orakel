from utils.database import get_chat_collection
from datetime import datetime

def log_chat_to_db(user_message, ai_response,email):
    get_chat_collection().insert_one({
        "message": user_message,
        "response": ai_response,
        "email": email,
        "timestamp": datetime.utcnow()
    })