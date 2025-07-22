from flask import session, Blueprint, jsonify, request
from utils.database_auth import find_valid_session_token
from utils.database import get_users_collection
from utils.database import log_chat_to_db
from utils.ai import GroqChat
import json

orakel_bp = Blueprint("orakel", __name__)


# --- Step 1: Authentication ---
def validate_session():
    session_token = session.get("session_token")
    if not session_token:
        return None, jsonify({"error": "Not authenticated"}), 401

    record = find_valid_session_token(session_token)
    if not record:
        return None, jsonify({"error": "Invalid session token"}), 401

    return record["email"], None, None


# --- Step 2: Load User Data ---
def get_user_profile(email):
    user_data = get_users_collection().find_one({"email": email}, {"answers": 1, "language": 1})
    answers = user_data.get("answers", {})
    language = user_data.get("language", "de")
    return answers, language


# --- Step 3: Extract Input ---
def extract_user_input():
    data = request.get_json()
    return data.get("message", "")


# --- Step 4: Decide if LLM Needs a Book ---
def check_if_needs_book(user_input):
    decision_prompt = f"""
Given the following user message, determine if it can be answered without consulting an external book or source.

Respond only in JSON format like this:
{{"needs_book": true}} or {{"needs_book": false}}

User message:
\"\"\"{user_input}\"\"\"
"""
    decision_response = GroqChat.response_text(decision_prompt)

    try:
        decision_json = json.loads(decision_response)
        return decision_json.get("needs_book", False), None
    except json.JSONDecodeError:
        return False, jsonify({
            "error": "Invalid response from AI decision phase",
            "raw": decision_response
        }), 500


# --- Step 5: Build Prompt with Profile ---
def build_full_prompt(user_input, answers, language):
    with open("orakel_base_prompt.txt", "r", encoding="utf-8") as f:
        base_prompt = f.read()

    return f"""{base_prompt}

User message: {user_input}

User profile:
{answers}

Respond in the user's preferred language: {language}
"""


# --- Step 6: Generate Final AI Response ---
def generate_response(prompt):
    return GroqChat.response_text(prompt)



# --- Main Route ---
@orakel_bp.route("/orakel", methods=["POST"])
def orakel():
    try:
        # Step 1: Session Validation
        email, error_response, status = validate_session()
        if error_response:
            return error_response, status

        # Step 2: Get user answers & language
        answers, language = get_user_profile(email)

        # Step 3: Get user input
        user_input = extract_user_input()

        # Step 4: Ask if book is needed
        needs_book, error_response = check_if_needs_book(user_input)
        if error_response:
            return error_response
        if needs_book:
            return jsonify({"response": "book"})

        # Step 5: Build full prompt
        full_prompt = build_full_prompt(user_input, answers, language)

        # Step 6: Generate response
        response = generate_response(full_prompt)

        # Step 7: Log chat
        log_chat_to_db(user_input, response,email)

        # Step 8: Return final response
        return jsonify({"response": response, "prompt": full_prompt})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
