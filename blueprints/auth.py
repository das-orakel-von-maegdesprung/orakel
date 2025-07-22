# blueprints/auth.py
from flask import Blueprint, request, jsonify, session, redirect, abort
from functools import wraps
from datetime import datetime, timedelta
import os
import random
import string
import secrets

from utils.database_auth import (
    create_login_token,
    find_valid_token_by_code,
    mark_token_verified,
    ensure_user_exists,
    find_token_record_by_token,
    get_user_data_by_email,
    create_session_token,
    find_valid_session_token,
    revoke_session_token
)

from utils.emailing import send_email  # Make sure you have this module

auth_bp = Blueprint("auth", __name__)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://127.0.0.1:5000")

def generate_code():
    return ''.join(random.choices(string.digits, k=6))

def generate_login_token():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

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

    return jsonify({
        "status": "logged_in",
        "user": {
            "email": user.get("email"),
            "answers": user.get("answers", {}),
            "language": user.get("language", "de")
        }
    })

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

    return jsonify({
        "answers": user.get("answers", {}),
        "language": user.get("language", "de"),
        "email": user.get("email")
    })

@auth_bp.route("/logout", methods=["POST", "GET"])
def logout():
    token = session.get("session_token")
    if token:
        revoke_session_token(token)
    session.clear()
    return redirect('/')
