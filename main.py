import pandas as pd
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime
from ask_gpt import ask_gpt

# Scopes required for the Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Path to the downloaded JSON credentials
CREDENTIALS_FILE = 'credentials.json'  # Ensure this is the correct path

def login():
    # Perform OAuth 2.0 authorization with a specified static port
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    creds = flow.run_local_server(port=61159)  # Use a static port (e.g., 8080)

    # Build the Gmail API service
    service = build('gmail', 'v1', credentials=creds)
    return service

def get_message_details(service, message_id):
    message = service.users().messages().get(userId='me', id=message_id).execute()
    payload = message.get('payload', {})
    headers = payload.get('headers', [])

    details = {
        'id': message_id,
        'snippet': message.get('snippet', ''),
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
    
    # Display DataFrame
    return df.to_csv('emails.csv', index=False)

def main():
    service = login()
    emails = get_emails(service)
    while True:
        question = input("Please enter something: ")
        print(ask_gpt(question, emails))
    
main()