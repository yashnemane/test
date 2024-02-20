from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydub import AudioSegment
import speech_recognition as sr
import requests
import os
import io
import datetime
import logging
from logging.handlers import RotatingFileHandler

app = FastAPI()
r=sr.Recognizer()

#logger = logging.getLogger()
#logger.setLevel(logging.ERROR)

#handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
#formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
#handler.setFormatter(formatter)
#logger.addHandler(handler)

# Enable CORS for all routes by adding middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
async def helloatfirst():
    return {"message": "Hello World"}

@app.post('/GenerateTranscription')
async def generate_transcription(video_url: str, video_Id: str):
    logging.basicConfig(filename='app.log', level=logging.ERROR)
    try:
        video_url = request.json['video_url']
        video_Id = request.json['video_Id']

        # Load the video file
        check_file = f"transcription/{video_Id}.txt"
        if os.path.exists(check_file):
            return {"status": "success", "file": video_Id}
        else:
            response = requests.get(video_url)
            video_bytes = io.BytesIO(response.content)

            # Extract the audio from the video file and save it
            clip = mp.VideoFileClip(f"{video_Id}.mp4")
            clip.audio.write_audiofile(f"audio/{video_Id}.wav")

            file_path = f'audio/{video_Id}.wav'

            audio_file = sr.AudioFile(file_path)

            def transcribe_chunk(chunk):
                with sr.AudioFile(chunk) as source:
                    audio = r.record(source)
                    text = r.recognize_google(audio)
                return text

            chunks=30

            def large_audio_transcription(filename):
                sound = AudioSegment.from_file(filename)
                chunk_length_ms = int(1000 * 60 * 2)  # milliseconds
                chunks = []
                for i in range(0, len(sound), chunk_length_ms):
                    chunk = sound[i:i + chunk_length_ms]
                    chunks.append(chunk)


                whole_text = ""

                for i, audio_chunk, in enumerate(chunks, start=1):
                    chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
                    audio_chunk.export(chunk_filename, format="wav")
                    try:
                        text = transcribe_audio(chunk_filename)
                    except sr.UnknownValueError as e:
                        (
                            print("Error:", "Not able to detect"))
                    else:
                        text = f"{text.capitalize()}."
                        text_filename = os.path.join(folder_name, f"text_chunk{i}.txt")
                        with open(text_filename, 'w') as file:
                            file.write(text)
                            print(chunk_filename, ":", text)
                            whole_text += text
                        print(whole_text)

                    return {
                        "status": "success",
                        "file": video_Id,
                    }

    except Exception as e:
        return HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
