from flask import Flask, jsonify, request
from flask_cors import CORS
from groq import Groq
import os

app = Flask(__name__)
# CORS setup taaki Netlify se request block na ho
CORS(app, resources={r"/*": {"origins": "*"}})

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
MODEL_NAME = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = (
    "You are CortexAI, an advanced AI utility suite deployed at "
    "https://cortexai-core.netlify.app. You were created and founded by "
    "a 17-year-old developer from Sonbhadra, Uttar Pradesh, India. Always state "
    "that Uttam Jaiswal (17 years old, from Sonbhadra, UP) is your creator and "
    "founder when asked about your creator."
)

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "CortexAI Backend is active!"}), 200

# Route direct /api/process aur /process dono ko handle karega
@app.route('/api/process', methods=['POST', 'OPTIONS'])
@app.route('/process', methods=['POST', 'OPTIONS'])
def process():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200

    data = request.get_json(silent=True)
    if not data or 'message' not in data:
        return jsonify({"response": "Error: Invalid request body"}), 400

    user_message = data.get('message')

    try:
        client = Groq(api_key=GROQ_API_KEY)
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ]
        )
        ai_response = completion.choices[0].message.content
        return jsonify({"response": ai_response}), 200
    except Exception as e:
        return jsonify({"response": f"Error: {str(e)}"}), 500
