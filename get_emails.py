import pandas as pd
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
    