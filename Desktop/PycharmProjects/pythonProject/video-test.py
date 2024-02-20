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
        #folder_name = "transcription"
        #video_filename = os.path.join(folder_name, f"{video_Id}.mp4")
        #video_bytes.export(video_filename, format="mp4")

        print(f"Video fetched Successfully")
        sound = AudioSegment.from_file(video_bytes, format="mp4")

        chunk_length = 25  #seconds

        folder_name = "transcription"
        if not os.path.isdir(folder_name):
            os.mkdir(folder_name)

        sound_filename=os.path.join(folder_name, f"{video_Id}.wav")
        sound.export(sound_filename,format="wav")

        file_path=f"transcription/{video_Id}.wav"
        audio_file = sr.AudioFile(file_path)
        print("Audio extracted successfully")

        def transcribe_chunk(chunk_index, chunk):
            with sr.AudioFile(chunk) as source:
                audio = r.record(source)  # read the entire audio file
                text = r.recognize_google(audio)  # perform speech recognition
            return chunk_index, text

        def transcribe_chunks(chunks):
            threads = []
            results = {}

            # Define a function to be executed by each thread
            def process_chunk(chunk_index, chunk):
                result = transcribe_chunk(chunk_index, chunk)
                results[result[0]] = result[1]

            # Create and start a thread for each chunk
            for idx, chunk in enumerate(chunks):
                thread = threading.Thread(target=process_chunk, args=(idx, chunk))
                thread.start()
                threads.append(thread)

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            # Sort the results based on chunk index and retrieve the text
            ordered_results = []
            sorted_keys=sorted(results)
            for key in sorted_keys:
                ordered_results.append(results[key])

            return ordered_results

        chunks=[]

        with audio_file as source:
            duration = source.DURATION
            print(int(duration / chunk_length))
            chunkss = int(duration / chunk_length) + 1
            chunks_del=chunkss
            for i in range(chunkss-1):
                start = i * chunk_length
                end = min(start + chunk_length, duration)
                print(f"Creating chunk {i + 1}...")
                chunk_file = f"{video_Id}_chunk_{i + 1}.wav"
                os.system(f"ffmpeg -i {file_path} -ss {start} -t {chunk_length} {chunk_file} -loglevel quiet")
                chunks.append(f"{video_Id}_chunk_{i+1}.wav")

        #define where to store all text
        whole_text=""
        print(f"Transcribing the chunks...")

        #transcribe the chunks
        whole_text_arr=transcribe_chunks(chunks)

        #save the text
        for i in range(len(whole_text_arr)):
            text=whole_text_arr[i]
            whole_text+=text

        print(f"Task completed successfully")

        os.path.join(folder_name, f"{video_Id}.txt")
        text_filename = f"transcription/{video_Id}.txt"
        with open(text_filename, 'w') as file:
            file.write(whole_text)

        for i in range(chunks_del-1):
            os.remove(f"{video_Id}_chunk_{i + 1}.wav")

        return {
            "status": "success",
            "file": text_filename
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