import speech_recognition as sr
import os
import requests
import json
from flask import Flask, request
import io
from flask_cors import CORS
import logging
from moviepy.editor import VideoFileClip
import threading

from pydub import AudioSegment

# Load the video file
app = Flask(__name__)
cors = CORS(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'application/json'
r=sr.Recognizer()

@app.route('/')
def hello():
    return {"Hello": "World"}

@app.route('/GenerateTranscription', methods=['POST'])
def generate_transcription():
    logging.basicConfig(filename='app.log', level=logging.ERROR)
    # video_url = request.args.get('video_url')
    video_url = request.json['video_url']
    # ct = datetime.datetime.now()
    video_Id = request.json['video_Id']
    # Load the video file
    # Download the video file as bytes
    check_file = f"transcription/{video_Id}.txt"

    chunk_length = 25  # seconds

    folder_name = "transcription"

    def fetch_video_and_convert_to_audio(video_url, folder_name, video_Id):
        # Fetch the video file from the URL
        response = requests.get(video_url, allow_redirects=True)
        video_bytes = io.BytesIO(response.content)

        # Convert video bytes to audio
        sound = AudioSegment.from_file(video_bytes, format="mp4")

        # Define the filename for the extracted audio
        sound_filename = os.path.join(folder_name, f"{video_Id}.wav")

        # Export the audio
        sound.export(sound_filename, format="wav")

        print(f"Audio extracted and saved successfully: {sound_filename}")


    thread = threading.Thread(target=fetch_video_and_convert_to_audio, args=(video_url, folder_name, video_Id))
    thread.start()