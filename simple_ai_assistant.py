from openai import OpenAI
from dotenv import load_dotenv
import json

from tools import TOOLS, FUNCTION_NAME_TO_FUNCTION_MAP

import os

load_dotenv() #by default looks for .env file

client = OpenAI(   # if the module is kept empty then it will automatically start calling a model
    base_url=os.getenv("BASE_URL"),  # here we specidied to call OLLAMA model
    api_key=os.getenv("API_KEY"),
)


messages = []

messages.append(
    {
        "role":"system",
        "content":"You are humble assitant. Resopond within 20 words"
    }
)

while True:
    user_input = input("Ravi: ")

    if user_input.lower() in ["exit", "bye", "quit"]:
        break

    messages.append(
        {
            "role":"user",
            "content":user_input
        }
    )

    #chained tool calling
    while True:

        response = client.chat.completions.create( 
            model=os.getenv("MODEL"),
            messages=messages,
            tools=TOOLS
        )

        msg = response.choices[0].message

        messages.append(msg)

        for tool_call in msg.tool_calls:

            func_name = tool_call.function.name

            func_args = json.loads(tool_call.function.arguments or "{}")

            fn = FUNCTION_NAME_TO_FUNCTION_MAP[func_name]

            result = fn(**func_args)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                }
            )

    messages.append(
        {
            "role": "assistant",
            "content": msg.content
        }
    )

    print(f"AI: {msg.content}")

        
