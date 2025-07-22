# blueprints/database_auth.py
from datetime import datetime
from utils.database import get_login_tokens_collection ,get_session_tokens_collection, get_users_collection
# from blueprints.database import users

# Ensure indexes
# login_tokens.create_index([("email", 1), ("code", 1), ("expires_at", 1)])
# login_tokens.create_index([("token", 1)], unique=True)
# users.create_index("email", unique=True)

def create_login_token(email, code, token, expires_at):
    get_login_tokens_collection().insert_one({
        "email": email,
        "code": code,
        "token": token,
        "expires_at": expires_at,
        "verified": False
    })

def find_valid_token_by_code(email, code, now):
    return get_login_tokens_collection().find_one({
        "email": email,
        "code": code,
        "expires_at": {"$gt": now}
    })

def mark_token_verified(token_id):
    get_login_tokens_collection().update_one({"_id": token_id}, {"$set": {"verified": True}})

def ensure_user_exists(email):
    get_users_collection().update_one({"email": email}, {"$setOnInsert": {"email": email}}, upsert=True)

def find_token_record_by_token(token):
    return get_login_tokens_collection().find_one({
        "token": token,
        "expires_at": {"$gt": datetime.utcnow()}
    })

def get_user_data_by_email(email):
    return get_users_collection().find_one({"email": email})

def create_session_token(email, token, expires_at):
    get_session_tokens_collection().insert_one({
        "email": email,
        "token": token,
        "expires_at": expires_at,
        "revoked": False,
        "created_at": datetime.utcnow()
    })

def find_valid_session_token(token):
    now = datetime.utcnow()
    return get_session_tokens_collection().find_one({
        "token": token,
        "revoked": False,
        "expires_at": {"$gt": now}
    })

def revoke_session_token(token):
    get_session_tokens_collection().update_one(
        {"token": token},
        {"$set": {"revoked": True}}
    )
