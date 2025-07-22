from flask import Blueprint, request, jsonify, current_app
from utils.database import get_books_collection
from utils.embedding import query_gemini_embedding


import os
import dotenv
dotenv.load_dotenv()

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/search_chunks", methods=["POST"])
def search_chunks():
    data = request.json
    title = data.get("title")
    query_text = data.get("query")

    if not title or not query_text:
        return jsonify({"error": "Both title and query are required"}), 400

    books_col = get_books_collection()

    # Fetch the document by title first to check existence
    book = books_col.find_one({"title": title})
    if not book:
        return jsonify({"error": "Book not found"}), 404

    # Embed the query text
    query_embedding = query_gemini_embedding([query_text])
    if not query_embedding:
        return jsonify({"error": "Failed to get query embedding"}), 500

    q_vector = query_embedding[0]  # a list of floats

    # MongoDB vector search pipeline
    pipeline = [
        {
            "$match": {"title": title}  # Filter documents by title first
        },
        {
            "$unwind": "$chunks"  # Unwind chunks array
        },
        {
            "$unwind": "$embeddings"  # Unwind embeddings array, must be aligned with chunks
        },
        {
            "$vectorSearch": {
                "index": current_app.config.get("VECTOR_INDEX_NAME", "default_vector_index"),
                "path": "embeddings",  # the vector field name in your documents
                "queryVector": q_vector,
                "numCandidates": 50,
                "limit": 3
            }
        },
        {
            "$project": {
                "_id": 0,
                "chunk": "$chunks",
                "similarity": {"$meta": "vectorSearchScore"}
            }
        }
    ]

    cursor = books_col.aggregate(pipeline)
    results = list(cursor)

    if not results:
        return jsonify({"results": []})

    # Round similarity for readability
    for r in results:
        r["similarity"] = round(r["similarity"], 4)

    return jsonify({"results": results})
