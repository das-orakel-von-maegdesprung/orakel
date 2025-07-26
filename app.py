from flask import Flask, request, render_template,  session, redirect
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import timedelta
import os

from utils.globals import Role
load_dotenv()

from utils.database import get_chat_collection

from blueprints.auth import auth_bp
from blueprints.questions import questions_bp
from blueprints.orakel import orakel_bp
# from blueprints.prompts import prompts_bp
from blueprints.auth import admin_required, login_required,find_valid_session_token, get_user_data_by_email



app = Flask(__name__, static_url_path='', static_folder='static')

CORS(app, origins=["*"], supports_credentials=True)

app.secret_key = os.getenv("SECRET_KEY", "default_secret_key")
app.permanent_session_lifetime = timedelta(days=30)


app.register_blueprint(orakel_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(questions_bp)
# app.register_blueprint(books_bp)

########################### Signup PAGE ###########################

@app.route("/")
def home():
    token = session.get("session_token")
    record = find_valid_session_token(token)
    if not record:
        return render_template("signup.html")

    user = get_user_data_by_email(record["email"])
    if user and user.get("answers"):
        return redirect("/chat")
    else:
        return redirect("/questions")


########################### AFTER LOGIN PAGES ###########################

@app.route("/chat")
@login_required
def chat():
    token = session.get("session_token")
    record = find_valid_session_token(token)
    if not record:
        return redirect('/')

    user = get_user_data_by_email(record["email"])
    if not user or not user.get("answers"):
        return redirect("/questions")
    return render_template("chat.html")

@app.route("/questions")
@login_required
def questions():
    token = session.get("session_token")
    record = find_valid_session_token(token)
    if not record:
        return redirect('/')

    user = get_user_data_by_email(record["email"])
    if user and user.get("answers"):
        return redirect("/chat")
    return render_template("questions.html")


########################### ADMIN PAGES ###########################
@app.route("/admin", methods=["GET"])
@admin_required
def admin():
    return render_template("admin.html")


@app.route("/users_admin", methods=["GET"])
@admin_required
def users_admin():
    return render_template("users_admin.html")


@app.route("/prompts_admin", methods=["GET"])
@admin_required
def prompts_admin():
    return render_template("prompts_admin.html")



@app.route('/logs_admin')
@admin_required
def logs_admin():
    chat_collection = get_chat_collection()
    logs = list(chat_collection.find().sort("timestamp", -1))  # Latest first
    
    # Convert MongoDB ObjectIds and timestamps to strings for easier display
    for log in logs:
        log["_id"] = str(log["_id"])
        log["timestamp"] = log["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
    
    return render_template('logs_admin.html', logs=logs)

from blueprints.auth import _set_user_role

if __name__ == "__main__":
    _set_user_role("leanderziehm@gmail.com",role=Role.ADMIN)
    app.run(debug=True)

