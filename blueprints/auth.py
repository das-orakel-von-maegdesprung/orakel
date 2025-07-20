from flask import Blueprint, request, jsonify, session, redirect
from blueprints.database import users, login_tokens
from emails import send_email
from datetime import datetime, timedelta
import os
import random
import string

auth_bp = Blueprint("auth", __name__)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://127.0.0.1:5000")

def generate_code():
    return ''.join(random.choices(string.digits, k=6))

def generate_token():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

@auth_bp.route("/request-login", methods=["POST"])
def request_login():
    data = request.get_json()
    email = data.get("email", "").strip().lower()

    code = generate_code()
    token = generate_token()
    expires_at = datetime.utcnow() + timedelta(minutes=10)

    login_tokens.insert_one({
        "email": email,
        "code": code,
        "token": token,
        "expires_at": expires_at,
        "verified": False
    })

    magic_link = f"{FRONTEND_URL}/magic-login/{token}"

    subject = "🔐 Your Login Code for Das Orakel"
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

    record = login_tokens.find_one({
        "email": email,
        "code": code,
        "expires_at": {"$gt": datetime.utcnow()}
    })

    if not record:
        return jsonify({"error": "Invalid or expired code"}), 400

    login_tokens.update_one({"_id": record["_id"]}, {"$set": {"verified": True}})
    users.update_one({"email": email}, {"$setOnInsert": {"email": email}}, upsert=True)

    session["email"] = email
    session.permanent = True

    return jsonify({"status": "logged_in"})


@auth_bp.route("/magic-login/<token>")
def magic_login(token):
    record = login_tokens.find_one({
        "token": token,
        "expires_at": {"$gt": datetime.utcnow()}
    })

    if not record:
        return "Invalid or expired link.", 400

    session["email"] = record["email"]
    session.permanent = True

    return redirect("/")


@auth_bp.route("/get-user-data")
def get_user_data():
    email = session.get("email")
    if not email:
        return jsonify({})

    user = users.find_one({"email": email})
    if not user:
        return jsonify({})

    return jsonify({
        "answers": user.get("answers", {}),
        "language": user.get("language", "de"),
        "email": user.get("email")
    })
