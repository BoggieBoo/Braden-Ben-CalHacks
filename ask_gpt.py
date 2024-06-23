from openai import OpenAI
from dotenv import load_dotenv
from io import StringIO
import os
import pandas as pd

def ask_gpt(question, emails):
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
        """You are a personal assistant named Ben who summarizes my emails. Be conversational. Be friendly. Be concise."""
        """I get your response read out to me by a text-to-speech program. NEVER write a bullet list or a number list — NO LISTS. """
        """When I ask a question, answer it succinctly, but if it would be appropriate in a conversation to ask a clarifying question to """
        """keep the conversation flowing, then do so. But don't try to keep the conversation flowing if it seems like I am done with the """
        """conversation. Here is a table of emails I recently received:\n\n{emails}\n\nQuestion: {question}"""
    ).format(emails=csv_string, question=question)

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    #print(response.choices[0].message.content)
    # Check if the response is in the expected format
    return response.choices[0].message.content