from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Scopes required for the Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly','https://www.googleapis.com/auth/gmail.send']

# Path to the downloaded JSON credentials
CREDENTIALS_FILE = 'credentials.json'  # Ensure this is the correct path

def login():
    # Perform OAuth 2.0 authorization with a specified static port
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    creds = flow.run_local_server(port=61159)  # Use a static port (e.g., 8080)

    # Build the Gmail API service
    service = build('gmail', 'v1', credentials=creds)
    return service
