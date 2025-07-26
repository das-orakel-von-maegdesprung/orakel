from flask import Blueprint, request, jsonify
from utils.database import get_text_collection
from datetime import datetime
from bson import ObjectId

text_bp = Blueprint("text", __name__)

@text_bp.route("/add_text", methods=["POST"])
def add_text():
    data = request.json
    content = data.get("content")
    author = data.get("author", "anonymous")

    if not content:
        return jsonify({"error": "Content is required"}), 400

    doc = {
        "content": content,
        "author": author,
        "timestamp": datetime.utcnow(),
        "enabled": True,
        "type": "user_prompt"
    }

    get_text_collection().insert_one(doc)
    return jsonify({"status": "added", "data": doc}), 201


@text_bp.route("/list_texts", methods=["GET"])
def list_texts():
    texts = list(get_text_collection().find(
        {"type": "user_prompt"},
        {"_id": 1, "content": 1, "author": 1, "timestamp": 1, "enabled": 1}
    ))
    for text in texts:
        text["_id"] = str(text["_id"])
    return jsonify({"texts": texts})


@text_bp.route("/toggle_text", methods=["POST"])
def toggle_text():
    data = request.json
    text_id = data.get("id")
    enabled = data.get("enabled")

    if text_id is None or enabled is None:
        return jsonify({"error": "id and enabled are required"}), 400

    result = get_text_collection().update_one(
        {"_id": ObjectId(text_id), "type": "user_prompt"},
        {"$set": {"enabled": enabled}}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Text not found"}), 404

    return jsonify({"status": "updated", "enabled": enabled})


@text_bp.route("/delete_text", methods=["DELETE"])
def delete_text():
    data = request.json
    text_id = data.get("id")

    if not text_id:
        return jsonify({"error": "id is required"}), 400

    result = get_text_collection().delete_one({"_id": ObjectId(text_id), "type": "user_prompt"})
    if result.deleted_count == 0:
        return jsonify({"error": "Text not found"}), 404

    return jsonify({"status": "deleted"})


# ----- SYSTEM PROMPT HANDLING -----

@text_bp.route("/set_system_prompt", methods=["POST"])
def set_system_prompt():
    data = request.json
    content = data.get("content")

    if not content:
        return jsonify({"error": "System prompt content is required"}), 400

    get_text_collection().update_one(
        {"type": "system_prompt"},
        {"$set": {"content": content, "timestamp": datetime.utcnow()}},
        upsert=True
    )
    return jsonify({"status": "system prompt updated"})


@text_bp.route("/get_system_prompt", methods=["GET"])
def get_system_prompt():
    prompt = get_text_collection().find_one(
        {"type": "system_prompt"},
        {"_id": 0, "content": 1, "timestamp": 1}
    )
    if not prompt:
        return jsonify({"system_prompt": None})
    return jsonify({"system_prompt": prompt})


@text_bp.route("/get_enabled_prompts", methods=["GET"])
def get_enabled_prompts():
    prompts = list(get_text_collection().find(
        {"type": "user_prompt", "enabled": True},
        {"_id": 0, "content": 1}
    ))
    return jsonify({"enabled_prompts": [p["content"] for p in prompts]})
