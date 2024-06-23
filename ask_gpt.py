import os
import pandas as pd
import re
from openai import OpenAI
from dotenv import load_dotenv
from io import StringIO
from send_email import gmail_send_message

def ask_gpt(question, emails, service):
    load_dotenv()

    # Convert DataFrame to CSV string
    csv_buffer = StringIO()
    emails.to_csv(csv_buffer, index=False)
    csv_string = csv_buffer.getvalue()

    #client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    client = OpenAI(api_key=api_key)
    prompt = (
        """You are a personal assistant who sends and summarizes my emails. Be conversational. Be friendly. Be concise."""
        """I get your response read out to me by a text-to-speech program. NEVER write a bullet list or a number list — NO LISTS."""
        """When prompted to write an email, split it into three parts, '####To: <recieving address (if not mentioned by the user, ask them)> ####Subject: <subject> ####Content: <content>"""
        """The email should conclude with 'Sent by Gmail Assistant'. No need to confirm if the email is ready to be sent, it is sent in the initial message."""
        """When I ask a question, answer it succinctly, but if it would be appropriate in a conversation to ask a clarifying question to """
        """keep the conversation flowing, then do so. But don't try to keep the conversation flowing if it seems like I am done with the """
        """conversation. Here is a table of emails I recently received:\n\n{emails}\n\nQuestion: {question}"""
    ).format(emails=csv_string, question=question)

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = response.choices[0].message.content
    pattern = r'####To:\s*(?P<to>[^\#\n]+)\s*####Subject:\s*(?P<subject>[^\#\n]+)\s*####Content:\s*(?P<content>.+)$'
    match = re.search(pattern, response_text, re.DOTALL)  # re.DOTALL allows '.' to match newlines in the content
    if match:
        to = match.group('to').strip()
        subject = match.group('subject').strip()
        content = match.group('content').strip()
        # Assuming you have a function to send emails
        gmail_send_message(to, subject, content, service)  # Your function to send the email
        return f"Email sent to {to} with subject '{subject}' and content '{content}"

    # Check if the response is in the expected format
    return response.choices[0].message.content