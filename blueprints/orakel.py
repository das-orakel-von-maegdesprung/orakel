from flask import session, Blueprint, jsonify, request
from blueprints.auth import find_valid_session_token
from utils.database import get_users_collection
from blueprints.chat_history import log_chat_to_db
from utils.ai import GroqChat

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






def build_full_prompt(user_input, answers, language, chat_history):
    with open("orakel_base_prompt.txt", "r", encoding="utf-8") as f:
        base_prompt = f.read()

    history_text = "\n".join(
        [f"Nutzer Nachricht: {chat['message']}\nAntwort: {chat['response']}" for chat in reversed(chat_history)]
    )

    return f"""{base_prompt}

Die Antworten des Nutzers auf den Fragebogen:
{answers}

Letzte Unterhaltungen:
{history_text}

Webseite ist in der Sprache: {language}, aber wenn der Nutzer eine andere Muttersprache angegeben hat oder in einer anderen Sprache spricht, passe dich an.

Nutzer Nachricht: {user_input}
"""




# --- Step 6: Generate Final AI Response ---
def generate_response(prompt):
    return GroqChat.response_text(prompt)


from blueprints.chat_history import get_last_chats  # or wherever it's defined

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

        # Step 4: Get recent chat history
        chat_history = get_last_chats(email, limit=5)

        # Step 5: Build full prompt
        full_prompt = build_full_prompt(user_input, answers, language, chat_history)

        # Step 6: Generate response
        response = generate_response(full_prompt)

        # Step 7: Log chat
        log_chat_to_db(user_input, response, email)

        # Step 8: Return final response
        return jsonify({"response": response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
