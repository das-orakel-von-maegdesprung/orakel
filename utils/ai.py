import os
import requests

class GroqChat:
    API_URL = "https://api.groq.com/openai/v1/chat/completions"
    API_KEY = os.getenv("GROQ_API_KEY")

    @staticmethod
    def response_text(prompt: str, model="llama-3.3-70b-versatile") -> str:
        headers = {
            "Authorization": f"Bearer {GroqChat.API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post(GroqChat.API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        return f"[ERROR {response.status_code}] {response.text}"
