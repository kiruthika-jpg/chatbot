import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai

app = Flask(__name__)
CORS(app)

API_KEY = "AQ.Ab8RN6J_dipfj8WKfIXGGW2u2raijNWeuiwXhNEf_LjNCZk_cg"
client = genai.Client(api_key=API_KEY)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'response': 'Invalid request.'}), 400

    user_message = data['message'].strip()
    history = data.get('history', [])

    if not user_message:
        return jsonify({'response': 'Please say something!'})

    try:
        # Build multi-turn conversation memory for Gemini
        contents = []
        for item in history:
            contents.append({
                "role": item["role"],
                "parts": [{"text": item["text"]}]
            })
        
        contents.append({
            "role": "user",
            "parts": [{"text": user_message}]
        })

        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=contents,
        )
        bot_reply = response.text
    except Exception as e:
        print(f"Gemini API Error: {e}")
        bot_reply = f"API Error: {e}"

    return jsonify({'response': bot_reply})

if __name__ == '__main__':
    print("🤖 Pro AI Chatbot backend running on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)