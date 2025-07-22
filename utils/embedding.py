#utils/embedding.py

import os
import requests
import time
import numpy as np
import dotenv
dotenv.load_dotenv()


# Your Gemini API key from environment variable
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("Please set the GEMINI_API_KEY environment variable")

api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent"
headers = {
    "x-goog-api-key": gemini_api_key,
    "Content-Type": "application/json",
}

def chunk_text(text, max_length=256):
    """
    Split the input text into chunks of max_length words.
    """
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_length):
        chunk = " ".join(words[i : i + max_length])
        chunks.append(chunk)
    return chunks

def normalize_embedding(embedding):
    """
    Normalize the embedding vector to unit length.
    """
    embedding_np = np.array(embedding)
    norm = np.linalg.norm(embedding_np)
    if norm == 0:
        return embedding_np
    return embedding_np / norm



def query_gemini_embedding(texts):
    data = {
        "content": {
            "parts": [{"text": chunk} for chunk in texts]
        }
    }

    for attempt in range(3):
        response = requests.post(api_url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            if "embeddings" in result:
                normalized_embeddings = [
                    normalize_embedding(item["embedding"]["values"]) for item in result["embeddings"]
                ]
                return normalized_embeddings
            else:
                raise RuntimeError(f"Unexpected response format: {result}")
        else:
            print(f"Request failed with status {response.status_code}, body: {response.text}, retrying...")
            time.sleep(5)
    raise RuntimeError("Failed to get embeddings after retries.")



def embed_large_text(text, max_length=256):
    """
    Chunk a large text, embed all chunks in a batch, and return embeddings.
    """
    chunks = chunk_text(text, max_length=max_length)
    embeddings = query_gemini_embedding(chunks)
    return embeddings

if __name__ == "__main__":
    large_text = (
        "This is a very long text that you want to embed. "
        "It might be hundreds or thousands of words long. "
        "This example just repeats the sentence to simulate a long text. " * 10
    )

    embeddings = embed_large_text(large_text)
    print(f"Number of chunks embedded: {len(embeddings)}")
    print(f"Embedding dimension (per chunk): {len(embeddings[0])}")
