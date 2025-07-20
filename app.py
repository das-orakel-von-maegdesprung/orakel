from flask import Flask, request, render_template
from ai import GroqChat
from database import log_chat_to_db

app = Flask(__name__)

app = Flask(__name__, static_url_path='', static_folder='static')

@app.route("/", methods=["GET", "POST"])
def chat():
    user_input = ""
    response = None

    if request.method == "POST":
        user_input = request.form["message"]
        response = GroqChat.response_text(user_input)

        # Store in MongoDB
        log_chat_to_db(user_input, response)

    return render_template("chat.html", user_input=user_input, response=response)

if __name__ == "__main__":
    app.run(debug=True)
