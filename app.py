import asyncio
import os
import subprocess
from flask import Flask, render_template, request, send_file
import edge_tts

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

async def generate_speech(text, voice_key, output_file):
    selected_voice = VOICES.get(voice_key, 'hi-IN-SwaraNeural')
    communicate = edge_tts.Communicate(text, selected_voice)
    await communicate.save(output_file)

def create_character_video(audio_file, video_output, character_type):
    image_file = f"{character_type}.jpg"
    
    if os.path.exists(image_file):
        cmd = [
            'ffmpeg', '-y',
            '-loop', '1',
            '-i', image_file,
            '-i', audio_file,
            '-c:v', 'libx264',
            '-tune', 'stillimage',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-pix_fmt', 'yuv420p',
            '-shortest',
            video_output
        ]
    else:
        bg_color = "0x1a0d2b" if character_type == 'anime' else "0x0d1a2b"
        title_text = "DKLR ANIME STORY" if character_type == 'anime' else "DKLR HUMAN STORY"
        
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', f'color=c={bg_color}:s=720x1280:r=25',
            '-i', audio_file,
            '-vf', f"drawtext=text='{title_text}':fontcolor=white:fontsize=40:x=(w-text_w)/2:y=(h-text_h)/2",
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-pix_fmt', 'yuv420p',
            '-shortest',
            video_output
        ]
        
    subprocess.run(cmd, check=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/preview_voice', methods=['POST'])
def preview_voice():
    voice_key = request.form.get('voice', 'hi_swara')
    preview_file = "static/preview.mp3"
    os.makedirs('static', exist_ok=True)
    
    text = PREVIEW_TEXTS.get(voice_key, "नमस्कार, चिराग एफएम में आपका स्वागत है।")
    asyncio.run(generate_speech(text, voice_key, preview_file))
    
    return send_file(preview_file)

@app.route('/generate', methods=['POST'])
def generate():
    text = request.form.get('text', '')
    voice = request.form.get('voice', 'hi_swara')
    character_type = request.form.get('character', 'anime')
    format_type = request.form.get('format_type', 'video')
    
    if not text:
        return "कृपया स्टोरी या टेक्स्ट दर्ज करें!", 400

    audio_file = "static/chirag_story.mp3"
    video_file = "static/chirag_story.mp4"
    
    os.makedirs('static', exist_ok=True)

    # 1. ऑडियो जनरेट करें
    asyncio.run(generate_speech(text, voice, audio_file))
    
    # 2. अगर MP3 चुना है तो सीधा ऑडियो भेजो, वरना वीडियो बनाकर भेजो
    if format_type == 'audio':
        return send_file(audio_file, as_attachment=True, download_name="chirag_story.mp3")
    else:
        create_character_video(audio_file, video_file, character_type)
        return send_file(video_file, as_attachment=True, download_name="chirag_story.mp4")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
