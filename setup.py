from utils.database import get_db

VECTOR_FIELD = "embeddings"  # adjust if needed, e.g. "embeddings" or "chunks_embeds.embedding"
VECTOR_INDEX_NAME = "embedding_vector_index"
DIMENSIONS = 768  # your embedding dimension

def main():
    db = get_db()
    try:
        db.books.create_search_index({
            "definition": {
                "mappings": {
                    "dynamic": True,
                    "fields": {
                        VECTOR_FIELD: {
                            "type": "knnVector",
                            "dimensions": DIMENSIONS,
                            "similarity": "dotProduct"
                        }
                    }
                }
            },
            "name": VECTOR_INDEX_NAME
        })
        print("Vector index created successfully.")
    except Exception as e:
        print(f"Could not create vector index: {e}")

if __name__ == "__main__":
    main()
