#standard library Imports
import os
# Third party imports
from openai import OpenAI
from dotenv import load_dotenv
# Local Module imports
from tools import TOOLS, execute_tool_call
from Utilities.utilities import log


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

    MAX_STEPS = 5

    #chained tool calling
    for steps in range(MAX_STEPS):

        response = client.chat.completions.create( 
            model=os.getenv("MODEL"),
            messages=messages,
            tools=TOOLS
        )

        msg = response.choices[0].message

        if not msg.tool_calls:
            break


        log(f"Step {steps+1}: model requested {len(msg.tool_calls)} tool calls")
        

        messages.append(msg)

        for tool_call in msg.tool_calls:

            result = execute_tool_call(tool_call)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                }
            )

    else:
        fallback = "Sorry i couldn't finish this within the steps limit"
        messages.append({
            "role":"assistant",
            "content":fallback
        })

        print(f"AI:{fallback}")
        continue


    messages.append(
        {
            "role": "assistant",
            "content": msg.content
        }
    )

    print(f"AI: {msg.content or ''}")
