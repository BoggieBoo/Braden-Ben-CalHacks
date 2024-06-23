import requests
import json
import base64
import os
from dotenv import load_dotenv


# Your API key
API_KEY = os.getenv('GOOGLE_API_KEY')

# Define the request payload
payload = {
    "input": {
        "text": "Hello, this is a sample text to synthesize."
    },
    "voice": {
        "languageCode": "en-US",
        "name": "en-US-Wavenet-D",
        "ssmlGender": "MALE"
    },
    "audioConfig": {
        "audioEncoding": "mp3"
    }
}

# Make the POST request to the Text-to-Speech API
response = requests.post(
    f'https://texttospeech.googleapis.com/v1/text:synthesize?key={API_KEY}',
    headers={
        'Content-Type': 'application/json'
    },
    data=json.dumps(payload)
)

# Check for errors in the response
if response.status_code != 200:
    print(f"Error: {response.status_code}")
    print(response.json())
else:
    # Parse the JSON response
    response_json = response.json()
    audio_content = response_json['audioContent']

    # Decode the base64 audio content and save it as an MP3 file
    with open("output.mp3", "wb") as audio_file:
        audio_file.write(base64.b64decode(audio_content))

    print("Audio content written to output.mp3")