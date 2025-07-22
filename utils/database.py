from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
import os
from threading import Lock

MONGODB_URI = os.getenv("MONGODB_URI")

_client = None
_db = None

_chat_collection = None
_users_collection = None
_books_collection = None
_login_tokens_collection = None
_session_tokens_collection = None

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

def get_chat_collection():
    global _chat_collection
    if _chat_collection is None:
        db = get_db()
        _chat_collection = db["chat_logs"]
    return _chat_collection

def get_users_collection():
    global _users_collection
    if _users_collection is None:
        db = get_db()
        _users_collection = db["users"]
    return _users_collection

def get_books_collection():
    global _books_collection
    if _books_collection is None:
        db = get_db()
        _books_collection = db["books"]
    return _books_collection

def get_login_tokens_collection():
    global _login_tokens_collection
    if _login_tokens_collection is None:
        db = get_db()
        _login_tokens_collection = db["login_tokens"]
    return _login_tokens_collection

def get_session_tokens_collection():
    global _session_tokens_collection
    if _session_tokens_collection is None:
        db = get_db()
        _session_tokens_collection = db["session_tokens"]
    return _session_tokens_collection

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

def log_chat_to_db(user_message, ai_response):
    _ensure_indexes()
    get_chat_collection().insert_one({
        "message": user_message,
        "response": ai_response,
        "timestamp": datetime.utcnow()
    })

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
