from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import timedelta
import os
load_dotenv()
from utils.ai import GroqChat
from blueprints.database import log_chat_to_db
from blueprints.auth import auth_bp
from blueprints.questions import questions_bp



app = Flask(__name__, static_url_path='', static_folder='static')

CORS(app, origins=["*"], supports_credentials=True)

app.secret_key = os.getenv("SECRET_KEY", "default_secret_key")
app.permanent_session_lifetime = timedelta(days=30)


# app.register_blueprint(oraclPOSTe_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(questions_bp)


@app.route("/", methods=["GET"])
def signup():
    return render_template("signup.html")


@app.route("/chat", methods=["GET"])
def chat():
    return render_template("chat.html")

@app.route("/questions", methods=["GET"])
def questions():
    return render_template("questions.html")

@app.route("/llm", methods=["POST"])
def llm():
    data = request.get_json()
    user_input = data.get("message", "")

    # Generate response
    response = GroqChat.response_text(user_input)

    # Log to database
    log_chat_to_db(user_input, response)

    # Return JSON response
    return jsonify({"response": response})
if __name__ == "__main__":
    app.run(debug=True)
