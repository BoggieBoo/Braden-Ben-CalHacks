from openai import OpenAI
from dotenv import load_dotenv
import os


def ask_gpt(question, emails):
    load_dotenv()
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    response = client.chat.completions.create(
    messages=[{"role": "user", "content": f"Here is a csv of emails:\n{emails}\n\nQuestion: {question}\nAnswer:"}],model="gpt-4",)
    return response.choices[0].message.content


