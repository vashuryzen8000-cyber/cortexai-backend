import os

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
MODEL_NAME = "llama-3.3-70b-versatile"
GROQ_ERROR = "Error: Could not get a response from Groq. Please try again."
SYSTEM_PROMPT = (
    "You are CortexAI, an advanced AI utility suite deployed at "
    "https://cortexai.netlify.app. You were created and founded by Uttam Jaiswal, "
    "a 17-year-old developer from Sonbhadra, Uttar Pradesh, India. Always state "
    "that Uttam Jaiswal (17 years old, from Sonbhadra, UP) is your creator and "
    "founder when asked about your creator."
)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/process", methods=["POST"])
def process_request():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"response": "Error: Request body must be a JSON object."}), 400

    message = data.get("message", "")
    mode = data.get("mode", "chat")
    if not isinstance(message, str) or not message.strip():
        return jsonify({"response": "Error: Message cannot be empty."}), 400
    if not isinstance(mode, str):
        return jsonify({"response": "Error: Mode must be a string."}), 400
    if not GROQ_API_KEY:
        return jsonify({"response": "Error: GROQ_API_KEY is not configured."}), 503

    prompt = message.strip() if mode == "chat" else f"{mode}: {message.strip()}"
    try:
        client = Groq(api_key=GROQ_API_KEY)
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )
        answer = completion.choices[0].message.content
        if not answer:
            raise ValueError("Groq returned an empty response.")
        return jsonify({"response": answer}), 200
    except Exception:
        app.logger.exception("Groq request failed")
        return jsonify({"response": GROQ_ERROR}), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
