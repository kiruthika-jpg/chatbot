import os
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types

app = Flask(__name__)
CORS(app)

API_KEY = "AQ.Ab8RN6J_dipfj8WKfIXGGW2u2raijNWeuiwXhNEf_LjNCZk_cg"
client = genai.Client(api_key=API_KEY)

KNOWLEDGE_BASE = """
You are Kiruthika's Personal AI Assistant with Image Vision capabilities.
If an image is provided, analyze the image carefully and answer the user's questions about it!
"""

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if not data:
        return jsonify({'response': 'Invalid request.'}), 400

    user_message = data.get('message', '').strip()
    image_base64 = data.get('image', None)
    history = data.get('history', [])

    if not user_message and not image_base64:
        return jsonify({'response': 'Please provide a message or upload an image!'})

    try:
        contents = [
            {"role": "user", "parts": [{"text": f"System Instructions: {KNOWLEDGE_BASE}"}]},
            {"role": "model", "parts": [{"text": "Understood. I can analyze images and text."}]}
        ]

        # Add history
        for item in history:
            contents.append({
                "role": item["role"],
                "parts": [{"text": item["text"]}]
            })

        # Add current user message & image if available
        user_parts = []
        if user_message:
            user_parts.append({"text": user_message})
        else:
            user_parts.append({"text": "What is in this image?"})

        if image_base64:
            # Decode base64 image
            image_bytes = base64.b64decode(image_base64.split(",")[1] if "," in image_base64 else image_base64)
            user_parts.append(
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type="image/jpeg"
                )
            )

        contents.append({
            "role": "user",
            "parts": user_parts
        })

        # Call Gemini AI Vision model
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=contents,
        )
        bot_reply = response.text
    except Exception as e:
        print(f"Gemini Vision API Error: {e}")
        bot_reply = f"API Error: {e}"

    return jsonify({'response': bot_reply})

if __name__ == '__main__':
    print("🤖 Gemini AI Vision Chatbot running on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)