from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import fitz  # PyMuPDF
import os
from utils.database import get_books_collection

books_bp = Blueprint("books", __name__)
# books = db["books"]

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@books_bp.route("/get-books", methods=["GET"])
def list_books():
    try:
        all_books = list(get_books_collection().find({}, {"_id": 0}))  # exclude _id for cleaner output
        return jsonify({"books": all_books})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@books_bp.route("/upload_book", methods=["POST"])
def upload_book():
    try:
        if "pdf" not in request.files:
            return jsonify({"error": "PDF file is required"}), 400

        file = request.files["pdf"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        # Secure the filename and derive the title from filename without extension
        filename = secure_filename(file.filename)
        title = os.path.splitext(filename)[0]

        # Save the file (can rename if you want uniqueness, here just saving as is)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Extract text using fitz
        doc = fitz.open(filepath)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()

        # Insert into MongoDB
        get_books_collection().insert_one({
            "title": title,
            "text": text
        })

        return jsonify({"status": "uploaded", "title": title})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@books_bp.route("/delete_book", methods=["DELETE"])
def delete_book():
    try:
        data = request.get_json()
        title = data.get("title")

        if not title:
            return jsonify({"error": "Title is required"}), 400

        result = get_books_collection().delete_one({"title": title})
        if result.deleted_count == 0:
            return jsonify({"error": "Book not found"}), 404

        return jsonify({"status": "deleted", "title": title})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
