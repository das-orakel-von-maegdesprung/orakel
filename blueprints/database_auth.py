# blueprints/database_auth.py
from datetime import datetime
from blueprints.database import db
from blueprints.database import users

login_tokens = db["login_tokens"]

session_tokens = db["session_tokens"]

# Ensure indexes
login_tokens.create_index([("email", 1), ("code", 1), ("expires_at", 1)])
login_tokens.create_index([("token", 1)], unique=True)
users.create_index("email", unique=True)

def create_login_token(email, code, token, expires_at):
    login_tokens.insert_one({
        "email": email,
        "code": code,
        "token": token,
        "expires_at": expires_at,
        "verified": False
    })

def find_valid_token_by_code(email, code, now):
    return login_tokens.find_one({
        "email": email,
        "code": code,
        "expires_at": {"$gt": now}
    })

def mark_token_verified(token_id):
    login_tokens.update_one({"_id": token_id}, {"$set": {"verified": True}})

def ensure_user_exists(email):
    users.update_one({"email": email}, {"$setOnInsert": {"email": email}}, upsert=True)

def find_token_record_by_token(token):
    return login_tokens.find_one({
        "token": token,
        "expires_at": {"$gt": datetime.utcnow()}
    })

def get_user_data_by_email(email):
    return users.find_one({"email": email})

def create_session_token(email, token, expires_at):
    session_tokens.insert_one({
        "email": email,
        "token": token,
        "expires_at": expires_at,
        "revoked": False,
        "created_at": datetime.utcnow()
    })

def find_valid_session_token(token):
    now = datetime.utcnow()
    return session_tokens.find_one({
        "token": token,
        "revoked": False,
        "expires_at": {"$gt": now}
    })

def revoke_session_token(token):
    session_tokens.update_one(
        {"token": token},
        {"$set": {"revoked": True}}
    )
