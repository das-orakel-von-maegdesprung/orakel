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

def chunk_text_by_chars(text, max_length_chars=5000):
    chunks = []
    start = 0
    while start < len(text):
        chunk = text[start:start+max_length_chars]
        chunks.append(chunk)
        start += max_length_chars
    return chunks


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




def embed_text(text):
    print(f"Embedding text: {text[:50]}...")  # Debugging output
    data = {
        "model": "models/gemini-embedding-001",
        "content": {
            "parts": [{"text": text}]
        }
    }

    for attempt in range(3):
        response = requests.post(api_url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            # Adapt to the correct response format:
            if "embedding" in result:
                embedding = result["embedding"]["values"]
                normalized = normalize_embedding(embedding)
                return normalized
            else:
                raise RuntimeError(f"Unexpected response format: {result}")
        else:
            print(f"Request failed with status {response.status_code}, body: {response.text}, retrying...")
            time.sleep(5)
    raise RuntimeError("Failed to get embedding after retries.")


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

