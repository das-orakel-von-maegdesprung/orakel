from flask import Blueprint, request, jsonify
from utils.database import get_users_collection

questions_bp = Blueprint("questions", __name__)
from flask import session
from utils.database_auth import find_valid_session_token, get_user_data_by_email

@questions_bp.route("/save-answers", methods=["POST"])
def save_answers():
    try:
        # Get the session token from Flask session (cookie)
        session_token = session.get("session_token")
        if not session_token:
            return jsonify({"error": "Not authenticated"}), 401

        # Validate session token & get user email
        record = find_valid_session_token(session_token)
        if not record:
            return jsonify({"error": "Invalid session token"}), 401

        email = record["email"]

        data = request.get_json(force=True)
        answers = data.get("answers")
        language = data.get("language", "de")

        # Update user data based on email (not token)
        result = get_users_collection().update_one(
            {"email": email},
            {"$set": {"answers": answers, "language": language,"answered_all_questions": True}},
            upsert=True
        )

        return jsonify({
            "status": "saved",
            "matched": result.matched_count,
            "modified": result.modified_count,
            "upserted": str(result.upserted_id) if result.upserted_id else None
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
