# utils/database.py
import pymongo
import pymongo.collection
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
import os
from threading import Lock
import dotenv
dotenv.load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

_client = None
_db = None

_collections_cache = {}
_indexes_created = False
_indexes_lock = Lock()

def get_client():
    global _client
    if _client is None:
        _client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))
        try:
            _client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(f"MongoDB connection error: {e}")
            _client = None
            raise
    return _client

def get_db():
    global _db
    if _db is None:
        client = get_client()
        _db = client["chat_database"]
    return _db



def get_collection(name) -> pymongo.collection.Collection:
    # _ensure_indexes()
    if name not in _collections_cache:
        db = get_db()
        _collections_cache[name] = db[name]
    return _collections_cache[name]

# Specific getters for convenience or future customization

def get_text_collection():
    return get_collection("get_text_collection")

def get_chat_history_collection() -> pymongo.collection.Collection:
    return get_collection("chat_logs")

def get_users_collection():
    return get_collection("users")

def get_books_collection():
    return get_collection("books")

def get_login_tokens_collection():
    return get_collection("login_tokens")

def get_session_tokens_collection():
    return get_collection("session_tokens")

def _ensure_indexes():
    global _indexes_created
    if _indexes_created:
        return
    with _indexes_lock:
        if _indexes_created:
            return
        print("Creating indexes lazily for the first time...")
        get_login_tokens_collection().create_index([("email", 1), ("code", 1), ("expires_at", 1)])
        get_login_tokens_collection().create_index([("token", 1)], unique=True)
        get_users_collection().create_index("email", unique=True)
        # Add any additional indexes here if needed
        _indexes_created = True

# def log_chat_to_db(user_message, ai_response,email):

#     get_chat_collection().insert_one({
#         "message": user_message,
#         "response": ai_response,
#         "email": email,
#         "timestamp": datetime.utcnow()
#     })

def create_login_token(email, code, token, expires_at):
    _ensure_indexes()
    get_login_tokens_collection().insert_one({
        "email": email,
        "code": code,
        "token": token,
        "expires_at": expires_at,
        "verified": False
    })

def find_valid_token_by_code(email, code, now):
    _ensure_indexes()
    return get_login_tokens_collection().find_one({
        "email": email,
        "code": code,
        "expires_at": {"$gt": now}
    })

def mark_token_verified(token_id):
    _ensure_indexes()
    get_login_tokens_collection().update_one({"_id": token_id}, {"$set": {"verified": True}})

def ensure_user_exists(email):
    _ensure_indexes()
    get_users_collection().update_one(
        {"email": email},
        {"$setOnInsert": {"email": email}},
        upsert=True
    )

def find_token_record_by_token(token):
    _ensure_indexes()
    return get_login_tokens_collection().find_one({
        "token": token,
        "expires_at": {"$gt": datetime.utcnow()}
    })

def get_user_data_by_email(email):
    _ensure_indexes()
    return get_users_collection().find_one({"email": email})

def create_session_token(email, token, expires_at):
    _ensure_indexes()
    get_session_tokens_collection().insert_one({
        "email": email,
        "token": token,
        "expires_at": expires_at,
        "revoked": False,
        "created_at": datetime.utcnow()
    })

def find_valid_session_token(token):
    _ensure_indexes()
    now = datetime.utcnow()
    return get_session_tokens_collection().find_one({
        "token": token,
        "revoked": False,
        "expires_at": {"$gt": now}
    })

def revoke_session_token(token):
    _ensure_indexes()
    get_session_tokens_collection().update_one(
        {"token": token},
        {"$set": {"revoked": True}}
    )
