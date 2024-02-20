import speech_recognition as sr
from pydub import AudioSegment
import os
import ffmpeg
import requests
import json
#import random
from flask import Flask, request
import datetime
import io
import subprocess
from flask_cors import CORS
import logging
import httptools
import assemblyai as asi

# Load the video file
app = Flask(__name__)
cors = CORS(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'application/json'

@app.route('/')
def hello():
    return {"Hello": "World"}

@app.route('/GenerateTranscription', methods=['POST'])
def GenerateTranscript():
    logging.basicConfig(filename='app.log', level=logging.ERROR)
    # video_url = request.args.get('video_url')
    video_url = request.json['video_url']
    # ct = datetime.datetime.now()
    video_Id = request.json['video_Id']
    # Load the video file
    # Download the video file as bytes
    check_file = f"transcription/{video_Id}.txt"
    if os.path.exists(check_file):
        return {
            "status": "success",
            "file": video_Id,
        }
    else:
        response = requests.get(video_url, allow_redirects=True)
        video_bytes = io.BytesIO(response.content)

        # Extract the audio from the video file

        video = AudioSegment.from_file(video_bytes, format="mp4")
        audio = video.set_channels(1).set_frame_rate(16000).set_sample_width(2)

        # Save the audio file to disk
        # Create an empty file

        wav_file = f"transcription/{video_Id}.wav"
        # Create an empty file
        with open(wav_file, "w") as file:
            pass
        # Set file permissions to 777
        os.chmod(wav_file, 0o777)
        audio.export(f"transcription/{video_Id}.wav", format="wav")

        # video = AudioSegment.from_file("./infinity.mp4", format="mp4")
        # audio = video.set_channels(1).set_frame_rate(16000).set_sample_width(2)
        # audio.export("audio.wav", format="wav")

        r = sr.Recognizer()
        # Set the path to the audio file
        file_path = f'transcription/{video_Id}.wav'

        # Create an AudioFile instance from the audio file
        audio_file = sr.AudioFile(file_path)
        # f = open('output.txt', 'r+')
        # f.truncate(0) # need '0' when using r+

        ct = datetime.datetime.now()
        file_name = video_Id

        # Define a function to split the audio file into chunks and perform speech recognition
        def transcribe_chunk(chunk):
            with sr.AudioFile(chunk) as source:
                audio = r.record(source)  # read the entire audio file
                text = r.recognize_google(audio)  # perform speech recognition
            return text

        # Define the chunk size (in seconds)
        chunk_size = 30

        # Split the audio file into chunks and perform speech recognition on each chunk

        with audio_file as source:
            duration = source.DURATION
            chunks = int(duration / chunk_size) + 1
            print(int(duration / chunk_size))
            for i in range(chunks - 1):
                start = i * chunk_size
                end = min(start + chunk_size, duration)
                print(f"Transcribing chunk {i + 1}...")
                chunk_file = f"{file_name}_chunk_{i + 1}.wav"
                os.system(f"ffmpeg -i {file_path} -ss {start} -t {chunk_size} {chunk_file} -loglevel quiet")
                text = transcribe_chunk(chunk_file)
                os.remove(chunk_file)
                # transcribe audio file and write text to output file
                # transcribe audio file and write text to output file
                # Create an empty text file
                text_file = f"transcription/{video_Id}.txt"
                # Create an empty file
                with open(text_file, "w") as file:
                    pass
                # Set file permissions to 777
                os.chmod(text_file, 0o777)
                with open(f"transcription/{file_name}.txt", "a") as f:
                    f.write(text)
                    print(text)
                # return "success"
        return {
            "status": "success",
            "file": text_file
        }


@app.route('/generateQuestions')
def GenerateQuestion():
    file_name = request.args.get('file_name')
    grade_id = request.args.get('grade_id')
    exam_id = request.args.get('exam_id')
    with open(f'transcription/{file_name}.txt', 'r') as file:
        text = file.read()
        # time.sleep(10)
    # print(text)

    VIDEO_TRANSCRIPTION = text
    NO_OF_MCQ = 5
    # GRADE = "12th"
    # EXAM = "NEET"
    GRADE = grade_id
    EXAM = exam_id
    OPEN_API_KEY = "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"
    # getGPT(OPEN_API_KEY, VIDEO_TRANSCRIPTION, NO_OF_MCQ, GRADE, EXAM):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {OPEN_API_KEY}',
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "assistant",
                "content": f"""
                        Generate a list of {NO_OF_MCQ} Multiple Choice Question from the text ```{VIDEO_TRANSCRIPTION}``` Questions along \ 
                        with their options and answer in string,
                        for student of grade {GRADE} and preparing for ```{EXAM}```.

                        Output JSON: <array with question and array of options and answers>
                        Step 1 - ...
                        All your questions should help in understanding the student's knowledge level of the concept taught. DON'T RETURN ANY TEXTUAL DATA if textual data convert it to JSON

                        Step 2 - …
                        If the response is not valid json, Try to generate questions .
                        Step3 - ...
                        json output to be Question object always
                        step N
                        If the response does not valid json format, \ then simply write empty array\"Failed".
                        """

            }
        ],
        "temperature": 0.7
    }

    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, data=json.dumps(data))
    # json_response = json.decoder(response)
    print("GPT response", response.text)
    response = response.text
    # json_response = json.decoder(response)
    # parse json response
    response_data = json.loads(response)

    # print choices
    choices = response_data['choices']
    # print(choices)
    for choice in choices:
        message = choice['message']
        content = message['content']
        print("Choice Response", content)
        print(type(content))
        return content


if __name__ == '__video__':
    app.run(debug=True)