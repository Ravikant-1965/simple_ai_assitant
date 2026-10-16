from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv() #by default looks for .env file

client = OpenAI(   # if the module is kept empty then it will automatically start calling a model
    base_url=os.getenv("BASE_URL"),  # here we specidied to call OLLAMA model
    api_key=os.getenv("API_KEY"),
)


messages = []

while True:
    user_input = input("Ravi: ")

    if user_input.lower() in ["Exit", "Bye", "quit"]:
        break

    messages.append(
        {
            "role":"user",
            "content":user_input
        }
    )

    response = client.chat.completions.create( 
        model=os.getenv("MODEL"),
        messages=messages
    )

    messages.append(
        {
            "role":"assistant",
            "content":response.choices[0].message.content
        }
    )

    print(f"AI : {response.choices[0].message.content}")

