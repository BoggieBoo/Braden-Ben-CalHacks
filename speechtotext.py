import os
import json
import base64
import requests
from pydub import AudioSegment
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# Set your Google Cloud project ID and the path to your service account key file
PROJECT_ID = 'gmailassistant-427219'
CREDENTIALS_FILE = 'service.json'
AUDIO_FILE_PATH = 'output.mp3'

# Function to get an access token using the service account
def get_access_token():
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=['https://www.googleapis.com/auth/cloud-platform']
    )
    credentials.refresh(Request())
    return credentials.token

# Function to convert MP3 to WAV and read the audio file
def convert_and_read_audio(file_path):
    audio = AudioSegment.from_mp3(file_path)
    audio = audio.set_frame_rate(16000)  # Set frame rate to 16000 Hz for compatibility
    audio = audio.set_channels(1)  # Set to mono
    audio_content = audio.export(format="wav")
    return audio_content.read()

# Function to make the API request
def transcribe_audio(access_token, audio_content):
    url = 'https://speech.googleapis.com/v1/speech:recognize'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json; charset=utf-8'
    }
    payload = {
        "config": {
            "encoding": "LINEAR16",
            "sampleRateHertz": 16000,
            "languageCode": "en-US"
        },
        "audio": {
            "content": base64.b64encode(audio_content).decode('utf-8')
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    response_data = response.json()
    
    # Check for errors in the response
    if 'error' in response_data:
        raise Exception(f"API error: {response_data['error']['message']}")
    
    # Extract the transcribed text from the response
    transcription = ""
    if 'results' in response_data:
        for result in response_data['results']:
            transcription += result['alternatives'][0]['transcript']
    
    return transcription

# Main script
def main():
    try:
        access_token = get_access_token()
        audio_content = convert_and_read_audio(AUDIO_FILE_PATH)
        transcription = transcribe_audio(access_token, audio_content)
        return transcription
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == '__main__':
    transcription = main()
    if transcription:
        print("Transcription:")
        print(transcription)
