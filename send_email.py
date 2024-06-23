import base64
from email.message import EmailMessage
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from main import login

# Path to the downloaded JSON credentials
CREDENTIALS_FILE = 'credentials.json'  # Ensure this is the correct path

def gmail_send_message(service, to, subject, content):
  """Create and send an email message
  Print the returned  message id
  Returns: Message object, including message id

  Load pre-authorized user credentials from the environment.
  TODO(developer) - See https://developers.google.com/identity
  for guides on implementing OAuth2 for the application.
  """

  try:
    message = EmailMessage()

    message.set_content(content)

    message["To"] = to
    message["Subject"] = subject

    # encoded message
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    create_message = {"raw": encoded_message}
    # pylint: disable=E1101
    send_message = (
        service.users()
        .messages()
        .send(userId="me", body=create_message)
        .execute()
    )
    print(f'Message Id: {send_message["id"]}') 
  except HttpError as error:
    print(f"An error occurred: {error}")
    send_message = None
  return send_message


service = login()
gmail_send_message(service, to="leungbraden@gmail.com", subject="Hi", content='sup')


