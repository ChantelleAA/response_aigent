from flask import Flask, request, jsonify, render_template
from app.chatbot import generate_response, save_data
import tempfile
import whisper

app = Flask(__name__)
model = whisper.load_model("base") 

@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    if "audio" not in request.files:
        return jsonify({"error": "No audio uploaded"}), 400

    file = request.files["audio"]
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=True) as tmp:
        file.save(tmp.name)
        result = model.transcribe(tmp.name)
        return jsonify({"text": result.get("text", "")})

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    user_input = data.get("message", "")
    history = [] 
    response_stream = generate_response(user_input, history)
    reply = "".join(response_stream)
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True)
