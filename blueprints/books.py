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
        # Get the file and title from the request
        if "pdf" not in request.files or "title" not in request.form:
            return jsonify({"error": "PDF file and title are required"}), 400

        file = request.files["pdf"]
        title = request.form["title"]

        # Secure the filename and save temporarily
        filename = secure_filename(file.filename)
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
