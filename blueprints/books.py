from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import fitz  # PyMuPDF
import os
from utils.database import get_books_collection
from utils.embedding import chunk_text_by_chars, embed_text  # explicit imports
import time
books_bp = Blueprint("books", __name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
@books_bp.route("/upload_book", methods=["POST"])
def upload_book():
    try:
        if "pdf" not in request.files:
            return jsonify({"error": "PDF file is required"}), 400

        file = request.files["pdf"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        filename = secure_filename(file.filename)
        title = os.path.splitext(filename)[0]
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Extract text
        doc = fitz.open(filepath)
        full_text = ""
        for page in doc:
            full_text += page.get_text()
        doc.close()

        # Chunk text
        chunks = chunk_text_by_chars(full_text, max_length_chars=50000)

        collection = get_books_collection()

        # Save or update book metadata doc
        collection.update_one(
            {"title": title, "type": "metadata"},
            {"$set": {"total_chunks": len(chunks), "full_text": full_text}},
            upsert=True,
        )

        # Insert all chunks upfront if they don't exist yet
        for i, chunk in enumerate(chunks):
            existing_chunk = collection.find_one({"title": title, "chunk_index": i, "type": "chunk"})
            if not existing_chunk:
                collection.insert_one({
                    "title": title,
                    "chunk_index": i,
                    "chunk": chunk,
                    "embedding": None,  # Placeholder
                    "processed": False,
                    "type": "chunk",
                })

        def embed_with_retry(text, retries=5, backoff=1.0):
            for attempt in range(retries):
                try:
                    return embed_text(text)
                except Exception as e:
                    wait = backoff * (2 ** attempt)
                    print(f"Rate limit hit or error: {e}, retrying in {wait}s...")
                    time.sleep(wait)
            raise Exception("Max retries exceeded for embedding")

        # Find unprocessed chunks
        unprocessed_chunks = collection.find({
            "title": title,
            "type": "chunk",
            "processed": False
        })

        # Process unprocessed chunks incrementally
        for chunk_doc in unprocessed_chunks:
            embedding = embed_with_retry(chunk_doc["chunk"])

            # Update chunk doc with embedding and processed=True
            collection.update_one(
                {"_id": chunk_doc["_id"]},
                {"$set": {
                    "embedding": embedding.tolist() if hasattr(embedding, "tolist") else embedding,
                    "processed": True,
                }}
            )

        return jsonify({"status": "uploaded", "title": title})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@books_bp.route("/get-book-chunks", methods=["GET"])
def get_book_chunks():
    title = request.args.get("title")
    if not title:
        return jsonify({"error": "Title query parameter is required"}), 400

    try:
        # Return chunk, chunk_index and embedding
        chunks = list(get_books_collection().find(
            {"title": title, "type": "chunk"},
            {"_id": 0, "chunk_index": 1, "chunk": 1, "embedding": 1}
        ).sort("chunk_index", 1))

        return jsonify({"chunks": chunks})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@books_bp.route("/get-books", methods=["GET"])
def list_books():
    try:
        all_books = list(get_books_collection().find(
            {"type": "metadata"},  # only metadata docs (full book info)
            {"_id": 0}
        ))
        return jsonify({"books": all_books})
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
