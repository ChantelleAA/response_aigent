# app.py
from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import json
from app.chatbot import chat_wrapper, save_history, load_history

app = Flask(__name__)
CORS(app)  # allow frontend to connect from browser

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "")
    history = data.get("history", [])

    def stream():
        for chunk in chat_wrapper(message, history):
            yield f"data: {json.dumps(chunk)}\n\n"  # SSE format

    return Response(stream(), content_type="text/event-stream")

@app.route("/history", methods=["GET", "POST"])
def manage_history():
    if request.method == "GET":
        return jsonify(load_history())
    elif request.method == "POST":
        history = request.get_json()
        save_history(history)
        return jsonify({"status": "saved"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860, debug=True)
