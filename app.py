from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import timedelta
import os
load_dotenv()

from utils.database import get_chat_collection

from blueprints.auth import auth_bp
from blueprints.questions import questions_bp
from blueprints.orakel import orakel_bp
from blueprints.books import books_bp


app = Flask(__name__, static_url_path='', static_folder='static')

CORS(app, origins=["*"], supports_credentials=True)

app.secret_key = os.getenv("SECRET_KEY", "default_secret_key")
app.permanent_session_lifetime = timedelta(days=30)


app.register_blueprint(orakel_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(questions_bp)
app.register_blueprint(books_bp)


@app.route("/", methods=["GET"])
def signup():
    return render_template("signup.html")


@app.route("/chat", methods=["GET"])
def chat():
    return render_template("chat.html")

@app.route("/questions", methods=["GET"])
def questions():
    return render_template("questions.html")

@app.route("/books_admin", methods=["GET"])
def books_admin():
    return render_template("books_admin.html")

@app.route("/view_books", methods=["GET"])
def view_books():
    return render_template("view_books.html")


@app.route('/logs_admin')
def logs_admin():
    chat_collection = get_chat_collection()
    logs = list(chat_collection.find().sort("timestamp", -1))  # Latest first
    
    # Convert MongoDB ObjectIds and timestamps to strings for easier display
    for log in logs:
        log["_id"] = str(log["_id"])
        log["timestamp"] = log["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
    
    return render_template('logs_admin.html', logs=logs)



if __name__ == "__main__":
    app.run(debug=True)
