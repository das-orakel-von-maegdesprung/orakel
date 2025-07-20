from flask import session,Blueprint,jsonify,request
from blueprints.database_auth import find_valid_session_token
from blueprints.database import users
from utils.ai import GroqChat
from blueprints.database import log_chat_to_db

orakel_bp = Blueprint("orakel", __name__)

@orakel_bp.route("/orakel", methods=["POST"])
def orakel():
    try:
        # Step 1: Validate session
        session_token = session.get("session_token")
        if not session_token:
            return jsonify({"error": "Not authenticated"}), 401

        record = find_valid_session_token(session_token)
        if not record:
            return jsonify({"error": "Invalid session token"}), 401

        email = record["email"]

        # Step 2: Get user data (answers and language)
        user_data = users.find_one({"email": email}, {"answers": 1, "language": 1})
        answers = user_data.get("answers", {})
        language = user_data.get("language", "de")

        # Step 3: Get user input from request
        data = request.get_json()
        user_input = data.get("message", "")

        # Step 4: Combine input with stored answers if needed
        # You could customize this based on how GroqChat is set up
        prompt = f"""
        You are the Orakel of Mägdesprung an Orakel to give live advice help users reflect and introspect. The user has a unique worldview, values, and personality. Use the information below to understand their perspective and speak in a way that aligns with their values. 

Do not mention that you know this information — just incorporate it naturally into your tone and advice. Make your reply feel like a personal, thoughtful response, not like an analysis.

User message: {user_input}

User profile:
{answers}

Respond in the user's preferred language: {language}

Instructions:
- Speak in a way that resonates with this user’s mindset.
- Offer meaningful, practical, and emotionally intelligent advice.
- Affirm their values and decision-making style.
- Keep your tone friendly, natural, and aligned with their beliefs.
"""

        # Step 5: Generate LLM response
        response = GroqChat.response_text(prompt)

        # Step 6: Log chat
        log_chat_to_db(user_input, response)

        # Step 7: Return response
        return jsonify({"response": response,"prompt": prompt})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
