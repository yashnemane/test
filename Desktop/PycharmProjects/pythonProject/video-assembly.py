import speech_recognition as sr
from pydub import AudioSegment
import os
import ffmpeg
import requests
import json
#import random
from flask import Flask, request
import io
from flask_cors import CORS
import logging
from pydub import AudioSegment
import assemblyai as asi

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
        sound = AudioSegment.from_file(video_bytes, format="mp4")

        chunk_length = 30  #seconds

        folder_name = "transcription"
        if not os.path.isdir(folder_name):
            os.mkdir(folder_name)

        sound_filename=os.path.join(folder_name, f"{video_Id}.wav")
        sound.export(sound_filename,format="wav")
        whole_text = ""

        file_path=f"transcription/{video_Id}.wav"
        audio_file = sr.AudioFile(file_path)

        file_name = video_Id

        asi.settings.api_key="0dcb42ad01f440949f451b37097e1207"

        transcriber=asi.Transcriber()

        def transcribe_chunk(chunk):
            transcript=transcriber.transcribe(chunk)
            text=transcript.text
            return text

        with audio_file as source:
            duration = source.DURATION
            chunks = int(duration / chunk_length) + 1
            print(int(duration / chunk_length))
            for i in range(chunks-1):
                start = i * chunk_length
                end = min(start + chunk_length, duration)
                print(f"Transcribing chunk {i + 1}...")
                chunk_file = f"{file_name}_chunk_{i + 1}.wav"
                try:
                    text = transcribe_chunk(chunk_file)
                    os.remove(chunk_file)
                except sr.UnknownValueError as e:
                    print("Error:", "Not able to detect")
                else:
                    text = f"{text.capitalize()}."
                    print(chunk_file, ":", text)
                    whole_text += text

        text_filename = os.path.join(folder_name, f"{video_Id}.txt")

        with open(text_filename, 'w') as file:
            file.write(whole_text)

        return {
            "status": "success",
            "file": whole_text
        }


@app.route('/generateQuestions')
def GenerateQuestion():
    file_name = request.json['file_name']
    grade_id = request.json['grade_id']
    exam_id = request.json['exam_id']
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


if __name__ == '__main__':
    app.run(debug=True)