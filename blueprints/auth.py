# blueprints/auth.py
from flask import Blueprint, request, jsonify, session, redirect, abort
from functools import wraps
from datetime import datetime, timedelta
import os
import random
import string
import secrets
from utils.emailing import send_email  # Make sure you have this module
from datetime import datetime
from utils.database import (
    get_login_tokens_collection,
    get_session_tokens_collection,
    get_users_collection,
)
from utils.globals import Role


auth_bp = Blueprint("auth", __name__)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://127.0.0.1:5000")


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = session.get("session_token")
        record = find_valid_session_token(token)
        if not record:
            session.clear()
            abort(401)
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = session.get("session_token")
        record = find_valid_session_token(token)
        if not record:
            session.clear()
            abort(401)  # Unauthorized

        email = record.get("email")
        user = get_user_data_by_email(email)
        if not user or user.get("role") != "admin":
            abort(403)  # Forbidden

        return f(*args, **kwargs)

    return decorated_function


def create_login_token(email, code, token, expires_at):
    get_login_tokens_collection().insert_one(
        {
            "email": email,
            "code": code,
            "token": token,
            "expires_at": expires_at,
            "verified": False,
        }
    )


def find_valid_token_by_code(email, code, now):
    return get_login_tokens_collection().find_one(
        {"email": email, "code": code, "expires_at": {"$gt": now}}
    )


def mark_token_verified(token_id):
    get_login_tokens_collection().update_one(
        {"_id": token_id}, {"$set": {"verified": True}}
    )


def ensure_user_exists(email):
    get_users_collection().update_one(
        {"email": email}, {"$setOnInsert": {"email": email}}, upsert=True
    )


def find_token_record_by_token(token):
    return get_login_tokens_collection().find_one(
        {"token": token, "expires_at": {"$gt": datetime.utcnow()}}
    )


def get_user_data_by_email(email):
    return get_users_collection().find_one({"email": email})


def create_session_token(email, token, expires_at):
    get_session_tokens_collection().insert_one(
        {
            "email": email,
            "token": token,
            "expires_at": expires_at,
            "revoked": False,
            "created_at": datetime.utcnow(),
        }
    )


def find_valid_session_token(token):
    now = datetime.utcnow()
    return get_session_tokens_collection().find_one(
        {"token": token, "revoked": False, "expires_at": {"$gt": now}}
    )


def revoke_session_token(token):
    get_session_tokens_collection().update_one(
        {"token": token}, {"$set": {"revoked": True}}
    )

def generate_code():
    return "".join(random.choices(string.digits, k=6))


def generate_login_token():
    return "".join(random.choices(string.ascii_letters + string.digits, k=32))


def generate_secure_token():
    return secrets.token_urlsafe(32)


@auth_bp.route("/session-data", methods=["GET"])
def session_status():
    token = session.get("session_token")
    record = find_valid_session_token(token)

    if not record:
        return jsonify({"status": "not_logged_in"})

    email = record["email"]
    user = get_user_data_by_email(email)
    if not user:
        return jsonify({"status": "not_logged_in"})

    return jsonify(
        {
            "status": "logged_in",
            "user": {
                "email": user.get("email"),
                "answers": user.get("answers", {}),
                "language": user.get("language", "de"),
            },
        }
    )


@auth_bp.route("/request-login", methods=["POST"])
def request_login():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    code = generate_code()
    login_token = generate_login_token()
    expires_at = datetime.utcnow() + timedelta(minutes=10)

    create_login_token(email, code, login_token, expires_at)

    magic_link = f"{FRONTEND_URL}/magic-login/{login_token}"
    subject = "🔐 Login Code Orakel von Mägdesprung"
    body = f"""
Hello,

Your login code is: {code}    

Or click the magic login link to sign in directly:
{magic_link}

This code and link expire in 10 minutes.
"""

    send_email(subject, body, email)
    return jsonify({"status": "sent"})


@auth_bp.route("/verify-code", methods=["POST"])
def verify_code():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    code = data.get("code", "").strip()

    record = find_valid_token_by_code(email, code, datetime.utcnow())
    if not record:
        return jsonify({"status": "not_logged_in"})

    mark_token_verified(record["_id"])
    ensure_user_exists(email)

    session_token = generate_secure_token()
    expires_at = datetime.utcnow() + timedelta(days=7)
    create_session_token(email, session_token, expires_at)

    session["session_token"] = session_token
    session.permanent = True

    return jsonify({"status": "logged_in"})


@auth_bp.route("/magic-login/<token>")
def magic_login(token):
    record = find_token_record_by_token(token)
    if not record:
        return "Invalid or expired link.", 400

    email = record["email"]
    ensure_user_exists(email)

    session_token = generate_secure_token()
    expires_at = datetime.utcnow() + timedelta(days=7)
    create_session_token(email, session_token, expires_at)

    session["session_token"] = session_token
    session.permanent = True

    return redirect("/")


@auth_bp.route("/get-user-data")
@login_required
def get_user_data():
    token = session.get("session_token")
    record = find_valid_session_token(token)
    if not record:
        session.clear()
        return jsonify({})

    email = record["email"]
    user = get_user_data_by_email(email)
    if not user:
        return jsonify({})

    return jsonify(
        {
            "answers": user.get("answers", {}),
            "language": user.get("language", "de"),
            "email": user.get("email"),
        }
    )


@auth_bp.route("/logout", methods=["POST", "GET"])
def logout():
    token = session.get("session_token")
    if token:
        revoke_session_token(token)
    session.clear()
    return redirect("/")


def _set_user_role(email, role: Role):
    if role not in Role.ROLES:
        raise ValueError("Invalid role")
    get_users_collection().update_one(
        {"email": email}, {"$set": {"role": role}}, upsert=True
    )


@auth_bp.route("/api/user/set-role", methods=["POST"])
@admin_required
def set_user_role():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    role = data.get("role", "").strip().lower()

    if role not in ["admin", "user"]:
        return jsonify({"status": "error", "message": "Invalid role"}), 400

    _set_user_role(email, role)
    return jsonify({"status": "success", "message": f"Role of {email} set to {role}."})
@auth_bp.route("/api/users/list")
@admin_required
def list_users():
    users = list(get_users_collection().find({}, {"_id": 0}))
    login_tokens = list(get_login_tokens_collection().find({}, {"_id": 0}))
    
    # Map email to verified status from login tokens
    verified_status = {}
    for token in login_tokens:
        if token.get("verified"):
            verified_status[token["email"]] = True

    for user in users:
        user["verified"] = verified_status.get(user["email"], False)

    return jsonify({"users": users})
