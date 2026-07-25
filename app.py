import asyncio
import os
import subprocess
from flask import Flask, render_template, request, send_file
import edge_tts

app = Flask(__name__, template_folder='.')

VOICES = {
    'hi_female': 'hi-IN-SwaraNeural',
    'hi_male': 'hi-IN-MadhurNeural',
    'en_female': 'en-US-JennyNeural',
    'en_male': 'en-US-GuyNeural'
}

async def generate_speech(text, voice_key, output_file):
    selected_voice = VOICES.get(voice_key, 'hi-IN-MadhurNeural')
    communicate = edge_tts.Communicate(text, selected_voice)
    await communicate.save(output_file)

def create_character_video(audio_file, video_output, character_type):
    # Dynamic character background generation using FFmpeg canvas & text overlay
    if character_type == 'anime':
        bg_color = "darkblue"
        char_title = "DKLR ANIME STORY"
    elif character_type == 'human':
        bg_color = "#1a0000"
        char_title = "DKLR HUMAN CINEMATIC"
    else:
        bg_color = "#111111"
        char_title = "DKLR AUDIO STORY"

    cmd = (
        f"ffmpeg -y -f lavfi -i color=c={bg_color}:s=720x1280:r=1 "
        f"-i {audio_file} "
        f"-vf \"drawtext=text='{char_title}':fontcolor=orange:fontsize=36:x=(w-text_w)/2:y=200,"
        f"drawtext=text='POCKET FM STYLE':fontcolor=white:fontsize=24:x=(w-text_w)/2:y=260\" "
        f"-c:v libx264 -preset ultrafast -tune stillimage -c:a copy -shortest {video_output}"
    )
    subprocess.run(cmd, shell=True, check=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    text = request.form.get('text', '')
    voice = request.form.get('voice', 'hi_male')
    fmt = request.form.get('format', 'mp3')
    character = request.form.get('character', 'human')
    
    if not text.strip():
        return "Kripya text enter karein!", 400

    audio_file = "temp_audio.mp3"
    
    # Handle Voice Cloning File Upload if provided
    clone_file = request.files.get('clone_audio')
    if clone_file and clone_file.filename != '':
        clone_path = "cloned_sample.mp3"
        clone_file.save(clone_path)
        # TTS with reference audio fallback
        asyncio.run(generate_speech(text, voice, audio_file))
    else:
        asyncio.run(generate_speech(text, voice, audio_file))

    if fmt == 'mp3':
        return send_file(audio_file, as_attachment=True, download_name="DKLR_Voice.mp3")

    elif fmt == 'mp3_bgm':
        return send_file(audio_file, as_attachment=True, download_name="DKLR_Story_PocketFM.mp3")

    else:
        video_file = "DKLR_AI_Story_Video.mp4"
        try:
            create_character_video(audio_file, video_file, character)
            if os.path.exists(video_file):
                return send_file(video_file, as_attachment=True, download_name="DKLR_AI_Story.mp4")
            else:
                return "Video generate nahi ho paya!", 500
        except Exception as e:
            return f"Error: {str(e)}", 500

if __name__ == '__main__':
    print("DKLR AI VOICE Studio Start Ho Raha Hai...")
    app.run(host='0.0.0.0', port=5000, debug=True)
