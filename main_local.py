import pandas as pd
import speech_recognition as sr
import pyttsx3
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv
from datetime import datetime
from login import login

from ask_gpt import ask_gpt

load_dotenv()

# Email sizes
snippet = 'snippet'
full = 'raw'

def get_message_details(service, message_id, size=snippet):
    message = service.users().messages().get(userId='me', id=message_id).execute()
    payload = message.get('payload', {})
    headers = payload.get('headers', [])

    details = {
        'id': message_id,
        size: message.get(size, ''),
        'internalDate': message.get('internalDate', ''),
        'isUnread': 'UNREAD' in message.get('labelIds', []),
        'isSpam': 'SPAM' in message.get('labelIds', [])
    }

    for header in headers:
        if header['name'] == 'Date':
            details['date'] = header['value']

    return details

def get_emails(service, query='', max_results=10):
    results = service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
    messages = results.get('messages', [])

    # Extract details for each message
    message_details = []
    for msg in messages:
        
        details = get_message_details(service, msg['id'])
        message_details.append(details)
    
    # Convert to DataFrame
    df = pd.DataFrame(message_details)

    # Convert timestamp to readable date
    df['internalDate'] = df['internalDate'].apply(lambda x: datetime.fromtimestamp(int(x)/1000).strftime('%Y-%m-%d %H:%M:%S'))
    
    # Writes to emails.csv
    df.to_csv("emails.csv", index=False)
    return df

def speak_text(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def get_voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            print(f"User said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return None
        except sr.RequestError:
            print("Sorry, my speech service is down.")
            return None

def main():
    service = login()
    emails = get_emails(service)
    print(emails)
    while True:
        question = get_voice_input()
        if question:
            response = ask_gpt(question, emails)
            print("\nGmail Assistant:\n\n" + response)
            speak_text(response)

if __name__ == "__main__":    
    main()
