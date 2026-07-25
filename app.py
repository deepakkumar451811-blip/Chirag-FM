import os
import requests
from flask import Flask, render_template, request, jsonify, send_file
import io

app = Flask(__name__)

# ElevenLabs API Key
ELEVENLABS_API_KEY = "sk_4903a7632b6f21bb2e62d1dea045fcb07d2f6f2ad07571d4"

# हिंदी वॉइस लिस्ट (Voice IDs)
VOICES = {
    "Aarav_Male": "pNInz6obpgDQGcFmaJgB",        # Multi-lingual Male Voice
    "Kavya_Female": "21m00Tcm4TlvDq8ikWAM",      # Multi-lingual Female Voice
    "Storyteller_Deep": "VR6AewLTigWG4xT1s5nF"   # Deep Narration Voice
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate-audio", methods=["POST"])
def generate_audio():
    try:
        data = request.json
        text = data.get("text", "")
        voice_key = data.get("voice", "Aarav_Male")

        if not text:
            return jsonify({"error": "कृपया टेक्स्ट दर्ज करें।"}), 400

        voice_id = VOICES.get(voice_key, VOICES["Aarav_Male"])

        # ElevenLabs TTS Endpoint
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        }

        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",  # हिंदी भाषा के लिए बेस्ट मॉडल
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            audio_io = io.BytesIO(response.content)
            return send_file(
                audio_io,
                mimetype="audio/mpeg",
                as_attachment=False,
                download_name="chirag_fm_voice.mp3"
            )
        else:
            return jsonify({"error": f"ElevenLabs API Error: {response.text}"}), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
