from flask import Blueprint, request, jsonify
from blueprints.database import users



questions_bp = Blueprint("questions", __name__)

@questions_bp.route("/save-answers", methods=["POST"])
def save_answers():
    data = request.get_json()
    email = data.get("email")
    answers = data.get("answers")
    language = data.get("language", "de")

    if not email or not answers:
        return jsonify({"error": "Invalid data"}), 400

    users.update_one(
        {"email": email},
        {"$set": {"answers": answers, "language": language}},
        upsert=True
    )

    return jsonify({"status": "saved"})
