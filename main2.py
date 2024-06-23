from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from dotenv import load_dotenv
from datetime import datetime
from ask_gpt import ask_gpt
import os
import pandas as pd
from io import StringIO
import json
import logging

# Enable logging
logging.basicConfig(level=logging.DEBUG)

# Allow HTTP for local testing
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Scopes required for the Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.readonly']

# Path to the downloaded JSON credentials
CREDENTIALS_FILE = 'credentials.json'  # Ensure this is the correct path

# Load environment variables
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/login')
def login():
    logging.debug("Starting OAuth login flow")
    flow = Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for('oauth2callback', _external=True)
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['state'] = state
    logging.debug(f"Authorization URL: {authorization_url}")
    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    logging.debug("OAuth callback initiated")
    state = session.get('state')
    if not state:
        logging.error("State not found in session")
        return redirect(url_for('login'))

    flow = Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        state=state,
        redirect_uri=url_for('oauth2callback', _external=True)
    )
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)
    logging.debug("OAuth flow completed, credentials obtained")
    return redirect(url_for('index'))

def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

def get_gmail_service():
    credentials = Credentials(**session['credentials'])
    service = build('gmail', 'v1', credentials=credentials)
    return service

def get_message_details(service, message_id, size='snippet'):
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

    message_details = []
    for msg in messages:
        details = get_message_details(service, msg['id'])
        message_details.append(details)

    df = pd.DataFrame(message_details)
    df['internalDate'] = df['internalDate'].apply(lambda x: datetime.fromtimestamp(int(x)/1000).strftime('%Y-%m-%d %H:%M:%S'))
    df.to_csv("emails.csv", index=False)
    return df

@app.route('/')
def index():
    if 'credentials' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@socketio.on('message')
def handle_message(data):
    print('Received message:', data)
    question = data.get('question')
    emails = pd.DataFrame(data.get('emails', []))
    response = ask_gpt(question, emails)
    emit('response', {'data': response})

if __name__ == '__main__':
    # Clear the session to ensure a fresh OAuth flow
    with app.test_request_context():
        session.clear()
    socketio.run(app, debug=True)



# from flask import Flask, render_template, request, redirect, url_for, session
# from flask_socketio import SocketIO, emit
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import Flow
# from googleapiclient.discovery import build
# from dotenv import load_dotenv
# from datetime import datetime
# from ask_gpt import ask_gpt
# import os
# import pandas as pd
# from io import StringIO
# import json

# # overrides https reqs
# # os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# # Scopes required for the Gmail API
# SCOPES = ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.readonly']

# # Path to the downloaded JSON credentials
# CREDENTIALS_FILE = 'credentials.json'  # Ensure this is the correct path

# # Email sizes
# snippet = 'snippet'
# full = 'raw'

# # Load environment variables
# load_dotenv()
# app = Flask(__name__)
# app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')
# socketio = SocketIO(app, cors_allowed_origins="*")

# @app.route('/login')
# def login():
#     flow = Flow.from_client_secrets_file(CREDENTIALS_FILE, scopes=SCOPES, redirect_uri=url_for('oauth2callback', _external=True))
#     authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
#     session['state'] = state
#     return redirect(authorization_url)

# @app.route('/oauth2callback')
# def oauth2callback():
#     state = session['state']
#     flow = Flow.from_client_secrets_file(CREDENTIALS_FILE, scopes=SCOPES, state=state, redirect_uri=url_for('oauth2callback', _external=True))
#     flow.fetch_token(authorization_response=request.url)
#     credentials = flow.credentials
#     session['credentials'] = credentials_to_dict(credentials)
#     return redirect(url_for('index'))

# def credentials_to_dict(credentials):
#     return {'token': credentials.token, 'refresh_token': credentials.refresh_token, 'token_uri': credentials.token_uri, 'client_id': credentials.client_id, 'client_secret': credentials.client_secret, 'scopes': credentials.scopes}

# def get_gmail_service():
#     credentials = Credentials(**session['credentials'])
#     service = build('gmail', 'v1', credentials=credentials)
#     return service

# def get_message_details(service, message_id, size=snippet):
#     message = service.users().messages().get(userId='me', id=message_id).execute()
#     payload = message.get('payload', {})
#     headers = payload.get('headers', [])

#     details = {
#         'id': message_id,
#         size: message.get(size, ''),
#         'internalDate': message.get('internalDate', ''),
#         'isUnread': 'UNREAD' in message.get('labelIds', []),
#         'isSpam': 'SPAM' in message.get('labelIds', [])
#     }

#     for header in headers:
#         if header['name'] == 'Date':
#             details['date'] = header['value']

#     return details

# def get_emails(service, query='', max_results=10):
#     results = service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
#     messages = results.get('messages', [])

#     message_details = []
#     for msg in messages:
#         details = get_message_details(service, msg['id'])
#         message_details.append(details)

#     df = pd.DataFrame(message_details)
#     df['internalDate'] = df['internalDate'].apply(lambda x: datetime.fromtimestamp(int(x)/1000).strftime('%Y-%m-%d %H:%M:%S'))
#     df.to_csv("emails.csv", index=False)
#     return df

# @app.route('/')
# def index():
#     if 'credentials' not in session:
#         return redirect(url_for('login'))
#     return render_template('index.html')

# @socketio.on('message')
# def handle_message(data):
#     print('Received message:', data)
#     question = data.get('question')
#     emails = pd.DataFrame(data.get('emails', []))
#     response = ask_gpt(question, emails)
#     emit('response', {'data': response})

# if __name__ == '__main__':
#     socketio.run(app, debug=True)