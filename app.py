import asyncio
import os
from flask import Flask, render_template, request, send_file
import edge_tts
from moviepy.editor import AudioFileClip, ColorClip

app = Flask(__name__, template_folder='.')

VOICES = {
    'hi_swara': 'hi-IN-SwaraNeural',
    'hi_madhur': 'hi-IN-MadhurNeural',
    'en_in_neerja': 'en-IN-NeerjaNeural',
    'en_in_prabhat': 'en-IN-PrabhatNeural'
}

PREVIEW_TEXTS = {
    'hi_swara': "नमस्कार, चिराग एफएम पर आपका स्वागत है।",
    'hi_madhur': "नमस्कार, चिराग एफएम पर आपकी पसंदीदा कहानी शुरू होने वाली है।",
    'en_in_neerja': "Hello and welcome to Chirag FM stories.",
    'en_in_prabhat': "Welcome to Chirag FM audio stories."
}

async def generate_speech(text, voice_key, rate, output_file):
    selected_voice = VOICES.get(voice_key, 'hi-IN-SwaraNeural')
    rate_str = f"{rate}%" if rate.startswith(('-', '+')) else f"+{rate}%"
    communicate = edge_tts.Communicate(text, selected_voice, rate=rate_str)
    await communicate.save(output_file)

def create_fast_video(audio_file, video_output, character_type):
    audio_clip = AudioFileClip(audio_file)
    bg_color = (26, 13, 43) if character_type == 'anime' else (13, 26, 43)
    
    # हल्का रंगीन बैकग्राउंड वीडियो
    video_clip = ColorClip(size=(720, 1280), color=bg_color, duration=audio_clip.duration)
    video_clip = video_clip.set_audio(audio_clip)
    
    # फास्ट रेंडरिंग (अटकने से बचाने के लिए)
    video_clip.write_videofile(
        video_output, 
        fps=1, 
        codec='libx264', 
        audio_codec='aac', 
        preset='ultrafast',
        logger=None
    )
    audio_clip.close()
    video_clip.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/preview_voice', methods=['POST'])
def preview_voice():
    try:
        voice_key = request.form.get('voice', 'hi_swara')
        preview_file = "static/preview.mp3"
        os.makedirs('static', exist_ok=True)
        
        text = PREVIEW_TEXTS.get(voice_key, "नमस्कार, चिराग एफएम में आपका स्वागत है।")
        asyncio.run(generate_speech(text, voice_key, "+0", preview_file))
        return send_file(preview_file)
    except Exception as e:
        return str(e), 500

@app.route('/generate', methods=['POST'])
def generate():
    try:
        text = request.form.get('text', '')
        voice = request.form.get('voice', 'hi_swara')
        character_type = request.form.get('character', 'anime')
        format_type = request.form.get('format_type', 'video')
        speed = request.form.get('speed', '0')
        
        if not text:
            return "कृपया स्टोरी या टेक्स्ट दर्ज करें!", 400

        audio_file = "static/chirag_story.mp3"
        video_file = "static/chirag_story.mp4"
        
        os.makedirs('static', exist_ok=True)

        # 1. ऑडियो बनाएँ
        asyncio.run(generate_speech(text, voice, speed, audio_file))

        # 2. MP3 या MP4 डाउनलोड भेजें
        if format_type == 'audio':
            return send_file(audio_file, as_attachment=True, download_name="chirag_story.mp3")
        else:
            create_fast_video(audio_file, video_file, character_type)
            return send_file(video_file, as_attachment=True, download_name="chirag_story.mp4")
            
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
