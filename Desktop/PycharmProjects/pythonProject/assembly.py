import assemblyai as asi

asi.settings.api_key="0dcb42ad01f440949f451b37097e1207"

FILE_URL = "https://il-cms-assets.s3.ap-south-1.amazonaws.com/media/1654754727452.mp4?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20240212T092115Z&X-Amz-SignedHeaders=host&X-Amz-Expires=3600&X-Amz-Credential=AKIA2R2EX7PZB3M2KJNB%2F20240212%2Fap-south-1%2Fs3%2Faws4_request&X-Amz-Signature=edc9e6ba332f04cd31c8704bb2888e1da3cfaa38135a62f2795ebad0dc1f4413"

transcriber = asi.Transcriber()
transcript = transcriber.transcribe(FILE_URL)

print(transcript.text)