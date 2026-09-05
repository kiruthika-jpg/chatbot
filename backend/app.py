import os
import base64
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except Exception as e:
    print(f"GenAI Import Warning: {e}")
    HAS_GENAI = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'frontend'))

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)

# 🔑 REPLACE PASTE_YOUR_AIZASY_KEY_HERE WITH YOUR KEY FROM https://aistudio.google.com/apikey
# Note: Google Gemini API keys ALWAYS start with AIzaSy...
API_KEY = os.environ.get("GEMINI_API_KEY", "PASTE_YOUR_AIZASY_KEY_HERE")

client = genai.Client(api_key=API_KEY) if (HAS_GENAI and API_KEY and not API_KEY.startswith("PASTE")) else None

KNOWLEDGE_BASE = """
You are Kiruthika's Personal AI Assistant with Image Vision and Voice capabilities.
Always answer politely, professionally, and accurately. You represent Kiruthika Ananthan.

KEY INFORMATION ABOUT KIRUTHIKA:
- Name: Kiruthika Ananthan
- Role: Full-Stack Web Developer & AI Integration Developer
- Technical Skills: Python, Flask, HTML5, CSS3, JavaScript, REST APIs, Google Gemini AI, Git/GitHub, SQL.
- Contact Email: kiruthikaananthan185@gmail.com
- GitHub Profile: https://github.com/kiruthika-jpg
"""

@app.route('/')
def home():
    if os.path.exists(os.path.join(FRONTEND_DIR, 'index.html')):
        return send_from_directory(FRONTEND_DIR, 'index.html')
    return "<h1>AI Chatbot Server Running!</h1>"

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join(FRONTEND_DIR, path)):
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, 'index.html')

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

    # Try calling Gemini AI model first
    if client:
        try:
            contents = [
                {"role": "user", "parts": [{"text": f"System Instructions: {KNOWLEDGE_BASE}"}]},
                {"role": "model", "parts": [{"text": "Understood. I can analyze images, text, and answer questions about Kiruthika."}]}
            ]

            for item in history:
                contents.append({
                    "role": item["role"],
                    "parts": [{"text": item["text"]}]
                })

            user_parts = []
            if user_message:
                user_parts.append({"text": user_message})
            else:
                user_parts.append({"text": "What is in this image?"})

            if image_base64:
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

            response = client.models.generate_content(
                model='gemini-3.6-flash',
                contents=contents,
            )
            return jsonify({'response': response.text})
        except Exception as e:
            print(f"Gemini API Error: {e}")

    # Fallback response if API key is not updated yet
    user_lower = user_message.lower()
    if any(g in user_lower for g in ['hello', 'hi', 'hey']):
        reply = "Hello! 👋 How can I help you today?"
    elif 'how are you' in user_lower:
        reply = "I'm doing great! Thank you for asking."
    elif 'kiruthika' in user_lower or 'who are you' in user_lower or 'name' in user_lower:
        reply = "I am Kiruthika Ananthan's Personal AI Portfolio Assistant! Kiruthika is a Full-Stack Web & AI Developer."
    elif 'skill' in user_lower:
        reply = "Kiruthika's skills include Python, Flask, HTML5, CSS3, JavaScript, REST APIs, Google Gemini AI, and Git!"
    elif 'contact' in user_lower or 'email' in user_lower:
        reply = "You can contact Kiruthika at kiruthikaananthan185@gmail.com or visit https://github.com/kiruthika-jpg!"
    else:
        reply = f"I received your message: '{user_message}'. (Note: To enable full Gemini AI, get a key starting with AIzaSy... from https://aistudio.google.com/apikey and paste it into line 19 of backend/app.py!)"

    return jsonify({'response': reply})

if __name__ == '__main__':
    print("🤖 Gemini AI Chatbot running on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)